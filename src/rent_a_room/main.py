from fastapi import FastAPI, HTTPException, status

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


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Welcome to rent a room"}


@app.get("/rooms", status_code=status.HTTP_200_OK)
def get_rooms():
    return [apartment, house, studio]


@app.get("/rooms/faq", status_code=status.HTTP_200_OK)
def rooms_faq():
    return {"check_in": "From 3PM", "check_out": "Until 11AM"}


@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK)
def get_room(room_id: int):
    for room in [apartment, house, studio]:
        if room["id"] == room_id:
            return room

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Room: {room_id} not found"
    )
