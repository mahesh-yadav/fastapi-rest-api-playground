from typing import Annotated

from fastapi import Depends, Path

from rent_a_room.dependencies.database import SessionDep
from rent_a_room.errors import RoomNotFound
from rent_a_room.models.room import Room

RoomId = Annotated[int, Path(ge=1, description="The id of the room to fetch")]


async def get_room_or_404(session: SessionDep, room_id: RoomId) -> Room:
    room = await session.get(Room, room_id)

    if room is None:
        raise RoomNotFound(f"Room ({room_id}) not found")

    return room


RoomDep = Annotated[Room, Depends(get_room_or_404)]
