#!/usr/bin/env python3

import os
import sys
sys.path.append('.')
from app import ThermoRawAnalyzer
import pandas as pd
import numpy as np

def test_hplc_pressure_extraction():
    """Test that we're extracting HPLC pump pressure (not vacuum pressure)"""
    print("=== Testing HPLC Pump Pressure Extraction ===")
    
    # Test with a real RAW file
    uploads_dir = 'uploads'
    target_file = '20250804_121751_QC-Pool1.raw'  # Use the latest uploaded file
    file_path = os.path.join(uploads_dir, target_file)
    
    if os.path.exists(file_path):
        print(f"Testing file: {target_file}")
        print(f"File path: {file_path}")
        print(f"File size: {os.path.getsize(file_path) / (1024*1024):.2f} MB")
        
        # Create analyzer and load data
        print("\nCreating analyzer...")
        analyzer = ThermoRawAnalyzer(file_path)
        
        # Check what data was loaded
        print("\nGetting pressure profile...")
        pressure_data = analyzer.get_pressure_profile()
        print(f"Data shape: {pressure_data.shape}")
        print(f"Columns: {list(pressure_data.columns)}")
        
        # Check pressure values in different units
        print(f"\nPressure statistics (bar):")
        print(f"  Min: {pressure_data['pressure'].min():.2f} bar")
        print(f"  Max: {pressure_data['pressure'].max():.2f} bar")
        print(f"  Mean: {pressure_data['pressure'].mean():.2f} bar")
        print(f"  Std: {pressure_data['pressure'].std():.2f} bar")
        
        print(f"\nPressure statistics (mbar):")
        print(f"  Min: {pressure_data['pressure_mbar'].min():.0f} mbar")
        print(f"  Max: {pressure_data['pressure_mbar'].max():.0f} mbar")
        print(f"  Mean: {pressure_data['pressure_mbar'].mean():.0f} mbar")
        
        print(f"\nPressure statistics (Pa):")
        print(f"  Min: {pressure_data['pressure_pa'].min():.0f} Pa")
        print(f"  Max: {pressure_data['pressure_pa'].max():.0f} Pa")
        print(f"  Mean: {pressure_data['pressure_pa'].mean():.0f} Pa")
        
        # Validate that these are HPLC pump pressures, not vacuum pressures
        min_pressure = pressure_data['pressure'].min()
        max_pressure = pressure_data['pressure'].max()
        
        print(f"\n=== Validation ===")
        if min_pressure > 10.0 and max_pressure < 500.0:
            print("✅ SUCCESS: Pressure values are in HPLC pump pressure range (10-500 bar)")
        elif min_pressure < 0.01:
            print("❌ FAIL: Pressure values appear to be vacuum pressure (< 0.01 bar)")
        else:
            print(f"⚠️  WARNING: Unusual pressure range: {min_pressure:.2f} - {max_pressure:.2f} bar")
        
        # Check file info
        print(f"\nFile info details:")
        for key, value in analyzer.file_info.items():
            print(f"  {key}: {value}")
            
        # Show first few data points
        print(f"\nFirst 5 data points:")
        print(pressure_data.head())
            
    else:
        print(f"File not found: {file_path}")
        print("Available files in uploads:")
        if os.path.exists(uploads_dir):
            for f in os.listdir(uploads_dir):
                if f.endswith('.raw'):
                    print(f"  {f}")

if __name__ == "__main__":
    test_hplc_pressure_extraction()