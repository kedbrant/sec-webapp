#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstrate the new frontend dashboard
"""

import webbrowser
import time
import requests

def demo_frontend():
    """Demo the new web frontend"""
    
    print("🌐 SEC FILINGS ANALYZER - WEB DASHBOARD DEMO")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("❌ Server responded with error:", response.status_code)
            return
    except requests.RequestException as e:
        print("❌ Server not accessible:", str(e))
        print("\nPlease start the server with:")
        print("python3.13 -m uvicorn app.main:app --reload")
        return
    
    print("\n🎯 FRONTEND FEATURES:")
    print("✓ Real-time trading opportunities dashboard")
    print("✓ Interactive data visualization") 
    print("✓ Sector activity analysis")
    print("✓ Recent SEC filings display")
    print("✓ Advanced filtering and sorting")
    print("✓ Responsive design for mobile/desktop")
    print("✓ Auto-refresh every 5 minutes")
    
    print("\n📊 DASHBOARD SECTIONS:")
    print("1. 📈 Stats Overview - Key metrics at a glance")
    print("2. 🎯 Trading Opportunities - High-value institutional positions") 
    print("3. 🏭 Sector Activity - Which sectors are hot")
    print("4. 📋 Recent Filings - Latest SEC submissions")
    
    print("\n🔍 INTERACTIVE FEATURES:")
    print("• Filter by ownership percentage (5%, 8%, 10%)")
    print("• Filter filings by form type (13D, 13G, 13G/A)")
    print("• Real-time data refresh")
    print("• Signal strength indicators")
    print("• Position value estimates")
    
    print("\n🌐 ACCESS URLS:")
    print("📊 Main Dashboard: http://127.0.0.1:8000/")
    print("📊 Alternative: http://127.0.0.1:8000/dashboard")
    print("🔧 API Documentation: http://127.0.0.1:8000/docs")
    print("📋 API Info: http://127.0.0.1:8000/api")
    
    # Test some endpoints to show data is flowing
    print("\n🔄 TESTING DATA ENDPOINTS:")
    
    try:
        # Test trading opportunities
        resp = requests.get("http://127.0.0.1:8000/api/v1/filings/trading-opportunities?limit=1")
        if resp.status_code == 200:
            data = resp.json()
            opportunities = data.get('opportunities', [])
            print(f"✅ Trading Opportunities: {len(opportunities)} found")
            if opportunities:
                opp = opportunities[0]
                company = opp['company']
                filing = opp['filing']
                print(f"   Example: {company['name']} ({company['ticker']}) - {filing['ownership_percent']}% stake")
        
        # Test sector activity
        resp = requests.get("http://127.0.0.1:8000/api/v1/analytics/sector-activity")
        if resp.status_code == 200:
            data = resp.json()
            sectors = data.get('sector_activity', [])
            print(f"✅ Sector Analysis: {len(sectors)} sectors with activity")
            if sectors:
                top_sector = sectors[0]
                print(f"   Top Sector: {top_sector['sector']} ({top_sector['filing_count']} filings)")
        
        # Test recent filings
        resp = requests.get("http://127.0.0.1:8000/api/v1/filings/?limit=1")
        if resp.status_code == 200:
            data = resp.json()
            total_filings = data.get('total', 0)
            print(f"✅ Recent Filings: {total_filings} total in database")
    
    except Exception as e:
        print(f"⚠️  Warning: Some API endpoints had issues: {e}")
    
    print("\n🚀 READY TO LAUNCH!")
    print("The web dashboard is now live and displaying your SEC trading data.")
    
    # Ask user if they want to open browser
    try:
        user_input = input("\n🌐 Open dashboard in browser? (y/n): ").lower().strip()
        if user_input in ['y', 'yes', '']:
            print("Opening dashboard in your default browser...")
            webbrowser.open('http://127.0.0.1:8000/')
            print("✅ Dashboard opened!")
        else:
            print("💡 You can manually visit: http://127.0.0.1:8000/")
    except KeyboardInterrupt:
        print("\n💡 You can manually visit: http://127.0.0.1:8000/")
    
    print("\n📱 MOBILE FRIENDLY:")
    print("The dashboard is responsive and works great on phones/tablets too!")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Explore the dashboard interface")
    print("2. Try filtering by different ownership levels") 
    print("3. Check out the sector analysis")
    print("4. Monitor for new trading opportunities")
    print("5. Use the API docs to build custom queries")
    
    print("\n" + "=" * 60)
    print("🎉 SEC TRADING DASHBOARD IS LIVE!")
    print("=" * 60)

if __name__ == "__main__":
    demo_frontend()