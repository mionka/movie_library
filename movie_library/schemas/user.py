# pylint: disable=no-self-argument
from datetime import datetime

from pydantic import BaseModel, EmailStr, constr, validator

from movie_library.config import get_settings


class User(BaseModel):
    username: str
    email: EmailStr
    dt_created: datetime
    dt_updated: datetime

    class Config:
        orm_mode = True


class RegistrationForm(BaseModel):
    username: str
    password: constr(min_length=8)
    email: EmailStr

    @validator("password")
    def validate_password(cls, password):
        settings = get_settings()
        password = settings.PWD_CONTEXT.hash(password)
        return password


class UserEdit(BaseModel):
    username: str
    password: constr(min_length=8) | None
    email: EmailStr

    @validator("password")
    def validate_password(cls, password):
        settings = get_settings()
        password = settings.PWD_CONTEXT.hash(password)
        return password


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    # role: str
