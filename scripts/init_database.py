#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize database and populate with sample SEC filing data
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.database import create_tables, SessionLocal
from app.models.models import Company, Filing

def init_database():
    """Initialize database with tables"""
    print("Creating database tables...")
    create_tables()
    print("✓ Database tables created")

def add_sample_data():
    """Add sample companies and filings to demonstrate functionality"""
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(Filing).delete()
        db.query(Company).delete()
        
        print("Adding sample companies...")
        
        # Sample companies based on real SEC data patterns
        companies = [
            Company(
                cik="0000789019",
                name="MICROSOFT CORP",
                ticker="MSFT",
                sector="Technology",
                industry="Software"
            ),
            Company(
                cik="0000320193",
                name="APPLE INC",
                ticker="AAPL", 
                sector="Technology",
                industry="Consumer Electronics"
            ),
            Company(
                cik="0001652044",
                name="ALPHABET INC",
                ticker="GOOGL",
                sector="Technology", 
                industry="Internet Services"
            ),
            Company(
                cik="0001018724",
                name="AMAZON COM INC",
                ticker="AMZN",
                sector="Consumer Discretionary",
                industry="E-commerce"
            ),
            Company(
                cik="0000051143",
                name="IBM",
                ticker="IBM",
                sector="Technology",
                industry="IT Services"
            )
        ]
        
        for company in companies:
            db.add(company)
        
        db.flush()  # Flush to get IDs
        print(f"✓ Added {len(companies)} companies")
        
        print("Adding sample SEC filings...")
        
        # Sample 13D/13G filings with realistic data
        sample_filings = [
            {
                "company": companies[0],  # Microsoft
                "form_type": "13D",
                "filing_date": datetime.now() - timedelta(days=15),
                "accession_number": "0001193125-24-001234",
                "url": "https://www.sec.gov/Archives/edgar/data/789019/000119312524001234/d123456d13d.htm",
                "owner_name": "BERKSHIRE HATHAWAY INC",
                "owner_cik": "0001067983",
                "shares_owned": 15000000,
                "ownership_percent": 2.1,
                "purpose": "Investment purposes. The reporting person acquired the securities for investment purposes and may acquire additional securities or dispose of securities.",
                "raw_text": "FORM 13D - MICROSOFT CORP... [Filing content would be here]"
            },
            {
                "company": companies[1],  # Apple
                "form_type": "13G", 
                "filing_date": datetime.now() - timedelta(days=8),
                "accession_number": "0000950170-24-005678",
                "url": "https://www.sec.gov/Archives/edgar/data/320193/000095017024005678/xslf345x03/primary_doc.xml",
                "owner_name": "VANGUARD GROUP INC",
                "owner_cik": "0000102909",
                "shares_owned": 1235000000,
                "ownership_percent": 8.2,
                "purpose": "Passive investment by investment adviser.",
                "raw_text": "FORM 13G - APPLE INC... [Filing content would be here]"
            },
            {
                "company": companies[2],  # Alphabet
                "form_type": "13D",
                "filing_date": datetime.now() - timedelta(days=3),
                "accession_number": "0001047469-24-009876",
                "url": "https://www.sec.gov/Archives/edgar/data/1652044/000104746924009876/a2287234z13d.htm",
                "owner_name": "BLACKROCK INC",
                "owner_cik": "0001047469", 
                "shares_owned": 85000000,
                "ownership_percent": 6.8,
                "purpose": "The shares were acquired in the ordinary course of business as an investment advisor.",
                "raw_text": "FORM 13D - ALPHABET INC... [Filing content would be here]"
            },
            {
                "company": companies[3],  # Amazon
                "form_type": "13G",
                "filing_date": datetime.now() - timedelta(days=22),
                "accession_number": "0001193125-24-011111", 
                "url": "https://www.sec.gov/Archives/edgar/data/1018724/000119312524011111/d234567d13g.htm",
                "owner_name": "STATE STREET CORP",
                "owner_cik": "0000093751",
                "shares_owned": 425000000,
                "ownership_percent": 4.1,
                "purpose": "Investment advisory services to institutional clients.",
                "raw_text": "FORM 13G - AMAZON COM INC... [Filing content would be here]"
            },
            {
                "company": companies[0],  # Microsoft (second filing)
                "form_type": "13G/A",
                "filing_date": datetime.now() - timedelta(days=45),
                "accession_number": "0000950170-24-002222",
                "url": "https://www.sec.gov/Archives/edgar/data/789019/000095017024002222/xslf345x02/wf-form13ga_16803341.xml", 
                "owner_name": "CAPITAL WORLD INVESTORS",
                "owner_cik": "0000199935",
                "shares_owned": 89500000,
                "ownership_percent": 1.2,
                "purpose": "Amendment to previously filed Schedule 13G. Investment advisory services.",
                "raw_text": "FORM 13G/A - MICROSOFT CORP... [Filing content would be here]"
            },
            {
                "company": companies[4],  # IBM
                "form_type": "13D",
                "filing_date": datetime.now() - timedelta(days=12),
                "accession_number": "0001140361-24-003333",
                "url": "https://www.sec.gov/Archives/edgar/data/51143/000114036124003333/brhc10045974_13d.htm",
                "owner_name": "WELLINGTON MANAGEMENT GROUP",
                "owner_cik": "0001140361",
                "shares_owned": 125000000,
                "ownership_percent": 13.7,
                "purpose": "The securities were acquired for investment purposes as part of ordinary investment activities.",
                "raw_text": "FORM 13D - INTERNATIONAL BUSINESS MACHINES CORP... [Filing content would be here]"
            }
        ]
        
        filings = []
        for filing_data in sample_filings:
            filing = Filing(
                company_id=filing_data["company"].id,
                form_type=filing_data["form_type"],
                filing_date=filing_data["filing_date"],
                accession_number=filing_data["accession_number"], 
                url=filing_data["url"],
                owner_name=filing_data["owner_name"],
                owner_cik=filing_data["owner_cik"],
                shares_owned=filing_data["shares_owned"],
                ownership_percent=filing_data["ownership_percent"],
                raw_text=filing_data["raw_text"],
                purpose=filing_data["purpose"]
            )
            filings.append(filing)
            db.add(filing)
        
        db.commit()
        print(f"✓ Added {len(filings)} SEC filings")
        
        # Display summary
        print("\n" + "=" * 50)
        print("DATABASE POPULATED SUCCESSFULLY!")
        print("=" * 50)
        
        print(f"\nCompanies in database: {db.query(Company).count()}")
        print(f"SEC filings in database: {db.query(Filing).count()}")
        
        print("\nSample data includes:")
        for company in companies:
            filing_count = db.query(Filing).filter(Filing.company_id == company.id).count()
            print(f"  - {company.name} ({company.ticker}): {filing_count} filing(s)")
        
        print("\nForm types:")
        form_types = db.query(Filing.form_type).distinct().all()
        for form_type in form_types:
            count = db.query(Filing).filter(Filing.form_type == form_type[0]).count()
            print(f"  - {form_type[0]}: {count} filing(s)")
            
        print("\nDatabase ready for API testing!")
        
    except Exception as e:
        print(f"Error adding sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function to initialize database and add sample data"""
    
    print("SEC Webapp Database Initialization")
    print("=" * 40)
    
    try:
        init_database()
        add_sample_data()
        
        print("\n✓ Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Start the server: python3.13 -m uvicorn app.main:app --reload")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Test endpoints:")
        print("   - GET /api/v1/companies/")
        print("   - GET /api/v1/filings/")
        
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())