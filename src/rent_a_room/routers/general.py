from typing import Annotated, Literal

from fastapi import APIRouter, Cookie, Header, Response, status
from pydantic import BaseModel

router = APIRouter()


class AppCookies(BaseModel):
    language: Literal["en", "es", "fr"] = "en"
    theme: Literal["dark", "light"] = "dark"


@router.get("/", status_code=status.HTTP_200_OK)
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


@router.get("/preferences", status_code=status.HTTP_200_OK, tags=["preferences"])
def set_preferences(response: Response):
    app_cookies = AppCookies()

    response.set_cookie("theme", app_cookies.theme)
    response.set_cookie("language", app_cookies.language)

    return {"message": "Preferences updated"}
