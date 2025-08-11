#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.scrapers.sec_downloader import SECFilingDownloader

def test_sec_downloader():
    """Test the SEC filing downloader with a known 13D filing"""
    
    downloader = SECFilingDownloader()
    
    # Test with a known 13D filing accession number
    # This is just an example - replace with an actual recent filing
    test_accession = "0001127602-21-000004"  # Example accession number
    
    print("Testing SEC downloader with filing: " + test_accession)
    print("-" * 50)
    
    # Try to download the filing
    filing_data = downloader.download_filing(test_accession)
    
    if filing_data:
        print("Successfully downloaded filing!")
        print("Form Type: " + str(filing_data.get('form_type')))
        print("Company: " + str(filing_data.get('company_name')))
        print("Filing Date: " + str(filing_data.get('filing_date')))
        print("Owner: " + str(filing_data.get('owner_name')))
        print("Shares Owned: " + str(filing_data.get('shares_owned')))
        print("Ownership %: " + str(filing_data.get('ownership_percent')))
        
        # Show first 500 characters of raw content
        raw_content = filing_data.get('raw_content', '')
        if raw_content:
            print("\nFirst 500 chars of content:")
            print("-" * 30)
            print(raw_content[:500] + "..." if len(raw_content) > 500 else raw_content)
    else:
        print("Failed to download filing")
        print("\nTrying to search for recent 13D filings instead...")
        
        # Search for recent filings
        recent_filings = downloader.search_recent_13d_filings(5)
        if recent_filings:
            print("\nFound " + str(len(recent_filings)) + " recent filings:")
            for i, filing in enumerate(recent_filings, 1):
                print(str(i) + ". " + str(filing.get('company')) + " - " + str(filing.get('form_type')) + " - " + str(filing.get('filing_date')))
                print("   Accession: " + str(filing.get('accession_number')))
        else:
            print("No recent filings found")

if __name__ == "__main__":
    test_sec_downloader()