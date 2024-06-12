from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repository_users
from config import settings


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.SECRET_KEY_JWT
    ALGORITHM = settings.ALGORITHM
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the pwd_context object to verify that the
        plain-text password matches the hashed one.

        :param self: Represent the instance of the class
        :param plain_password: Store the password that is entered by the user
        :param hashed_password: Check the password that is being passed in against the hashed password stored in the database
        :return: A boolean value
        :doc-author: Trelent
        """
        
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

        :param self: Represent the instance of the class
        :param password: str: Pass the password to be hashed into the function
        :return: A hash of the password
        :doc-author: Trelent
        """
        
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        
        """
        The create_access_token function creates a new access token.

        Args:
            data (dict): A dictionary containing the claims to be encoded in the JWT.
            expires_delta (Optional[float]): An optional parameter specifying how long, in seconds, 
            from now that this token should expire. If not specified, it will default to 15 minutes.

        Returns:
            str: A string with the encoded access token.

        :param self: Access the class variables
        :param data: dict: Pass the claims to be encoded in the jwt
        :param expires_delta: Optional[float]: Specify how long the token will be valid for
        :doc-author: Trelent
        """
        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the refresh token expires. Defaults to None, which sets it to 7 days from now.

        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded in the token
        :param expires_delta: Optional[float]: Set the expiration time for the refresh token
        :return: A refresh token
        :doc-author: Trelent
        """
        
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        
        """
        The decode_refresh_token function is used to decode the refresh token.
        It takes a refresh_token as an argument and returns the email of the user if it's valid.
        If not, it raises an HTTPException with status code 401 (UNAUTHORIZED) and detail 'Could not validate credentials'.


        :param self: Represent the instance of the class
        :param refresh_token: str: Pass in the refresh token that was sent from the client
        :return: The email of the user that is associated with the refresh token
        :doc-author: Trelent
        """
        
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        
        """
        The get_current_user function is a dependency that will be used in the
            protected endpoints. It takes a token as an argument and returns the user
            if it's valid, or raises an exception otherwise.

        :param self: Refer to the class itself
        :param token: str: Get the token from the request header
        :param db: AsyncSession: Get the database session, and the token: str parameter is used to pass in a jwt
        :return: The user object that corresponds to the email in the jwt payload
        :doc-author: Trelent
        """
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    async def create_email_token(self, data: dict):
        
        """
        The create_email_token function takes in a dictionary of data and returns a token.
        The token is created using the JWT library, which encodes the data into a string that can be decoded later.
        The function adds an iat (issued at) key to the dictionary with its value being datetime.now(timezone.utc).
        It also adds an exp (expiration) key to the dictionary with its value being datetime now plus 7 days.

        :param self: Access the class attributes and methods
        :param data: dict: Pass the data that will be encoded into a jwt
        :return: A token that is encoded with the user's email address and a secret key
        :doc-author: Trelent
        """
        
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    async def get_email_from_token(self, token: str):
        
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        The function uses the jwt library to decode the token, which is then used to return the email address.

        :param self: Represent the instance of the class
        :param token: str: Pass the token to the function
        :return: The email address associated with the token
        :doc-author: Trelent
        """
        
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
