from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from app.core.config import settings
from jose import JWTError, jwt
from typing import Optional
from sqlalchemy.orm import Session
from app import User
from app import get_db
from .schemas import  UserInDB, JWTCreds, JWTPayload, JWTMeta, TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

''' Authenticate: This class will contain methods for hashing and verifying passwords, creating access tokens, and verifying access tokens. It will also contain a method for getting the current user from the database.'''
class Authenticate:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    ''' hash_password: This method will take a password and return a hashed version of it.'''
    def hash_password(self, *, password: str) -> str:
        return pwd_context.hash(password)

    ''' verify_password: This method will take a password and a hashed password and return True if the password matches the hashed password, and False if it does not.'''
    def verify_password(self, *, password: str, hashed_pw: str) -> bool:
        return pwd_context.verify(password, hashed_pw)

    ''' create_hashed_password: This method will take a plaintext password and return a hashed version of it. This method will be used when creating a new user.'''
    def create_hashed_password(self, *, plaintext_password: str) :
        hashed_password = self.hash_password(password=plaintext_password)
        return hashed_password

    ''' create_access_token: This method will take a user and return an access token. This method will be used when a user logs in.'''
    def create_access_token(self, *, user, secret_key: str = str(settings.SECRET_KEY), audience: str = settings.JWT_AUDIENCE, expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,) -> Optional[str]:
        if not user :
            return None
        issued_at = datetime.timestamp(datetime.now())
        expiration_time = int(datetime.timestamp(datetime.now() + timedelta(minutes=expires_in)))
        jwt_meta = JWTMeta(aud=audience, iat=issued_at, exp=expiration_time)
        jwt_creds = JWTCreds(sub=user.email, username=user.username)
        token_payload = JWTPayload(**jwt_meta.model_dump(), **jwt_creds.model_dump(),)
        token = jwt.encode(token_payload.model_dump(), secret_key, algorithm=settings.JWT_ALGORITHM)
        return token

    ''' verify_access_token: This method will take an access token and return the username of the user. This method will be used when a user makes a request to an endpoint that requires authentication.'''
    def verify_access_token(self, *,token:str, credentials_exception:Exception, secret_key: str = str(settings.SECRET_KEY)) -> Optional[str]:
        try:
            decoded_token = jwt.decode(token, secret_key, audience=settings.JWT_AUDIENCE, algorithms=[settings.JWT_ALGORITHM])
            payload = JWTPayload(**decoded_token)
        except (JWTError, ValidationError):
            raise credentials_exception
        username = payload.model_dump().get('username')
        return TokenData(username=username)
    
    ''' get_current_user: This method will take an access token and return the user from the database. This method will be used when a user makes a request to an endpoint that requires authentication.'''
    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserInDB:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            token_data = self.verify_access_token(token=token, credentials_exception=credentials_exception)
        except JWTError :
            raise credentials_exception
        user = db.query(User).filter(User.username == token_data.username).first()
        if user is None:
            raise credentials_exception
        return user

''' get_current_active_user: This function will take a UserInDB object and verify that the user is active. If the user is not active, it will raise an HTTPException.'''
async def get_current_active_user(current_user:UserInDB = Depends(Authenticate().get_current_user)) -> UserInDB:
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

''' user_is_admin: This function will take a UserInDB object and verify that the user is an admin. If the user is not an admin, it will raise an HTTPException.'''
def user_is_admin(current_user: UserInDB = Depends(Authenticate().get_current_user)) -> UserInDB:
    if not current_user.is_admin:
        raise HTTPException(status_code=401, detail="You have not enough privileges")
    return True