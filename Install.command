#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ "$#" -eq 0 ]; then
  python3 scripts/install.py --interactive
  echo '本機工具安裝完成。請依 docs/CHATGPT.md 設定私人通道，在一般 ChatGPT 對話驗證。'
  printf '按 Enter 關閉視窗。'
  read -r ignored
  exit 0
fi
exec python3 scripts/install.py "$@"
