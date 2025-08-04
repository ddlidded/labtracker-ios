import os
import tempfile
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
from io import BytesIO
import zipfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'raw'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ThermoRawAnalyzer:
    """Mock class for Thermo .raw file analysis - replace with actual implementation"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.load_data()
    
    def load_data(self):
        """Load and parse the .raw file"""
        # This is a mock implementation
        # In a real application, you would use a library like pymzml or thermo-raw-reader
        # For demonstration, we'll generate synthetic data
        
        # Generate synthetic retention times (0-30 minutes)
        retention_times = np.linspace(0, 30, 3000)
        
        # Generate synthetic pressure data with some realistic patterns
        base_pressure = 1.0  # Torr
        pressure_variations = (
            base_pressure + 
            0.1 * np.sin(retention_times * 0.5) +  # Slow oscillation
            0.05 * np.random.randn(len(retention_times)) +  # Noise
            0.2 * np.exp(-(retention_times - 15)**2 / 10)  # Peak around 15 min
        )
        
        self.data = pd.DataFrame({
            'retention_time': retention_times,
            'pressure': pressure_variations,
            'pressure_mbar': pressure_variations * 1.333,  # Convert Torr to mbar
            'pressure_pa': pressure_variations * 133.3     # Convert Torr to Pa
        })
    
    def get_pressure_profile(self):
        """Get the complete pressure profile"""
        return self.data
    
    def get_pressure_at_time(self, retention_time, tolerance=0.1):
        """Get pressure at a specific retention time"""
        # Find the closest retention time within tolerance
        time_diff = np.abs(self.data['retention_time'] - retention_time)
        if np.min(time_diff) <= tolerance:
            closest_idx = np.argmin(time_diff)
            return {
                'retention_time': self.data.iloc[closest_idx]['retention_time'],
                'pressure_torr': self.data.iloc[closest_idx]['pressure'],
                'pressure_mbar': self.data.iloc[closest_idx]['pressure_mbar'],
                'pressure_pa': self.data.iloc[closest_idx]['pressure_pa']
            }
        else:
            return None
    
    def get_pressure_range(self, start_time, end_time):
        """Get pressure data within a time range"""
        mask = (self.data['retention_time'] >= start_time) & (self.data['retention_time'] <= end_time)
        return self.data[mask]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            
            # Analyze the file
            analyzer = ThermoRawAnalyzer(filepath)
            pressure_data = analyzer.get_pressure_profile()
            
            # Create plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=pressure_data['retention_time'],
                y=pressure_data['pressure'],
                mode='lines',
                name='Pressure (Torr)',
                line=dict(color='blue', width=2)
            ))
            
            fig.update_layout(
                title='Pressure Profile Over Time',
                xaxis_title='Retention Time (minutes)',
                yaxis_title='Pressure (Torr)',
                template='plotly_white',
                height=500
            )
            
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            # Get summary statistics
            summary = {
                'min_pressure': float(pressure_data['pressure'].min()),
                'max_pressure': float(pressure_data['pressure'].max()),
                'mean_pressure': float(pressure_data['pressure'].mean()),
                'std_pressure': float(pressure_data['pressure'].std()),
                'total_time': float(pressure_data['retention_time'].max()),
                'data_points': len(pressure_data)
            }
            
            return jsonify({
                'success': True,
                'filename': filename,
                'plot': plot_json,
                'summary': summary,
                'data': pressure_data.to_dict('records')[:100]  # First 100 points for preview
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/pressure_at_time', methods=['POST'])
def get_pressure_at_time():
    data = request.get_json()
    filename = data.get('filename')
    retention_time = float(data.get('retention_time'))
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        analyzer = ThermoRawAnalyzer(filepath)
        pressure_info = analyzer.get_pressure_at_time(retention_time)
        
        if pressure_info:
            return jsonify({
                'success': True,
                'pressure_info': pressure_info
            })
        else:
            return jsonify({
                'error': f'No data found at retention time {retention_time} minutes'
            }), 404
            
    except Exception as e:
        return jsonify({'error': f'Error analyzing file: {str(e)}'}), 500

@app.route('/export_data', methods=['POST'])
def export_data():
    data = request.get_json()
    filename = data.get('filename')
    format_type = data.get('format', 'csv')
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        analyzer = ThermoRawAnalyzer(filepath)
        pressure_data = analyzer.get_pressure_profile()
        
        if format_type == 'csv':
            output = BytesIO()
            pressure_data.to_csv(output, index=False)
            output.seek(0)
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'pressure_profile_{filename}.csv'
            )
        elif format_type == 'excel':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                pressure_data.to_excel(writer, sheet_name='Pressure_Profile', index=False)
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'pressure_profile_{filename}.xlsx'
            )
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Error exporting data: {str(e)}'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Clean up uploaded files"""
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        return jsonify({'success': True, 'message': 'Files cleaned up successfully'})
    except Exception as e:
        return jsonify({'error': f'Error cleaning up files: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)