#!/usr/bin/env python3
import requests
import json
import os

def test_latest_upload():
    """Test the backend response for the latest uploaded file"""
    print("=== Testing Latest Real File Upload ===")
    
    # Check what files are in uploads directory
    uploads_dir = 'uploads'
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        raw_files = [f for f in files if f.endswith('.raw')]
        if raw_files:
            latest_file = max(raw_files, key=lambda f: os.path.getctime(os.path.join(uploads_dir, f)))
            print(f"Latest uploaded file: {latest_file}")
            
            # Try to get pressure at time to see what data is available
            url = 'http://localhost:9847/get_pressure_at_time'
            data = {'filename': latest_file, 'time': 5.0}
            
            try:
                response = requests.post(url, json=data)
                print(f"Pressure at time response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Pressure at time result: {result}")
                    
                    if 'pressure' in result:
                        pressure = result['pressure']
                        print(f"Pressure value: {pressure} bar")
                        print(f"Pressure type: {type(pressure)}")
                        
                        # Check if pressure is very small
                        if pressure < 1e-10:
                            print("⚠️  Pressure value is extremely small - might be zero or conversion issue")
                        elif pressure < 0.01:
                            print("✓ Pressure value appears to be in bar units")
                        else:
                            print("⚠️  Pressure value seems large for bar units")
                else:
                    print(f"Error getting pressure: {response.text}")
                    
            except Exception as e:
                print(f"Error testing pressure endpoint: {e}")
        else:
            print("No .raw files found in uploads directory")
    else:
        print("Uploads directory not found")
    
    # Also test with a simple upload
    print("\n=== Testing Simple Upload ===")
    
    # Create a test file
    with open('test_debug.raw', 'w') as f:
        f.write('test raw file content for debugging')
    
    url = 'http://localhost:9847/upload'
    
    try:
        with open('test_debug.raw', 'rb') as f:
            files = {'file': ('test_debug.raw', f, 'application/octet-stream')}
            response = requests.post(url, files=files)
        
        print(f"Upload status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'summary' in data:
                summary = data['summary']
                print(f"\nSummary data received:")
                for key, value in summary.items():
                    print(f"  {key}: {value} (type: {type(value)})")
                
                # Check pressure values specifically
                pressure_fields = ['min_pressure', 'max_pressure', 'mean_pressure', 'std_pressure']
                for field in pressure_fields:
                    if field in summary:
                        val = summary[field]
                        print(f"\n{field}: {val}")
                        print(f"  Type: {type(val)}")
                        print(f"  String representation: '{str(val)}'")
                        print(f"  Scientific notation: {val:.2e}")
                        print(f"  Fixed 6 decimals: {val:.6f}")
                        print(f"  Fixed 8 decimals: {val:.8f}")
                        
                        if val == 0:
                            print(f"  ⚠️  {field} is exactly zero!")
                        elif abs(val) < 1e-10:
                            print(f"  ⚠️  {field} is extremely small (near zero)")
            else:
                print("No summary in response")
        else:
            print(f"Upload failed: {response.text}")
            
    except Exception as e:
        print(f"Upload test failed: {e}")
    finally:
        # Clean up
        if os.path.exists('test_debug.raw'):
            os.remove('test_debug.raw')

if __name__ == "__main__":
    test_latest_upload()