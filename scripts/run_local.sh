#!/usr/bin/env bash
set -euo pipefail
[ -d .venv ] || python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e '.[dev,vision]'
[ -f .env ] || cp .env.example .env
uvicorn control_tower.api.app:app --host 127.0.0.1 --port 8000 --reload
