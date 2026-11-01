from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from rent_a_room.models.booking import Booking

# model: refers to any class that interacts with the database e.g. Room
# model: any class that models a domain idea e.g. rooms, users
# schema: classes that model a request or response payload


# shared fields for a room
class RoomBase(SQLModel):
    name: str = Field()
    price_per_night: int = Field()
    bedrooms: float = Field(multiple_of=0.5)
    bathrooms: float = Field(multiple_of=0.5)


# Maps to the "rooms" table
class Room(RoomBase, table=True):
    __tablename__: str = "rooms"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)

    # Field maps to a database column, bookings will not be a column in rooms table, so we use Relationship, back_populates establishes the association between two models in code.
    bookings: list[Booking] = Relationship(back_populates="room", passive_deletes="all")


# Response payload
class RoomPublic(RoomBase):
    id: int


# Update payload
class RoomUpdate(SQLModel):
    name: str | None = None
    price_per_night: int | None = None
    bedrooms: float | None = None
    bathrooms: float | None = None
