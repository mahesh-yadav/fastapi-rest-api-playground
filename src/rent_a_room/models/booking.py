from typing import TYPE_CHECKING

from pydantic import NaiveDatetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from rent_a_room.models.room import Room
    from rent_a_room.models.user import User


class BookingBase(SQLModel):
    room_id: int
    user_id: int
    check_in: NaiveDatetime
    check_out: NaiveDatetime


class Booking(BookingBase, table=True):
    __tablename__: str = "bookings"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="rooms.id", ondelete="CASCADE")
    user_id: int = Field(foreign_key="users.id")

    room: Room = Relationship(back_populates="bookings")
    user: User = Relationship(back_populates="bookings")


class BookingPublic(BookingBase):
    id: int


class BookingCreate(BookingBase):
    pass
