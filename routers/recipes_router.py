from typing import List

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status

from database.repositories import RecipeRepo, DishTypeRepo, HashtagRepo, CuisineRepo
from routers.dto.dtos import RecipeOutDTO, CuisineOutDTO, DishTypeOutDTO, HashtagOutDTO, RecipeInDTO
from security.security import check_user_role

recipes_router = APIRouter(prefix='/recipes', tags=['Recipes'])


@recipes_router.get('', response_model=List[RecipeOutDTO],
                    description='Получить рецепты. Возможны фильтры переданные, как query params в формате REST')
async def get_all_recipes(cuisines: list[int] = Query(default=[]),
                          max_cooking_time: int = Query(default=-1),
                          dish_types: list[int] = Query(default=[]),
                          search: str = Query(default=''),
                          hashtags: list[int] = Query(default=[]),
                          author_id: int = Query(default=-1)):
    recipes = await RecipeRepo.get_all(cuisines=cuisines,
                                       max_cooking_time=max_cooking_time,
                                       dish_types=dish_types,
                                       search=search,
                                       hashtags=hashtags,
                                       author_id=author_id)

    if not recipes:
        return []

    return recipes


@recipes_router.get('/cuisines', response_model=List[CuisineOutDTO],
                    description='Получить все кухни')
async def get_all_cuisines():
    return await CuisineRepo.get_all()


@recipes_router.get('/types', response_model=List[DishTypeOutDTO],
                    description='Получить все типы блюд')
async def get_all_dish_types():
    return await DishTypeRepo.get_all()


@recipes_router.get('/hashtags', response_model=List[HashtagOutDTO],
                    description='Получить все хэштеги')
async def get_all_hashtags():
    return await HashtagRepo.get_all()


@recipes_router.post('', response_model=int,
                     description='Добавить рецепт. Возвращает id созданного рецепта')
async def create_recipe(recipe: RecipeInDTO,
                        current_user=Depends(check_user_role)):
    recipe_attrs = recipe.dict()
    hashtags = await HashtagRepo.get_hashtags_by_id_list(ids=recipe.hashtags)
    recipe_attrs['hashtags'] = hashtags
    recipe_attrs['user_id'] = current_user.id

    try:
        recipe_id = await RecipeRepo.add(fields=recipe_attrs)
        return recipe_id
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Какие-то из атрибутов переданы с несуществующими идентификаторами.')
