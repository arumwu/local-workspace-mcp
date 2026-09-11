import base64
import hashlib
import json
import re
import secrets
from urllib.parse import parse_qs, urlsplit

import pytest
from starlette.testclient import TestClient

from local_workspace_mcp.auth import digest
from local_workspace_mcp.server import create_server, http_app

BASE = "https://mcp.example.com"
REDIRECT = "https://chatgpt.com/connector_platform/oauth_redirect"


@pytest.fixture
def service(tmp_path):
    secret = secrets.token_urlsafe(32)
    mcp, ws, auth = create_server(tmp_path, writable=True, base_url=BASE, owner_secret=secret)
    with TestClient(http_app(mcp, BASE, auth), base_url=BASE) as client:
        yield client, mcp, ws, auth, secret, tmp_path
    ws.close()


def register(client, redirect=REDIRECT):
    return client.post(
        "/register",
        json={
            "client_name": "Test Client",
            "redirect_uris": [redirect],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none",
            "scope": "workspace",
        },
    )


def begin(client, client_id, **overrides):
    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT,
        "response_type": "code",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "scope": "workspace",
        "state": "original-state",
        "resource": BASE + "/mcp",
    }
    params.update(overrides)
    res = client.get("/authorize", params=params, follow_redirects=False)
    return res, verifier


def consent(client, location, secret, **overrides):
    page = client.get(location)
    assert page.status_code == 200, page.text
    csrf = re.search(r'name="csrf" value="([^"]+)"', page.text).group(1)
    data = {"csrf": csrf, "owner_key": secret}
    data.update(overrides)
    return client.post(location, data=data, headers={"Origin": BASE}, follow_redirects=False)


def authorize(client, secret):
    reg = register(client)
    assert reg.status_code == 201, reg.text
    cid = reg.json()["client_id"]
    start, verifier = begin(client, cid)
    assert start.status_code == 302, start.text
    result = consent(client, start.headers["location"], secret)
    assert result.status_code == 303, result.text
    query = parse_qs(urlsplit(result.headers["location"]).query)
    assert query["state"] == ["original-state"]
    code = query["code"][0]
    data = {
        "grant_type": "authorization_code",
        "client_id": cid,
        "code": code,
        "code_verifier": verifier,
        "redirect_uri": REDIRECT,
        "resource": BASE + "/mcp",
    }
    return cid, data


def rpc(client, token, method, params=None, request_id=1):
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json, text/event-stream"}
    body = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        body["params"] = params
    return client.post("/mcp", json=body, headers=headers)


def test_oauth_mcp_flow_and_artifact(service):
    client, mcp, ws, auth, secret, root = service
    cid, data = authorize(client, secret)
    exchanged = client.post("/token", data=data)
    assert exchanged.status_code == 200, exchanged.text
    token = exchanged.json()["access_token"]
    init = rpc(
        client,
        token,
        "initialize",
        {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}},
    )
    assert init.status_code == 200, init.text
    assert init.json()["result"]["serverInfo"]["name"] == "Local Workspace MCP"
    tools = rpc(client, token, "tools/list").json()["result"]["tools"]
    assert "create_text" in {t["name"] for t in tools}
    result = rpc(
        client,
        token,
        "tools/call",
        {"name": "create_text", "arguments": {"path": "new.md", "content": "hello"}},
    )
    assert result.status_code == 200, result.text
    assert (root / "new.md").read_text() == "hello"
    (root / "exports").mkdir()
    (root / "exports/report.txt").write_text("report")
    link_result = rpc(
        client, token, "tools/call", {"name": "get_download_link", "arguments": {"filename": "report.txt"}}
    ).json()
    url = json.loads(link_result["result"]["content"][0]["text"])["url"]
    download = client.get(url)
    assert download.content == b"report"
    assert download.headers["content-disposition"].startswith("attachment;")
    assert download.headers["cache-control"] == "no-store"
    (root / "exports/report.txt").write_text("changed")
    assert client.get(url).status_code == 410
    assert client.post("/token", data=data).status_code == 400  # code cannot be reused
    revoke = client.post("/revoke", data={"token": token, "client_id": cid})
    assert revoke.status_code == 200, revoke.text
    assert rpc(client, token, "tools/list").status_code == 401


def test_pkce_csrf_redirect_and_resource(service):
    client, _, _, _, secret, _ = service
    assert register(client, "https://evil.example/callback").status_code == 400
    reg = register(client).json()
    res, _ = begin(client, reg["client_id"], resource="https://other.example/mcp")
    assert "error=" in res.headers["location"]
    res, _ = begin(client, reg["client_id"])
    bad = consent(client, res.headers["location"], secret, csrf="wrong")
    assert bad.status_code == 403
    cid, data = authorize(client, secret)
    assert client.post("/token", data={**data, "code_verifier": "wrong"}).status_code == 400
    assert (
        client.post("/token", data={**data, "redirect_uri": "https://chatgpt.com/wrong"}).status_code == 400
    )
    assert client.post("/token", data=data).status_code == 200


def test_no_auth_host_origin_body(service):
    client, _, _, _, _, _ = service
    assert client.post("/mcp", json={}).status_code == 401
    assert client.get("/health", headers={"Host": "evil.example"}).status_code == 421
    assert client.get("/health", headers={"Origin": "https://evil.example"}).status_code == 403
    assert client.post("/token", content=b"x" * (2 * 1024 * 1024 + 1)).status_code == 413
    meta = client.get("/.well-known/oauth-authorization-server").json()
    assert "S256" in meta["code_challenge_methods_supported"]
    resource = client.get("/.well-known/oauth-protected-resource/mcp").json()
    assert resource["resource"] == BASE + "/mcp"


def test_refresh_rotation_and_replay(service):
    client, _, _, auth, secret, _ = service
    cid, data = authorize(client, secret)
    tokens = client.post("/token", data=data).json()
    form = {"client_id": cid, "grant_type": "refresh_token", "refresh_token": tokens["refresh_token"]}
    renewed = client.post("/token", data=form)
    assert renewed.status_code == 200, renewed.text
    assert rpc(client, tokens["access_token"], "tools/list").status_code == 401
    assert rpc(client, renewed.json()["access_token"], "tools/list").status_code == 200
    assert client.post("/token", data=form).status_code == 400
    assert rpc(client, renewed.json()["access_token"], "tools/list").status_code == 401
    assert digest(tokens["access_token"]) not in auth.tokens


def test_wrong_owner_key(service):
    client, _, _, _, _, _ = service
    cid = register(client).json()["client_id"]
    res, _ = begin(client, cid)
    assert consent(client, res.headers["location"], "wrong").status_code == 403
    assert client.get(res.headers["location"]).status_code == 400
