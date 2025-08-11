from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api import filings, scraping

app = FastAPI(
    title="SEC Filings Analyzer", 
    version="2.0.0",
    description="Real-time SEC filings analysis for identifying trading opportunities"
)

# Include API routers
app.include_router(filings.router, prefix="/api/v1")
app.include_router(scraping.router, prefix="/api/v1", tags=["scraping"])

@app.get("/")
def read_root():
    return {
        "message": "SEC Filings Analyzer API", 
        "version": "2.0.0",
        "features": [
            "Real-time SEC filing scraping",
            "Trading signal analysis", 
            "Institutional position tracking",
            "On-demand data updates"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}