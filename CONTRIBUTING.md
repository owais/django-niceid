# Contributing

Thanks for your interest in django-niceid.

## Development setup

Requires Python 3.14+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/owais/django-niceid.git
cd django-niceid
uv sync --extra dev
```

For PostgreSQL integration tests:

```bash
docker compose up -d
export POSTGRES_HOST=localhost POSTGRES_PORT=54329
uv run pytest -m postgres
```

## Running checks

```bash
make check          # lint + format check + unit tests
make test           # unit tests only
make test-postgres  # starts Docker Postgres, then integration tests
make lint format    # individual targets
```

Or directly with uv: `uv run ruff check .`, `uv run pytest -m "not postgres"`, etc.

## Building release artifacts

```bash
make build
```

Produces `dist/*.tar.gz` and `dist/*.whl` using the hatchling backend from `pyproject.toml`.

Run `make help` for all targets.

## Pull requests

1. Open an issue for larger changes when possible.
2. Keep PRs focused; include tests for behavior changes.
3. Update `CHANGELOG.md` under **Unreleased** for user-visible changes.
4. Ensure CI passes before requesting review.
