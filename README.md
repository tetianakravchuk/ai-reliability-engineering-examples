# AI Reliability Engineering Examples

A **standalone, original educational example** of atomic observation ingestion and optimistic checkpoint concurrency in PostgreSQL. This repository does not contain private World Publishing Houses source code, data, credentials, or architecture details.

## The problem
Two workers attempt to ingest different records against checkpoint version `0`. If the observation insert commits separately from the checkpoint update, a stale worker can leave behind a record even though its cursor advancement failed.

## The solution
Each worker inserts an observation and performs a version-checked checkpoint update **in the same transaction**. If the version update affects zero rows, the transaction raises an exception and the observation insert rolls back. The observation's unique external ID also provides a duplicate-write guard.

## Run tests

Start a disposable PostgreSQL instance (Docker example):

```bash
docker run --rm --name atomicity-demo -e POSTGRES_USER=demo -e POSTGRES_PASSWORD=demo -e POSTGRES_DB=atomicity_demo -p 5432:5432 -d postgres:16
python -m pip install -r requirements.txt
export TEST_DATABASE_URL='postgresql+psycopg://demo:demo@localhost:5432/atomicity_demo'
python -m pytest -q
```

Tests cover: (1) a stale checkpoint update rolling back its associated observation; (2) two competing worker sessions, with exactly one successful commit.

**Safety:** Tests drop and recreate tables. Run **only** against a disposable database. Do not use a shared or production database.

## Skills demonstrated
- SQLAlchemy transaction boundaries and rollback
- PostgreSQL compare-and-swap / optimistic concurrency
- Concurrent integration testing with separate sessions
- CI via GitHub Actions PostgreSQL service

## Scope and limitations
This is a deliberately small educational demonstration. It is **not** a production ingestion service, does not implement retries or full replay semantics, and does not claim to validate the private WPH deployment. PostgreSQL tests have to run in CI or against a disposable local database to establish results.
