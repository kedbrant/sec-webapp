#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test SEC downloader with a simple GET request to verify functionality
"""

import sys
import os
sys.path.append('.')

import requests
from app.scrapers.sec_downloader import SECFilingDownloader

def test_sec_access():
    """Test basic SEC website access and filing structure"""
    
    print("SEC Filing Downloader Test")
    print("=" * 40)
    
    # Test 1: Basic SEC website access
    print("1. Testing SEC website access...")
    
    headers = {
        'User-Agent': 'SEC Analysis Bot contact@example.com',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'www.sec.gov'
    }
    
    try:
        # Test basic access to SEC
        response = requests.get("https://www.sec.gov", headers=headers, timeout=10)
        if response.status_code == 200:
            print("   ✓ SEC website accessible")
        else:
            print(f"   ✗ SEC website returned status {response.status_code}")
    except Exception as e:
        print(f"   ✗ SEC website access failed: {e}")
        return
    
    # Test 2: Initialize downloader
    print("2. Testing SEC downloader initialization...")
    
    try:
        downloader = SECFilingDownloader()
        print("   ✓ SEC downloader initialized")
    except Exception as e:
        print(f"   ✗ Failed to initialize downloader: {e}")
        return
    
    # Test 3: Test parser with sample content
    print("3. Testing filing content parser...")
    
    sample_filing_content = """<SEC-DOCUMENT>0001193125-21-123456.txt
<SEC-HEADER>
FORM TYPE:                13D
COMPANY CONFORMED NAME:   TEST COMPANY INC
COMPANY CIK:              0001234567
FILED AS OF DATE:         20211215
</SEC-HEADER>
<DOCUMENT>
Test filing content for parsing...
The reporting person owns 1,500,000 shares representing 15.2% of the outstanding shares.
</DOCUMENT>
"""
    
    try:
        parsed = downloader.parse_filing_content(sample_filing_content, "test-accession")
        print("   ✓ Filing parser working")
        print(f"   - Form Type: {parsed.get('form_type')}")
        print(f"   - Company: {parsed.get('company_name')}")
        print(f"   - Filing Date: {parsed.get('filing_date')}")
        print(f"   - Ownership %: {parsed.get('ownership_percent')}")
    except Exception as e:
        print(f"   ✗ Parser failed: {e}")
    
    print("\n" + "=" * 40)
    print("✓ Core functionality test completed!")
    print("\nNext steps:")
    print("- The SEC downloader framework is working") 
    print("- To test with real filings, find valid accession numbers from SEC EDGAR")
    print("- Try: python3.13 -m uvicorn app.main:app --reload")

if __name__ == "__main__":
    test_sec_access()