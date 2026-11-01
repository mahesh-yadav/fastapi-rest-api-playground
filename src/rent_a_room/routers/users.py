from fastapi import APIRouter, status
from sqlalchemy.orm import selectinload

from rent_a_room.dependencies.database import SessionDep
from rent_a_room.dependencies.users import UserDep, UserId
from rent_a_room.errors import UserNotFound
from rent_a_room.models.booking import BookingPublic
from rent_a_room.models.user import User, UserCreate, UserPublic
from rent_a_room.schemas.errors import NOT_FOUND_RESPONSE

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def create_user(session: SessionDep, user: UserCreate):
    validated_user = User.model_validate(user)

    session.add(validated_user)
    await session.commit()
    await session.refresh(validated_user)

    return validated_user


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    responses=NOT_FOUND_RESPONSE,
)
async def get_user(user: UserDep):
    return user


@router.get(
    "/{user_id}/bookings",
    status_code=status.HTTP_200_OK,
    response_model=list[BookingPublic],
    responses=NOT_FOUND_RESPONSE,
)
async def get_user_bookings(session: SessionDep, user_id: UserId):
    # lazy loading: ORM fetches the bookings only when we access them, not when we fetched the user using the UserDep
    # This lazy loading is Sync by default and we have a Async db connection
    # If we had a Sync route handle and Sync db session, this would have worked fine
    # return user.bookings

    # eager loading: fetch immediately, while fetching the user, the ORM is going the fetch the associated bookings as well: two SQL queries

    user = await session.get(
        User,
        user_id,
        options=[
            selectinload(User.bookings)  #  type: ignore
        ],
    )

    if user is None:
        raise UserNotFound(f"User ({user_id}) not found")

    # bookings are already fetched
    return user.bookings
