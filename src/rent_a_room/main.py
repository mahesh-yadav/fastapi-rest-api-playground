from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import AfterValidator

app = FastAPI(
    title="Rent a Room API",
    description="Book a stay in a house or room",
    version="1.0.0",
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

search_query_validation = Query(
    min_length=3,
    max_length=10,
    title="Search term",
    description="Provide a keyword to look for within the room's title",
)


def fail_if_funny(search: str):
    if "lol" in search:
        raise ValueError("No funny business allowed")
    return search


search_humor_ban_validation = AfterValidator(fail_if_funny)

SearchQuery = Annotated[
    str | None,
    search_query_validation,
    search_humor_ban_validation,
]


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Welcome to rent a room"}


@app.get("/rooms", status_code=status.HTTP_200_OK)
def get_rooms(
    search: SearchQuery = None,
    max_price: Annotated[int | None, Query(ge=10, le=10_000)] = None,
):
    results = [apartment, house, studio]

    if search:
        results = [room for room in results if search.lower() in room["name"].lower()]

    if max_price:
        results = [room for room in results if room["price_per_night"] <= max_price]

    return results


@app.get("/rooms/mansions", status_code=status.HTTP_200_OK)
def get_mansions(
    search: SearchQuery = None,
    max_price: Annotated[int | None, Query(ge=10, le=10_000)] = None,
):
    results = [house]

    if search:
        results = [room for room in results if search.lower() in room["name"].lower()]

    if max_price:
        results = [room for room in results if room["price_per_night"] <= max_price]

    return results


@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK)
def get_room(room_id: int):
    for room in [apartment, house, studio]:
        if room["id"] == room_id:
            return room

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Room: {room_id} not found"
    )
