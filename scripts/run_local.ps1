$ErrorActionPreference = "Stop"

if (-not (Test-Path .venv)) {
    Write-Host "[INFO] Creation de l'environnement virtuel (.venv)..."
    $venvCreated = $false
    if (Get-Command py -ErrorAction SilentlyContinue) {
        try {
            & py -3.11 -m venv .venv
            $venvCreated = Test-Path .venv
        } catch {
            Write-Host "[WARN] 'py -3.11' indisponible, tentative avec 'python'..."
        }
    }
    if (-not $venvCreated) {
        & python -m venv .venv
    }
}

.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -e ".[dev,vision]"
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
uvicorn control_tower.api.app:app --host 127.0.0.1 --port 8000 --reload

