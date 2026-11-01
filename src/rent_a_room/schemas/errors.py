from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


# Passed to `responses=` so the errors show up in the OpenAPI docs
type ResponseSpec = dict[int | str, dict[str, Any]]

NOT_FOUND_RESPONSE: ResponseSpec = {
    404: {"model": ErrorResponse, "description": "Not found"}
}
MAINTENANCE_RESPONSE: ResponseSpec = {
    503: {"model": ErrorResponse, "description": "Service under maintenance"}
}
