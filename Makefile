.PHONY: install lint types arch test test-unit test-integration migrate migration run docker-up check

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

# Test tích hợp. Không có DATABASE_URL thì nhánh Postgres tự bỏ qua.
test-integration:
	pytest -q tests/integration

# Migration. DSN lấy từ DATABASE_URL; không có thì dùng SQLite cục bộ.
migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(m)"

check: lint types arch test

run:
	uvicorn entrypoints.api.app:app --reload --port 8000

docker-up:
	docker compose -f infra/docker/docker-compose.yml up -d
