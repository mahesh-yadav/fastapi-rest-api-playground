from typing import Annotated

from fastapi import Depends, HTTPException, Path, status

from rent_a_room.dependencies.database import SessionDep
from rent_a_room.models.room import Room

RoomId = Annotated[int, Path(ge=1, description="The id of the room to fetch")]


async def get_room_or_404(session: SessionDep, room_id: RoomId) -> Room:
    room = await session.get(Room, room_id)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Room: {room_id} not found"
        )

    return room


RoomDep = Annotated[Room, Depends(get_room_or_404)]
