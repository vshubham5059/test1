from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql://review:SXGiz4DDnL4vt9jsdD+3N9bUv1o2z7fHaPv9ntekPFt8EySP8VndQgn7vvbb4Ex8@10.8.14.150:5490/review"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:King#123@localhost:5432/mydb"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
