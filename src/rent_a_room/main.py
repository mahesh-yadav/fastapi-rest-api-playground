from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, StringConstraints, field_validator

openapi_tags = [
    {
        "name": "rooms",
        "description": "Operations with **rooms** (a 4-wall _space_ that can be slept in)",
    }
]


app = FastAPI(
    title="Rent a Room API",
    description="Book a stay in a house or room",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

apartment = {
    "id": 1,
    "name": "Sunny 2-bedroom apartment",
    "price_per_night": 200,
    "bedrooms": 2,
    "bathrooms": 1.5,
}

house = {
    "id": 2,
    "name": "Cozy 3-bedroom house",
    "price_per_night": 350,
    "bedrooms": 3,
    "bathrooms": 2.5,
}

studio = {
    "id": 3,
    "name": "Modern studio near museum",
    "price_per_night": 150,
    "bedrooms": 1,
    "bathrooms": 1,
}


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

    @field_validator("search")
    @classmethod
    def fail_if_funny(cls, search: str) -> str:
        if "lol" in search:
            raise ValueError("No funny business allowed")
        return search


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Welcome to rent a room"}


@app.get(
    "/rooms",
    status_code=status.HTTP_200_OK,
    tags=["rooms"],
    summary="List all available rooms",
    description="Returns all rooms. Supports filtering by price and search term",
    response_description="List of rooms matching the filter criteria",
)
def get_rooms(params: Annotated[RoomQueryParams, Query()]):
    results = [apartment, house, studio]

    if params.search:
        results = [room for room in results if params.search in room["name"].lower()]

    if params.max_price:
        results = [
            room for room in results if room["price_per_night"] <= params.max_price
        ]

    return results


@app.get(
    "/rooms/mansions", status_code=status.HTTP_200_OK, tags=["rooms"], deprecated=True
)
def get_mansions(params: Annotated[RoomQueryParams, Query()]):
    results = [house]

    if params.search:
        results = [room for room in results if params.search in room["name"].lower()]

    if params.max_price:
        results = [
            room for room in results if room["price_per_night"] <= params.max_price
        ]

    return results


@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK, tags=["rooms"])
def get_room(room_id: int):
    for room in [apartment, house, studio]:
        if room["id"] == room_id:
            return room

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Room: {room_id} not found"
    )
