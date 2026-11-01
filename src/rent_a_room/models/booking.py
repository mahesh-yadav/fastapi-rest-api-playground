from typing import TYPE_CHECKING

from pydantic import NaiveDatetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from rent_a_room.models.room import Room


class BookingBase(SQLModel):
    room_id: int
    guest_name: str
    check_in: NaiveDatetime
    check_out: NaiveDatetime


class Booking(BookingBase, table=True):
    __tablename__: str = "bookings"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="rooms.id")

    room: Room = Relationship(back_populates="bookings")


class BookingPublic(BookingBase):
    id: int


class BookingCreate(BookingBase):
    pass
