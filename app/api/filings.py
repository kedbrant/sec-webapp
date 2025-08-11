from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models import models

router = APIRouter()

@router.get("/filings/")
def get_filings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    filings = db.query(models.Filing).offset(skip).limit(limit).all()
    return filings

@router.get("/companies/")
def get_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = db.query(models.Company).offset(skip).limit(limit).all()
    return companies