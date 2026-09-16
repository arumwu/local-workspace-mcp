# Local Workspace MCP

**繁體中文** · [English](docs/README.en.md)

讓**一般 ChatGPT 對話**使用你電腦上的檔案、文件處理、Python 與終端工具。
透過 OpenAI 官方私人 MCP 通道連線，本機工具由你自己執行，不需要我們代管的伺服器。

**[下載最新版原始碼](https://github.com/arumwu/local-workspace-mcp/archive/refs/heads/main.zip)** · **[開始使用：一般 ChatGPT 連線教學](docs/CHATGPT.md)**

**實測：一般 ChatGPT 網頁對話已成功呼叫 Python，通道重啟後也成功。**
本機 ChatGPT App 的一般對話仍待獨立驗證。不能把 Codex／Work 的工具設定當作一般對話已接通。
目前是 alpha；macOS、Linux 可安裝，原生 Windows 尚不支援。

## 可以做什麼？

- 讀取、搜尋、修改、搬移電腦裡的檔案，整理專案與文件。
- 製作 Word、Excel、PowerPoint、PDF 與圖表，產生預覽並檢查內容。
- 啟動程式、傳入指令、查看執行結果，以及管理測試或開發用的程序。
- 設定其他自己的電腦，再用名稱指定要在哪一台執行。

完整安裝提供 **41 個工具**，其中 25 個來自 MIT 授權的 Desktop Commander 引擎。
功能包含讀取、搜尋、編輯、終端、設定與使用紀錄。多機連線使用自行設定的 SSH；SSH 就是遠端登入自己電腦的連線方式。

## 怎麼安裝？

1. 下載上方最新版原始碼，放到準備長期保留的位置。
2. 準備 Python、uv 等[必備工具](docs/README.zh-TW.md)，文件工作還需要運作中的 Docker。
3. 執行 `Install.command`，明確選擇完整模式或文件模式。
4. 依[一般 ChatGPT 教學](docs/CHATGPT.md)建立官方私人通道與受限制的 runtime key。
5. 在 ChatGPT 的「外掛程式」新增通道，於新的普通「對話」呼叫 `run_python` 驗證。
6. Mac 可安裝有名稱的登入啟動 App，讓通道在登入後自動恢復。

新版安裝器預設不修改 Codex／本機 STDIO 設定。只安裝本機程式，還不等於已接上 ChatGPT。
舊版 `v0.1.1-alpha.1` ZIP 不含這次通道相容性修正，請使用上方最新版原始碼。
這仍是需準備工具與帳戶設定的原始碼安裝，不是全部預先包好的簽章安裝包。

## 兩種模式怎麼選？

**文件模式（預設）**：適合做報表、簡報、PDF 與圖表。程式在 Docker 的隔離環境執行，原始資料只能讀取，產出放在 `exports` 資料夾。執行文件工作的環境沒有網路。

**完整模式**：適合操作檔案、修改程式、管理開發環境。安裝時輸入 `y` 才會啟用。**權限等同目前登入的使用者，可以改檔案、執行程式及連網；不是只限制在某個資料夾內。**

不確定時，先選文件模式。需要完整工具時，再以完整模式重跑同一份安裝器。

## 安裝後可以這樣說

> 讀取工作資料夾裡的銷售 CSV，做一份 Excel 報表和長條圖，確認總額正確。

> 把這份筆記整理成 Word 和五頁簡報，先做預覽，再告訴我檔案放在哪裡。

> 檢查這個程式專案，找出啟動方式並執行測試。（需要完整模式）

安裝不會增加 ChatGPT 額度或解鎖其他訂閱功能。
AI 實際讀取的檔案內容仍會傳給你使用的 AI 供應商；「在本機執行工具」不代表資料完全不會離開電腦。

## 常見問題

**為什麼設定裡有 MCP，普通對話卻找不到？**
本機 STDIO 設定與 ChatGPT 帳戶的外掛連線不同。請完成[通道連線與真實對話測試](docs/CHATGPT.md)。

**一定要使用 Codex 或 Work 嗎？**
不需要。主要目標是一般 ChatGPT 對話。其他相容 MCP 用戶端仍可選擇 STDIO。

**金鑰、Docker 和常駐程序要留著嗎？**
通道需要你自己的受限制金鑰與常駐程序；`run_python` 需要 Docker。
測試容器與暫存可清理，正式程式、金鑰與產出不能當作暫存刪掉。

**程式資料夾可以裝好後移走嗎？**
先不要。啟動器記住了安裝路徑；移走後需要重新設定。一般產出放在你選擇的工作資料夾下的 `exports`。

## 更多說明

- [中文安裝教學、常見錯誤與停用方式](docs/README.zh-TW.md)
- [English README](docs/README.en.md)
- [進階連線與多機設定（English）](docs/CONNECT.md)
- [完整功能對照（English）](docs/FEATURES.md)
- [測試結果與待驗證項目（English）](docs/VALIDATION.md)
- [安全與權限說明（English）](SECURITY.md)
- [第三方來源與授權](THIRD_PARTY_NOTICES.md)

macOS 與 Linux 的自動測試已通過；原生 Windows 目前不支援，也沒有 Windows CI。以上雙擊安裝步驟適用於 Mac。
本專案採 MIT 授權，使用 Desktop Commander 0.2.50 的開源引擎；與 OpenAI、Desktop Commander 官方無隸屬關係。
