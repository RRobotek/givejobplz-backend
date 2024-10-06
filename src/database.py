from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./graph.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class GraphEdgeDB(Base):
    __tablename__ = "graph_edges"

    id = Column(String, primary_key=True, index=True)
    src = Column(String, index=True)
    dst = Column(String, index=True)
    score = Column(Float)

class Developer(Base):
    __tablename__ = "developers"

    address = Column(String, primary_key=True, index=True)
    bio = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
