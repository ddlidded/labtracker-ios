#!/usr/bin/env python3

import os
import sys
import subprocess
import json
import tempfile
from app import ThermoRawAnalyzer

def test_rawfilereader_integration():
    """Test the RawFileReader integration step by step"""
    
    # Test file path
    test_file = "uploads/20250804_121751_QC-Pool1.raw"
    
    if not os.path.exists(test_file):
        print(f"ERROR: Test file {test_file} not found")
        return False
    
    print(f"Testing RawFileReader integration with: {test_file}")
    print("=" * 60)
    
    # Test 1: Check if RawFileReader executable exists
    console_exe = os.path.join(os.path.dirname(__file__), 'RawFileReaderConsole', 'bin', 'Debug', 'net8.0', 'osx-x64', 'RawFileReaderConsole')
    print(f"1. Checking RawFileReader executable: {console_exe}")
    
    if os.path.exists(console_exe):
        print("   ✓ RawFileReader executable found")
    else:
        print("   ✗ RawFileReader executable NOT found")
        return False
    
    # Test 2: Test direct subprocess call
    print("\n2. Testing direct subprocess call...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_output = temp_file.name
    
    cmd = [console_exe, test_file, temp_output]
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        print(f"   Return code: {result.returncode}")
        print(f"   Stdout length: {len(result.stdout)} chars")
        print(f"   Stderr length: {len(result.stderr)} chars")
        
        if result.stderr:
            print(f"   Stderr: {result.stderr[:500]}...")
        
        if result.returncode == 0 and os.path.exists(temp_output):
            print("   ✓ Subprocess call successful")
            
            # Test 3: Check output file
            print("\n3. Checking output file...")
            try:
                with open(temp_output, 'r') as f:
                    raw_data = json.load(f)
                
                print(f"   Output file size: {os.path.getsize(temp_output)} bytes")
                print(f"   JSON keys: {list(raw_data.keys())}")
                
                if 'scans' in raw_data:
                    print(f"   Number of scans: {len(raw_data['scans'])}")
                    
                    # Check first few scans
                    for i, scan in enumerate(raw_data['scans'][:3]):
                        print(f"   Scan {i+1}: RT={scan.get('retention_time', 'N/A')}, Pressure={scan.get('pressure', 'N/A')}")
                    
                    print("   ✓ Valid scan data found")
                else:
                    print("   ✗ No 'scans' key in output")
                    
            except Exception as e:
                print(f"   ✗ Error reading output file: {e}")
                
        else:
            print("   ✗ Subprocess call failed or no output file")
            
    except Exception as e:
        print(f"   ✗ Subprocess error: {e}")
    
    # Clean up
    if os.path.exists(temp_output):
        os.unlink(temp_output)
    
    # Test 4: Test ThermoRawAnalyzer class
    print("\n4. Testing ThermoRawAnalyzer class...")
    
    try:
        analyzer = ThermoRawAnalyzer(test_file)
        analyzer.load_data()
        
        print(f"   Data shape: {analyzer.data.shape if analyzer.data is not None else 'None'}")
        print(f"   Data columns: {list(analyzer.data.columns) if analyzer.data is not None else 'None'}")
        print(f"   File info: {analyzer.file_info}")
        
        if analyzer.data is not None and len(analyzer.data) > 0:
            print(f"   First few pressure values: {analyzer.data['pressure'].head().tolist()}")
            print(f"   Pressure range: {analyzer.data['pressure'].min():.2f} - {analyzer.data['pressure'].max():.2f} bar")
            
            # Check if data looks synthetic
            pressure_values = analyzer.data['pressure'].values
            if len(set(pressure_values[:10])) < 5:  # Very few unique values suggests synthetic
                print("   ⚠️  WARNING: Data appears to be synthetic (low variation)")
            else:
                print("   ✓ Data appears to be real (good variation)")
        else:
            print("   ✗ No data loaded")
            
    except Exception as e:
        print(f"   ✗ ThermoRawAnalyzer error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Debug complete")

if __name__ == "__main__":
    test_rawfilereader_integration()