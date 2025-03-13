from sqlalchemy import String, Table, Column, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.model.attributes import Role

recipe_hashtags = Table(
    'recipe_hashtags',
    Base.metadata,
    Column('recipe_id', ForeignKey('recipes.id'), primary_key=True),
    Column('hashtag_id', ForeignKey('hashtags.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    login: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(
        default=Role.USER,
        server_default=text("'USER'"),
        nullable=False
    )

    recipes: Mapped[list['Recipe']] = relationship('Recipe',
                                                   back_populates='user',
                                                   )


class Hashtag(Base):
    __tablename__ = 'hashtags'

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    recipes: Mapped[list['Recipe']] = relationship('Recipe',
                                                   secondary=recipe_hashtags,
                                                   back_populates='hashtags'
                                                   )


class Cuisine(Base):
    __tablename__ = 'cuisines'

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    recipes: Mapped[list['Recipe']] = relationship('Recipe',
                                                   back_populates='cuisine',
                                                   )


class DishType(Base):
    __tablename__ = 'dish_types'

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    recipes: Mapped[list['Recipe']] = relationship('Recipe',
                                                   back_populates='dish_type',
                                                   )


class Recipe(Base):
    __tablename__ = 'recipes'

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    cooking_time: Mapped[int | None]
    content: Mapped[str] = mapped_column(nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped['User'] = relationship('User', back_populates='recipes')

    cuisine_id: Mapped[int] = mapped_column(ForeignKey("cuisines.id"))
    cuisine: Mapped['Cuisine'] = relationship('Cuisine', back_populates='recipes')

    dish_type_id: Mapped[int] = mapped_column(ForeignKey("dish_types.id"))
    dish_type: Mapped['DishType'] = relationship('DishType', back_populates='recipes')

    hashtags: Mapped[list['Hashtag']] = relationship('Hashtag',
                                                     secondary=recipe_hashtags,
                                                     back_populates='recipes',
                                                     lazy='joined'
                                                     )
