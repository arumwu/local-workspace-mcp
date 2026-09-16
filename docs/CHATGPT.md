# 一般 ChatGPT 對話：完整連線教學

[English](CHATGPT.en.md) · [本機環境安裝](README.zh-TW.md) · [驗證紀錄](VALIDATION.md)

目標是在 **ChatGPT 的一般「對話」**使用本機檔案、文件與 Python 工具。
本機 MCP 設定或 Codex／Work 能使用工具，不代表一般對話已接通。
本教學使用 OpenAI 官方私人通道，無須公開你的電腦或租伺服器。

2026-09-17 已在一般 ChatGPT 網頁對話成功呼叫 `run_python`，重啟通道後也成功。
本機 ChatGPT App 的一般對話仍待獨立驗證；不能把網頁成功寫成 App 已驗證。

## 1. 安裝本機工具

下載 [main 最新原始碼 ZIP](https://github.com/arumwu/local-workspace-mcp/archive/refs/heads/main.zip)，
解壓縮到長期保留的位置。依[環境教學](README.zh-TW.md)安裝 Python、uv、Node、ripgrep 與 Docker。
在專案目錄執行，將範例路徑換成自己的：

```sh
./Install.command --workspace /absolute/path/task-files \
  --state /absolute/path/private-state --mode full
```

`full` 提供 41 個工具，包含檔案、終端及 Docker 文件處理。這是完整使用者權限，不是資料夾沙盒。
`documents` 是較小的隔離文件模式。完整權限須由你明確選擇，預設仍是 documents。
新版安裝器**預設不更動 Codex／本機 STDIO 用戶端設定**；真正接上 ChatGPT 是下一步。
舊版 v0.1.1-alpha.1 ZIP 不含這次修正，請使用上面的 main ZIP。

## 2. 建立官方私人通道與金鑰

在自己的 OpenAI Platform 帳戶，進入[通道設定](https://platform.openai.com/settings/organization/tunnels)：
建立通道，名稱例如 `ChatGPT Local Workspace`，關聯你要使用的 ChatGPT 工作區，記下 `tunnel_...` ID。
再到 API keys 建立受限制的 runtime key，只給 **Tunnels Read + Use**。
建立／管理通道的權限與執行通道的權限不同；不要給執行金鑰不需要的模型或管理權限。
帳號是否有這些功能，以及費用，以你帳戶與官方當前條件為準。

從 [OpenAI 官方 tunnel-client releases](https://github.com/openai/tunnel-client/releases)
下載符合系統架構的版本；本次驗證為 **v0.0.14，macOS arm64**。核對官方 SHA256，解壓縮到自己的工具目錄。
以下以 `tunnel-client` 已在 PATH 為例；也可以使用二進位檔的絕對路徑。

不要把金鑰貼在對話、Git、命令列引數或工作資料夾。這段會以隱藏輸入儲存，且不覆寫既有金鑰：

```sh
python3 - <<'PY'
import getpass, os
from pathlib import Path
path = Path(input('金鑰檔案完整路徑（放在私有設定資料夾）: ')).expanduser()
key = getpass.getpass('貼上 Tunnels runtime key: ').strip()
if not key.startswith('sk-'):
    raise SystemExit('金鑰格式不正確')
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as f:
    f.write(key + '\n')
PY
```

## 3. 設定並啟動通道

將路徑、ID 換成自己的值：

```sh
tunnel-client init --sample sample_mcp_stdio_local \
  --profile local-workspace --profile-dir /absolute/path/private-state/tunnel-profiles \
  --tunnel-id tunnel_YOUR_ID \
  --mcp-command /absolute/path/private-state/launch.sh \
  --health-listen-addr 127.0.0.1:0
```

開啟產生的 `local-workspace.yaml`，把 `control_plane.api_key` 改成金鑰檔案引用，**不是金鑰內容**：

```yaml
api_key: "file:/absolute/path/private-state/runtime-key"
```

在 `health` 下設定 `url_file`，方便檢查；檔案位置仍使用私有設定資料夾：

```yaml
health:
  listen_addr: "127.0.0.1:0"
  url_file: "/absolute/path/private-state/tunnel-health.url"
```

```sh
chmod 600 /absolute/path/private-state/tunnel-profiles/local-workspace.yaml
tunnel-client doctor --config /absolute/path/private-state/tunnel-profiles/local-workspace.yaml
tunnel-client run --config /absolute/path/private-state/tunnel-profiles/local-workspace.yaml
```

這個前景程序需要保持執行；此時關閉終端機會中斷連線。正式使用可接著設定第 5 節的登入自啟。
`/healthz` 與 `/readyz` 均需成功，然後做實際對話測試；只看程序存在不算接通。

## 4. 在 ChatGPT 連線

1. ChatGPT 設定 → 安全性與登入 → 開啟開發者模式（帳戶必須支援）。
2. 外掛程式 → 建立應用程式，名稱填 `Local Workspace MCP`。
3. 連線選 **通道**，選剛才建立的通道或輸入 ID。
4. 這個 STDIO 通道的驗證選 **無驗證**：通道本身已有帳戶／工作區與 runtime key 控制，並非公開匿名 HTTP。
5. 閱讀權限與風險，建立並連線。應能看到 `run_python`、`host_read_file` 等工具。
6. 開新的普通「對話」，選取／提及這個外掛，貼上：

> 使用 Local Workspace MCP，先呼叫 get_workflow_instructions，再用 run_python 執行 print('CHATGPT_LOCAL_MCP_OK')。不要使用內建 Python 代替。回報 stdout 與 exit code。

成功應回傳 `CHATGPT_LOCAL_MCP_OK` 與 exit code `0`，且有實際工具呼叫。
本機 App 也必須在它自己的新對話執行同一測試；不可只看共用設定列表就宣稱成功。

## 5. macOS 登入後自動啟動

先停止第 3 節的前景程序（Ctrl-C）。若使用官方 `runtimes connect`，先執行
`tunnel-client runtimes stop local-workspace`，避免同一通道跑兩份。

在專案目錄執行（需 Xcode Command Line Tools 的 `xcrun clang`）：

```sh
python3 scripts/install_macos_autostart.py \
  --tunnel-client /absolute/path/tunnel-client \
  --config /absolute/path/private-state/tunnel-profiles/local-workspace.yaml \
  --name 'ChatGPT 本機工具'
```

它建立 `/Applications/ChatGPT 本機工具.app` 與 `~/Library/LaunchAgents/ChatGPT 本機工具.plist`。
這是小型、在本機編譯並 ad-hoc 簽章的啟動程式，不是公證的下載版 App。
macOS 背景項目會關聯這個有名稱的 App，不再以 `/bin/sh` 當正式入口。
通道、Python、Node 與資料仍留在你指定的位置。存在 Storage Guard 時會先檢查；磁碟缺失就不啟動。
服務崩潰會由 launchd 重啟；每 30 秒最多重試一次。**登入後**才啟動，不是開機未登入時執行。
Docker 必須另外保持運作；`run_python` 不會代替你啟動 Docker Desktop。

```sh
launchctl print "gui/$(id -u)/ChatGPT 本機工具"
```

確認 `state = running`，用 health URL 檔案中的網址檢查 `/readyz`，再重做第 4 節測試。
重複安裝遇到同名檔會停止，不會覆蓋其他服務。要停用／移除這個登入項目：

```sh
launchctl bootout "gui/$(id -u)/ChatGPT 本機工具"
rm "$HOME/Library/LaunchAgents/ChatGPT 本機工具.plist"
```

再從 ChatGPT 斷開外掛。確認不再使用後，可刪除對應啟動 App；你的文件與金鑰不會被此命令刪掉。
不要為了清除舊名稱重設整台 Mac 的登入項目資料庫，或刪除無法辨識用途的其他 `sh`。

## 產出、暫存與限制

`run_python` 的輸入在 `/workspace`（唯讀）、產出在 `/output`，對應工作資料夾的 `exports`。
每次是可拋棄的 Docker 工作，結束就移除容器；產出保留。
通道與工具程序需常駐，有記憶體用量；不要同時留著測試用的重複服務。
STDIO 通道回傳的是本機檔案路徑，不會自動變成 ChatGPT 可下載的附件。
完整權限工具可以修改其他檔案與啟動持續執行的程序；這些不保證自動清理，任務結束應停止自己建立的程序。

官方參考：[連接 ChatGPT 外掛](https://developers.openai.com/plugins/deploy/connect-chatgpt) ·
[Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)。
