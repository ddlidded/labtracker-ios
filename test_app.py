#!/usr/bin/env python3
"""
Test script for the Mass Spec Pressure Analyzer application.
This script tests the basic functionality of the Flask app.
"""

import unittest
import tempfile
import os
import json
from io import BytesIO
from app import app, ThermoRawAnalyzer

class TestMassSpecAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and temporary files."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_home_page(self):
        """Test that the home page loads correctly."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thermo Mass Spec Pressure Analyzer', response.data)
    
    def test_upload_without_file(self):
        """Test upload endpoint without file."""
        response = self.app.post('/upload')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'This is not a .raw file')
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = self.app.post('/upload', 
                                       data={'file': (file, 'test.txt')},
                                       content_type='multipart/form-data')
        
        os.unlink(f.name)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
    
    def test_upload_valid_file(self):
        """Test upload with a valid .raw file (mock)."""
        # Create a mock .raw file
        with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as f:
            f.write(b'Mock Thermo .raw file content')
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = self.app.post('/upload', 
                                       data={'file': (file, 'test.raw')},
                                       content_type='multipart/form-data')
        
        os.unlink(f.name)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('filename', data)
        self.assertIn('plot', data)
        self.assertIn('summary', data)
        self.assertIn('data', data)
    
    def test_pressure_at_time(self):
        """Test getting pressure at specific time."""
        # First upload a file
        with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as f:
            f.write(b'Mock Thermo .raw file content')
            f.flush()
            
            with open(f.name, 'rb') as file:
                upload_response = self.app.post('/upload', 
                                              data={'file': (file, 'test.raw')},
                                              content_type='multipart/form-data')
        
        os.unlink(f.name)
        upload_data = json.loads(upload_response.data)
        
        # Test pressure at time
        response = self.app.post('/pressure_at_time',
                               data=json.dumps({
                                   'filename': upload_data['filename'],
                                   'retention_time': 15.0
                               }),
                               content_type='application/json')
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('pressure_info', data)
    
    def test_export_data(self):
        """Test data export functionality."""
        # First upload a file
        with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as f:
            f.write(b'Mock Thermo .raw file content')
            f.flush()
            
            with open(f.name, 'rb') as file:
                upload_response = self.app.post('/upload', 
                                              data={'file': (file, 'test.raw')},
                                              content_type='multipart/form-data')
        
        os.unlink(f.name)
        upload_data = json.loads(upload_response.data)
        
        # Test CSV export
        response = self.app.post('/export_data',
                               data=json.dumps({
                                   'filename': upload_data['filename'],
                                   'format': 'csv'
                               }),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response.headers['Content-Type'])
    
    def test_thermo_raw_analyzer(self):
        """Test the ThermoRawAnalyzer class."""
        # Create a temporary file path
        temp_file = os.path.join(self.temp_dir, 'test.raw')
        with open(temp_file, 'w') as f:
            f.write('Mock file content')
        
        # Test analyzer initialization
        analyzer = ThermoRawAnalyzer(temp_file)
        self.assertIsNotNone(analyzer.data)
        
        # Test pressure profile
        profile = analyzer.get_pressure_profile()
        self.assertIsNotNone(profile)
        self.assertGreater(len(profile), 0)
        
        # Test pressure at time
        pressure_info = analyzer.get_pressure_at_time(15.0)
        self.assertIsNotNone(pressure_info)
        self.assertIn('retention_time', pressure_info)
        self.assertIn('pressure_torr', pressure_info)
        
        # Test pressure range
        range_data = analyzer.get_pressure_range(10.0, 20.0)
        self.assertIsNotNone(range_data)
        self.assertGreater(len(range_data), 0)

def run_tests():
    """Run all tests."""
    print("Running Mass Spec Pressure Analyzer tests...")
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests()