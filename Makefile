up:
	docker compose up -d --build

ingest:
	docker compose run --rm worker python -m app.workers.pipeline --ingest data/input

docs:
	@echo "Open http://localhost:8000/docs"
