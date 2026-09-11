#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ "$#" -eq 0 ]; then
  python3 scripts/install.py --interactive
  echo '安裝完成。請在 ChatGPT 重新載入 MCP 伺服器，或開啟新工作。'
  printf '按 Enter 關閉視窗。'
  read -r ignored
  exit 0
fi
exec python3 scripts/install.py "$@"
