# Database Migrations

Database migrations record database schema changes. Each migration holds the code to apply a change and usually the code to undo it.

Migrations give:

1. History: you can see how the schema got to its current shape

2. Reproducibility: a fresh database can be brought to the current schema by running all migrations in order

## Alembic

Alembic detects the differences between the models and the current database schema, then generates the migrations.

### Workflow

1. Initialize: 

```bash
uv run alembic init migrations
```

2. Generate the Migration: 

```bash
uv run alembic revision --autogenerate -m "Create movies table"
```

3. Apply the Migration:

```bash
uv run alembic upgrade head
```

### Adding a non-null column

**Problem:** If the table already has data, a new `NOT NULL` column has no value for them and the migration fails.

**Solution:** 

- Add the column as nullable

- Populate existing rows with a valid value

- Generate another migration to make the column non-null.
