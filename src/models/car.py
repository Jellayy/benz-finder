from .base import Base
from sqlalchemy import Column, Integer, String


class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True)
