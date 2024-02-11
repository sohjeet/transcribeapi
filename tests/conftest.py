import pytest
import sys
from datetime import datetime 
sys.path.append("C:/Users/admin/Desktop/fastAPI")

from app.main import app
from httpx import AsyncClient

from users.schemas import UserInDB, UserCreate
from users import auth_service
from users.accounts import generate_username


@pytest.fixture(scope="class")
def auth_obj():
    return auth_service


@pytest.fixture(scope="class")
def dummy_user() -> UserInDB:
    new_user = UserCreate(
        email="dummy_user@example.com",
        password="dummyuserswesomepass"
    )
    generated_username = generate_username(new_user.email)
    new_password = auth_service.create_hashed_password(plaintext_password=new_user.password)
    new_user.password = new_password
    credit = 60
    time = datetime.now()
    return UserInDB(**new_user.model_dump(), username=generated_username, current_credit=credit, created_at=time, updated_at=time)
