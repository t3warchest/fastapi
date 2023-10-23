"""
import psycopg2
from psycopg2.extras import RealDictCursor
import time
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:po @{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:           # the response i.e, the db session is first given to path operation and then once it is recieved only then it is closed,,done so that a request creates asingle session and uses it throughout the request
        yield db
    finally:
        db.close()
        
""" To be inserted at --xxHereXX--
while True:
    try:
        conn = psycopg2.connect(host = "localhost", database='fastapi', user='postgres',
                                password='password123', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("sucess")
        break
    except Exception as error:
        print("connection failed")
        print("Error",error)
        time.sleep(2)
"""