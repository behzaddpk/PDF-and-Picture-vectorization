from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, Boolean, func
# from app.db.config import DATABASE_URL
load_dotenv()

DATABASE_URL='postgresql://postgres.wooeiskurodztyfcgdtk:HasteAI!24!@aws-0-ap-south-1.pooler.supabase.com:5432/postgres'

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
