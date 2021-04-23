import sqlalchemy
from .db_session import SqlAlchemyBase


class Cars(SqlAlchemyBase):
    __tablename__ = 'cars'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    person_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.login'), nullable=False)
    photo = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)
    mark = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    model = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    gen = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    km = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    year = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    vin = sqlalchemy.Column(sqlalchemy.String, nullable=True)