from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models import User
from src.schemas.schemas import UserModel


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email. If no such user exists, it returns None.

    :param email: str: Filter the user by email
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    :doc-author: Trelent
    """
    
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserModel, db: AsyncSession) -> User:
    
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Pass in the user model that is created from the request body
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def confirmed_email(email: str, db: AsyncSession) -> None:
    
    """
    The confirmed_email function is used to set the confirmed field of a user in the database
    to True. This function is called when a user clicks on an email confirmation link sent to them
    by the application.

    :param email: str: Get the email of the user that is being confirmed
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        await db.commit()

    
async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user in the database
    :param token: str | None: Specify that the token parameter can be a string or none
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    
    user.refresh_token = token
    await db.commit()

async def update_avatar(email, url: str, db: AsyncSession) -> User:
    
    """
    The update_avatar function updates the avatar of a user.

    :param email: Get the user from the database
    :param url: str: Specify the type of the parameter
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    
    user = await get_user_by_email(email, db)
    if user:
        user.avatar = url
        await db.commit()
        await db.refresh(user)
        return user

async def update_password(email, password: str | None, db: AsyncSession) -> User:
    
    """
    The update_password function updates the password of a user.

    :param email: Find the user in the database
    :param password: str | None: Set the password of a user
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    
    user = await get_user_by_email(email, db)
    if user:
        user.password = password
        await db.commit()
        await db.refresh(user)
        return user
