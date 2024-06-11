from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_confirm_email, send_reset_email, send_update_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks,
                 request: Request, db: AsyncSession = Depends(get_db)):
    
    """
    The signup function creates a new user in the database.
        It takes a UserModel object as input, which is validated by pydantic.
        If the email address already exists in the database, an HTTP 409 error is raised.
        The password field of the UserModel object is hashed using Argon2 and stored in that form.
        A new user record is created with this information and returned to the client.

    :param body: UserModel: Get the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the server
    :param db: AsyncSession: Get the database session
    :return: A dictionary with the user and a detail message
    :doc-author: Trelent
    """
    
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_confirm_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    
    """
    The login function is used to authenticate a user.
        It takes in the username and password of the user, verifies them against
        what's stored in the database, and returns an access token if successful.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: AsyncSession: Pass the database session to the function
    :return: A dict with the following keys:
    :doc-author: Trelent
    """
    
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: AsyncSession = Depends(get_db)):
    
    """
    The refresh_token function is used to refresh the access token.
    It takes in a refresh token and returns a new access token.
    The function first decodes the refresh_token to get the email of the user who owns it, then gets that user from
    the database and checks if their stored refresh_token matches what was passed in. If they don't match, we update
    the users stored tokens with None (effectively logging them out) and raise an HTTPException with status code 401
    (UNAUTHORIZED). If they do match, we create new tokens for this user using auth_service's create functions

    :param credentials: HTTPAuthorizationCredentials: Get the access token from the request header
    :param db: AsyncSession: Get the database session
    :return: The same payload as the login function
    :doc-author: Trelent
    """
    
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it checks if that user exists in our database, and if they do not exist, returns an error message.
        If they do exist but their account has already been confirmed, we return a message saying so.
        Otherwise (if they are real and have not yet confirmed), we update their account status in our database.

    :param token: str: Get the token from the url
    :param db: AsyncSession: Get the database session
    :return: A message that the email is already confirmed
    :doc-author: Trelent
    """
    
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed == True:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    
    """
    The request_email function is used to send a confirmation email to the user.
    It takes in an email address and sends a confirmation link to that address.
    The function also checks if the user has already confirmed their account, and returns an error message if they have.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks
    :param request: Request: Get the base url of the server
    :param db: AsyncSession: Get the database session
    :return: A message to the user
    :doc-author: Trelent
    """
    
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_confirm_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}

@router.post("/forget_password")
async def forget_password(background_tasks: BackgroundTasks, user: UserModel, request: Request,
                            db: AsyncSession = Depends(get_db)):
    
    """
    The forget_password function is used to send a reset password email to the user.
        The function takes in the following parameters:
            background_tasks: BackgroundTasks,
            user: UserModel,
            request: Request,
            db: AsyncSession = Depends(get_db)

    :param background_tasks: BackgroundTasks: Add a task to the background tasks
    :param user: UserModel: Get the email from the user
    :param request: Request: Get the base url of the application
    :param db: AsyncSession: Pass in the database session
    :return: A message to the user
    :doc-author: Trelent
    """
    
    user_in_db = await repository_users.get_user_by_email(user.email, db)    
    if user_in_db:
        background_tasks.add_task(send_reset_email, user_in_db.email, user_in_db.username, request.base_url)
    return {"message": "Check your email for reset password."}
    

@router.post("/reset_password/{token:str}")
async def reset_password(token: str, body: UserModel, background_tasks: BackgroundTasks, request: Request,
                         db: AsyncSession = Depends(get_db)):
    
    """
    The reset_password function is used to reset a user's password.
        It takes in the token from the email sent to the user, and then uses that token to get their email address.
        The function then gets their username using that email address, and updates their password with a new one.

    :param token: str: Get the email of the user who requested a password reset
    :param body: UserModel: Get the user's new password
    :param background_tasks: BackgroundTasks: Add a background task to the queue
    :param request: Request: Get the base_url of the application
    :param db: AsyncSession: Get the database session
    :return: A dict with a user and detail key
    :doc-author: Trelent
    """
    
    email = await auth_service.get_email_from_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user = await repository_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password = auth_service.get_password_hash(body.password)
    updated_user = await repository_users.update_password(user, db)
    background_tasks.add_task(send_update_email, user.email, user.username, request.base_url)
    return {"user": updated_user, "detail": "Password successfully reset. Check your email for confirmation."}
