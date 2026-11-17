#!/bin/bash
# flet build ios не існує — треба ipa.
# Шлях з iCloud ("Mobile Documents") ламає sync site-packages, тому збираємо з ~/HappyGarden.
set -euo pipefail

SRC="/Users/zakhar/Library/Mobile Documents/com~apple~CloudDocs/Downloads/HappyGarden"
DST="$HOME/HappyGarden"

rsync -a --delete \
  --exclude '.git' \
  --exclude 'build' \
  --exclude '.venv' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '.flet' \
  --exclude '.dart_tool' \
  --exclude '.DS_Store' \
  "$SRC/" "$DST/"

export PATH="$HOME/flutter/3.47.9/bin:${PATH:-}"
cd "$DST"
flet build ipa --no-swift-package-manager --yes
open "$DST/build/flutter/ios/Runner.xcworkspace"
