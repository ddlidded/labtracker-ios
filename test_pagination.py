#!/usr/bin/env python3
"""
Test script to verify pagination functionality for the Mass Spec Pressure Analyzer
"""

import requests
import json

def test_pagination():
    base_url = 'http://localhost:9847'
    
    # Test file path
    test_file = 'uploads/20250804_121751_QC-Pool1.raw'
    
    print("Testing pagination functionality...")
    
    # First, upload a file
    print("\n1. Uploading test file...")
    with open(test_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(f'{base_url}/upload', files=files)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.status_code}")
        return
    
    upload_result = response.json()
    if not upload_result.get('success'):
        print(f"Upload failed: {upload_result.get('error')}")
        return
    
    filename = upload_result['filename']
    print(f"File uploaded successfully: {filename}")
    
    # Test pagination with different page sizes
    test_cases = [
        {'page': 1, 'per_page': 25},
        {'page': 1, 'per_page': 50},
        {'page': 2, 'per_page': 50},
        {'page': 1, 'per_page': 100}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i+1}. Testing pagination - Page {test_case['page']}, {test_case['per_page']} records per page")
        
        response = requests.post(f'{base_url}/get_paginated_data', 
                               json={
                                   'filename': filename,
                                   'page': test_case['page'],
                                   'per_page': test_case['per_page']
                               })
        
        if response.status_code != 200:
            print(f"  ❌ Request failed: {response.status_code}")
            continue
        
        result = response.json()
        
        if not result.get('success'):
            print(f"  ❌ API error: {result.get('error')}")
            continue
        
        data = result['data']
        pagination = result['pagination']
        
        print(f"  ✅ Success! Retrieved {len(data)} records")
        print(f"     Page: {pagination['page']}/{pagination['total_pages']}")
        print(f"     Total records: {pagination['total_records']}")
        print(f"     Has next: {pagination['has_next']}, Has prev: {pagination['has_prev']}")
        
        # Verify data structure
        if data:
            first_record = data[0]
            expected_fields = ['retention_time', 'pressure_mbar', 'pressure', 'pressure_pa']
            missing_fields = [field for field in expected_fields if field not in first_record]
            
            if missing_fields:
                print(f"  ⚠️  Missing fields in data: {missing_fields}")
            else:
                print(f"  ✅ Data structure is correct")
                print(f"     Sample record: RT={first_record['retention_time']:.2f}min, P={first_record['pressure_mbar']:.2f}mbar")
    
    # Test edge cases
    print("\n6. Testing edge cases...")
    
    # Test invalid page
    response = requests.post(f'{base_url}/get_paginated_data', 
                           json={
                               'filename': filename,
                               'page': 9999,
                               'per_page': 50
                           })
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success') and len(result['data']) == 0:
            print("  ✅ Invalid page handled correctly (empty data)")
        else:
            print(f"  ⚠️  Invalid page returned data: {len(result.get('data', []))} records")
    
    # Test invalid filename
    response = requests.post(f'{base_url}/get_paginated_data', 
                           json={
                               'filename': 'nonexistent.raw',
                               'page': 1,
                               'per_page': 50
                           })
    
    if response.status_code == 404:
        print("  ✅ Invalid filename handled correctly (404 error)")
    else:
        print(f"  ⚠️  Invalid filename returned: {response.status_code}")
    
    print("\n✅ Pagination testing completed!")

if __name__ == '__main__':
    test_pagination()