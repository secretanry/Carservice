import sqlalchemy
from .db_session import SqlAlchemyBase


class History(SqlAlchemyBase):
    __tablename__ = 'history'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    car_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('cars.id'), nullable=False)
    work_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('works.id'), nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    km = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    date = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)