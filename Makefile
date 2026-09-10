.PHONY: install ingest run api ui test

export PYTHONPATH := .

install:
	python -m pip install -r requirements.txt

ingest:
	python scripts/ingest_sample_data.py

api:
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

ui:
	streamlit run frontend/streamlit_app.py

run: api

test:
	pytest -q
