#!/usr/bin/env python3
import os
import sys
sys.path.append('.')
from app import ThermoRawAnalyzer
import pandas as pd
import numpy as np

def test_real_file_processing():
    """Test the actual processing of the uploaded RAW file"""
    print("=== Testing Real RAW File Processing ===")
    
    # Test the actual QC-Pool1.raw file
    uploads_dir = 'uploads'
    target_file = '20250804_120348_QC-Pool1.raw'  # One of the real RAW files
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
        print(f"\nPressure statistics (original units - should be Torr):")
        print(f"  Min: {pressure_data['pressure'].min():.6f}")
        print(f"  Max: {pressure_data['pressure'].max():.6f}")
        print(f"  Mean: {pressure_data['pressure'].mean():.6f}")
        print(f"  Std: {pressure_data['pressure'].std():.6f}")
        
        print(f"\nPressure statistics (mbar):")
        print(f"  Min: {pressure_data['pressure_mbar'].min():.6f}")
        print(f"  Max: {pressure_data['pressure_mbar'].max():.6f}")
        print(f"  Mean: {pressure_data['pressure_mbar'].mean():.6f}")
        print(f"  Std: {pressure_data['pressure_mbar'].std():.6f}")
        
        # Convert to bar (like in the upload endpoint)
        pressure_bar = pressure_data['pressure_mbar'] * 0.001
        print(f"\nPressure statistics (bar):")
        print(f"  Min: {pressure_bar.min():.8f}")
        print(f"  Max: {pressure_bar.max():.8f}")
        print(f"  Mean: {pressure_bar.mean():.8f}")
        print(f"  Std: {pressure_bar.std():.8f}")
        
        # Check if values are exactly zero
        zero_count = (pressure_bar == 0).sum()
        near_zero_count = (pressure_bar < 1e-10).sum()
        print(f"\nZero pressure values: {zero_count} out of {len(pressure_bar)}")
        print(f"Near-zero pressure values (< 1e-10): {near_zero_count} out of {len(pressure_bar)}")
        
        if zero_count == len(pressure_bar):
            print("⚠️  ALL PRESSURE VALUES ARE ZERO!")
            print("This explains why the frontend shows 0.000000")
            
            # Check the original pressure column
            print(f"\nOriginal pressure column stats:")
            print(f"  All zeros: {(pressure_data['pressure'] == 0).all()}")
            print(f"  All NaN: {pressure_data['pressure'].isna().all()}")
            print(f"  Sample values: {pressure_data['pressure'].head(10).tolist()}")
            
            # Check file info
            print(f"\nFile info: {analyzer.file_info}")
            
            # Check if this is synthetic data
            if 'estimated_duration_min' in analyzer.file_info:
                print("\n⚠️  This appears to be synthetic data, not real RAW file data!")
                print("The real RAW file processing failed and fell back to synthetic data.")
                print("But the synthetic data generation is producing zeros instead of realistic values.")
                
        elif near_zero_count == len(pressure_bar):
            print("⚠️  ALL PRESSURE VALUES ARE NEAR ZERO!")
            print("Values are extremely small, might be a unit conversion issue")
        else:
            print("✓ Pressure values look normal")
            
        # Test the summary calculation (like in upload endpoint)
        summary = {
            'min_pressure': float(pressure_bar.min()),
            'max_pressure': float(pressure_bar.max()),
            'mean_pressure': float(pressure_bar.mean()),
            'std_pressure': float(pressure_bar.std()),
            'total_time': float(pressure_data['retention_time'].max()),
            'data_points': len(pressure_data)
        }
        
        print(f"\nSummary (as sent to frontend):")
        for key, value in summary.items():
            print(f"  {key}: {value} (type: {type(value)})")
            if isinstance(value, float) and 'pressure' in key:
                print(f"    .toFixed(6): {value:.6f}")
                print(f"    Scientific: {value:.2e}")
                
        # Check what processing method was used
        print(f"\nFile info details:")
        for key, value in analyzer.file_info.items():
            print(f"  {key}: {value}")
            
    else:
        print(f"File not found: {file_path}")

if __name__ == "__main__":
    test_real_file_processing()