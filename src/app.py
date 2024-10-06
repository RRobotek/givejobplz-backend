import logging

from src.services import gh

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from . import models, database

from .database import get_db, GraphEdgeDB

from .models import GraphEdge
import uuid


from fastapi import FastAPI, Depends, HTTPException, Response, status


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


@app.get("/summary/{username}")
async def summary(username: str):
    summary = gh.summarize_github_profile(username)

    return {"summary": summary}



@app.post("/edges/", response_model=models.GraphEdge)
def create_edge(edge: models.GraphEdgeCreate, db: Session = Depends(get_db)):
    # Check if an edge with the same src and dst already exists
    existing_edge = db.query(GraphEdgeDB).filter(
        GraphEdgeDB.src == edge.src,
        GraphEdgeDB.dst == edge.dst
    ).first()

    if existing_edge:
        # Update the existing edge
        existing_edge.score = edge.score
        db.commit()
        db.refresh(existing_edge)
        return models.GraphEdge(
            id=existing_edge.id,
            src=existing_edge.src,
            dst=existing_edge.dst,
            score=existing_edge.score
        )
    else:
        # Create a new edge
        new_id = str(uuid.uuid4())
        db_edge = GraphEdgeDB(id=new_id, src=edge.src, dst=edge.dst, score=edge.score)
        db.add(db_edge)
        db.commit()
        db.refresh(db_edge)
        return models.GraphEdge(
            id=db_edge.id,
            src=db_edge.src,
            dst=db_edge.dst,
            score=db_edge.score
        )

@app.get("/edges/", response_model=list[models.GraphEdge])
def read_edges(db: Session = Depends(get_db)):
    edges = db.query(GraphEdgeDB).all()
    return [models.GraphEdge(id=edge.id, src=edge.src, dst=edge.dst, score=edge.score) for edge in edges]

@app.get("/edges/{edge_id}", response_model=models.GraphEdge)
def read_edge(edge_id: str, db: Session = Depends(get_db)):
    db_edge = db.query(GraphEdgeDB).filter(GraphEdgeDB.id == edge_id).first()
    if db_edge is None:
        raise HTTPException(status_code=404, detail="Edge not found")
    return models.GraphEdge(
        id=db_edge.id,
        src=db_edge.src,
        dst=db_edge.dst,
        score=db_edge.score
    )


@app.delete("/edges/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_edge_by_id(edge_id: str, db: Session = Depends(get_db)):
    db_edge = db.query(GraphEdgeDB).filter(GraphEdgeDB.id == edge_id).first()
    if db_edge is None:
        raise HTTPException(status_code=404, detail="Edge not found")
    db.delete(db_edge)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.delete("/edges/", status_code=status.HTTP_204_NO_CONTENT)
def delete_edge_by_src_dst(src: str, dst: str, db: Session = Depends(get_db)):
    db_edge = db.query(GraphEdgeDB).filter(
        GraphEdgeDB.src == src,
        GraphEdgeDB.dst == dst
    ).first()
    if db_edge is None:
        raise HTTPException(status_code=404, detail="Edge not found")
    db.delete(db_edge)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/developers/{address}")
def read_developer(address: str, db: Session = Depends(get_db)):
    developer = db.query(database.Developer).filter(database.Developer.address == address).first()
    if developer is None:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer


@app.post("/register_developer/")
def register_developer(developer: models.DeveloperCreate, db: Session = Depends(get_db)):
    bio = gh.summarize_github_profile(developer.github_username)
    db_developer = database.Developer(address=developer.address, bio=bio)
    db.add(db_developer)
    db.commit()


@app.get("/developers/")
def read_developers(db: Session = Depends(get_db)):
    developers = db.query(database.Developer).all()
    return developers

