# FastAPI REST API Playground

A repo for learning how to build REST APIs with FastAPI and a modern Python stack. It's a mix of a worked example project and notes on the concepts behind it.

## What I'm learning

- Routing, request validation and response models with FastAPI and Pydantic
- Async database access with SQLModel/SQLAlchemy, plus Alembic migrations
- Authentication: JWT, refresh tokens, password reset, roles and OAuth2 scopes
- Dependency injection and structured error handling
- Load testing with Locust and k6

## Example project: Rent-a-Room

A room-booking API that ties these topics together (`src/rent_a_room/`). It has endpoints for users, rooms and bookings, with admin-only routes.

## Notes

Study notes live in [notes/](notes/):

- [Authentication](notes/authentication.md)
- [Database migrations](notes/database_migrations.md)
- [Dependency injection](notes/dependency_injection.md)
- [ORM](notes/orm.md)
- [Querying options](notes/querying_options.md)
- [Delete options](notes/delete_options.md)
- [Load testing](notes/load_testing.md)

## Getting started

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/mahesh-yadav/fastapi-rest-api-playground.git
cd fastapi-rest-api-playground
uv sync
uv run fastapi dev
```

The API runs at http://localhost:8000. Interactive docs are at `/docs`.

## Tech stack

Python 3.14, FastAPI, SQLModel, SQLAlchemy (async), Alembic, Pydantic, PyJWT, pwdlib, uv, Locust, k6
