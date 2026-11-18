#!/bin/bash
# HTMLをA4のPDFにする（ヘッドレスChrome）。添削シートを紙で渡すとき用。
#   ./tools/to_pdf.sh 採点/2026-11-18_添削.html
set -euo pipefail
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for f in "$@"; do
  abs="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
  out="${abs%.html}.pdf"
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
            --virtual-time-budget=4000 --print-to-pdf="$out" "file://$abs" >/dev/null 2>&1
  echo "$(basename "$out")  $(du -h "$out" | cut -f1)"
done
