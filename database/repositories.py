from typing import List

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, joinedload

from database.base import connection
from database.interfaces import BaseReadable, BaseWritable
from database.model.models import Recipe, User, Cuisine, DishType, Hashtag


class RecipeRepo(BaseWritable):
    model = Recipe

    @classmethod
    @connection
    async def get_all(cls,
                      cuisines: List[int],
                      max_cooking_time: int,
                      dish_types: List[int],
                      search: str,
                      hashtags: List[int],
                      author_id: int,
                      session: AsyncSession):
        query = select(cls.model).join(Recipe.hashtags)

        if cuisines:
            query = query.filter(cls.model.cuisine_id.in_(cuisines))
        if max_cooking_time != -1:
            query = query.filter(cls.model.cooking_time.isnot(None),
                                 cls.model.cooking_time <= max_cooking_time
                                 )
        if dish_types:
            query = query.filter(cls.model.dish_type_id.in_(dish_types))
        if author_id != -1:
            query = query.filter(cls.model.user_id == author_id)
        if search:
            query = query.filter(cls.model.title.ilike(f'%{search}%'))
        if hashtags:
            query = query \
                .filter(Hashtag.id.in_(hashtags)) \
                .group_by(cls.model.id) \
                .having(func.count(func.distinct(Hashtag.id)) == len(hashtags))

        query = query.options(
            joinedload(cls.model.user).load_only(User.id, User.login),
            joinedload(cls.model.cuisine).load_only(Cuisine.id, Cuisine.name),
            joinedload(cls.model.dish_type).load_only(DishType.id, DishType.name),
            load_only(cls.model.id, cls.model.title, cls.model.cooking_time, cls.model.content)
        )

        result = await session.execute(query)
        recipes = result.unique().scalars().all()

        return recipes

    @classmethod
    @connection
    async def get_by_id(cls, model_id: int, session: AsyncSession):
        query = select(cls.model).join(Recipe.hashtags)\
            .filter(cls.model.id == model_id)\
            .options(
            joinedload(cls.model.user).load_only(User.id, User.login),
            joinedload(cls.model.cuisine).load_only(Cuisine.id, Cuisine.name),
            joinedload(cls.model.dish_type).load_only(DishType.id, DishType.name),
            load_only(cls.model.id, cls.model.title, cls.model.cooking_time, cls.model.content)
            )

        result = await session.execute(query)
        recipe = result.unique().scalars().one_or_none()

        return recipe

    @classmethod
    @connection
    async def delete_by_id(cls, model_id: int, user_id: int, session: AsyncSession):
        query = (
            delete(cls.model)
            .where(
                (cls.model.id == model_id) &
                (cls.model.user_id == user_id)
            )
            .returning(cls.model.id)
        )
        result = await session.execute(query)
        await session.commit()

        deleted_id = result.scalars().one_or_none()

        return deleted_id


class HashtagRepo(BaseReadable):
    model = Hashtag

    @classmethod
    @connection
    async def get_hashtags_by_id_list(cls, ids: List[int], session: AsyncSession):
        query = (
            select(cls.model)
            .filter(cls.model.id.in_(ids))
        )

        result = await session.execute(query)
        hashtags = result.scalars().all()

        return hashtags


class CuisineRepo(BaseReadable):
    model = Cuisine


class DishTypeRepo(BaseReadable):
    model = DishType


class UserRepo:
    model: User = User

    @classmethod
    @connection
    async def get_user_by_login(cls, login: str, session: AsyncSession):
        query = select(cls.model).filter_by(login=login)
        result = await session.execute(query)
        record = result.scalar_one_or_none()

        return record

    @classmethod
    @connection
    async def register_user(cls, login: str, password: str, session: AsyncSession):
        new_user = cls.model(login=login, password=password)
        session.add(new_user)
        await session.commit()

        return new_user
