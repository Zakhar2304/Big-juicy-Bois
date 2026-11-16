#!/usr/bin/env bash
# iOS збірка: Flet ламається на шляхах з пробілами (iCloud «Mobile Documents»).
# Скрипт копіює проєкт у ~/HappyGarden і збирає .xcarchive для Xcode.
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST="$HOME/HappyGarden"

echo "Синхронізація: $SRC -> $DST"
rsync -a --delete \
  --exclude '.git' \
  --exclude 'build' \
  --exclude '.venv' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '.flet' \
  --exclude '.dart_tool' \
  "$SRC/" "$DST/"

export PATH="$HOME/flutter/3.47.9/bin:${PATH:-}"

cd "$DST"
flet build ipa --no-swift-package-manager --yes "$@"
python3 "$DST/scripts/attach_ios_widget.py" "$DST/build/flutter/ios"

open "$DST/build/flutter/ios/Runner.xcworkspace"
echo "Готово. У Xcode: Team → Signing, обери iPhone → Run."
echo "Архів: $DST/build/ipa/happygarden.xcarchive"