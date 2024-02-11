from pydantic import BaseModel, EmailStr, constr, validator, field_validator
from datetime import datetime, timedelta
from app import settings
from typing import Optional

class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    @field_validator("created_at", "updated_at", mode="before")
    def default_datetime(cls, value: datetime) -> datetime:
        return value or datetime.now()

class UserBase(BaseModel):
    email: Optional[EmailStr]
    username: Optional[str]
    current_credit: int
    is_superuser: bool = False

class UserCreate(BaseModel):
    email: EmailStr
    # password: constr(min_length=7, max_length=100)

class UserInDB(DateTimeModelMixin, UserBase):
    # password: constr(min_length=7, max_length=100)
    pass

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[str] = None
    current_credit: Optional[int] = None

class JWTMeta(BaseModel):
    iss: str = settings.JWT_ISSUER # issuer of the token
    aud: str = settings.JWT_AUDIENCE
    iat: float = datetime.timestamp(datetime.now())
    exp: float = datetime.timestamp(datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


class JWTCreds(BaseModel):
    """How we'll identify users"""
    sub: EmailStr
    username: str


class JWTPayload(JWTMeta, JWTCreds):
    """
    JWT Payload right before it's encoded - combine meta and username
    """
    pass


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
