from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = None
Session = None


def init_db(db_location='./benz_finder.db'):
    global engine, Session
    engine = create_engine(f"sqlite:///{db_location}")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)


def get_session():
    global Session
    if Session is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return Session()
