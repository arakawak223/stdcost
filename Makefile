.PHONY: up down build migrate seed test lint generate-api-client

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

migrate:
	docker compose exec backend alembic upgrade head

migration:
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

seed:
	docker compose exec backend python -m app.seed

test:
	docker compose exec backend python -m pytest tests/ -v

lint-backend:
	docker compose exec backend ruff check app/

lint-frontend:
	docker compose exec frontend npm run lint

lint: lint-backend lint-frontend

generate-api-client:
	curl -s http://localhost:8000/openapi.json -o frontend/openapi.json
	cd frontend && npx openapi-typescript openapi.json -o src/lib/api-client/schema.d.ts

reset-db:
	docker compose down -v
	docker compose up -d db
	sleep 3
	$(MAKE) migrate
	$(MAKE) seed
