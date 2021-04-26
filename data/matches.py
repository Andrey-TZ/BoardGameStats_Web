import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Matches(SqlAlchemyBase):
    __tablename__ = 'matches'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    game_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('games.id'))
    result = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    user = orm.relation('User')
    game = orm.relation('Games')
