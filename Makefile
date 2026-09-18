.PHONY: install lint types arch test test-unit run docker-up check

install:
	pip install -e ".[api,worker,dev]"

lint:
	ruff check src tests evals

types:
	mypy src

arch:
	lint-imports

test:
	pytest -q

test-unit:
	pytest -q tests/unit

check: lint types arch test

run:
	uvicorn entrypoints.api.app:app --reload --port 8000

docker-up:
	docker compose -f infra/docker/docker-compose.yml up -d
