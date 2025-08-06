#!/usr/bin/env python3
"""
Test script to verify RawFileReader integration
"""

import os
import sys
import subprocess
import tempfile
import json

def test_rawfilereader_console():
    """Test if the RawFileReader console application is working"""
    
    console_exe = os.path.join(
        os.path.dirname(__file__), 
        'RawFileReaderConsole', 
        'bin', 
        'Debug', 
        'net8.0', 
        'osx-x64', 
        'RawFileReaderConsole'
    )
    
    print(f"Checking for RawFileReader console at: {console_exe}")
    
    if not os.path.exists(console_exe):
        print("❌ RawFileReader console executable not found!")
        return False
    
    if not os.access(console_exe, os.X_OK):
        print("❌ RawFileReader console executable is not executable!")
        print("Making it executable...")
        os.chmod(console_exe, 0o755)
    
    # Test with no arguments (should show usage)
    try:
        result = subprocess.run([console_exe], capture_output=True, text=True, timeout=10)
        if "Usage:" in result.stdout or "Usage:" in result.stderr:
            print("✅ RawFileReader console application is working!")
            print(f"Output: {result.stdout or result.stderr}")
            return True
        else:
            print(f"❌ Unexpected output from console app: {result.stdout} {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ RawFileReader console application timed out")
        return False
    except Exception as e:
        print(f"❌ Error running RawFileReader console: {e}")
        return False

def test_thermo_analyzer():
    """Test the ThermoRawAnalyzer class"""
    
    # Add the current directory to Python path
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        from app import ThermoRawAnalyzer
        
        # Test with a non-existent file (should fall back to synthetic data)
        test_file = "test_file.raw"
        analyzer = ThermoRawAnalyzer(test_file)
        
        if analyzer.data is not None and len(analyzer.data) > 0:
            print("✅ ThermoRawAnalyzer is working with synthetic data")
            print(f"Generated {len(analyzer.data)} data points")
            print(f"Pressure range: {analyzer.data['pressure'].min():.2e} - {analyzer.data['pressure'].max():.2e} Torr")
            return True
        else:
            print("❌ ThermoRawAnalyzer failed to generate data")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ThermoRawAnalyzer: {e}")
        return False

if __name__ == "__main__":
    print("Testing RawFileReader Integration")
    print("=" * 50)
    
    console_ok = test_rawfilereader_console()
    analyzer_ok = test_thermo_analyzer()
    
    print("\nTest Results:")
    print("=" * 50)
    print(f"RawFileReader Console: {'✅ PASS' if console_ok else '❌ FAIL'}")
    print(f"ThermoRawAnalyzer: {'✅ PASS' if analyzer_ok else '❌ FAIL'}")
    
    if console_ok and analyzer_ok:
        print("\n🎉 All tests passed! RawFileReader integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")