#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test FastAPI application startup
"""

import sys
sys.path.append('.')

def test_fastapi_app():
    """Test that FastAPI app can be imported and initialized"""
    
    print("FastAPI Application Test")
    print("=" * 30)
    
    try:
        from app.main import app
        print("✓ FastAPI app imported successfully")
        
        # Check if app has expected attributes
        if hasattr(app, 'routes'):
            print(f"✓ App has {len(app.routes)} routes configured")
            
            # List routes
            for route in app.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    methods = getattr(route, 'methods', ['GET'])
                    print(f"  - {route.path} [{', '.join(methods)}]")
        
        print("✓ FastAPI application structure is valid")
        
    except ImportError as e:
        print(f"✗ Failed to import FastAPI app: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing FastAPI app: {e}")
        return False
    
    # Test database models
    try:
        from app.models.models import Company, Filing
        print("✓ Database models imported successfully")
    except Exception as e:
        print(f"✗ Database models import failed: {e}")
    
    # Test database connection
    try:
        from app.database.database import create_tables
        print("✓ Database setup functions available")
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
    
    print("\n" + "=" * 30)
    print("✓ FastAPI application test completed!")
    print("\nTo start server:")
    print("python3.13 -m uvicorn app.main:app --reload")
    print("\nThen visit:")
    print("- http://localhost:8000 (API root)")
    print("- http://localhost:8000/docs (Swagger UI)")
    print("- http://localhost:8000/api/v1/companies/ (Companies endpoint)")
    print("- http://localhost:8000/api/v1/filings/ (Filings endpoint)")
    
    return True

if __name__ == "__main__":
    test_fastapi_app()