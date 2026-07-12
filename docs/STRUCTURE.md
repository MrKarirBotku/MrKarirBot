# Struktur Folder MrKarirBot

```text
MrKarirBot/
├── app/
│   ├── api/
│   │   ├── dependencies/
│   │   └── v1/
│   │       ├── health.py
│   │       ├── status.py
│   │       └── telegram.py
│   ├── bot/
│   │   ├── commands/
│   │   ├── conversations/
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   ├── middleware/
│   │   └── application.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   └── telemetry.py
│   ├── database/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── base.py
│   │   └── session.py
│   ├── schemas/
│   ├── services/
│   │   ├── ai/
│   │   ├── applications/
│   │   ├── companies/
│   │   ├── cv/
│   │   ├── interviews/
│   │   ├── jobs/
│   │   ├── notifications/
│   │   ├── recommendations/
│   │   └── security/
│   ├── sources/
│   ├── workers/
│   ├── utils/
│   └── main.py
├── alembic/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── security/
│   └── end_to_end/
├── scripts/
├── docs/
├── assets/
├── .github/
├── railway.toml
└── pyproject.toml
```

Legacy compatibility wrappers are kept temporarily under `app/db`, `app/models`, and `app/telegram` so older imports keep working while new code uses the enterprise layout.
