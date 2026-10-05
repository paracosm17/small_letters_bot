# small_letters_bot

Telegram bot that composes small Cyrillic characters above regular text.

## Runtime architecture

```text
Telegram
   |
   | HTTPS webhook
   v
Coolify / reverse proxy
   |
   v
small_letters_bot :8080
   |-- GET  /
   |-- GET  /healthz
   `-- POST /telegram/webhook
        |
        +--> PostgreSQL
        `--> Redis (aiogram FSM)
```

Production characteristics:

- Python 3.13.15;
- aiogram 3 webhook transport;
- PostgreSQL schema managed by Alembic;
- Redis-backed FSM;
- non-root container UID/GID 10001;
- fail-closed `/healthz` checking PostgreSQL and Redis;
- immutable GHCR images deployed by exact registry digest;
- `APP_SMOKE_MODE=true` for production bootstrap without Telegram API side effects.

## Release model

Only `main` is a deployment branch.

```text
main -> quality -> PostgreSQL 18 preflight -> image publish
     -> exact digest smoke verification -> Coolify production
```

Automatic production deployment is gated by repository variable:

```text
DEPLOY_PRODUCTION_ENABLED
```

Keep it `false` until production data is restored and smoke validation is complete.

## Setup / quality

```bash
export UV_LINK_MODE=copy
make setup
make check
```

The project intentionally has no development Coolify environment or dev compose stack.

## Configuration

Runtime variables:

```text
APP_ENV
LOG_LEVEL
APP_SMOKE_MODE
NOTIFY_ADMINS_ON_STARTUP
RELEASE_REVISION

DATABASE_URL

USE_REDIS
REDIS_URL

BOT_TOKEN
ADMIN_IDS

WEB_SERVER_HOST
PORT
WEBHOOK_BASE_URL
WEBHOOK_PATH
WEBHOOK_SECRET
```

Legacy `DB_*` / `POSTGRES_*`, `REDIS_*`, and `ADMINS` variables are accepted only as migration fallbacks.

## Database migration

The active legacy service already uses PostgreSQL 14. Production migration is therefore:

```text
stop old bot only
-> final PostgreSQL 14 custom-format dump
-> restore to fresh PostgreSQL 18
-> schema/Alembic validation
-> smoke-mode application validation
-> live webhook cutover
```

For a compatible restored database that has no `alembic_version` table:

```bash
python -m scripts.migration_preflight --adopt-existing --expected-users <count>
```

Normal verification:

```bash
python -m scripts.db_verify --expected-users <count>
```

The retired `migrate_db.py` belonged to an older SQLite migration and is intentionally removed.
