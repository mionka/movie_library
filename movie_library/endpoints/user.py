from datetime import timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from movie_library.config import get_settings
from movie_library.db.connection import get_session
from movie_library.db.models import User
from movie_library.schemas import MessageSuccess, RegistrationForm, Token
from movie_library.schemas import User as UserSchema
from movie_library.schemas import UserEdit
from movie_library.utils.user import (
    authenticate_user,
    create_access_token,
    delete_user,
    get_current_user,
    register_user,
    update_user,
)


api_router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@api_router.post(
    "/registration",
    status_code=status.HTTP_201_CREATED,
    response_model=MessageSuccess,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad parameters for registration.",
        },
    },
)
async def registration(
    _: Request,
    registration_form: RegistrationForm = Body(...),
    session: AsyncSession = Depends(get_session),
):
    is_success, message = await register_user(session, registration_form)
    if is_success:
        return {"message": message}

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )


@api_router.post(
    "/authentication",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate cerdentials.",
        },
    },
)
async def authentication(
    _: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@api_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials.",
        },
    },
)
async def get_me(
    _: Request,
    current_user: User = Depends(get_current_user),
):
    return UserSchema.from_orm(current_user)


@api_router.put(
    "/edit",
    status_code=status.HTTP_200_OK,
    response_class=Response,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Could not change user info.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials.",
        },
    },
)
async def edit(
    edited_user: UserEdit,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result, message = await update_user(session, current_user, edited_user)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@api_router.delete(
    "/takeout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials.",
        },
    },
)
async def takeout(
    _: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await delete_user(session, current_user)
