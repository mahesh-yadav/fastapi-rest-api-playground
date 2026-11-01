from sqlmodel import Session

from database import engine
from models import Genre, Movie


def create_movie_with_genre():
    # Session represents a transaction: it keeps track of all changes
    with Session(engine) as session:
        try:
            genre = Genre(name="Sci-Fi")
            session.add(genre)  # queues the change
            session.flush()  # writes changes to the database and does not complete the transaction

            movie = Movie(
                title="Dune Part TWo",
                in_theaters=False,
                release_year=2024,
                genre_id=genre.id,
            )
            session.add(movie)

            session.commit()  # writes the changes and also marks the transaction as complete
        except Exception:  # noqa: BLE001
            session.rollback()


create_movie_with_genre()
