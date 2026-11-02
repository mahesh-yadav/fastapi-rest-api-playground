from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select

from authentication.database import SessionDep, create_db_and_tables
from authentication.models import User, UserCreate, UserResponse
from authentication.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


def get_current_user(
    session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]
):
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(session: SessionDep, user_data: UserCreate):
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    new_user = User(
        email=user_data.email, hashed_password=hash_password(user_data.password)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@app.post("/token", status_code=status.HTTP_200_OK)
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)],
):
    existing_user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": existing_user.email})

    # bearer token: client has the responsibility to send the token
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user
