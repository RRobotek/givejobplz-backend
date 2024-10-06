from pydantic import BaseModel, Field

class GraphEdgeBase(BaseModel):
    src: str
    dst: str
    score: float = Field(..., ge=0, le=1)

class GraphEdgeCreate(GraphEdgeBase):
    pass

class GraphEdge(GraphEdgeBase):
    id: str

    class Config:
        from_attributes = True

class DeveloperBase(BaseModel):
    address: str
    bio: str

class DeveloperCreate(BaseModel):
    github_username: str
    address: str
