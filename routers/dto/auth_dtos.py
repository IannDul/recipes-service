from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, field_validator
from starlette import status

from database.model.attributes import Role


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    login: str | None = None


class UserAuthDTO(BaseModel):
    id: int
    login: str
    role: Role

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class UserCreateDTO(BaseModel):
    login: str
    password: str

    @field_validator('login')
    def validate_login(cls, v: str) -> str:
        if len(v) < 5:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='Логин должен быть не менее 5 символов')
        return v

    @field_validator('password')
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='Длина пароля должна быть не менее 8 символов')
        return v
