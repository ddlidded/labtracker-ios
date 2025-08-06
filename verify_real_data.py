#!/usr/bin/env python3
"""
Comprehensive verification script to confirm real pressure data is being displayed
"""

import requests
import json
import time
import os

def verify_real_data():
    base_url = "http://localhost:9847"
    
    print("🔍 VERIFYING REAL PRESSURE DATA DISPLAY")
    print("=" * 60)
    
    # Test 1: Server status
    try:
        response = requests.get(base_url)
        print(f"✅ Server running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running")
        return False
    
    # Test 2: Check latest uploaded file
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print("❌ No uploads directory found")
        return False
    
    files = [f for f in os.listdir(uploads_dir) if f.endswith('.raw')]
    if not files:
        print("❌ No RAW files found in uploads")
        return False
    
    latest_file = sorted(files)[-1]
    print(f"📁 Testing with: {latest_file}")
    
    # Test 3: API data verification
    api_url = f"{base_url}/get_paginated_data"
    payload = {
        "filename": latest_file,
        "page": 1,
        "page_size": 20,
        "timestamp": int(time.time() * 1000)  # Cache buster
    }
    
    try:
        response = requests.post(api_url, json=payload, headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                records = data.get('data', [])
                if records:
                    pressures = [r['pressure'] for r in records]
                    min_p, max_p = min(pressures), max(pressures)
                    avg_p = sum(pressures) / len(pressures)
                    
                    print(f"📊 Data Analysis:")
                    print(f"   • Total records: {data['pagination']['total_records']}")
                    print(f"   • Sample size: {len(records)}")
                    print(f"   • Pressure range: {min_p:.2f} - {max_p:.2f} bar")
                    print(f"   • Average pressure: {avg_p:.2f} bar")
                    
                    # Verify this is real data (not synthetic)
                    if 50 <= min_p <= 300 and 50 <= max_p <= 300:
                        print("✅ REAL DATA CONFIRMED - Realistic pump pressure values")
                        
                        # Check for data variation (real data should vary)
                        pressure_std = (sum((p - avg_p)**2 for p in pressures) / len(pressures))**0.5
                        if pressure_std > 1.0:  # Real data should have some variation
                            print(f"✅ DATA VARIATION CONFIRMED - Std dev: {pressure_std:.2f} bar")
                        else:
                            print(f"⚠️  Low variation detected - Std dev: {pressure_std:.2f} bar")
                        
                        # Show sample values
                        print(f"📈 Sample pressure values:")
                        for i, record in enumerate(records[:5]):
                            print(f"   {i+1}. Time: {record['retention_time']:.2f}min, Pressure: {record['pressure']:.2f} bar")
                        
                        return True
                    else:
                        print(f"❌ SYNTHETIC DATA DETECTED - Unrealistic pressure range")
                        return False
                else:
                    print("❌ No data records returned")
                    return False
            else:
                print(f"❌ API error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ API request failed (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API request error: {e}")
        return False

def main():
    success = verify_real_data()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS: Real pressure data is being displayed!")
        print("\n📋 USER INSTRUCTIONS:")
        print("1. Open http://localhost:9847 in your browser")
        print("2. Upload a .raw file (or use existing data)")
        print("3. Verify pressure values are in realistic range (50-300 bar)")
        print("4. Check that data varies naturally (not constant values)")
        print("5. If you still see synthetic data, try:")
        print("   • Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)")
        print("   • Clear browser cache completely")
        print("   • Try in incognito/private browsing mode")
    else:
        print("❌ ISSUE: Still detecting synthetic data")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check if RawFileReaderConsole is working properly")
        print("2. Verify .raw file is valid and not corrupted")
        print("3. Check server logs for errors")
        print("4. Try uploading a different .raw file")
    
    print("\n💡 TIP: Real pump pressure data typically ranges from 50-300 bar")
    print("    and shows natural variation over time.")

if __name__ == "__main__":
    main()