from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import (
    Cookie,
    FastAPI,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)
from pydantic import BaseModel, Field, StringConstraints, field_validator
from sqlmodel import col, select

from .database import SessionDep, create_db_and_tables
from .models import Room

openapi_tags = [
    {
        "name": "rooms",
        "description": "Operations with **rooms** (a 4-wall _space_ that can be slept in)",
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Rent a Room API",
    description="Book a stay in a house or room",
    version="1.0.0",
    openapi_tags=openapi_tags,
)


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


RoomId = Annotated[int, Path(ge=1, description="The id of the room to fetch")]


class AppCookies(BaseModel):
    language: Literal["en", "es", "fr"] = "en"
    theme: Literal["dark", "light"] = "dark"


@app.get("/", status_code=status.HTTP_200_OK)
def root(
    app_cookies: Annotated[AppCookies, Cookie()],
    user_agent: Annotated[str | None, Header()] = None,
):
    greetings = {
        "en": "Welcome to rent a room",
        "es": "Bienvenido a rent a room",
        "fr": "Bienvenue sur rent a room",
    }

    greeting = greetings.get(app_cookies.language)

    return {"message": greeting, "user_agent": user_agent}


@app.post("/rooms", status_code=status.HTTP_201_CREATED, tags=["rooms"])
def create_room(session: SessionDep, room: Room) -> Room:
    session.add(room)  # Queues a write to the database
    session.commit()  # Writes to the database
    session.refresh(room)  # Sync the room instance with the database row

    return room


@app.get(
    "/rooms",
    status_code=status.HTTP_200_OK,
    tags=["rooms"],
    summary="List all available rooms",
    description="Returns all rooms. Supports filtering by price and search term",
    response_description="List of rooms matching the filter criteria",
)
def get_rooms(session: SessionDep, params: Annotated[RoomQueryParams, Query()]):
    statement = select(Room)

    if params.max_price:
        statement = statement.where(Room.price_per_night <= params.max_price)

    if params.search:
        statement = statement.where(col(Room.name).ilike(f"%{params.search}%"))

    statement = statement.limit(params.limit).offset(params.offset).order_by(Room.id)

    results = session.exec(statement).all()

    return results


@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK, tags=["rooms"])
def get_room(
    session: SessionDep,
    room_id: RoomId,
) -> Room:
    room = session.get(Room, room_id)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Room: {room_id} not found"
        )

    return room


@app.get("/preferences", status_code=status.HTTP_200_OK, tags=["preferences"])
def set_preferences(response: Response):
    app_cookies = AppCookies()

    response.set_cookie("theme", app_cookies.theme)
    response.set_cookie("language", app_cookies.language)

    return {"message": "Preferences updated"}
