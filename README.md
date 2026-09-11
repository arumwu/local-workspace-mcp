# Local Workspace MCP

**繁體中文** · [English](docs/README.en.md)

讓支援本機 MCP 的 ChatGPT 桌面版，使用你電腦上的檔案、文件處理與終端工具。
MCP 可以理解成「AI 呼叫你電腦工具的連接方式」。程式由你自己執行，沒有我們代管的雲端服務。

**[下載安裝包](https://github.com/arumwu/local-workspace-mcp/releases/tag/v0.1.1-alpha.1)** · **[第一次使用：中文安裝教學](docs/README.zh-TW.md)**

目前是 **alpha 測試版**。安裝、工具呼叫與文件處理已通過測試；實際 ChatGPT 對話呼叫及實體多機操作仍待完整驗收。

## 可以做什麼？

- 讀取、搜尋、修改、搬移電腦裡的檔案，整理專案與文件。
- 製作 Word、Excel、PowerPoint、PDF 與圖表，產生預覽並檢查內容。
- 啟動程式、傳入指令、查看執行結果，以及管理測試或開發用的程序。
- 設定其他自己的電腦，再用名稱指定要在哪一台執行。

完整安裝提供 **41 個工具**，其中 25 個來自 MIT 授權的 Desktop Commander 引擎。
功能包含讀取、搜尋、編輯、終端、設定與使用紀錄。多機連線使用自行設定的 SSH；SSH 就是遠端登入自己電腦的連線方式。

## 怎麼安裝？

以下適用於 **Mac 上支援「標準輸入／輸出（STDIO）」MCP 的 ChatGPT 桌面版**。
STDIO 表示 ChatGPT 直接啟動本機程式，這個方式不需要公開網址或另外租主機。

1. 到[下載頁](https://github.com/arumwu/local-workspace-mcp/releases/tag/v0.1.1-alpha.1)，下載 `local-workspace-mcp-v0.1.1-alpha.1.zip`。
2. 解壓縮，把整個資料夾放到打算長期保留的位置。
3. 依[安裝教學](docs/README.zh-TW.md)準備 Python、uv 等必備工具；需要文件處理時，先開啟 Docker Desktop。
4. 雙擊資料夾裡的 `Install.command`，依提示選擇工作資料夾與模式。
5. 安裝器會**自動加入 ChatGPT／Codex 的 MCP 設定**，先備份，並保留其他既有設定。
6. 在 ChatGPT 重新載入 MCP 伺服器或開啟新工作，確認伺服器已連線。

這是包含安裝腳本的原始碼包，還不是把所有必備工具都包好的 `.app` 或 `.pkg`。
如果安裝器提示缺少工具，先補裝，再重跑即可；不會默默替你安裝全域軟體。

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

**一定要填 MCP 的名稱、指令與環境變數嗎？**
正常安裝會自動處理。若先前已自行設定相同啟動器，會沿用原有項目，不重複新增；也不會擅自把停用項目打開。

**ChatGPT 網頁版也可以直接用嗎？**
網頁版不能直接使用你電腦的 `127.0.0.1`。需要另外設定官方 tunnel 或自己的 HTTPS 入口；tunnel 就是讓雲端透過通道連到本機。這不包含在一般桌面安裝流程內。

**只有下載就能使用嗎？**
還要準備必備工具並執行安裝腳本。第一次請照[中文安裝教學](docs/README.zh-TW.md)操作。

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

macOS 與 Linux 的自動測試已通過；**Windows 已有使用者回報測試成功**。
Windows 的版本、執行環境（原生 Windows 或 WSL2）及測試範圍尚未提供，維護者尚未重現驗證；以上雙擊安裝步驟適用於 Mac。
本專案採 MIT 授權，使用 Desktop Commander 0.2.50 的開源引擎；與 OpenAI、Desktop Commander 官方無隸屬關係。
