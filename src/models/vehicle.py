from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint


class Vehicle(Base):
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True)
    stock_number = Column(String, nullable=False)
    model = Column(String, nullable=False)
    color = Column(String, nullable=False)
    year = Column(String, nullable=False)
    location = Column(String, nullable=False)
    row = Column(String, nullable=False)
    date_recieved = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('stock_number', 'model', name='uix_stock_make_model'),
    )

    def __repr__(self):
        return f"<Vehicle(stock_number='{self.stock_number}', year={self.year}, model='{self.model}')>"
