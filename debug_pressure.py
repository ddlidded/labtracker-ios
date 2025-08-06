#!/usr/bin/env python3

import requests
import json
import os
from app import ThermoRawAnalyzer

# Test the actual data processing
print("=== Testing Pressure and Summary Statistics ===")

# Create a test file to analyze
test_file = "test_debug.raw"
with open(test_file, 'w') as f:
    f.write("dummy raw file content")

try:
    # Initialize analyzer
    analyzer = ThermoRawAnalyzer(test_file)
    
    # Get the data
    data = analyzer.data
    print(f"\nData columns: {list(data.columns)}")
    print(f"Data shape: {data.shape}")
    
    # Check pressure values
    if 'pressure_mbar' in data.columns:
        print(f"\nPressure (mbar) - Min: {data['pressure_mbar'].min():.6f}, Max: {data['pressure_mbar'].max():.6f}, Mean: {data['pressure_mbar'].mean():.6f}")
    
    if 'pressure' in data.columns:
        print(f"Pressure (original) - Min: {data['pressure'].min():.6f}, Max: {data['pressure'].max():.6f}, Mean: {data['pressure'].mean():.6f}")
    
    # Test pressure conversion to bar
    if 'pressure_mbar' in data.columns:
        pressure_bar = data['pressure_mbar'] * 0.001
        print(f"Pressure (bar) - Min: {pressure_bar.min():.6f}, Max: {pressure_bar.max():.6f}, Mean: {pressure_bar.mean():.6f}")
    
    # Test summary statistics methods
    print("\n=== Testing Summary Statistics Methods ===")
    
    try:
        pressure_profile = analyzer.get_pressure_profile()
        print(f"Pressure profile type: {type(pressure_profile)}")
        if hasattr(pressure_profile, 'keys'):
            print(f"Pressure profile keys: {list(pressure_profile.keys())}")
            
        # Test manual summary calculation like in Flask app
        pressure_bar = pressure_profile['pressure_mbar'] * 0.001
        summary = {
            'min_pressure': float(pressure_bar.min()),
            'max_pressure': float(pressure_bar.max()),
            'mean_pressure': float(pressure_bar.mean()),
            'std_pressure': float(pressure_bar.std()),
            'total_time': float(pressure_profile['retention_time'].max()),
            'data_points': len(pressure_profile)
        }
        print(f"Manual summary calculation: {summary}")
        
    except Exception as e:
        print(f"Error in pressure profile: {e}")
    
    # Test the Flask app endpoint
    print("\n=== Testing Flask App Response ===")
    
    # Simulate file upload to Flask app
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/octet-stream')}
            response = requests.post('http://localhost:9847/upload', files=files)
            
        if response.status_code == 200:
            result = response.json()
            print(f"Flask response keys: {list(result.keys())}")
            
            if 'summary' in result:
                print(f"Summary stats from Flask: {result['summary']}")
                
                # Test if all required fields are present
                required_fields = ['min_pressure', 'max_pressure', 'mean_pressure', 'std_pressure', 'total_time', 'data_points']
                missing_fields = [field for field in required_fields if field not in result['summary']]
                if missing_fields:
                    print(f"Missing fields in summary: {missing_fields}")
                else:
                    print("✅ All required summary fields are present")
            else:
                print("❌ No summary in response")
                
            if 'plot' in result:
                print("✅ Plot data is present")
            else:
                print("❌ No plot data in response")
                
            if 'data' in result:
                print(f"✅ Data preview present with {len(result['data'])} points")
                if len(result['data']) > 0:
                    first_point = result['data'][0]
                    print(f"First data point keys: {list(first_point.keys())}")
            else:
                print("❌ No data preview in response")
        else:
            print(f"Flask request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error testing Flask app: {e}")
        
finally:
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)

print("\n=== Debug Complete ===")