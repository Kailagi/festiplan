from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
import pytest

from app import database
from app.database import Base
from app import models
_ = models

test_engine = create_engine(
     "sqlite://",
     connect_args={"check_same_thread": False},
     poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
database.engine = test_engine
database.SessionLocal = TestSessionLocal

from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session",autouse=True)
def prepare():
 Base.metadata.create_all(bind=test_engine)
 yield
 Base.metadata.drop_all(bind=test_engine)
 test_engine.dispose()

@pytest.fixture()
def client():
 Base.metadata.drop_all(bind=test_engine)
 Base.metadata.create_all(bind=test_engine)
 with TestClient(app) as c: 
   yield c
