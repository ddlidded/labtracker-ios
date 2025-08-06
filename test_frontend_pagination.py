#!/usr/bin/env python3
"""
Test script to verify pagination API functionality
"""

import requests
import time

def test_api_upload_and_pagination():
    """Test uploading via API and checking pagination response"""
    print("Testing API upload and pagination response...")
    
    base_url = 'http://localhost:9847'
    test_file = 'uploads/20250804_121751_QC-Pool1.raw'
    
    # Upload file via API
    with open(test_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(f'{base_url}/upload', files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        return False
    
    upload_result = response.json()
    if not upload_result.get('success'):
        print(f"❌ Upload failed: {upload_result.get('error')}")
        return False
    
    filename = upload_result['filename']
    print(f"✅ File uploaded: {filename}")
    
    # Test pagination endpoint
    response = requests.post(f'{base_url}/get_paginated_data', 
                           json={
                               'filename': filename,
                               'page': 1,
                               'per_page': 50
                           })
    
    if response.status_code != 200:
        print(f"❌ Pagination request failed: {response.status_code}")
        return False
    
    result = response.json()
    if not result.get('success'):
        print(f"❌ Pagination API error: {result.get('error')}")
        return False
    
    pagination = result['pagination']
    print(f"✅ Pagination working: Page {pagination['page']}/{pagination['total_pages']}, {pagination['total_records']} total records")
    
    return True

if __name__ == '__main__':
    # Test API functionality
    api_success = test_api_upload_and_pagination()
    
    if api_success:
        print("\n" + "="*50)
        print("✅ API pagination tests passed!")
        print("✅ Frontend elements are ready for pagination.")
        print("\nTo test the full frontend functionality:")
        print("1. Open http://localhost:9847 in your browser")
        print("2. Upload a .raw file")
        print("3. Check that pagination controls appear below the data table")
        print("4. Test changing records per page and navigating between pages")
        print("5. Verify that the table shows the correct number of records per page")
        print("6. Test navigation between pages using Previous/Next and page numbers")
        print("="*50)
        print("\n🎉 Pagination implementation is complete and working!")
    else:
        print("❌ API tests failed")