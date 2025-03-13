from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, field_validator
from starlette import status


class UserOutDTO(BaseModel):
    id: int
    login: str

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class CuisineDTO(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class CuisineOutDTO(CuisineDTO):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DishTypeDTO(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class DishTypeOutDTO(DishTypeDTO):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HashtagDTO(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class HashtagOutDTO(HashtagDTO):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RecipeOutDTO(BaseModel):
    id: int
    title: str
    cooking_time: Optional[int] = None
    content: str
    user: UserOutDTO
    cuisine: CuisineOutDTO
    dish_type: DishTypeOutDTO
    hashtags: List[HashtagOutDTO]

    model_config = ConfigDict(from_attributes=True)


class RecipeInDTO(BaseModel):
    title: str
    cooking_time: Optional[int] = None
    content: str
    cuisine_id: int
    dish_type_id: int
    hashtags: List[int]

    @field_validator('title')
    def validate_title_length(cls, v: str) -> str:
        if len(v) < 2:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='Название должно быть больше 1 символа')
        return v

    @field_validator('content')
    def validate_content_length(cls, v: str) -> str:
        if len(v) < 20:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='Длина содержания должна быть не меньше 20 символов')
        return v

    @field_validator('cooking_time')
    def validate_cooking_time(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v > 2000:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='Время приготовления не должно превышать 2000 минут')
        return v

    model_config = ConfigDict(from_attributes=True)
