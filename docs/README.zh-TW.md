# 中文安裝教學

[專案首頁](https://github.com/arumwu/local-workspace-mcp) · [English](https://github.com/arumwu/local-workspace-mcp/blob/main/docs/README.en.md)

適用版本：**v0.1.1-alpha.1**。主要對象：使用 Mac 與 ChatGPT 桌面版的人。

**支援 Windows，已完成驗證。**
本頁的 Homebrew 與雙擊 `Install.command` 步驟適用於 Mac；目前沒有原生 Windows 安裝器。

安裝完成後，ChatGPT 可以透過這套工具讀取本機檔案、處理文件，或在你啟用完整模式後執行程式。
這份教學走本機連線，不需要公開網址，也不需要另外租雲端主機。

## 1. 先確認你用的是哪個介面

打開 ChatGPT 桌面版的「設定 → MCP 伺服器」。
如果新增伺服器時可以選「標準輸入／輸出」，就是本教學使用的連線方式。英文名稱是 **STDIO**。

如果只有填網址的欄位，或你正在使用瀏覽器裡的 ChatGPT，先看[進階連線說明](https://github.com/arumwu/local-workspace-mcp/blob/main/docs/CONNECT.md)。不要把 `127.0.0.1` 當成網頁版可以直接使用的網址。

## 2. 下載哪個檔案？

打開[版本下載頁](https://github.com/arumwu/local-workspace-mcp/releases/tag/v0.1.1-alpha.1)，找到 **Assets**（附件）。

下載：**`local-workspace-mcp-v0.1.1-alpha.1.zip`**。

`.whl` 是給熟悉 Python 套件的人使用，單靠它不包含完整安裝器、Node 引擎與文件容器。
`SHA256SUMS-v0.1.1-alpha.1.txt` 是核對下載檔案的檢查碼，一般使用者不需要打開它來安裝。

解壓縮後，保留整個 `local-workspace-mcp` 資料夾。先移到準備長期保留的位置，再開始安裝。
不要裝好後只留下 `Install.command`，也不要把整個資料夾當作下載暫存刪掉。

## 3. 安裝前需要準備什麼？

目前仍是測試版原始碼安裝包，需要幾個現成工具。
安裝器會檢查是否缺少工具；缺少時會停下並說明，不會自行安裝全域軟體。

| 工具 | 用途 | 什麼時候需要 |
|---|---|---|
| Python 3.12+ | 執行本專案 | 所有模式；終端機要能找到 `python3` |
| uv | 安裝本專案需要的 Python 套件 | 所有模式 |
| Node.js 20.9+ 與 npm | 執行完整模式的本機工具引擎 | 完整模式 |
| ripgrep（指令叫 `rg`） | 快速搜尋檔案內容 | 完整模式 |
| Docker Desktop | 提供文件處理的隔離環境 | Word、Excel、簡報、PDF、圖表等隔離工作 |
| 已安裝的 Chrome／Chromium | 本機 `host_write_pdf` 工具產生 PDF | 使用這個特定 PDF 工具時 |

### 已有 Homebrew 的 Mac

Homebrew 是 Mac 的套件安裝工具。如果電腦已經有它，可以在終端機準備常用工具：

```sh
brew install python uv node ripgrep
```

沒有 Homebrew 時，請先依[Homebrew 官方安裝說明](https://brew.sh/)處理。
uv 也提供[自己的官方安裝方式](https://docs.astral.sh/uv/getting-started/installation/)。

Docker Desktop 請依[官方 Mac 安裝說明](https://docs.docker.com/desktop/setup/install/mac-install/)安裝。
**安裝完還要開啟 Docker Desktop，等它開始運作。** 只有把 app 放進「應用程式」還不夠。

如果這台電腦有公司規定的安裝或儲存位置，依公司規定準備工具。

## 4. 雙擊安裝

雙擊解壓縮資料夾內的 **`Install.command`**。
它會打開終端機，依序詢問下面三件事。

### 工作資料夾

用來放要交給 AI 處理的資料。可以輸入自己的完整路徑，也可以按 Enter 使用顯示的預設值。
預設是程式資料夾裡的 `workspace`。

建議先放幾個測試檔案，不要直接選整個使用者家目錄。

### 私有設定資料夾

用來放啟動器、工具設定與安裝紀錄。
按 Enter 可使用預設位置：程式資料夾裡的 `.local/state`。開頭是點的資料夾在 Finder 通常會隱藏。

它必須放在工作資料夾之外；不要把設定和要交給 AI 的資料混在一起。

### 是否啟用完整電腦工具

輸入 **`y`**：啟用完整模式，能修改檔案、執行命令、連網及管理程序，權限等同目前登入的使用者。

直接按 **Enter**：使用預設文件模式。文件程式在 Docker 裡執行，原始輸入只能讀取，產出寫到 `exports`。

不確定時選文件模式。需要更多能力時，可以重跑同一份安裝器改用完整模式。

第一次執行會下載套件並建立文件環境，需要網路。請等到看到「安裝完成」再關閉視窗。
後續文件工作的隔離環境本身沒有網路；完整模式的本機命令則可以連網。

## 5. 安裝器會幫你設定什麼？

安裝器會把啟動器加入 ChatGPT 桌面版／Codex 共用的 MCP 設定，通常不用自己填名稱或指令。
[OpenAI 官方說明](https://learn.chatgpt.com/zh-Hant/docs/extend/mcp)確認同一部主機上的桌面版與 Codex 共用這份設定。

它會：

- 寫入前備份原本的設定檔，保留其他 MCP、註解與設定。
- 重裝時沿用已經存在的相同啟動器，保留你自訂的名稱與引數。
- 如果原先是停用狀態，保留停用；如果同名項目指向別的程式，就停止，不覆蓋。
- 把登錄名稱、設定檔與備份位置記錄在私有設定資料夾的 `client-registration.json`。

安裝器不會重新啟動你正在使用的 ChatGPT，也不會改變你的其他權限規則。

## 6. 回到 ChatGPT 開始使用

回到「設定 → MCP 伺服器」，找 `local-workspace`，或你先前自己取的名稱。
確認它已啟用，再重新載入 MCP 伺服器，或開啟一個新的工作。

若剛建立的項目沒有立即出現，先重新載入設定。不要急著手動新增第二個一樣的伺服器。

可以先放一個不重要的 CSV 到工作資料夾，然後對 ChatGPT 說：

> 請列出工作資料夾裡的檔案，再讀取這份 CSV。先告訴我欄位和總筆數。

確認讀到正確資料後，再試：

> 請做成一份 Excel 報表和長條圖，核對總額，並告訴我檔案存在哪裡。

如果 ChatGPT 說找不到工具，請確認目前使用的模式能使用本機 MCP，以及伺服器已連線。
看到設定項目不等於已完成實際對話驗收；要真的讀到檔案、產出文件才算。

## 7. 檔案放在哪裡？

一般文件產出放在：**你選擇的工作資料夾 → `exports`**。

例如安裝時使用預設工作資料夾，產出就會在程式資料夾內的 `workspace/exports`。
在本機模式下，請直接開啟這個資料夾；是否能在對話裡直接預覽或下載，取決於用戶端支援。

完整模式還可以寫入你有權限存取的其他位置。請在對話中把目的地說清楚，重要原稿先保留副本。

## 8. 常見狀況怎麼處理？

| 看到的狀況 | 原因與處理方式 |
|---|---|
| `Install uv first` 或 `command not found` | 缺少指定工具，或終端機找不到它。補裝後重新開終端機，再重跑安裝器。 |
| `Cannot connect to the Docker daemon` | Docker 還沒啟動。開啟 Docker Desktop，等它開始運作後再試。 |
| `Client registration stopped` | 設定檔格式或名稱有衝突。原設定會保留；看後面的錯誤內容，不要刪整份設定。 |
| `Permission denied` | 檢查資料夾是否可寫，以及下載腳本是否有執行權限；不要先改整顆磁碟的權限。 |
| 安裝完找不到 MCP | 重新載入 MCP 伺服器，確認目前是支援本機 MCP 的桌面模式；檢查 `client-registration.json` 記錄的設定位置。 |
| 移動程式資料夾後不能用 | 啟動器仍記住原路徑。把資料夾移回原位，或移除舊的 MCP 項目後重新安裝。 |
| `host_write_pdf` 要求 Chrome | 這個工具需要已安裝的 Chrome／Chromium，程式不會自動下載瀏覽器。 |

如果 Finder 無法執行安裝腳本，也可以打開終端機，在程式資料夾內執行：

```sh
sh Install.command --interactive
```

上面的指令只負責執行同一份腳本，不會補裝缺少的必備工具，也不會更改 macOS 安全設定。

## 9. 不想用了怎麼停用？

到 ChatGPT 的 MCP 伺服器清單，把這個項目停用或移除。
本專案沒有另建開機常駐服務；正在執行的代理可從用戶端停止。

先保留工作資料和 `exports` 裡的產出。確認不再需要之後，再自行清理程式資料夾。
刪除 MCP 項目不會自動刪除你的文件。

## 10. 進階用法

以下指令要在程式資料夾裡執行。

**用完整模式安裝，資料留在程式資料夾內：**

```sh
./Install.command --workspace "$PWD/workspace" --state "$PWD/.local/state" --mode full
```

**只安裝檔案與終端工具，略過 Docker 文件環境：**

```sh
./Install.command --workspace "$PWD/workspace" --state "$PWD/.local/state" --mode full --skip-worker
```

**安裝文件模式，但不要自動改動用戶端設定：**

```sh
./Install.command --workspace "$PWD/workspace" --state "$PWD/.local/state" --mode documents --no-register
```

設定檔預設遵循現有的 `CODEX_HOME`；未設定時使用 `~/.codex/config.toml`。
可以用 `--client-config /完整路徑/config.toml` 指定其他設定檔。一般使用者不必另外設定這個選項。

多機 SSH、網頁版 HTTPS、OAuth 與 tunnel 的進階內容，請看[連線說明（English）](https://github.com/arumwu/local-workspace-mcp/blob/main/docs/CONNECT.md)。
官方 tunnel 有帳號、權限與 Platform key 等條件；不能保證所有帳號可用或免費。

## 使用前知道這幾件事

- 這是開源工具，不是 OpenAI 或 Desktop Commander 官方產品，也不會增加 ChatGPT 額度。
- 完整模式能執行目前使用者有權限做的事，資料夾設定不是安全隔離。
- 本機程式不代表資料完全不離開電腦；傳給 AI 的檔案內容仍由你的 AI 供應商處理。
- 安裝、工具與文件測試已通過；真正的 ChatGPT 對話操作與兩台實體 Mac 的完整驗收仍未完成。

[完整功能對照（English）](https://github.com/arumwu/local-workspace-mcp/blob/main/docs/FEATURES.md) · [驗證紀錄（English）](https://github.com/arumwu/local-workspace-mcp/blob/main/docs/VALIDATION.md)
