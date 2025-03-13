from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from config import settings
from database.repositories import UserRepo
from routers.dto.auth_dtos import UserCreateDTO, Token
from routers.dto.dtos import UserOutDTO
from security.security import get_password_hash, authenticate_user, create_access_token, get_current_user

auth_router = APIRouter(prefix='/auth', tags=['Auth'])


@auth_router.post('/register', response_model=UserOutDTO,
                  description='Регистрация пользователя с ролью USER')
async def register(user: UserCreateDTO):
    existing_user = await UserRepo.get_user_by_login(user.login)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользователь с таким логином уже существует'
        )

    hashed_password = get_password_hash(user.password)

    new_user = await UserRepo.register_user(login=user.login, password=hashed_password)

    return new_user


@auth_router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(login=form_data.username,
                                   password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверное имя пользователя или пароль',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'login': user.login}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type='bearer')


@auth_router.get('/users/me', response_model=UserOutDTO)
async def read_current_user(current_user=Depends(get_current_user)):
    return current_user
