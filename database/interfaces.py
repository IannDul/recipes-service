from typing import Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import connection


class BaseReadable:
    model = None

    def __new__(cls, *args, **kwargs):
        if cls is BaseReadable:
            raise TypeError('Нельзя создавать экземпляры базового класса BaseReadable.')
        return super().__new__(cls)

    @classmethod
    @connection
    async def get_all(cls, session: AsyncSession):
        query = select(cls.model)
        result = await session.execute(query)
        records = result.scalars().all()

        return records

    @classmethod
    @connection
    async def get_by_id(cls, model_id: int, session: AsyncSession):
        query = select(cls.model).filter_by(id=model_id)
        result = await session.execute(query)
        record = result.scalar().one_or_none()

        return record


class BaseWritable:
    model = None

    def __new__(cls, *args, **kwargs):
        if cls is BaseWritable:
            raise TypeError('Нельзя создавать экземпляры базового класса BaseWritable.')
        return super().__new__(cls)

    @classmethod
    @connection
    async def add(cls, fields: Dict[str, Any], session: AsyncSession):
        new_instance = cls.model(**fields)
        session.add(new_instance)
        await session.commit()

        return new_instance.id
