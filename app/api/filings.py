from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.database.database import get_db
from app.models import models

router = APIRouter(tags=["filings"])

@router.get("/filings/")
def get_filings(
    skip: int = 0, 
    limit: int = 100,
    form_type: Optional[str] = None,
    min_ownership: Optional[float] = None,
    min_shares: Optional[int] = None,
    days_back: Optional[int] = None,
    sector: Optional[str] = None,
    sort_by: str = "filing_date",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    """
    Get SEC filings with advanced filtering for trading analysis
    """
    query = db.query(models.Filing).join(models.Company)
    
    # Apply filters
    if form_type:
        query = query.filter(models.Filing.form_type == form_type)
    
    if min_ownership:
        query = query.filter(models.Filing.ownership_percent >= min_ownership)
    
    if min_shares:
        query = query.filter(models.Filing.shares_owned >= min_shares)
    
    if days_back:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        query = query.filter(models.Filing.filing_date >= cutoff_date)
    
    if sector:
        query = query.filter(models.Company.sector == sector)
    
    # Apply sorting
    if sort_by == "filing_date":
        sort_column = models.Filing.filing_date
    elif sort_by == "ownership_percent":
        sort_column = models.Filing.ownership_percent  
    elif sort_by == "shares_owned":
        sort_column = models.Filing.shares_owned
    else:
        sort_column = models.Filing.filing_date
    
    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    filings = query.offset(skip).limit(limit).all()
    
    return {
        "filings": filings,
        "total": total,
        "page_info": {
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        },
        "filters_applied": {
            "form_type": form_type,
            "min_ownership": min_ownership,
            "min_shares": min_shares,
            "days_back": days_back,
            "sector": sector,
            "sort_by": sort_by,
            "order": order
        }
    }

@router.get("/filings/trading-opportunities")
def get_trading_opportunities(
    min_ownership: float = 5.0,
    days_back: int = 30,
    high_value_threshold: int = 100000000,  # $100M+ positions
    db: Session = Depends(get_db)
):
    """
    Get filings that represent potential trading opportunities
    Focus on significant positions and recent activity
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    # Find high-value, recent filings
    opportunities = db.query(models.Filing).join(models.Company).filter(
        and_(
            models.Filing.filing_date >= cutoff_date,
            models.Filing.ownership_percent >= min_ownership,
            # Estimate position value (assuming $50 average share price)
            models.Filing.shares_owned * 50 >= high_value_threshold
        )
    ).order_by(desc(models.Filing.filing_date)).all()
    
    # Enhance with analysis
    enhanced_opportunities = []
    for filing in opportunities:
        opportunity = {
            "filing": filing,
            "company": filing.company,
            "analysis": {
                "estimated_position_value": filing.shares_owned * 50,  # Rough estimate
                "signal_strength": "Strong" if filing.ownership_percent >= 10 else "Moderate",
                "days_since_filing": (datetime.utcnow() - filing.filing_date).days,
                "is_activist_form": filing.form_type == "13D",
                "ownership_tier": _get_ownership_tier(filing.ownership_percent)
            }
        }
        enhanced_opportunities.append(opportunity)
    
    return {
        "opportunities": enhanced_opportunities,
        "total": len(enhanced_opportunities),
        "parameters": {
            "min_ownership": min_ownership,
            "days_back": days_back,
            "high_value_threshold": high_value_threshold
        }
    }

@router.get("/companies/")
def get_companies(
    skip: int = 0, 
    limit: int = 100, 
    sector: Optional[str] = None,
    has_recent_filings: bool = False,
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get companies with optional filtering
    """
    query = db.query(models.Company)
    
    if sector:
        query = query.filter(models.Company.sector == sector)
    
    if has_recent_filings:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        query = query.filter(
            models.Company.filings.any(models.Filing.filing_date >= cutoff_date)
        )
    
    total = query.count()
    companies = query.offset(skip).limit(limit).all()
    
    return {
        "companies": companies,
        "total": total,
        "page_info": {
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    }

@router.get("/companies/{cik}/filings")
def get_company_filings(
    cik: str,
    skip: int = 0,
    limit: int = 50,
    form_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all filings for a specific company
    """
    company = db.query(models.Company).filter(models.Company.cik == cik).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    query = db.query(models.Filing).filter(models.Filing.company_id == company.id)
    
    if form_type:
        query = query.filter(models.Filing.form_type == form_type)
    
    query = query.order_by(desc(models.Filing.filing_date))
    
    total = query.count()
    filings = query.offset(skip).limit(limit).all()
    
    return {
        "company": company,
        "filings": filings,
        "total_filings": total
    }

@router.get("/analytics/sector-activity")
def get_sector_activity(
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get filing activity breakdown by sector
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    # Get activity by sector
    sector_activity = db.query(
        models.Company.sector,
        db.func.count(models.Filing.id).label('filing_count'),
        db.func.sum(models.Filing.shares_owned).label('total_shares'),
        db.func.avg(models.Filing.ownership_percent).label('avg_ownership')
    ).join(models.Filing).filter(
        models.Filing.filing_date >= cutoff_date
    ).group_by(models.Company.sector).order_by(
        desc(db.text('filing_count'))
    ).all()
    
    results = []
    for sector, filing_count, total_shares, avg_ownership in sector_activity:
        results.append({
            "sector": sector,
            "filing_count": filing_count,
            "total_shares_tracked": int(total_shares) if total_shares else 0,
            "average_ownership": round(float(avg_ownership), 2) if avg_ownership else 0,
            "activity_score": filing_count * (avg_ownership or 0)
        })
    
    return {
        "sector_activity": results,
        "analysis_period": f"Last {days_back} days",
        "total_sectors": len(results)
    }

@router.get("/analytics/form-type-trends")
def get_form_type_trends(
    days_back: int = 90,
    db: Session = Depends(get_db)
):
    """
    Analyze trends in different form types over time
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    form_trends = db.query(
        models.Filing.form_type,
        db.func.count(models.Filing.id).label('count'),
        db.func.avg(models.Filing.ownership_percent).label('avg_ownership'),
        db.func.max(models.Filing.filing_date).label('latest_filing')
    ).filter(
        models.Filing.filing_date >= cutoff_date
    ).group_by(models.Filing.form_type).all()
    
    trends = []
    for form_type, count, avg_ownership, latest_filing in form_trends:
        trends.append({
            "form_type": form_type,
            "total_filings": count,
            "average_ownership": round(float(avg_ownership), 2) if avg_ownership else 0,
            "latest_filing": latest_filing,
            "interpretation": _interpret_form_type(form_type)
        })
    
    return {
        "form_trends": trends,
        "analysis_period": f"Last {days_back} days"
    }

# Helper functions

def _get_ownership_tier(ownership_percent: float) -> str:
    """Categorize ownership percentage"""
    if ownership_percent >= 15:
        return "Major Holder"
    elif ownership_percent >= 10:
        return "Significant Holder"  
    elif ownership_percent >= 5:
        return "Notable Position"
    else:
        return "Minor Position"

def _interpret_form_type(form_type: str) -> str:
    """Provide interpretation of form type significance"""
    interpretations = {
        "13D": "Activist positions - indicates potential for operational influence",
        "13G": "Passive institutional positions - indicates confidence in company",
        "13G/A": "Position changes - monitor for increasing/decreasing stakes"
    }
    return interpretations.get(form_type, "Unknown form type")