from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.Model.DatabaseModel import Base
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
database = os.getenv("MYSQL_DATABASE")

DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}/{database}"

engine = create_engine(DATABASE_URI, echo=True, pool_size=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)