from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from todo_app.core.database import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    db = session()
    try:
        yield db
    finally:
        db.close()