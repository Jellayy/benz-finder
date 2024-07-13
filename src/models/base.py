from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///benz_finder.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(engine)
