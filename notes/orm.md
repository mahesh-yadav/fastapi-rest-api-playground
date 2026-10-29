# Object-Relational Mapper

## Relational Databases

They organize data in tables. Tables are linked to each other. e.g. SQLite or Postgres

## Challenge of working with a database

The backend is written in a programming language like Python but a relational database uses SQL. The problem is we have two different languages that need to communicate with each other.

An ORM is a library that acts as a translation layer between a programming language and SQL.

- e.g. An ORM translates Python code into equivalent SQL statements and database records into Python objects.

- e.g. SQLModel, SQLAlchemy

## SQLModel

It is built on top of Pydantic and SQLAlchemy. It merges Pydantic's data validation with SQLAlchemy's database communication.

### Engine

It's a Python object that manages the connections to the database.

### Database Model

We create a `Model` for every table in the database. A Model is a class whose responsibility is to interact with the corresponding table.

The `Model` defines the schema of the database table: columns and their types