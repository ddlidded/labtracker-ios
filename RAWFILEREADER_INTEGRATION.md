# RawFileReader Integration

This document describes the integration of Thermo Fisher Scientific's RawFileReader libraries into the LabTracker application.

## Overview

The application now supports reading actual Thermo Scientific .raw files using the official RawFileReader .NET libraries. This integration provides access to authentic mass spectrometry data including:

- Scan information
- Retention times
- Pressure data (when available)
- Instrument metadata
- File creation information

## Architecture

The integration uses a hybrid approach:

1. **C# Console Application**: `RawFileReaderConsole` - A .NET 8 console application that uses the official RawFileReader libraries
2. **Python Interface**: The `ThermoRawAnalyzer` class calls the C# console application via subprocess
3. **JSON Data Exchange**: Data is exchanged between C# and Python using JSON files

## Components

### RawFileReader Libraries

Located in `RawFileReader/Libs/NetCore/Net8/Assemblies/`:
- `ThermoFisher.CommonCore.Data.dll`
- `ThermoFisher.CommonCore.RawFileReader.dll`
- `ThermoFisher.CommonCore.BackgroundSubtraction.dll`
- `ThermoFisher.CommonCore.MassPrecisionEstimator.dll`
- `OpenMcdf.dll` and `OpenMcdf.Extensions.dll`

### C# Console Application

**Location**: `RawFileReaderConsole/`

**Files**:
- `Program.cs` - Main application logic
- `RawFileReaderConsole.csproj` - Project configuration
- `bin/Debug/net8.0/osx-x64/RawFileReaderConsole` - Compiled executable

**Usage**:
```bash
./RawFileReaderConsole input.raw output.json
```

**Output Format**:
```json
{
  "file_info": {
    "filename": "sample.raw",
    "creation_date": "2024-01-01T10:00:00",
    "operator_name": "Operator",
    "instrument_model": "Q Exactive",
    "scan_count": 1000,
    "time_range": { "start": 0.0, "end": 60.0 }
  },
  "scans": [
    {
      "scan_number": 1,
      "retention_time": 0.5,
      "pressure": 1.2e-6,
      "base_peak_mass": 445.12,
      "base_peak_intensity": 1000000,
      "total_ion_current": 5000000
    }
  ]
}
```

### Python Integration

**Class**: `ThermoRawAnalyzer` in `app.py`

**Key Methods**:
- `_try_rawfilereader_reading()` - Attempts to read .raw files using the C# console
- `load_data()` - Main data loading method with fallback strategies

**Fallback Strategy**:
1. Try RawFileReader for .raw files
2. Try pymzml for .mzml files
3. Generate synthetic data as last resort

## Installation and Setup

### Prerequisites

1. **.NET 8 SDK** - Required to build the C# console application
2. **Python 3.7+** - For the Flask web application
3. **macOS/Linux/Windows** - RawFileReader supports all platforms

### Build Process

1. **Build C# Console Application**:
   ```bash
   cd RawFileReaderConsole
   dotnet build
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Test Integration**:
   ```bash
   python3 test_rawfilereader.py
   ```

## Usage

### Web Interface

1. Start the application: `python3 run.py`
2. Open browser to `http://localhost:9847`
3. Upload a .raw file
4. View pressure analysis results

### Supported File Types

- **.raw** - Thermo Scientific RAW files (primary support)
- **.mzml** - mzML format files (secondary support)
- **Other formats** - Synthetic data generation for testing

## Data Extraction

The integration extracts the following data from .raw files:

### File Metadata
- Creation date and operator information
- Instrument model, name, and serial number
- Software and firmware versions
- Scan count and time range
- Mass range information

### Scan Data
- Scan numbers and retention times
- Pressure information (from trailer extra data)
- Base peak mass and intensity
- Total ion current (TIC)

### Pressure Data Processing

1. **Direct Extraction**: Looks for pressure fields in trailer extra data
2. **Synthetic Generation**: Creates realistic pressure values if not found
3. **Unit Conversion**: Provides pressure in Torr, mbar, and Pa

## Testing

Run the test suite to verify integration:

```bash
python3 test_rawfilereader.py
```

**Expected Output**:
```
Testing RawFileReader Integration
==================================================
✅ RawFileReader console application is working!
✅ ThermoRawAnalyzer is working with synthetic data

Test Results:
==================================================
RawFileReader Console: ✅ PASS
ThermoRawAnalyzer: ✅ PASS

🎉 All tests passed! RawFileReader integration is ready.
```

## Troubleshooting

### Common Issues

1. **C# Console Not Found**:
   - Ensure .NET 8 SDK is installed
   - Build the console application: `cd RawFileReaderConsole && dotnet build`

2. **Permission Denied**:
   - Make console executable: `chmod +x RawFileReaderConsole/bin/Debug/net8.0/osx-x64/RawFileReaderConsole`

3. **Missing Dependencies**:
   - Verify all .dll files are present in `RawFileReader/Libs/NetCore/Net8/Assemblies/`

4. **Timeout Errors**:
   - Large .raw files may take time to process
   - Increase timeout in `_try_rawfilereader_reading()` method

### Debug Mode

Enable debug output by checking the Flask application logs when uploading files. The application will show:
- Which reading method was successful
- Fallback reasons if RawFileReader fails
- Data extraction statistics

## Performance Considerations

- **Large Files**: The integration samples every 10th scan for files with >1000 scans
- **Memory Usage**: JSON output is limited to essential data points
- **Timeout**: 5-minute timeout for processing large files
- **Caching**: Consider implementing file caching for repeated analysis

## Future Enhancements

1. **Direct .NET Integration**: Use pythonnet when Python 3.14 compatibility is resolved
2. **Advanced Filtering**: Add scan filtering options
3. **Batch Processing**: Support multiple file processing
4. **Real-time Processing**: Stream processing for large files
5. **Enhanced Metadata**: Extract additional instrument parameters

## License and Attribution

This integration uses Thermo Fisher Scientific's RawFileReader libraries. Please ensure compliance with Thermo Fisher Scientific's licensing terms when using this software.

The RawFileReader libraries are provided by Thermo Fisher Scientific and are subject to their terms of use.