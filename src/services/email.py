from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="Olesia Shevchuk",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_confirm_email(email: EmailStr, username: str, host: str):
    
    """
    Sends a confirmation email to the user with a link to confirm their email address.

    The function takes the following parameters:
    
    Args:
        email (EmailStr): The user's email address. This is used both as the recipient of the message and as part of
        token_verification.
        username (str): The username of the user who is registering. This is used to personalize the message.
        host (str): The host of the server. This is used to generate the confirmation link.
    Returns:
        None

    :param email: EmailStr: Specify the email address of the user
    :param username: str: Get the username of the user who is registering
    :param host: str: Get the host of the server
    :return: None
    :doc-author: Trelent
    """
    
    try:
        token_verification = await auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_email(email: EmailStr, username: str, host: str):
    
    """
    The send_reset_email function sends a password reset email to the user.

    :param email: EmailStr: Validate the email address
    :param username: str: Identify the user in the database
    :param host: str: Pass the hostname of the server to send_reset_email function
    :return: A coroutine
    :doc-author: Trelent
    """
    
    try:
        token_verification = auth_service.create_access_token({"username": username})
        message = MessageSchema(
            subject="Reset password",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_template.html")
    except ConnectionErrors as err:
        print(err)


async def send_update_email(email: EmailStr, username: str, host: str):
    
    """
    The send_update_email function sends an email to the user with a link to reset their password.
        Args:
            email (str): The user's email address.
            username (str): The username of the account that needs its password reset.
            host (str): The hostname of the server where this function is being called from.

    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Identify the user
    :param host: str: Pass the hostname of the server to
    :return: A coroutine, which is an object that can be awaited
    :doc-author: Trelent
    """
    
    try:
        message = MessageSchema(
            subject="Reset password",
            recipients=[email],
            template_body={"host": host, "username": username},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_template.html")
    except ConnectionErrors as err:
        print(err)
        