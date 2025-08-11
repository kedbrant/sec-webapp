from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api import filings, scraping
import os

app = FastAPI(
    title="SEC Filings Analyzer", 
    version="2.0.0",
    description="Real-time SEC filings analysis for identifying trading opportunities"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(filings.router, prefix="/api/v1")
app.include_router(scraping.router, prefix="/api/v1", tags=["scraping"])

# Serve frontend
@app.get("/dashboard")
async def dashboard():
    """Serve the trading dashboard"""
    return FileResponse('static/index.html')

@app.get("/")
async def root():
    """Serve the trading dashboard at root"""
    return FileResponse('static/index.html')

@app.get("/api")
def api_info():
    """API information endpoint"""
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