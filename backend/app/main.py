from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine

from app.db import models


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LumenFlow"
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }