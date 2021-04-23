import sqlalchemy
from .db_session import SqlAlchemyBase


class Works(SqlAlchemyBase):
    __tablename__ = 'works'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    car_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('cars.id'), nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    km = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)