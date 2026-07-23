$ErrorActionPreference = "Stop"
if (-not (Test-Path .venv)) { py -3.11 -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -e ".[dev,vision]"
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
uvicorn control_tower.api.app:app --host 127.0.0.1 --port 8000 --reload
