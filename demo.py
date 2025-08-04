#!/usr/bin/env python3
"""
Demo script for the Mass Spec Pressure Analyzer application.
This script demonstrates the application structure and functionality.
"""

import os
import sys
import json
import tempfile
from datetime import datetime

def create_mock_data():
    """Create mock pressure data for demonstration."""
    import numpy as np
    
    # Generate synthetic retention times (0-30 minutes)
    retention_times = np.linspace(0, 30, 3000)
    
    # Generate synthetic pressure data with realistic patterns
    base_pressure = 1.0  # Torr
    pressure_variations = (
        base_pressure + 
        0.1 * np.sin(retention_times * 0.5) +  # Slow oscillation
        0.05 * np.random.randn(len(retention_times)) +  # Noise
        0.2 * np.exp(-(retention_times - 15)**2 / 10)  # Peak around 15 min
    )
    
    return {
        'retention_times': retention_times.tolist(),
        'pressures': pressure_variations.tolist(),
        'pressures_mbar': (pressure_variations * 1.333).tolist(),
        'pressures_pa': (pressure_variations * 133.3).tolist()
    }

def demo_analysis():
    """Demonstrate the analysis functionality."""
    print("=" * 60)
    print("Mass Spec Pressure Analyzer - Demo")
    print("=" * 60)
    
    # Create mock data
    print("1. Generating mock pressure data...")
    data = create_mock_data()
    
    # Calculate statistics
    print("2. Calculating summary statistics...")
    pressures = data['pressures']
    stats = {
        'min_pressure': min(pressures),
        'max_pressure': max(pressures),
        'mean_pressure': sum(pressures) / len(pressures),
        'total_time': max(data['retention_times']),
        'data_points': len(pressures)
    }
    
    print(f"   - Min Pressure: {stats['min_pressure']:.4f} Torr")
    print(f"   - Max Pressure: {stats['max_pressure']:.4f} Torr")
    print(f"   - Mean Pressure: {stats['mean_pressure']:.4f} Torr")
    print(f"   - Total Time: {stats['total_time']:.1f} minutes")
    print(f"   - Data Points: {stats['data_points']:,}")
    
    # Demonstrate pressure at specific time
    print("\n3. Getting pressure at specific retention time...")
    target_time = 15.0
    closest_idx = min(range(len(data['retention_times'])), 
                     key=lambda i: abs(data['retention_times'][i] - target_time))
    
    pressure_at_time = {
        'retention_time': data['retention_times'][closest_idx],
        'pressure_torr': data['pressures'][closest_idx],
        'pressure_mbar': data['pressures_mbar'][closest_idx],
        'pressure_pa': data['pressures_pa'][closest_idx]
    }
    
    print(f"   - At {target_time} minutes:")
    print(f"     * Pressure: {pressure_at_time['pressure_torr']:.4f} Torr")
    print(f"     * Pressure: {pressure_at_time['pressure_mbar']:.4f} mbar")
    print(f"     * Pressure: {pressure_at_time['pressure_pa']:.2f} Pa")
    
    # Save demo data
    print("\n4. Saving demo data...")
    demo_data = {
        'timestamp': datetime.now().isoformat(),
        'data': data,
        'statistics': stats,
        'pressure_at_time': pressure_at_time
    }
    
    with open('demo_data.json', 'w') as f:
        json.dump(demo_data, f, indent=2)
    
    print("   - Demo data saved to 'demo_data.json'")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)

def show_application_structure():
    """Show the application file structure."""
    print("\nApplication Structure:")
    print("├── app.py                 # Main Flask application")
    print("├── run.py                 # Startup script")
    print("├── requirements.txt       # Python dependencies")
    print("├── README.md             # Documentation")
    print("├── demo.py               # This demo script")
    print("├── test_app.py           # Unit tests")
    print("├── .gitignore            # Git ignore rules")
    print("├── templates/")
    print("│   └── index.html        # Main HTML template")
    print("├── static/")
    print("│   ├── css/")
    print("│   │   └── style.css     # Custom styles")
    print("│   └── js/")
    print("│       └── app.js        # Frontend JavaScript")
    print("└── uploads/              # File upload directory")

def show_installation_instructions():
    """Show installation and usage instructions."""
    print("\nInstallation Instructions:")
    print("1. Install Python dependencies:")
    print("   pip install -r requirements.txt")
    print("\n2. Run the application:")
    print("   python run.py")
    print("   # or")
    print("   python app.py")
    print("\n3. Open your browser and navigate to:")
    print("   http://localhost:5000")
    print("\n4. Upload a .raw file and start analyzing!")

def main():
    """Main demo function."""
    try:
        # Check if numpy is available
        import numpy as np
        demo_analysis()
    except ImportError:
        print("NumPy not available. Showing application structure only.")
    
    show_application_structure()
    show_installation_instructions()
    
    print("\nFeatures:")
    print("✓ File upload and validation")
    print("✓ Pressure profile visualization")
    print("✓ Retention time analysis")
    print("✓ Data export (CSV/Excel)")
    print("✓ Summary statistics")
    print("✓ Responsive web interface")
    print("✓ Interactive charts")
    print("✓ Modern UI design")

if __name__ == '__main__':
    main()