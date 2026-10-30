from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

import rent_a_room.models.room  # noqa: F401  (registers tables on SQLModel.metadata)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(
    url=sqlite_url, connect_args={"check_same_thread": False}, echo=True
)


def create_db_and_tables():
    # import all SQLModel models before creating the actual database
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
