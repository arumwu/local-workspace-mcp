# Local Workspace MCP

把本機檔案、終端、文件處理及多機工具交給支援 MCP 的 AI 用戶端。
程式已整合並可本機執行；**ChatGPT 實際桌面／網頁接線仍待驗證**，不能當成完整 Work 替代品。

## 安裝

先備妥 Python 3.12+、uv、Git。完整模式另需 Node.js 20.9+、npm、ripgrep。
文件隔離執行需要 Docker；本機 PDF 工具需要已安裝 Chrome／Chromium。

```sh
git clone https://github.com/arumwu/local-workspace-mcp.git
cd local-workspace-mcp
./Install.command --workspace /絕對路徑/工作資料 \
  --state /絕對路徑/私有設定 --mode full
```

路徑換成自己的位置；私有設定不能放進工作資料夾。
安裝程式不會安裝全域工具、不會覆寫 ChatGPT 設定；不是簽章版 `.app` 或 `.pkg`。
安裝後，把產生的 `launch.sh` 加進支援本機 MCP 的用戶端，類型選 STDIO，參數留空。

## 權限

`--mode full`：25 個 Desktop Commander 工具，加上本專案的文件、多機與輔助工具。
能改檔案、跑程式、連網、停止程序，權限等同目前使用者；目錄限制不是安全沙箱。

`--mode documents`：Docker 內處理 Word、Excel、PowerPoint、PDF 與圖表。
來源唯讀，結果寫入 `exports`，執行時沒有網路；可用 LibreOffice／Poppler 產生預覽。

## ChatGPT 連線

本機 STDIO 不需要雲端主機、公開網址或 API key，但必須確認使用中的 ChatGPT 模式支援它。
網頁版不能直接連你的 `127.0.0.1`；需要官方 tunnel 或自己的 HTTPS 入口。
官方 tunnel 有帳號與權限條件，也需要 Platform key，不能保證所有方案可用或免費。

[連線與多機教學](CONNECT.md) · [功能對照](FEATURES.md) · [實測與未完成項目](VALIDATION.md)

沒有我們代管的服務或帳號。不會把回饋送給廠商；工具讀出的資料仍會傳給你的 AI 供應商。
本專案使用 MIT 授權的 Desktop Commander 0.2.50 引擎，保留來源及授權。
