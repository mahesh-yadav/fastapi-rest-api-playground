# Dependency Injection

Any route handler that wants to interact with the database, needs to have a session object.

The pattern that FastAPI provides for adding these dependencies to a route handler is called `dependency injection`.

- Dependency injection is a pattern in which any dependency that a function needs, is provided as a parameter rather than created in line.