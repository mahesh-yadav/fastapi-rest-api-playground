from sqlmodel import Session

from database import engine
from models import Genre, Movie


def create_movie_with_genre():
    # Session represents a transaction: it keeps track of all changes
    with Session(engine) as session:
        try:
            genre = Genre(name="Horror")
            session.add(genre)  # queues the change
            session.flush()  # writes changes to the database and does not complete the transaction

            movie = Movie(
                title="A Quiet Place",
                in_theaters=50,  # type: ignore
                release_year=2008,
                genre_id=genre.id,
            )
            session.add(movie)

            session.commit()  # writes the changes and also marks the transaction as complete
        except Exception as error:  # noqa: BLE001
            # rollback is automatically called by with context manager
            session.rollback()
            print(f"Rolled back: {error}")


create_movie_with_genre()
