from fastapi import APIRouter, status

from rent_a_room.dependencies.database import SessionDep
from rent_a_room.dependencies.users import UserDep
from rent_a_room.models.booking import BookingPublic
from rent_a_room.models.user import User, UserCreate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def create_user(session: SessionDep, user: UserCreate):
    validated_user = User.model_validate(user)

    session.add(validated_user)
    await session.commit()
    await session.refresh(validated_user)

    return validated_user


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserPublic)
async def get_user(user: UserDep):
    return user


@router.get(
    "/{user_id}/bookings",
    status_code=status.HTTP_200_OK,
    response_model=list[BookingPublic],
)
async def get_user_bookings(user: UserDep):
    return user.bookings
