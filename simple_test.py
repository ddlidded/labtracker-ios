#!/usr/bin/env python3
import requests
import json

def test_backend():
    """Test the backend API directly"""
    print("=== Testing Backend API ===")
    
    # Create a test file
    with open('test.raw', 'w') as f:
        f.write('test raw file content')
    
    # Upload file to Flask app
    url = 'http://localhost:9847/upload'
    
    try:
        with open('test.raw', 'rb') as f:
            files = {'file': ('test.raw', f, 'application/octet-stream')}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            if 'summary' in data:
                summary = data['summary']
                print(f"Summary keys: {list(summary.keys())}")
                print("\nSummary data:")
                for key, value in summary.items():
                    print(f"  {key}: {value}")
                
                # Check pressure units - should be in bar (very small values)
                if 'min_pressure' in summary:
                    min_p = summary['min_pressure']
                    max_p = summary['max_pressure']
                    mean_p = summary['mean_pressure']
                    
                    print(f"\nPressure Analysis:")
                    print(f"  Min pressure: {min_p:.6f} bar")
                    print(f"  Max pressure: {max_p:.6f} bar")
                    print(f"  Mean pressure: {mean_p:.6f} bar")
                    
                    # Check if values are reasonable for bar units (should be very small)
                    if min_p < 0.01 and max_p < 0.01:
                        print("  ✓ Pressure values appear to be in bar units (small values)")
                    else:
                        print("  ✗ Pressure values seem too large for bar units - might still be in Torr")
            else:
                print("No 'summary' key in response!")
                
            # Check if plot data exists
            if 'plot' in data:
                print("\n✓ Plot data present")
            else:
                print("\n✗ No plot data")
                
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Backend test failed: {e}")

if __name__ == "__main__":
    test_backend()