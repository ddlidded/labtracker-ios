# Thermo Mass Spec Pressure Analyzer

A web-based GUI application for analyzing Thermo mass spectrometry .raw files to extract pressure profiles and analyze retention time data.

## Features

- **File Upload**: Upload Thermo .raw files (up to 2GB)
- **Pressure Profile Analysis**: Extract and visualize pressure data over time
- **Retention Time Analysis**: Get pressure values at specific retention times
- **Interactive Charts**: Dynamic pressure profile plots using Plotly
- **Data Export**: Export results as CSV or Excel files
- **Summary Statistics**: Comprehensive statistical analysis of pressure data
- **Modern UI**: Responsive design with Bootstrap 5 and custom styling

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mass-spec-analyzer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   
   **Development mode:**
   ```bash
   python run.py
   # or
   python app.py
   ```
   
   **Production mode (recommended for large files):**
   ```bash
   ./start_production.sh
   ```

4. **Access the application**:
   Open your web browser and navigate to `http://localhost:5000`

## Usage

### Uploading Files
1. Click "Choose File" and select a Thermo .raw file
2. Click "Upload and Analyze" to process the file
3. The application will display the pressure profile and summary statistics

### Analyzing Pressure at Specific Times
1. After uploading a file, use the "Pressure at Specific Time" section
2. Enter a retention time in minutes
3. Click "Get Pressure" to retrieve pressure data at that time

### Exporting Data
1. Use the "Export Data" section to download results
2. Choose between CSV or Excel format
3. The file will be automatically downloaded

## File Structure

```
mass-spec-analyzer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Custom CSS styles
│   └── js/
│       └── app.js        # Frontend JavaScript
└── uploads/              # Temporary file storage
```

## API Endpoints

- `GET /` - Main application page
- `POST /upload` - Upload and analyze .raw files
- `POST /pressure_at_time` - Get pressure at specific retention time
- `POST /export_data` - Export data as CSV or Excel
- `POST /cleanup` - Clean up uploaded files

## Technical Details

### Backend
- **Framework**: Flask (Python)
- **Data Processing**: NumPy, Pandas
- **Visualization**: Plotly
- **File Handling**: Werkzeug

### Frontend
- **UI Framework**: Bootstrap 5
- **Charts**: Plotly.js
- **Icons**: Font Awesome
- **Responsive Design**: Mobile-friendly interface

### Data Processing
The application includes a mock `ThermoRawAnalyzer` class that generates synthetic pressure data. In a production environment, this should be replaced with actual .raw file parsing libraries such as:

- `pymzml` for mzML files
- `thermo-raw-reader` for Thermo .raw files
- Custom parsers for specific instrument formats

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key (default: 'your-secret-key-here')
- `UPLOAD_FOLDER`: Directory for uploaded files (default: 'uploads')
- `MAX_CONTENT_LENGTH`: Maximum file size in bytes (default: 2GB)
- `FLASK_ENV`: Environment mode (development/production)

### File Size Limits
- Maximum file size: 2GB
- Supported formats: .raw files only
- Optimized for large file uploads with chunked processing

## Production Deployment

### Large File Upload Support
The application is optimized for handling large .raw files up to 2GB:

- **Chunked Upload Processing**: Files are processed in 8KB chunks to avoid memory issues
- **Extended Timeouts**: 1-hour timeout for large file processing
- **Progress Tracking**: Real-time upload progress for large files
- **Memory Optimization**: Efficient memory usage during file processing

### Production Server Setup
For production deployment with large file support:

1. **Install Gunicorn**:
   ```bash
   pip install gunicorn
   ```

2. **Start Production Server**:
   ```bash
   ./start_production.sh
   ```

3. **Alternative Gunicorn Command**:
   ```bash
   gunicorn --config gunicorn.conf.py wsgi:application
   ```

### Server Configuration
The `gunicorn.conf.py` file includes optimized settings for large file uploads:
- Worker processes: CPU cores × 2 + 1
- Timeout: 3600 seconds (1 hour)
- Request buffer: 2GB
- Memory management for large files

## Development
To integrate with actual Thermo .raw files, replace the mock `ThermoRawAnalyzer` class with real parsing logic:

```python
# Example integration with thermo-raw-reader
from thermo_raw_reader import ThermoRawReader

class ThermoRawAnalyzer:
    def __init__(self, file_path):
        self.reader = ThermoRawReader(file_path)
        self.data = self.load_data()
    
    def load_data(self):
        # Extract pressure data from .raw file
        pressure_data = self.reader.get_pressure_data()
        return pd.DataFrame(pressure_data)
```

### Customizing the Interface
- Modify `templates/index.html` for layout changes
- Update `static/css/style.css` for styling
- Edit `static/js/app.js` for functionality

## Troubleshooting

### Common Issues

1. **File upload fails**:
   - Check file size (must be < 2GB)
   - Ensure file has .raw extension
   - Verify file is not corrupted
   - For large files (>100MB), use production server mode

2. **Application won't start**:
   - Ensure all dependencies are installed
   - Check Python version (3.7+ required)
   - Verify port 5000 is available

3. **Charts not displaying**:
   - Check browser console for JavaScript errors
   - Ensure Plotly.js is loading correctly
   - Verify data format is correct

4. **Large file upload timeout**:
   - Use production server mode with Gunicorn
   - Ensure stable internet connection
   - Check server timeout settings
   - Monitor server memory usage

### Logs
Check the Flask application logs for detailed error information:
```bash
python app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thermo Fisher Scientific for mass spectrometry data formats
- Plotly for interactive charting capabilities
- Bootstrap for responsive UI components
- Flask community for the web framework

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the application logs
3. Create an issue in the repository
4. Contact the development team

---

**Note**: This application currently uses synthetic data for demonstration purposes. For production use with real Thermo .raw files, implement proper file parsing using appropriate libraries.