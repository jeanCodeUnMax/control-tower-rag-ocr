.PHONY: install test lint demo api
install:
	python -m pip install -e ".[dev]"
test:
	pytest -q
lint:
	ruff check src tests
demo:
	control-tower init-project demo
	control-tower ingest --project demo examples/sample.txt
	control-tower query --project demo --text "architecture isolée"
api:
	uvicorn control_tower.api.app:app --reload
