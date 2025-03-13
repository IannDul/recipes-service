from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from starlette import status

from config import settings
from database.model.attributes import Role
from database.model.models import User
from database.repositories import UserRepo
from routers.dto.auth_dtos import TokenData

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta
                                  if expires_delta
                                  else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                                  )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


async def authenticate_user(login: str, password: str):
    user = await UserRepo.get_user_by_login(login)

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Невалидные учётные данные',
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        login: str | None = payload.get('login')

        if not login:
            raise credentials_exception

        token_data = TokenData(login=login)
    except PyJWTError:
        raise credentials_exception

    user = await UserRepo.get_user_by_login(login=token_data.login)

    if user is None:
        raise credentials_exception

    return user


async def check_user_role(current_user: User = Depends(get_current_user)):
    if current_user.role not in [Role.USER, Role.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Пользователь должен быть авторизован, чтобы совершить это действие')
    return current_user


async def check_admin_role(current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Пользователь должен быть администратором, чтобы совершить это действие')
    return current_user
