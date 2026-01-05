import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.environ.get('LEADS_DB', os.path.join(DATA_DIR, 'leads.db'))

DATABASE_URL = f'sqlite:///{DB_PATH}'

# For sqlite + SQLAlchemy in multi-threaded webserver, disable same_thread check
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    email = Column(String(200), index=True)
    message = Column(Text)
    ip = Column(String(45))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    emailed = Column(Boolean, default=False)
    emailed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)
