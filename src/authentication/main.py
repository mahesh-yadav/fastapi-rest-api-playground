import secrets
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select

from authentication.database import SessionDep, create_db_and_tables
from authentication.models import (
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetToken,
    User,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from authentication.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
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
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
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
    refresh_token = create_refresh_token(data={"sub": existing_user.email})

    # bearer token: client has the responsibility to send the token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@app.post("/token/refresh")
def refresh_token(session: SessionDep, refresh_token: Annotated[str, Body(embed=True)]):
    payload = decode_token(refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "refresh":
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

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


user_router = APIRouter(tags=["users"], dependencies=[Depends(get_current_user)])


@user_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user


@user_router.patch("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
def update_me(
    session: SessionDep, current_user: CurrentUser, update_payload: UserUpdate
):
    if not update_payload.email:
        return current_user

    # new email should not belong to another user
    user_with_email = session.exec(
        select(User).where(User.email == update_payload.email)
    ).first()
    if user_with_email and user_with_email.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken"
        )

    current_user.email = update_payload.email
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


app.include_router(user_router)


@app.post("/password-request/request")
def request_password_reset(session: SessionDep, payload: PasswordResetRequest):
    message = {
        "message": "If an account exists with this email, a reset link has been sent"
    }

    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not user.id:
        return message

    token = secrets.token_urlsafe(nbytes=32)

    reset_token = PasswordResetToken(
        token=token,
        user_id=user.id,
        expires_at=datetime.now(UTC) + timedelta(minutes=10),
    )

    session.add(reset_token)
    session.commit()

    # In prod, send an email to the user

    return message


@app.post("/password-request/confirm")
def confirm_password_reset(session: SessionDep, payload: PasswordResetConfirm):
    reset_token = session.exec(
        select(PasswordResetToken).where(PasswordResetToken.token == payload.token)
    ).first()

    if not reset_token or reset_token.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token"
        )

    token_expired = reset_token.expires_at < datetime.now(UTC).replace(tzinfo=None)
    if token_expired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token"
        )

    user = session.get(User, reset_token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token"
        )

    user.hashed_password = hash_password(payload.new_password)
    session.add(user)
    reset_token.used = True
    session.add(reset_token)

    session.commit()

    # In prod, send an email to the user

    return {"message": "Password reset successfully"}
