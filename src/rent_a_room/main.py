from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request

from rent_a_room.dependencies.database import create_db_and_tables
from rent_a_room.errors import register_error_handlers
from rent_a_room.routers import bookings, general, rooms, users

openapi_tags = [
    {
        "name": "rooms",
        "description": "Operations with **rooms** (a 4-wall _space_ that can be slept in)",
    }
]


def log_request(request: Request):
    print(f"{request.method} / {request.url.path}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    dependencies=[Depends(log_request)],
    title="Rent a Room API",
    description="Book a stay in a house or room",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

register_error_handlers(app)

app.include_router(general.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
app.include_router(users.router)
