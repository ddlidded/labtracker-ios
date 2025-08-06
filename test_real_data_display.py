#!/usr/bin/env python3

import requests
import os
import json

def test_real_data_upload():
    """Test that the web application displays real data from uploaded files"""
    print("=== Testing Real Data Display in Web Application ===")
    
    # Test file path
    test_file = 'uploads/20250804_121751_QC-Pool1.raw'
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return
    
    # Test the upload endpoint
    url = 'http://localhost:9847/upload'
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/octet-stream')}
            response = requests.post(url, files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload successful!")
            print(f"Status: {data.get('status')}")
            
            # Check if real data is being returned
            if 'data' in data:
                pressure_data = data['data']
                print(f"\nData points received: {len(pressure_data)}")
                
                if len(pressure_data) > 0:
                    first_point = pressure_data[0]
                    last_point = pressure_data[-1]
                    
                    print(f"First data point:")
                    print(f"  Retention time: {first_point.get('retention_time', 'N/A')} min")
                    print(f"  Pressure: {first_point.get('pressure', 'N/A')} bar")
                    print(f"  Pressure (mbar): {first_point.get('pressure_mbar', 'N/A')} mbar")
                    print(f"  Pressure (Pa): {first_point.get('pressure_pa', 'N/A')} Pa")
                    
                    print(f"\nLast data point:")
                    print(f"  Retention time: {last_point.get('retention_time', 'N/A')} min")
                    print(f"  Pressure: {last_point.get('pressure', 'N/A')} bar")
                    
                    # Calculate pressure statistics
                    pressures = [point.get('pressure', 0) for point in pressure_data]
                    min_pressure = min(pressures)
                    max_pressure = max(pressures)
                    avg_pressure = sum(pressures) / len(pressures)
                    
                    print(f"\nPressure Statistics:")
                    print(f"  Min: {min_pressure:.2f} bar")
                    print(f"  Max: {max_pressure:.2f} bar")
                    print(f"  Average: {avg_pressure:.2f} bar")
                    
                    # Validate this is real HPLC data, not synthetic
                    if min_pressure > 50 and max_pressure < 400:
                        print("\n✅ SUCCESS: Real HPLC pump pressure data is being displayed!")
                        print("   Pressure values are in typical HPLC range (50-400 bar)")
                    else:
                        print(f"\n⚠️  WARNING: Unusual pressure range for HPLC: {min_pressure:.2f} - {max_pressure:.2f} bar")
                
            # Check file info
            if 'file_info' in data:
                file_info = data['file_info']
                print(f"\nFile Information:")
                for key, value in file_info.items():
                    print(f"  {key}: {value}")
                    
                # Check if it's using real data or synthetic
                format_info = file_info.get('format', '')
                if 'RawFileReader' in format_info:
                    print("\n✅ SUCCESS: Using real data extraction via RawFileReader!")
                elif 'synthetic' in format_info.lower():
                    print("\n❌ WARNING: Still using synthetic data!")
                    
        else:
            print(f"❌ Upload failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_real_data_upload()