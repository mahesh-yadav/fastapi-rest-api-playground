from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from rent_a_room.schemas.errors import ErrorResponse


class AppError(Exception):
    status_code = 500
    default_detail = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    default_detail = "Resource not found"


class RoomNotFound(NotFoundError):
    default_detail = "Room not found"


class UserNotFound(NotFoundError):
    default_detail = "User not found"


class BookingNotFound(NotFoundError):
    default_detail = "Booking not found"


class ServiceUnderMaintenance(AppError):
    status_code = 503
    default_detail = "Service is under maintenance. Try again later"


def register_error_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(detail=exc.detail).model_dump(),
        )
