from typing import Annotated

from fastapi import Depends, HTTPException, Path, status

from rent_a_room.dependencies.database import SessionDep
from rent_a_room.models.user import User

UserId = Annotated[int, Path(ge=1, description="The id of the user to fetch")]


async def get_user_or_404(session: SessionDep, user_id: UserId) -> User:
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User: {user_id} not found"
        )

    return user


UserDep = Annotated[User, Depends(get_user_or_404)]
