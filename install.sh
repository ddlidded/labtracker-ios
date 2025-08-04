#!/bin/bash

# Mass Spec Pressure Analyzer - Installation Script

echo "============================================================"
echo "Thermo Mass Spec Pressure Analyzer - Installation"
echo "============================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.7+ is required. Current version: $python_version"
    exit 1
fi

echo "✓ Python $python_version detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✓ pip3 detected"

# Create virtual environment (optional)
read -p "Do you want to create a virtual environment? (y/n): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
fi

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Create uploads directory
mkdir -p uploads
echo "✓ Uploads directory created"

# Set permissions
chmod +x run.py
chmod +x demo.py
echo "✓ Executable permissions set"

echo ""
echo "============================================================"
echo "Installation completed successfully!"
echo "============================================================"
echo ""
echo "To start the application:"
echo "  python3 run.py"
echo ""
echo "To run the demo:"
echo "  python3 demo.py"
echo ""
echo "To run tests:"
echo "  python3 test_app.py"
echo ""
echo "The application will be available at: http://localhost:5000"
echo ""
echo "For more information, see README.md"
echo "============================================================"