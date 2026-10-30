from sqlmodel import Field, SQLModel


# shared fields for a room
class RoomBase(SQLModel):
    name: str = Field()
    price_per_night: int = Field()
    bedrooms: float = Field(multiple_of=0.5)
    bathrooms: float = Field(multiple_of=0.5)


# Maps to the "rooms" table
class Room(RoomBase, table=True):
    __tablename__: str = "rooms"

    id: int | None = Field(default=None, primary_key=True)


# Response payload
class RoomPublic(RoomBase):
    id: int


# Update payload
class RoomUpdate(SQLModel):
    name: str | None = None
    price_per_night: int | None = None
    bedrooms: float | None = None
    bathrooms: float | None = None
