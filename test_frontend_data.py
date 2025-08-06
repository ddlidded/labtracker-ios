#!/usr/bin/env python3
"""
Test script to verify what data is being served by the frontend
and check if there are any caching issues.
"""

import requests
import json
import time

def test_frontend_data():
    base_url = "http://localhost:9847"
    
    print("Testing Frontend Data Display")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(base_url)
        print(f"✓ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running")
        return
    
    # Test 2: Check uploaded files
    print("\nUploaded files:")
    import os
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        files = [f for f in os.listdir(uploads_dir) if f.endswith('.raw')]
        for f in sorted(files)[-3:]:  # Show last 3 files
            print(f"  - {f}")
        
        if files:
            latest_file = sorted(files)[-1]
            print(f"\nTesting with latest file: {latest_file}")
            
            # Test 3: Check paginated data API
            api_url = f"{base_url}/get_paginated_data"
            payload = {
                "filename": latest_file,
                "page": 1,
                "page_size": 10
            }
            
            try:
                response = requests.post(api_url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        records = data.get('data', [])
                        if records:
                            print(f"\n✓ API returning {len(records)} records")
                            print(f"  Total records: {data['pagination']['total_records']}")
                            print(f"  Pressure range: {min(r['pressure'] for r in records):.2f} - {max(r['pressure'] for r in records):.2f} bar")
                            
                            # Check if data looks synthetic
                            pressures = [r['pressure'] for r in records]
                            if all(p > 50 and p < 300 for p in pressures):  # Realistic range
                                print("  ✓ Data appears to be REAL (realistic pressure values)")
                            else:
                                print("  ⚠ Data might be synthetic (unusual pressure values)")
                        else:
                            print("  ✗ No data records returned")
                    else:
                        print(f"  ✗ API error: {data.get('error', 'Unknown error')}")
                else:
                    print(f"  ✗ API request failed (Status: {response.status_code})")
            except Exception as e:
                print(f"  ✗ API request error: {e}")
    else:
        print("  No uploads directory found")
    
    print("\n" + "=" * 50)
    print("RECOMMENDATIONS:")
    print("1. If API shows real data but frontend shows synthetic:")
    print("   - Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)")
    print("   - Check browser developer tools > Network tab")
    print("   - Verify JavaScript is making correct API calls")
    print("2. Upload a new file to force data refresh")
    print("3. Check browser console for JavaScript errors")

if __name__ == "__main__":
    test_frontend_data()