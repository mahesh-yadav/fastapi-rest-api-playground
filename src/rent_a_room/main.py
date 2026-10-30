from contextlib import asynccontextmanager

from fastapi import FastAPI

from rent_a_room.dependencies.database import create_db_and_tables
from rent_a_room.routers import general, rooms

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

app.include_router(general.router)
app.include_router(rooms.router)
