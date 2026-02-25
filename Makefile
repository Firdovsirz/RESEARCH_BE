.PHONY: build up up-build down down-v restart logs logs-api shell \
        migrate migrate-new ps clean

# ── Build ──────────────────────────────────────────────────────────────────────
build:
	docker compose build

# ── Start / Stop ───────────────────────────────────────────────────────────────
up:
	docker compose up -d

up-build:
	docker compose up -d --build

down:
	docker compose down

down-v:                          ## also removes named volumes (data loss!)
	docker compose down -v

restart:
	docker compose restart

# ── Logs ───────────────────────────────────────────────────────────────────────
logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

# ── Shell ──────────────────────────────────────────────────────────────────────
shell:
	docker compose exec api bash

# ── Database / Migrations ──────────────────────────────────────────────────────
migrate:                         ## apply all pending migrations
	docker compose exec api alembic upgrade head

migrate-new:                     ## usage: make migrate-new MSG="add users table"
	docker compose exec api alembic revision --autogenerate -m "$(MSG)"

migrate-down:                    ## roll back the last migration
	docker compose exec api alembic downgrade -1

# ── Status ─────────────────────────────────────────────────────────────────────
ps:
	docker compose ps

# ── Clean ──────────────────────────────────────────────────────────────────────
clean:                           ## remove containers, networks, volumes, dangling images
	docker compose down -v --remove-orphans
	docker system prune -f
