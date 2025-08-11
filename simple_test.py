# -*- coding: utf-8 -*-
"""
Simple test to verify project structure
"""

print("SEC Webapp - Simple Structure Test")
print("=" * 40)

try:
    import os
    print("✓ Python working")
    
    # Check if files exist
    files_to_check = [
        'app/main.py',
        'app/models/models.py',
        'app/database/database.py', 
        'app/scrapers/sec_downloader.py',
        'app/api/filings.py',
        'requirements.txt'
    ]
    
    print("\nChecking project files:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print("✓ " + file_path)
        else:
            print("✗ " + file_path)
    
    print("\nProject structure verification complete!")
    print("\nTo run with dependencies:")
    print("1. Install Python 3.7+")
    print("2. pip install -r requirements.txt") 
    print("3. python scripts/test_downloader.py")
    print("4. uvicorn app.main:app --reload")
    
except Exception as e:
    print("Error: " + str(e))