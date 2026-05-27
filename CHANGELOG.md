# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-27

### Added

- `NiceID` type: namespaced, Crockford base32-encoded UUIDv7 strings.
- `NiceIDField`, `NiceIDPrimaryKeyField`, and abstract `NiceIDModel`.
- URL path converter registered as `niceid`.
- Optional integrations: DRF (`niceid.drf`), Django Ninja, Pydantic, Tortoise ORM.
- PostgreSQL native UUID storage with `uuidv7()` database default.

### Notes

- Python 3.14+ required (`uuid.uuid7` in the standard library).
- PostgreSQL 18+ with native UUID support and a `uuidv7()` function required for primary keys.

[0.1.0]: https://github.com/owais/django-niceid/releases/tag/v0.1.0
