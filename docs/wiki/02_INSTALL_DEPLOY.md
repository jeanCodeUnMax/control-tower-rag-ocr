# 2. Installation et déploiement

## Windows local

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -e ".[dev,vision]"
copy .env.example .env
control-tower init-project demo
uvicorn control_tower.api.app:app --host 127.0.0.1 --port 8000 --reload
```

Interface : `http://127.0.0.1:8000/ui/`
Swagger : `http://127.0.0.1:8000/docs`

## Linux/macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e '.[dev,vision]'
cp .env.example .env
control-tower init-project demo
uvicorn control_tower.api.app:app --host 127.0.0.1 --port 8000 --reload
```

## Docker

```bash
docker compose up --build
```

Les données persistantes sont montées dans `./runtime-data`.

## Vérification

```bash
pytest -q
control-tower inspect-project --project demo
```
