from typing import Annotated

from fastapi import APIRouter, Path, status
from sqlalchemy.orm import joinedload

from rent_a_room.dependencies.database import SessionDep
from rent_a_room.errors import BookingNotFound, RoomNotFound, UserNotFound
from rent_a_room.models.booking import Booking, BookingCreate, BookingPublic
from rent_a_room.models.room import Room
from rent_a_room.models.user import User
from rent_a_room.schemas.errors import NOT_FOUND_RESPONSE
from rent_a_room.schemas.responses import BookingWithDetails

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BookingPublic,
    responses=NOT_FOUND_RESPONSE,
)
async def create_booking(session: SessionDep, booking: BookingCreate):
    room = await session.get(Room, booking.room_id)
    if not room:
        raise RoomNotFound(f"Room ({booking.room_id}) not found")

    user = await session.get(User, booking.user_id)
    if not user:
        raise UserNotFound(f"User ({booking.user_id}) not found")

    validated_booking = Booking.model_validate(booking)

    session.add(validated_booking)
    await session.commit()
    await session.refresh(validated_booking)

    return validated_booking


@router.get(
    "/{booking_id}",
    status_code=status.HTTP_200_OK,
    response_model=BookingWithDetails,
    responses=NOT_FOUND_RESPONSE,
)
async def get_booking(
    session: SessionDep,
    booking_id: Annotated[
        int, Path(ge=1, description="The id of the booking to fetch")
    ],
):
    booking = await session.get(
        Booking,
        booking_id,
        options=[
            joinedload(Booking.room),  # type: ignore
            joinedload(Booking.user),  # type: ignore
        ],
    )

    if not booking:
        raise BookingNotFound(f"Booking ({booking_id}) not found")

    return booking
