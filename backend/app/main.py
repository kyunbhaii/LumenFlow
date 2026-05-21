from fastapi import FastAPI
from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine
from app.db import models

# NEW: Ensure pgvector extension exists before models are registered/created
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LumenFlow"
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
