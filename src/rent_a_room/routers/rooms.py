from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field, StringConstraints, field_validator
from sqlmodel import col, exists, func, select

from rent_a_room.dependencies.database import SessionDep
from rent_a_room.dependencies.rooms import RoomDep
from rent_a_room.errors import ServiceUnderMaintenance
from rent_a_room.models.booking import Booking
from rent_a_room.models.room import Room, RoomBase, RoomPublic, RoomUpdate
from rent_a_room.schemas.errors import MAINTENANCE_RESPONSE, NOT_FOUND_RESPONSE
from rent_a_room.schemas.responses import RoomWithBookingCount

router = APIRouter(prefix="/rooms", tags=["rooms"])


class RoomQueryParams(BaseModel):
    max_price: int | None = Field(
        default=None, ge=10, le=10_000, examples=[100, 2000, 10_000]
    )
    search: Annotated[str | None, StringConstraints(to_lower=True)] = Field(
        default=None,
        min_length=3,
        max_length=10,
        title="Search term",
        description="Provide a keyword to look for within the room's title",
        examples=["sunny", "bedroom", "house"],
    )
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator("search")
    @classmethod
    def fail_if_funny(cls, search: str) -> str:
        if "lol" in search:
            raise ValueError("No funny business allowed")
        return search


MAINTENANCE_MODE = False


def check_maintenance_mode():
    if MAINTENANCE_MODE:
        raise ServiceUnderMaintenance()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=RoomPublic,
    dependencies=[Depends(check_maintenance_mode)],
    responses=MAINTENANCE_RESPONSE,
)
async def create_room(session: SessionDep, room: RoomBase):
    validated_room = Room.model_validate(room)
    session.add(validated_room)  # Queues a write to the database
    await session.commit()  # Writes to the database
    await session.refresh(
        validated_room
    )  # Sync the room instance with the database row

    return validated_room


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[RoomPublic],
    summary="List all available rooms",
    description="Returns all rooms. Supports filtering by price and search term",
    response_description="List of rooms matching the filter criteria",
)
async def get_rooms(session: SessionDep, params: Annotated[RoomQueryParams, Query()]):
    statement = select(Room)

    if params.max_price:
        statement = statement.where(Room.price_per_night <= params.max_price)

    if params.search:
        statement = statement.where(col(Room.name).ilike(f"%{params.search}%"))

    statement = (
        statement.limit(params.limit).offset(params.offset).order_by(col(Room.id))
    )

    rooms = await session.exec(statement)

    return rooms.all()


@router.get("/booked", status_code=status.HTTP_200_OK, response_model=list[RoomPublic])
async def get_booked_rooms(session: SessionDep):
    room_has_bookings = exists().where(col(Booking.room_id) == Room.id)

    statement = select(Room).where(room_has_bookings).order_by(col(Room.id))
    rooms = await session.exec(statement)

    return rooms.all()


@router.get(
    "/unbooked", status_code=status.HTTP_200_OK, response_model=list[RoomPublic]
)
async def get_unbooked_rooms(session: SessionDep):
    room_has_bookings = ~exists().where(col(Booking.room_id) == Room.id)

    statement = select(Room).where(room_has_bookings).order_by(col(Room.id))
    rooms = await session.exec(statement)

    return rooms.all()


@router.get(
    "/stats", status_code=status.HTTP_200_OK, response_model=list[RoomWithBookingCount]
)
async def get_room_stats(session: SessionDep):
    statement = (
        select(Room, func.count(col(Booking.id)).label("booking_count"))
        .outerjoin(Booking, col(Booking.room_id) == Room.id)
        .group_by(col(Room.id))
        .order_by(col(Room.id))
    )

    result = await session.exec(statement)
    result = result.all()

    rooms = [
        RoomWithBookingCount(**room.model_dump(), booking_count=booking_count)
        for room, booking_count in result
    ]

    return rooms


@router.get(
    "/booked-between", status_code=status.HTTP_200_OK, response_model=list[RoomPublic]
)
async def get_rooms_booked_between(session: SessionDep, start_date: str, end_date: str):
    statement = (
        select(Room)
        .join(Booking, col(Booking.room_id) == Room.id)
        .where(col(Booking.check_in) >= start_date)
        .where(col(Booking.check_out) <= end_date)
        .distinct()
        .order_by(col(Room.id))
    )

    rooms = await session.exec(statement)
    return rooms.all()


@router.get(
    "/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoomPublic,
    responses=NOT_FOUND_RESPONSE,
)
async def get_room(room: RoomDep):
    return room


@router.patch(
    "/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoomPublic,
    dependencies=[Depends(check_maintenance_mode)],
    responses=NOT_FOUND_RESPONSE | MAINTENANCE_RESPONSE,
)
async def update_room(session: SessionDep, room: RoomDep, room_payload: RoomUpdate):
    room.sqlmodel_update(room_payload.model_dump(exclude_unset=True))
    session.add(room)
    await session.commit()
    await session.refresh(room)

    return room


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoomPublic,
    dependencies=[Depends(check_maintenance_mode)],
    responses=NOT_FOUND_RESPONSE | MAINTENANCE_RESPONSE,
)
async def delete_room(session: SessionDep, room: RoomDep):
    await session.delete(room)
    await session.commit()
    return room
