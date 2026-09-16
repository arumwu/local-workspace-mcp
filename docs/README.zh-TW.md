# 中文安裝教學

[專案首頁](https://github.com/arumwu/local-workspace-mcp) · [English](https://github.com/arumwu/local-workspace-mcp/blob/main/docs/README.en.md)

適用版本：main 最新原始碼。主要用途：**一般 ChatGPT 對話操作本機工具**。

**原生 Windows 目前不支援，也尚未驗證。** 程式使用 Unix 專用 API；本頁安裝步驟適用於 Mac。
本頁負責本機工具安裝；完成後接著照[ChatGPT 私人通道教學](CHATGPT.md)連線。

## 1. 先確認完成條件

要在新的普通 ChatGPT「對話」真正呼叫工具成功，才算接通。
不要因為本機 MCP 列表或 Codex／Work 顯示已安裝，就省略帳戶外掛設定。
一般網頁對話已完成 Python 呼叫驗證；本機 App 仍需獨立驗證。

## 2. 下載哪個檔案？

下載 [main 最新原始碼 ZIP](https://github.com/arumwu/local-workspace-mcp/archive/refs/heads/main.zip)。
舊版 v0.1.1-alpha.1 發行包不含這次修正。wheel 不含完整安裝器、Node 引擎與文件容器。

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

## 5. 安裝完成後接上 ChatGPT

本機工具安裝器產生私有設定資料夾內的 `launch.sh`。
預設不再修改 Codex／本機 STDIO 設定；請繼續[官方私人通道教學](CHATGPT.md)，
完成通道、金鑰、ChatGPT 外掛連線及 Python 真實呼叫測試。

## 6. 回到一般 ChatGPT 對話使用

新的普通「對話」中提及或選取 `Local Workspace MCP`，先做教學中的無檔案 Python 測試。
再放一份測試 CSV 到工作資料夾，請它核對欄位、總筆數與總額，產出 Excel 報表。
本機 App 也要獨立測試；不要把網頁版的成功當成本機 App 已驗收。

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
| 安裝完找不到 MCP | 依通道教學確認 `/readyz`、ChatGPT 外掛與工作區，開新普通對話重測。 |
| 移動程式資料夾後不能用 | 啟動器仍記住原路徑。把資料夾移回原位，或移除舊的 MCP 項目後重新安裝。 |
| `host_write_pdf` 要求 Chrome | 這個工具需要已安裝的 Chrome／Chromium，程式不會自動下載瀏覽器。 |

如果 Finder 無法執行安裝腳本，也可以打開終端機，在程式資料夾內執行：

```sh
sh Install.command --interactive
```

上面的指令只負責執行同一份腳本，不會補裝缺少的必備工具，也不會更改 macOS 安全設定。

## 9. 不想用了怎麼停用？

到 ChatGPT 外掛程式中斷開連線。若已選擇登入自啟，依[通道教學](CHATGPT.md#5-macos-登入後自動啟動)停止並移除該登入項目；不要刪除其他不相關的背景服務。

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

僅在另選 `--register-local-client`（或明確傳入 `--client-config`）時登錄本機 STDIO 用戶端。這不是一般 ChatGPT 通道連線。
此選用設定遵循 `CODEX_HOME`；未設定時使用 `~/.codex/config.toml`。
可以用 `--client-config /完整路徑/config.toml` 指定其他設定檔。一般使用者不必另外設定這個選項。

多機 SSH、網頁版 HTTPS、OAuth 與 tunnel 的進階內容，請看[連線說明（English）](https://github.com/arumwu/local-workspace-mcp/blob/main/docs/CONNECT.md)。
官方 tunnel 有帳號、權限與 Platform key 等條件；不能保證所有帳號可用或免費。

## 使用前知道這幾件事

- 這是開源工具，不是 OpenAI 或 Desktop Commander 官方產品，也不會增加 ChatGPT 額度。
- 完整模式能執行目前使用者有權限做的事，資料夾設定不是安全隔離。
- 本機程式不代表資料完全不離開電腦；傳給 AI 的檔案內容仍由你的 AI 供應商處理。
- 一般 ChatGPT 網頁對話的 Python 真實呼叫已通過；本機 App、實體多機與所有文件流程的完整驗收仍未完成。

[完整功能對照（English）](https://github.com/arumwu/local-workspace-mcp/blob/main/docs/FEATURES.md) · [驗證紀錄（English）](https://github.com/arumwu/local-workspace-mcp/blob/main/docs/VALIDATION.md)
