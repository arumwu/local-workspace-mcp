# v0.1.1-alpha.1｜自動設定 MCP

安裝完成後，程式會自動加入 ChatGPT 桌面版／Codex 的 MCP 設定，通常不用再自己填名稱和啟動指令。

**第一次使用：先看「中文安裝指南.html」，再下載 `local-workspace-mcp-v0.1.1-alpha.1.zip`。**
解壓縮後，準備必備工具，雙擊 `Install.command`。安裝後重新載入 MCP 或開啟新工作。

[線上中文安裝教學](https://github.com/arumwu/local-workspace-mcp/blob/main/docs/README.zh-TW.md) · [English](https://github.com/arumwu/local-workspace-mcp/blob/main/docs/README.en.md)

這版新增：

- 自動登錄 MCP，寫入前備份，保留其他伺服器、註解及設定。
- 重裝會沿用已存在的啟動器與自訂名稱，不重複新增，也不擅自啟用原先停用的項目。
- 雙擊安裝引導；可用 `--no-register` 跳過自動設定，或用 `--client-config` 指定設定檔。

macOS、Ubuntu 與文件容器測試已通過；也已實測獨立安裝、自動登錄及真正的檔案寫入。

目前仍是 **alpha 測試版**，需要 Python、uv 等必備工具；不是包含所有工具的 `.app` 或 `.pkg`。
完整模式可修改檔案、執行命令及連網，權限等同目前使用者。
真正的 ChatGPT 對話呼叫與實體多機驗收仍待完成。
