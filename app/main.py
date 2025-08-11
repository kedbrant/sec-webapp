from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api import filings

app = FastAPI(title="SEC Filings Analyzer", version="1.0.0")

app.include_router(filings.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "SEC Filings Analyzer API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}