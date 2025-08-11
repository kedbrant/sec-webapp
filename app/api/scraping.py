from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio

from app.database.database import get_db
from app.models import models
from app.scrapers.sec_downloader import SECFilingDownloader
from app.scrapers.sec_scraper import SECRealTimeScraper

router = APIRouter()

@router.post("/scrape/recent-filings")
async def scrape_recent_filings(
    background_tasks: BackgroundTasks,
    days_back: int = 7,
    form_types: List[str] = ["13D", "13G", "13G/A"],
    db: Session = Depends(get_db)
):
    """
    Scrape recent SEC filings for the specified form types
    This will run in the background and return immediately
    """
    background_tasks.add_task(
        _scrape_recent_filings_task,
        db,
        days_back,
        form_types
    )
    
    return {
        "message": "Scraping started in background",
        "parameters": {
            "days_back": days_back,
            "form_types": form_types
        },
        "status": "running"
    }

@router.get("/scrape/status")
async def get_scraping_status(db: Session = Depends(get_db)):
    """Get current scraping status and recent activity"""
    
    recent_filings = db.query(models.Filing).filter(
        models.Filing.created_at >= datetime.utcnow() - timedelta(hours=1)
    ).count()
    
    latest_filing = db.query(models.Filing).order_by(
        models.Filing.filing_date.desc()
    ).first()
    
    return {
        "recent_scrapes": recent_filings,
        "latest_filing_date": latest_filing.filing_date if latest_filing else None,
        "total_filings": db.query(models.Filing).count(),
        "total_companies": db.query(models.Company).count(),
        "status": "ready"
    }

@router.post("/scrape/company/{cik}")
async def scrape_company_filings(
    cik: str,
    background_tasks: BackgroundTasks,
    form_types: List[str] = ["13D", "13G", "13G/A"],
    db: Session = Depends(get_db)
):
    """
    Scrape all recent filings for a specific company CIK
    """
    # Check if company exists
    company = db.query(models.Company).filter(models.Company.cik == cik).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with CIK {cik} not found")
    
    background_tasks.add_task(
        _scrape_company_filings_task,
        db,
        cik,
        form_types
    )
    
    return {
        "message": f"Scraping started for company {company.name}",
        "cik": cik,
        "form_types": form_types,
        "status": "running"
    }

@router.get("/analysis/trading-signals")
async def get_trading_signals(
    min_ownership_percent: float = 5.0,
    min_shares: int = 1000000,
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Identify potential trading signals based on recent large position changes
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    # Find significant recent filings
    significant_filings = db.query(models.Filing).join(models.Company).filter(
        models.Filing.filing_date >= cutoff_date,
        models.Filing.ownership_percent >= min_ownership_percent,
        models.Filing.shares_owned >= min_shares
    ).order_by(models.Filing.filing_date.desc()).all()
    
    trading_signals = []
    for filing in significant_filings:
        signal_strength = _calculate_signal_strength(filing)
        
        trading_signals.append({
            "company": {
                "name": filing.company.name,
                "ticker": filing.company.ticker,
                "cik": filing.company.cik,
                "sector": filing.company.sector
            },
            "filing": {
                "form_type": filing.form_type,
                "filing_date": filing.filing_date,
                "owner_name": filing.owner_name,
                "shares_owned": filing.shares_owned,
                "ownership_percent": filing.ownership_percent,
                "purpose": filing.purpose
            },
            "signal": {
                "strength": signal_strength,
                "type": _determine_signal_type(filing),
                "urgency": _calculate_urgency(filing),
                "recommendation": _generate_recommendation(filing)
            }
        })
    
    return {
        "signals": trading_signals,
        "parameters": {
            "min_ownership_percent": min_ownership_percent,
            "min_shares": min_shares,
            "days_back": days_back
        },
        "total_signals": len(trading_signals)
    }

@router.get("/analysis/top-movers")
async def get_top_movers(
    days_back: int = 7,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get companies with the most significant recent filing activity
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    # Get companies with recent activity
    recent_activity = db.query(
        models.Company,
        db.func.count(models.Filing.id).label('filing_count'),
        db.func.sum(models.Filing.shares_owned).label('total_shares'),
        db.func.avg(models.Filing.ownership_percent).label('avg_ownership')
    ).join(models.Filing).filter(
        models.Filing.filing_date >= cutoff_date
    ).group_by(models.Company.id).order_by(
        db.text('filing_count DESC, total_shares DESC')
    ).limit(limit).all()
    
    top_movers = []
    for company, filing_count, total_shares, avg_ownership in recent_activity:
        # Get latest filing for this company
        latest_filing = db.query(models.Filing).filter(
            models.Filing.company_id == company.id,
            models.Filing.filing_date >= cutoff_date
        ).order_by(models.Filing.filing_date.desc()).first()
        
        top_movers.append({
            "company": {
                "name": company.name,
                "ticker": company.ticker,
                "cik": company.cik,
                "sector": company.sector
            },
            "activity": {
                "recent_filings": filing_count,
                "total_shares_tracked": int(total_shares) if total_shares else 0,
                "average_ownership": float(avg_ownership) if avg_ownership else 0,
                "latest_filing_date": latest_filing.filing_date if latest_filing else None,
                "latest_owner": latest_filing.owner_name if latest_filing else None
            },
            "momentum_score": _calculate_momentum_score(filing_count, total_shares, avg_ownership)
        })
    
    return {
        "top_movers": top_movers,
        "parameters": {
            "days_back": days_back,
            "limit": limit
        }
    }

# Helper functions

def _calculate_signal_strength(filing: models.Filing) -> str:
    """Calculate signal strength based on filing characteristics"""
    if filing.ownership_percent >= 10.0:
        return "Strong"
    elif filing.ownership_percent >= 5.0:
        return "Moderate" 
    else:
        return "Weak"

def _determine_signal_type(filing: models.Filing) -> str:
    """Determine the type of signal based on form type and purpose"""
    if filing.form_type == "13D":
        return "Activist Position"
    elif "amendment" in filing.purpose.lower():
        return "Position Change"
    else:
        return "New Position"

def _calculate_urgency(filing: models.Filing) -> str:
    """Calculate urgency based on filing recency"""
    days_ago = (datetime.utcnow() - filing.filing_date).days
    if days_ago <= 3:
        return "High"
    elif days_ago <= 7:
        return "Medium"
    else:
        return "Low"

def _generate_recommendation(filing: models.Filing) -> str:
    """Generate trading recommendation"""
    if filing.form_type == "13D" and filing.ownership_percent >= 5.0:
        return "Monitor for potential activist campaign"
    elif filing.ownership_percent >= 10.0:
        return "Strong institutional interest - consider position"
    else:
        return "Track for momentum building"

def _calculate_momentum_score(filing_count: int, total_shares: int, avg_ownership: float) -> float:
    """Calculate momentum score for ranking companies"""
    base_score = filing_count * 10
    if total_shares:
        base_score += min(total_shares / 1000000, 100)  # Cap shares impact
    if avg_ownership:
        base_score += avg_ownership
    return round(base_score, 2)

# Background task functions

async def _scrape_recent_filings_task(db: Session, days_back: int, form_types: List[str]):
    """Background task to scrape recent filings"""
    try:
        scraper = SECRealTimeScraper()
        filings = await scraper.get_recent_filings(days_back, form_types)
        
        # Process and save filings
        for filing_data in filings:
            # Implementation would go here
            pass
            
    except Exception as e:
        print(f"Error in background scraping task: {e}")

async def _scrape_company_filings_task(db: Session, cik: str, form_types: List[str]):
    """Background task to scrape company-specific filings"""
    try:
        scraper = SECRealTimeScraper()
        filings = await scraper.get_company_filings(cik, form_types)
        
        # Process and save filings  
        for filing_data in filings:
            # Implementation would go here
            pass
            
    except Exception as e:
        print(f"Error in company scraping task: {e}")