from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy.orm import joinedload

from rent_a_room.dependencies.database import SessionDep
from rent_a_room.models.booking import Booking, BookingCreate, BookingPublic
from rent_a_room.models.room import Room
from rent_a_room.models.user import User
from rent_a_room.schemas.responses import BookingWithDetails

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookingPublic)
async def create_booking(session: SessionDep, booking: BookingCreate):
    room = await session.get(Room, booking.room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room ({booking.room_id}) does not exist",
        )

    user = await session.get(User, booking.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User ({booking.user_id}) does not exist",
        )

    validated_booking = Booking.model_validate(booking)

    session.add(validated_booking)
    await session.commit()
    await session.refresh(validated_booking)

    return validated_booking


@router.get(
    "/{booking_id}", status_code=status.HTTP_200_OK, response_model=BookingWithDetails
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking ({booking_id}) does not exist",
        )

    return booking
