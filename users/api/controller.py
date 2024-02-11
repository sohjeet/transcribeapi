from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app import User
from app import get_db
from ..accounts import generate_username, generate_password
from ..schemas import UserCreate, UserInDB, UserUpdate, AccessToken
from users import auth_service, get_current_active_user, user_is_admin
from app.mail import send_welcome_email

# Create a new APIRouter instance
router = APIRouter()

''' user_create: This function creates a new user in the database. It takes a UserCreate object and a database session as arguments and returns a UserInDB object.'''
@router.post(
    "/create",
    tags=["User Create"],
    description="Register the User",
    response_model=UserInDB,
)
async def user_create(user: UserCreate, 
                      db: Session = Depends(get_db),
                      admin: bool = Depends(user_is_admin)) -> UserInDB:
    generated_username = generate_username(user.email)
    generated_password = generate_password()
    new_password = auth_service.create_hashed_password(plaintext_password=generated_password)

    initial_credit = 60
    try:
        created_user = User(**user.model_dump(),
                            username=generated_username, 
                            password=new_password,
                            current_credit=initial_credit,
                            )
        # created_user.save()  # Assuming your User model has an async save method
        db.add(created_user)
        db.commit()
        db.refresh(created_user)
        send_welcome_email(created_user.username, generated_password, created_user.email, initial_credit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
    return created_user

''' login: This function logs in a user. It takes a form_data object and a database session as arguments and returns an AccessToken object.'''
@router.post(
    '/login',
    tags=["User Login"],
    description="Log in the User",
)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), 
                db: Session= Depends(get_db),
                ) :
    found_user = db.query(User).filter(User.username == form_data.username).first()
    if auth_service.verify_password(password=form_data.password, hashed_pw=found_user.password):
        # If the provided password is valid one then we are going to create an access token
        token = auth_service.create_access_token(user=found_user)
        if token is None:
            raise HTTPException(status_code=500, detail='Failed to create access token')
        return AccessToken(access_token=token, token_type='bearer')
    raise HTTPException(status_code=401, detail='Incorrect password provided')

''' get_me: This function returns the current logged in user. It takes a UserInDB object as an argument and returns a UserInDB object.'''
@router.get(
    "/me",
    tags=["Get current logged in user"],
    description="Get current logged in user",
    response_model=UserInDB,
)
async def get_me(current_user = Depends(get_current_active_user)) :
    return current_user

''' read_users: This function returns all the users in the database. It takes a database session as an argument and returns a list of UserInDB objects.'''
@router.get("/", 
            tags=["Get all users"],
            description="Get all users",
            response_model=List[UserInDB])
def read_users(db: Session = Depends(get_db),
               admin: bool = Depends(user_is_admin)):
    if admin:
        users = db.query(User).all()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to view this page.")
    return users


''' get_users: This function returns a user by username. It takes a username and a database session as arguments and returns a UserInDB object.'''
@router.get("/{username}", 
            tags=["Get user by username"],
            description="Get user by username",
            response_model=UserInDB)
async def get_user(username:str, db: Session= Depends(get_db),
                admin: bool = Depends(user_is_admin) 
              ):
    if admin:
        user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User: {username} does not exist.")
    return user

''' delete_user: This function deletes a user by username. It takes a username and a database session as arguments and returns a UserInDB object.'''
@router.delete("/{username}", 
               tags=["Delete user by username"],
               description="Delete user by username",
               response_model=UserInDB)
async def delete_user(username: str, db: Session = Depends(get_db), 
                admin: bool = Depends(user_is_admin)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User: {username} does not exist.")

    if admin:
        db.delete(user)
        db.commit()
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to delete this user.")


''' update_user: This function updates a user by username. It takes a username, a UserUpdate object, and a database session as arguments and returns a UserInDB object.'''
@router.put("/{username}",
            tags=["Update user by username"],
            description="Update user by username",
            response_model=UserInDB)
async def update_user(username: str, 
                user_input: UserUpdate, db: Session = Depends(get_db),
                admin: bool = Depends(user_is_admin)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User: {username} does not exist.")
    
    if admin:
        for key, value in user_input.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to update this user.")