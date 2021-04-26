import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Results(SqlAlchemyBase):
    __tablename__ = 'results'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String,  nullable=True)
