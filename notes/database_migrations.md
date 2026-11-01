# Database Migrations

Database migrations record database schema changes. Each migration holds the code to apply a change and usually the code to undo it.

Migrations give:

1. History: you can see how the schema got to its current shape

2. Reproducibility: a fresh database can be brought to the current schema by running all migrations in order

## Alembic

Alembic detects the differences between the models and the current database schema, then generates the migrations.