from sqlalchemy import create_engine, Index, Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import getenv
import datetime

Base = declarative_base()

def init_db():
  global session
  dburl = getenv("DB_URL")
  engine = create_engine(dburl, echo=False)
  Base.metadata.create_all(engine)
  Session = sessionmaker(bind=engine)
  session = Session()

class Page(Base):
  __tablename__ = "pages"
  id = Column(Integer, primary_key=True)
  url = Column(String(1024), nullable=False, unique=True)
  date_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
  date_scraped = Column(DateTime)

class Recipe(Base):
  __tablename__ = "recipes"
  id = Column(Integer, primary_key=True)
  page_id = Column(Integer, ForeignKey("pages.id"), nullable=False, unique=True)
  recipe_info = Column(JSON, nullable=False)
  date_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
