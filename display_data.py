#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Display SEC filing data from the running API server
"""

import requests
import json
from datetime import datetime

def display_companies():
    """Display companies data from API"""
    
    print("📊 COMPANIES IN DATABASE")
    print("=" * 60)
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/companies/")
        if response.status_code == 200:
            companies = response.json()
            
            for company in companies:
                print(f"🏢 {company['name']} ({company['ticker']})")
                print(f"   CIK: {company['cik']}")
                print(f"   Sector: {company['sector']}")
                print(f"   Industry: {company['industry']}")
                print()
        else:
            print(f"❌ Failed to fetch companies: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")

def display_filings():
    """Display SEC filings data from API"""
    
    print("\n📋 SEC FILINGS (13D/13G FORMS)")
    print("=" * 60)
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/filings/")
        if response.status_code == 200:
            filings = response.json()
            
            for i, filing in enumerate(filings, 1):
                # Format filing date
                filing_date = datetime.fromisoformat(filing['filing_date'].replace('Z', '+00:00'))
                formatted_date = filing_date.strftime("%Y-%m-%d")
                
                print(f"📄 FILING #{i} - {filing['form_type']}")
                print(f"   Company ID: {filing['company_id']}")
                print(f"   Accession: {filing['accession_number']}")
                print(f"   Filing Date: {formatted_date}")
                print(f"   Owner: {filing['owner_name']}")
                print(f"   Shares Owned: {filing['shares_owned']:,}")
                print(f"   Ownership %: {filing['ownership_percent']}%")
                print(f"   Purpose: {filing['purpose'][:100]}...")
                print(f"   SEC URL: {filing['url']}")
                print("-" * 60)
                
        else:
            print(f"❌ Failed to fetch filings: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")

def display_summary():
    """Display summary statistics"""
    
    print("\n📈 SUMMARY STATISTICS")
    print("=" * 60)
    
    try:
        companies_response = requests.get("http://127.0.0.1:8000/api/v1/companies/")
        filings_response = requests.get("http://127.0.0.1:8000/api/v1/filings/")
        
        if companies_response.status_code == 200 and filings_response.status_code == 200:
            companies = companies_response.json()
            filings = filings_response.json()
            
            print(f"📊 Total Companies: {len(companies)}")
            print(f"📊 Total Filings: {len(filings)}")
            
            # Form type breakdown
            form_types = {}
            total_shares = 0
            
            for filing in filings:
                form_type = filing['form_type']
                form_types[form_type] = form_types.get(form_type, 0) + 1
                total_shares += filing['shares_owned']
            
            print("\n📋 Form Type Breakdown:")
            for form_type, count in form_types.items():
                print(f"   {form_type}: {count} filing(s)")
            
            print(f"\n💰 Total Shares Tracked: {total_shares:,}")
            
            # Largest holdings
            print("\n🔝 TOP 3 LARGEST HOLDINGS:")
            sorted_filings = sorted(filings, key=lambda x: x['shares_owned'], reverse=True)[:3]
            
            for i, filing in enumerate(sorted_filings, 1):
                print(f"   {i}. {filing['owner_name']}")
                print(f"      Shares: {filing['shares_owned']:,}")
                print(f"      Ownership: {filing['ownership_percent']}%")
                print()
                
    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")

def main():
    """Main function to display all data"""
    
    print("🚀 SEC FILINGS ANALYZER - LIVE DATA DISPLAY")
    print("🌐 Server: http://127.0.0.1:8000")
    print("📖 API Docs: http://127.0.0.1:8000/docs")
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("❌ Server not responding properly")
            return
    except requests.RequestException:
        print("❌ Server is not running!")
        print("Start with: python3.13 -m uvicorn app.main:app --reload")
        return
    
    # Display all data
    display_companies()
    display_filings() 
    display_summary()
    
    print("\n🎯 NEXT STEPS:")
    print("   • Visit http://127.0.0.1:8000/docs for interactive API testing")
    print("   • Use /api/v1/companies/ to get company data")
    print("   • Use /api/v1/filings/ to get SEC filing data")
    print("   • Add real SEC scraping functionality")
    print("   • Build a web frontend")

if __name__ == "__main__":
    main()