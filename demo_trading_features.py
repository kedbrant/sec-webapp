#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstrate the new trading analysis features
"""

import requests
import json
from datetime import datetime

def demo_trading_analysis():
    """Demonstrate trading analysis endpoints"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🎯 SEC FILINGS ANALYZER - TRADING ANALYSIS DEMO")
    print("=" * 60)
    
    # Check server status
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code != 200:
            print("❌ Server not running!")
            return
        print("✅ Server is running - Enhanced v2.0.0")
        
        # Show new API features
        root_response = requests.get(base_url)
        if root_response.status_code == 200:
            features = root_response.json().get('features', [])
            print("\n🚀 NEW FEATURES:")
            for feature in features:
                print(f"   • {feature}")
                
    except requests.RequestException:
        print("❌ Cannot connect to server!")
        return

    print("\n" + "=" * 60)
    print("📊 1. TRADING OPPORTUNITIES ANALYSIS")
    print("=" * 60)
    
    # Get trading opportunities
    try:
        response = requests.get(f"{base_url}/api/v1/filings/trading-opportunities?min_ownership=5.0&days_back=60")
        if response.status_code == 200:
            data = response.json()
            opportunities = data.get('opportunities', [])
            
            print(f"Found {len(opportunities)} potential trading opportunities")
            print(f"Analysis period: {data['parameters']['days_back']} days")
            print(f"Minimum ownership: {data['parameters']['min_ownership']}%")
            print(f"Value threshold: ${data['parameters']['high_value_threshold']:,}")
            
            for i, opp in enumerate(opportunities[:3], 1):  # Show top 3
                filing = opp['filing']
                company = opp['company'] 
                analysis = opp['analysis']
                
                print(f"\n🎯 OPPORTUNITY #{i}")
                print(f"   Company: {company['name']} ({company['ticker']})")
                print(f"   Sector: {company['sector']}")
                print(f"   Owner: {filing['owner_name']}")
                print(f"   Ownership: {filing['ownership_percent']}% ({analysis['ownership_tier']})")
                print(f"   Shares: {filing['shares_owned']:,}")
                print(f"   Est. Position Value: ${analysis['estimated_position_value']:,}")
                print(f"   Signal Strength: {analysis['signal_strength']}")
                print(f"   Form Type: {filing['form_type']} {'(Activist)' if analysis['is_activist_form'] else '(Passive)'}")
                print(f"   Days Since Filing: {analysis['days_since_filing']}")
                
    except Exception as e:
        print(f"Error fetching trading opportunities: {e}")

    print("\n" + "=" * 60)  
    print("📈 2. SECTOR ACTIVITY ANALYSIS")
    print("=" * 60)
    
    # Get sector activity
    try:
        response = requests.get(f"{base_url}/api/v1/analytics/sector-activity?days_back=30")
        if response.status_code == 200:
            data = response.json()
            sectors = data.get('sector_activity', [])
            
            print(f"Sector analysis for {data['analysis_period']}")
            print(f"Total sectors with activity: {data['total_sectors']}")
            
            print("\n🏭 TOP SECTORS BY ACTIVITY:")
            for i, sector in enumerate(sectors, 1):
                print(f"   {i}. {sector['sector']}")
                print(f"      Filings: {sector['filing_count']}")
                print(f"      Total Shares: {sector['total_shares_tracked']:,}")
                print(f"      Avg Ownership: {sector['average_ownership']}%")
                print(f"      Activity Score: {sector['activity_score']:.1f}")
                print()
                
    except Exception as e:
        print(f"Error fetching sector activity: {e}")

    print("=" * 60)
    print("📋 3. FORM TYPE TRENDS")
    print("=" * 60)
    
    # Get form type trends
    try:
        response = requests.get(f"{base_url}/api/v1/analytics/form-type-trends?days_back=90")
        if response.status_code == 200:
            data = response.json()
            trends = data.get('form_trends', [])
            
            print(f"Form type analysis for {data['analysis_period']}")
            
            for trend in trends:
                print(f"\n📄 {trend['form_type']} FILINGS")
                print(f"   Total: {trend['total_filings']}")
                print(f"   Avg Ownership: {trend['average_ownership']}%")
                print(f"   Latest Filing: {trend['latest_filing']}")
                print(f"   📝 {trend['interpretation']}")
                
    except Exception as e:
        print(f"Error fetching form trends: {e}")

    print("\n" + "=" * 60)
    print("🔍 4. ADVANCED FILTERING DEMO")
    print("=" * 60)
    
    # Demo advanced filtering
    try:
        # Filter for high-ownership filings
        response = requests.get(f"{base_url}/api/v1/filings/?min_ownership=8.0&sort_by=ownership_percent&order=desc&limit=3")
        if response.status_code == 200:
            data = response.json()
            filings = data.get('filings', [])
            
            print("🎯 HIGH OWNERSHIP POSITIONS (>8%):")
            for filing in filings:
                print(f"   • {filing['owner_name']}: {filing['ownership_percent']}%")
                print(f"     Shares: {filing['shares_owned']:,} | Form: {filing['form_type']}")
            
            print(f"\nFilters applied: {data['filters_applied']}")
            print(f"Total matching: {data['total']} | Showing: {len(filings)}")
                
    except Exception as e:
        print(f"Error with advanced filtering: {e}")

    print("\n" + "=" * 60)
    print("🎯 TRADING STRATEGY INSIGHTS")
    print("=" * 60)
    
    print("📊 KEY TRADING SIGNALS TO MONITOR:")
    print("   🔥 13D Filings = Activist positions (potential catalysts)")
    print("   📈 High ownership % = Strong institutional confidence") 
    print("   ⚡ Recent filings = Fresh opportunities")
    print("   🏢 Sector concentration = Thematic plays")
    print("   💰 Large positions = Significant capital allocation")
    
    print("\n🚨 NEXT STEPS FOR TRADING:")
    print("   1. Monitor /api/v1/filings/trading-opportunities daily")
    print("   2. Set up alerts for 13D filings > 5% ownership")
    print("   3. Track sector rotation via /api/v1/analytics/sector-activity")
    print("   4. Use advanced filters to find specific opportunities")
    print("   5. Implement automated scraping for real-time data")
    
    print("\n🌐 API ENDPOINTS FOR TRADING:")
    print("   📊 Interactive Docs: http://127.0.0.1:8000/docs")
    print("   🎯 Trading Opportunities: /api/v1/filings/trading-opportunities")
    print("   🔍 Advanced Filtering: /api/v1/filings/")
    print("   📈 Sector Analysis: /api/v1/analytics/sector-activity")
    print("   📋 Form Trends: /api/v1/analytics/form-type-trends")
    print("   🔄 On-demand Scraping: /api/v1/scrape/recent-filings")

if __name__ == "__main__":
    demo_trading_analysis()