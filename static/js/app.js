// Mass Spec Pressure Analyzer - Frontend JavaScript

let currentFilename = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    showWelcomeMessage();
});

function initializeEventListeners() {
    // File upload form
    const uploadForm = document.getElementById('uploadForm');
    uploadForm.addEventListener('submit', handleFileUpload);
    
    // Pressure at time form
    const pressureAtTimeForm = document.getElementById('pressureAtTimeForm');
    pressureAtTimeForm.addEventListener('submit', handlePressureAtTime);
    
    // File input change
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', handleFileSelection);
}

function handleFileSelection(event) {
    const file = event.target.files[0];
    if (file) {
        // Validate file type
        if (!file.name.toLowerCase().endsWith('.raw')) {
            showMessage('Please select a valid .raw file.', 'error');
            event.target.value = '';
            return;
        }
        
        // Validate file size (16MB limit)
        if (file.size > 16 * 1024 * 1024) {
            showMessage('File size must be less than 16MB.', 'error');
            event.target.value = '';
            return;
        }
        
        showMessage(`Selected file: ${file.name}`, 'success');
    }
}

async function handleFileUpload(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('Please select a file to upload.', 'error');
        return;
    }
    
    // Show loading state
    const uploadBtn = document.getElementById('uploadBtn');
    const originalText = uploadBtn.innerHTML;
    uploadBtn.innerHTML = '<span class="loading-spinner"></span> Processing...';
    uploadBtn.disabled = true;
    
    const uploadProgress = document.getElementById('uploadProgress');
    uploadProgress.style.display = 'block';
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentFilename = result.filename;
            displayResults(result);
            showMessage('File uploaded and analyzed successfully!', 'success');
        } else {
            showMessage(result.error || 'Upload failed.', 'error');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showMessage('An error occurred during upload. Please try again.', 'error');
    } finally {
        // Reset loading state
        uploadBtn.innerHTML = originalText;
        uploadBtn.disabled = false;
        uploadProgress.style.display = 'none';
    }
}

function displayResults(result) {
    // Hide welcome message and show results
    document.getElementById('welcomeMessage').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    
    // Show additional cards
    document.getElementById('pressureAtTimeCard').style.display = 'block';
    document.getElementById('exportCard').style.display = 'block';
    
    // Display summary statistics
    displaySummaryStats(result.summary);
    
    // Display pressure plot
    displayPressurePlot(result.plot);
    
    // Display data table
    displayDataTable(result.data);
    
    // Add fade-in animation
    document.getElementById('resultsSection').classList.add('fade-in');
}

function displaySummaryStats(summary) {
    const summaryStats = document.getElementById('summaryStats');
    
    const stats = [
        { label: 'Min Pressure', value: summary.min_pressure.toFixed(3), unit: 'Torr', icon: 'fas fa-arrow-down' },
        { label: 'Max Pressure', value: summary.max_pressure.toFixed(3), unit: 'Torr', icon: 'fas fa-arrow-up' },
        { label: 'Mean Pressure', value: summary.mean_pressure.toFixed(3), unit: 'Torr', icon: 'fas fa-chart-line' },
        { label: 'Std Deviation', value: summary.std_pressure.toFixed(3), unit: 'Torr', icon: 'fas fa-chart-bar' },
        { label: 'Total Time', value: summary.total_time.toFixed(1), unit: 'min', icon: 'fas fa-clock' },
        { label: 'Data Points', value: summary.data_points.toLocaleString(), unit: '', icon: 'fas fa-database' }
    ];
    
    summaryStats.innerHTML = stats.map(stat => `
        <div class="col-md-4 col-lg-2 mb-3">
            <div class="stat-card">
                <i class="${stat.icon} fa-2x text-primary mb-2"></i>
                <div class="stat-value">${stat.value}</div>
                <div class="stat-label">${stat.label}</div>
                <small class="text-muted">${stat.unit}</small>
            </div>
        </div>
    `).join('');
}

function displayPressurePlot(plotJson) {
    const plotData = JSON.parse(plotJson);
    Plotly.newPlot('pressurePlot', plotData.data, plotData.layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false
    });
}

function displayDataTable(data) {
    const tableBody = document.getElementById('dataTableBody');
    
    tableBody.innerHTML = data.map(row => `
        <tr>
            <td>${row.retention_time.toFixed(2)}</td>
            <td>${row.pressure.toFixed(4)}</td>
            <td>${row.pressure_mbar.toFixed(4)}</td>
            <td>${row.pressure_pa.toFixed(2)}</td>
        </tr>
    `).join('');
}

async function handlePressureAtTime(event) {
    event.preventDefault();
    
    const retentionTime = parseFloat(document.getElementById('retentionTime').value);
    
    if (!currentFilename) {
        showMessage('Please upload a file first.', 'error');
        return;
    }
    
    if (isNaN(retentionTime) || retentionTime < 0) {
        showMessage('Please enter a valid retention time.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/pressure_at_time', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: currentFilename,
                retention_time: retentionTime
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayPressureResult(result.pressure_info);
        } else {
            showMessage(result.error || 'Failed to get pressure data.', 'error');
        }
        
    } catch (error) {
        console.error('Error getting pressure:', error);
        showMessage('An error occurred. Please try again.', 'error');
    }
}

function displayPressureResult(pressureInfo) {
    const pressureResult = document.getElementById('pressureResult');
    const pressureDetails = document.getElementById('pressureDetails');
    
    pressureDetails.innerHTML = `
        <div class="row">
            <div class="col-md-4">
                <strong>Retention Time:</strong><br>
                ${pressureInfo.retention_time.toFixed(2)} minutes
            </div>
            <div class="col-md-4">
                <strong>Pressure (Torr):</strong><br>
                ${pressureInfo.pressure_torr.toFixed(4)}
            </div>
            <div class="col-md-4">
                <strong>Pressure (mbar):</strong><br>
                ${pressureInfo.pressure_mbar.toFixed(4)}
            </div>
        </div>
        <div class="row mt-2">
            <div class="col-md-4">
                <strong>Pressure (Pa):</strong><br>
                ${pressureInfo.pressure_pa.toFixed(2)}
            </div>
        </div>
    `;
    
    pressureResult.style.display = 'block';
    pressureResult.classList.add('fade-in');
}

async function exportData(format) {
    if (!currentFilename) {
        showMessage('Please upload a file first.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/export_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: currentFilename,
                format: format
            })
        });
        
        if (response.ok) {
            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `pressure_profile_${currentFilename}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showMessage(`Data exported successfully as ${format.toUpperCase()}!`, 'success');
        } else {
            const result = await response.json();
            showMessage(result.error || 'Export failed.', 'error');
        }
        
    } catch (error) {
        console.error('Export error:', error);
        showMessage('An error occurred during export. Please try again.', 'error');
    }
}

function showWelcomeMessage() {
    document.getElementById('welcomeMessage').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('pressureAtTimeCard').style.display = 'none';
    document.getElementById('exportCard').style.display = 'none';
}

function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message-success, .message-error');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-${type}`;
    messageDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close float-end" onclick="this.parentElement.remove()"></button>
    `;
    
    // Insert at the top of the container
    const container = document.querySelector('.container-fluid');
    container.insertBefore(messageDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentElement) {
            messageDiv.remove();
        }
    }, 5000);
}

// Utility function to format numbers
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

// Add some interactive features
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + U to focus file upload
        if ((event.ctrlKey || event.metaKey) && event.key === 'u') {
            event.preventDefault();
            document.getElementById('fileInput').click();
        }
        
        // Ctrl/Cmd + E to export as CSV
        if ((event.ctrlKey || event.metaKey) && event.key === 'e') {
            event.preventDefault();
            if (currentFilename) {
                exportData('csv');
            }
        }
    });
});

// Add tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});