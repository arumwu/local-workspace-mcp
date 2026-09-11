"""Single-owner OAuth provider. SDK handles DCR, PKCE and protocol validation.

No identity federation or URL fetching. Rotating refresh tokens; restart revokes everything.
"""

import hashlib
import hmac
import html
import re
import secrets
import time
from urllib.parse import urlsplit

from mcp.server.auth.middleware.client_auth import AuthenticationError, ClientAuthenticator
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizeError,
    RefreshToken,
    RegistrationError,
    TokenError,
    construct_redirect_uri,
)
from mcp.shared.auth import OAuthToken
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response

SCOPE = "workspace"
TTL = 3600
REFRESH_TTL = 8 * 3600


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class OwnerOAuth:
    def __init__(
        self,
        base_url: str,
        owner_secret: str,
        writable: bool,
        redirect_hosts: tuple[str, ...] = ("chatgpt.com", "chat.openai.com"),
    ):
        self.full_access = False
        self.base = base_url
        self.resource = base_url + "/mcp"
        self.secret_hash = digest(owner_secret)
        self.writable = writable
        self.redirect_hosts = redirect_hosts
        self.clients = {}
        self.pending = {}
        self.codes = {}
        self.tokens = {}
        self.refresh = {}
        self.spent_refresh = {}

    def clean(self):
        now = time.time()
        self.pending = {k: v for k, v in self.pending.items() if v[2] > now}
        self.codes = {k: v for k, v in self.codes.items() if v.expires_at > now}
        self.tokens = {k: v for k, v in self.tokens.items() if v.expires_at > now}
        self.refresh = {k: v for k, v in self.refresh.items() if v.expires_at > now}
        self.spent_refresh = {k: v for k, v in self.spent_refresh.items() if v[1] > now}

    async def get_client(self, client_id):
        return self.clients.get(client_id)

    async def register_client(self, client_info):
        if len(self.clients) >= 128:
            raise RegistrationError(
                "invalid_client_metadata", "Registration capacity reached; restart server."
            )
        for uri in client_info.redirect_uris or []:
            p = urlsplit(str(uri))
            if (
                p.scheme != "https"
                or p.hostname not in self.redirect_hosts
                or p.port not in (None, 443)
                or p.username
                or p.password
                or p.fragment
            ):
                raise RegistrationError(
                    "invalid_redirect_uri", "Redirect must use an allowed HTTPS hostname."
                )
        if set(client_info.grant_types) != {"authorization_code", "refresh_token"}:
            raise RegistrationError(
                "invalid_client_metadata", "Only authorization_code and refresh_token are supported."
            )
        self.clients[client_info.client_id] = client_info

    async def authorize(self, client, params):
        self.clean()
        if params.resource not in (None, self.resource):
            raise AuthorizeError("invalid_request", "Wrong resource.")
        if not re.fullmatch(r"[A-Za-z0-9_-]{43}", params.code_challenge):
            raise AuthorizeError("invalid_request", "S256 PKCE required.")
        if len(self.pending) >= 128 or len(self.refresh) >= 128:
            raise AuthorizeError("temporarily_unavailable", "Capacity reached.")
        request_id = secrets.token_urlsafe(32)
        self.pending[request_id] = (client, params, time.time() + 300, None)
        return self.base + "/consent?request=" + request_id

    async def consent(self, request):
        self.clean()
        rid = request.query_params.get("request", "")
        item = self.pending.get(rid)
        if not item:
            return PlainTextResponse("Expired request. Reconnect from your MCP client.", 400)
        client, params, expiry, csrf_hash = item
        if request.method == "GET":
            csrf = secrets.token_urlsafe(32)
            self.pending[rid] = (client, params, expiry, digest(csrf))
            capability = (
                "Read workspace files; create text files; Python (if enabled) can modify/delete exports"
                if self.writable
                else "Read text files only"
            )
            if self.full_access:
                capability = (
                    "FULL user-account access: read/change/delete files, run programs, network access, "
                    "stop processes; configured peer computers included. "
                    "Directory settings are NOT a sandbox."
                )
            page = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Authorize Local Workspace MCP</title><body>
<h1>Authorize access to your workspace</h1>
<p>Only continue if you started this connection yourself.</p>
<p>Client (unverified name): <strong>{html.escape(client.client_name or client.client_id)}</strong></p>
<p>Return address: <code>{html.escape(str(params.redirect_uri))}</code></p>
<p>Permission: <strong>{capability}</strong>.</p>
<p>Access tokens last one hour; the connection can renew for up to eight hours.</p>
<p>File contents will be sent to your AI provider. This is not an OpenAI login page.</p>
<form method="post"><input type="hidden" name="csrf" value="{csrf}">
<label>Owner key (from your local key file)<br>
<input type="password" name="owner_key" required autocomplete="off" size="48"></label>
<p><button type="submit">Authorize this connection</button></p></form>
<p>To cancel, close this page. Never paste the owner key into an AI conversation.</p></body></html>'''
            response = HTMLResponse(page)
            response.set_cookie(
                "lwmcp_consent", csrf, secure=True, httponly=True, samesite="strict", max_age=300
            )
            return response
        form = await request.form()
        csrf = str(form.get("csrf", ""))
        cookie = request.cookies.get("lwmcp_consent", "")
        if (
            not csrf_hash
            or not hmac.compare_digest(digest(csrf), csrf_hash)
            or not hmac.compare_digest(csrf, cookie)
            or request.headers.get("origin") != self.base
        ):
            return PlainTextResponse("Invalid consent request.", 403)
        # A failed key consumes the request; there is no reusable login session.
        self.pending.pop(rid, None)
        if not hmac.compare_digest(digest(str(form.get("owner_key", ""))), self.secret_hash):
            return PlainTextResponse("Authorization refused. Start a new connection.", 403)
        code = secrets.token_urlsafe(32)
        self.codes[digest(code)] = AuthorizationCode(
            code=code,
            scopes=[SCOPE],
            expires_at=time.time() + 60,
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=self.resource,
        )
        response = RedirectResponse(
            construct_redirect_uri(str(params.redirect_uri), code=code, state=params.state), 303
        )
        response.delete_cookie("lwmcp_consent", secure=True, httponly=True, samesite="strict")
        return response

    async def load_authorization_code(self, client, authorization_code):
        self.clean()
        code = self.codes.get(digest(authorization_code))
        return code if code and code.client_id == client.client_id else None

    async def exchange_authorization_code(self, client, authorization_code):
        code = self.codes.pop(digest(authorization_code.code), None)
        if not code or code.expires_at <= time.time() or code.client_id != client.client_id:
            raise TokenError("invalid_grant", "Code expired or already used.")
        return self.issue(client.client_id, secrets.token_urlsafe(16), int(time.time()) + REFRESH_TTL)

    def issue(self, client_id, family, deadline):
        token, refresh = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        expires_in = min(TTL, max(1, deadline - int(time.time())))
        self.tokens[digest(token)] = AccessToken(
            token=digest(token),
            client_id=client_id,
            scopes=[SCOPE],
            expires_at=int(time.time()) + expires_in,
            resource=self.resource,
            subject=family,
        )
        self.refresh[digest(refresh)] = RefreshToken(
            token=digest(refresh),
            client_id=client_id,
            scopes=[SCOPE],
            expires_at=deadline,
            resource=self.resource,
            subject=family,
        )
        return OAuthToken(
            access_token=token, refresh_token=refresh, token_type="Bearer", expires_in=expires_in, scope=SCOPE
        )

    def revoke_family(self, family):
        self.tokens = {k: v for k, v in self.tokens.items() if v.subject != family}
        self.refresh = {k: v for k, v in self.refresh.items() if v.subject != family}

    async def load_access_token(self, token):
        self.clean()
        return self.tokens.get(digest(token))

    async def load_refresh_token(self, client, refresh_token):
        self.clean()
        key = digest(refresh_token)
        spent = self.spent_refresh.get(key)
        if spent and spent[2] == client.client_id:
            self.revoke_family(spent[0])
            return None
        token = self.refresh.get(key)
        return token if token and token.client_id == client.client_id else None

    async def exchange_refresh_token(self, client, refresh_token, scopes):
        token = self.refresh.pop(refresh_token.token, None)
        if (
            not token
            or token.expires_at <= time.time()
            or token.client_id != client.client_id
            or scopes != [SCOPE]
        ):
            raise TokenError("invalid_grant", "Refresh token expired or already used.")
        if len(self.spent_refresh) >= 4096:
            self.revoke_family(token.subject)
            raise TokenError("invalid_grant", "Refresh capacity reached; reconnect.")
        self.spent_refresh[token.token] = (token.subject, token.expires_at, token.client_id)
        self.revoke_family(token.subject)
        return self.issue(client.client_id, token.subject, token.expires_at)

    async def revoke_token(self, token):
        self.revoke_family(token.subject)

    async def revoke_request(self, request):
        """RFC 7009 endpoint, including public clients without a client_secret form field.

        The SDK 1.30 handler incorrectly requires that field even for public clients.
        Keep SDK client authentication; only handle token selection/revocation here.
        """
        try:
            client = await ClientAuthenticator(self).authenticate_request(request)
        except AuthenticationError:
            return JSONResponse({"error": "invalid_client"}, status_code=401)
        form = await request.form()
        raw = form.get("token")
        if not isinstance(raw, str) or not raw:
            return JSONResponse({"error": "invalid_request"}, status_code=400)
        token = await self.load_access_token(raw) or await self.load_refresh_token(client, raw)
        if token and token.client_id == client.client_id:
            await self.revoke_token(token)
        return Response(status_code=200, headers={"Cache-Control": "no-store"})
