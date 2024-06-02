from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models import User
from src.schemas.schemas import UserModel


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserModel, db: AsyncSession) -> User:
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
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        await db.commit()

    
async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    user.refresh_token = token
    await db.commit()

async def update_avatar(email, url: str, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    if user:
        user.avatar = url
        await db.commit()
        await db.refresh(user)
        return user

async def update_password(email, password: str | None, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    if user:
        user.password = password
        await db.commit()
        await db.refresh(user)
        return user
