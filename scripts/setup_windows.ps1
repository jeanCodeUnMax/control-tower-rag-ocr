$ErrorActionPreference = "Stop"

Write-Host "[1/5] Vérification de Python"
py -3.11 --version

Write-Host "[2/5] Création de l'environnement virtuel"
py -3.11 -m venv .venv

Write-Host "[3/5] Activation"
& .\.venv\Scripts\Activate.ps1

Write-Host "[4/5] Installation du projet"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"

Write-Host "[5/5] Vérifications"
python -m pytest -q
$tesseract = Get-Command tesseract -ErrorAction SilentlyContinue
if ($null -eq $tesseract) {
    Write-Warning "Tesseract n'est pas dans le PATH. TXT et PDF natifs fonctionneront, mais pas les images/PDF scannés."
    Write-Warning "Après installation, règle ocr.tesseract_cmd dans le config.yaml du projet si nécessaire."
} else {
    tesseract --version | Select-Object -First 1
    python scripts/prove_ocr.py
}
