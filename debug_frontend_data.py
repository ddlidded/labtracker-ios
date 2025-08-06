#!/usr/bin/env python3
"""
Debug Frontend Data Display
This script helps identify why the frontend might still show simulated data
"""

import requests
import json
import os
from datetime import datetime

def test_frontend_data_flow():
    base_url = "http://localhost:9847"
    
    print("=" * 60)
    print("FRONTEND DATA FLOW DEBUG")
    print("=" * 60)
    
    # 1. Check server status
    try:
        response = requests.get(base_url)
        print(f"✓ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running")
        return
    
    # 2. List uploaded files from uploads directory
    uploads_dir = "uploads"
    try:
        if os.path.exists(uploads_dir):
            files = [f for f in os.listdir(uploads_dir) if f.endswith('.raw')]
            files.sort()  # Sort to get latest file
            print(f"✓ Found {len(files)} uploaded .raw files")
            if files:
                latest_file = files[-1]
                print(f"  Latest file: {latest_file}")
            else:
                print("  No .raw files found")
                return
        else:
            print("✗ Uploads directory not found")
            return
    except Exception as e:
        print(f"✗ Error listing files: {e}")
        return
    
    # 3. Test API endpoint with cache-busting
    print("\n" + "-" * 40)
    print("TESTING API ENDPOINT")
    print("-" * 40)
    
    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'filename': latest_file,
        'page': 1,
        'per_page': 10,
        'timestamp': int(datetime.now().timestamp() * 1000)
    }
    
    try:
        response = requests.post(
            f"{base_url}/get_paginated_data",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('data', [])
            
            print(f"✓ API returned {len(records)} records")
            print(f"  Total records: {data.get('total_records', 'Unknown')}")
            print(f"  Total pages: {data.get('total_pages', 'Unknown')}")
            
            if records:
                # Analyze first few records
                print("\n  First 5 pressure values:")
                for i, record in enumerate(records[:5]):
                    pressure = record.get('pressure', 'N/A')
                    time_val = record.get('retention_time', 'N/A')
                    print(f"    {i+1}. Time: {time_val}, Pressure: {pressure} bar")
                
                # Check for data characteristics
                pressures = [r.get('pressure', 0) for r in records if 'pressure' in r]
                if pressures:
                    min_p = min(pressures)
                    max_p = max(pressures)
                    avg_p = sum(pressures) / len(pressures)
                    
                    print(f"\n  Pressure Statistics:")
                    print(f"    Range: {min_p:.2f} - {max_p:.2f} bar")
                    print(f"    Average: {avg_p:.2f} bar")
                    print(f"    Variation: {max_p - min_p:.2f} bar")
                    
                    # Check if data looks synthetic
                    if min_p == max_p:
                        print("    ⚠️  WARNING: All pressure values are identical (likely synthetic)")
                    elif max_p - min_p < 1.0:
                        print("    ⚠️  WARNING: Very low pressure variation (possibly synthetic)")
                    else:
                        print("    ✓ Data shows natural variation (likely real)")
                        
        else:
            print(f"✗ API request failed (Status: {response.status_code})")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Error testing API: {e}")
    
    # 4. Check for common synthetic data patterns
    print("\n" + "-" * 40)
    print("SYNTHETIC DATA DETECTION")
    print("-" * 40)
    
    if records:
        # Check for common synthetic patterns
        synthetic_indicators = []
        
        # Pattern 1: Sequential or mathematical progression
        if len(records) >= 3:
            diffs = []
            for i in range(1, min(5, len(records))):
                if 'pressure' in records[i] and 'pressure' in records[i-1]:
                    diff = abs(records[i]['pressure'] - records[i-1]['pressure'])
                    diffs.append(diff)
            
            if diffs and all(abs(d - diffs[0]) < 0.01 for d in diffs):
                synthetic_indicators.append("Constant pressure differences")
        
        # Pattern 2: Round numbers
        round_numbers = sum(1 for r in records[:10] if 'pressure' in r and r['pressure'] == round(r['pressure']))
        if round_numbers > 7:  # More than 70% are round numbers
            synthetic_indicators.append("Too many round numbers")
        
        # Pattern 3: Common synthetic ranges
        if pressures:
            if all(100 <= p <= 200 for p in pressures[:10]):
                if max(pressures[:10]) - min(pressures[:10]) < 5:
                    synthetic_indicators.append("Suspiciously narrow range in common synthetic range")
        
        if synthetic_indicators:
            print("  ⚠️  Potential synthetic data indicators:")
            for indicator in synthetic_indicators:
                print(f"    - {indicator}")
        else:
            print("  ✓ No obvious synthetic data patterns detected")
    
    # 5. Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if records and pressures:
        if max(pressures) - min(pressures) > 5:
            print("✓ API is serving real data with natural variation")
            print("\nIf frontend still shows synthetic data:")
            print("1. Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)")
            print("2. Open browser developer tools (F12)")
            print("3. Go to Network tab and check if requests have cache-busting parameters")
            print("4. Check Console tab for JavaScript errors")
            print("5. Try uploading the same file again (triggers page reload)")
            print("6. Try a different browser or incognito mode")
        else:
            print("⚠️  API might be serving synthetic data")
            print("\nTroubleshooting steps:")
            print("1. Check if RawFileReader is properly integrated")
            print("2. Verify the uploaded file is a valid Thermo RAW file")
            print("3. Check server logs for RawFileReader errors")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_frontend_data_flow()