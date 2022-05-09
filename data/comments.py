import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    news_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("news.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    news = orm.relation('News')
