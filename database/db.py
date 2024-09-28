import logging
from fastapi import Depends
from typing import Annotated
from sqlalchemy import create_engine,text
from sqlalchemy.ext.declarative import declarative_base,DeclarativeMeta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker,Session
import urllib.parse

host="gurukul-prod-ci-sqlserver.database.windows.net"
username="gurukul-admin"
password="24/m_Mp~V-x}"
port = 1433
database = "gurukul-prod-ci-sqldatabase"
encoded_username = urllib.parse.quote_plus(username)
encoded_password = urllib.parse.quote_plus(password)

SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{encoded_username}:{encoded_password}@{host}:1433/{database}?driver=ODBC+Driver+18+for+SQL+Server"

# creating connections
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)
BASE = declarative_base()


def execute_raw_sql(sql_query, params=None):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query), params)
            # Fetch column names
            column_names = result.keys()
            # Fetch all rows
            rows = result.fetchall()
            # Convert rows to list of tuples for pandas
            return column_names, [row for row in rows]
    except SQLAlchemyError as e:
        logging.error("Error executing SQL query: %s", e)
        return None, None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]