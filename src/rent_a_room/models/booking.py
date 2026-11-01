from typing import TYPE_CHECKING, Optional

from pydantic import NaiveDatetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from rent_a_room.models.room import Room
    from rent_a_room.models.user import User


class BookingBase(SQLModel):
    user_id: int
    check_in: NaiveDatetime
    check_out: NaiveDatetime


class Booking(BookingBase, table=True):
    __tablename__: str = "bookings"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    room_id: int | None = Field(
        default=None, foreign_key="rooms.id", ondelete="SET NULL"
    )
    user_id: int = Field(foreign_key="users.id")

    # `Room | None` fails: SQLAlchemy looks up the string 'Room | None' as a class name
    room: Optional["Room"] = Relationship(back_populates="bookings")  # noqa: UP037, UP045
    user: User = Relationship(back_populates="bookings")


class BookingPublic(BookingBase):
    id: int
    room_id: int | None


class BookingCreate(BookingBase):
    room_id: int
