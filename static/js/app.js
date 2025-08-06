// Mass Spec Pressure Analyzer - Frontend JavaScript

let currentFilename = null;

// Helper function to format pressure values appropriately
function formatPressure(value) {
    if (value === 0) return '0.000000';
    if (value < 1e-6) {
        // Use scientific notation for very small values
        return value.toExponential(2);
    } else if (value < 0.001) {
        // Use 8 decimal places for small values
        return value.toFixed(8);
    } else {
        // Use 6 decimal places for normal values
        return value.toFixed(6);
    }
}

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
    
    // Records per page selector
    const recordsPerPageSelect = document.getElementById('recordsPerPage');
    if (recordsPerPageSelect) {
        recordsPerPageSelect.addEventListener('change', function() {
            if (currentFilename) {
                recordsPerPage = parseInt(this.value);
                currentPage = 1;
                loadPaginatedData(currentPage, recordsPerPage);
            }
        });
    }
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
        
        // Validate file size (2GB limit)
        if (file.size > 2 * 1024 * 1024 * 1024) {
            showMessage('File size must be less than 2GB.', 'error');
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
    
    // Update progress message for large files
    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(1);
    const progressText = uploadProgress.querySelector('small');
    if (fileSizeMB > 100) {
        progressText.textContent = `Processing large file (${fileSizeMB} MB)... This may take several minutes.`;
    } else {
        progressText.textContent = 'Processing file...';
    }
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        // For large files, show more detailed progress
        const response = await fetch('/upload', {
            method: 'POST',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentFilename = result.filename;
            displayResults(result);
            showMessage(`File uploaded and analyzed successfully! (${fileSizeMB} MB)`, 'success');
            
            // Force complete page reload to ensure fresh data
            setTimeout(() => {
                window.location.reload(true); // Force reload from server
            }, 1000);
        } else {
            showMessage(result.error || 'Upload failed.', 'error');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            showMessage('Upload timeout or connection error. For large files, please ensure stable internet connection.', 'error');
        } else {
            showMessage('An error occurred during upload. Please try again.', 'error');
        }
    } finally {
        // Reset loading state
        uploadBtn.innerHTML = originalText;
        uploadBtn.disabled = false;
        uploadProgress.style.display = 'none';
    }
}

function displayResults(result) {
    console.log('displayResults called with:', result);
    console.log('result.summary:', result.summary);
    
    // Clear any cached data
    clearCachedData();
    
    // Hide welcome message and show results
    document.getElementById('welcomeMessage').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    
    // Show additional cards
    document.getElementById('pressureAtTimeCard').style.display = 'block';
    document.getElementById('exportCard').style.display = 'block';
    
    // Display summary statistics
    console.log('About to call displaySummaryStats with:', result.summary);
    displaySummaryStats(result.summary);
    
    // Display pressure plot
    displayPressurePlot(result.plot);
    
    // Store current filename for other operations
    currentFilename = result.filename;
    
    // Load first page of data with pagination with forced refresh
    currentPage = 1;
    recordsPerPage = parseInt(document.getElementById('recordsPerPage').value) || 50;
    loadPaginatedData(currentPage, recordsPerPage);
    
    // Add fade-in animation
    document.getElementById('resultsSection').classList.add('fade-in');
}

function clearCachedData() {
    // Clear any browser cached data
    if ('caches' in window) {
        caches.keys().then(function(names) {
            names.forEach(function(name) {
                caches.delete(name);
            });
        });
    }
    
    // Clear localStorage and sessionStorage
    if (typeof(Storage) !== "undefined") {
        localStorage.clear();
        sessionStorage.clear();
    }
    
    // Force reload of static assets on next request
    const timestamp = Date.now();
    const links = document.querySelectorAll('link[rel="stylesheet"]');
    links.forEach(link => {
        const href = link.href.split('?')[0];
        link.href = href + '?v=' + timestamp;
    });
    
    // Add cache-busting to current page
    if (window.history && window.history.replaceState) {
        const url = new URL(window.location);
        url.searchParams.set('v', timestamp);
        window.history.replaceState({}, '', url);
    }
}

function displaySummaryStats(summary) {
    console.log('displaySummaryStats called with:', summary);
    
    const summaryStats = document.getElementById('summaryStats');
    console.log('summaryStats element:', summaryStats);
    
    if (!summaryStats) {
        console.error('summaryStats element not found!');
        return;
    }
    
    if (!summary) {
        console.error('No summary data provided!');
        return;
    }
    
    // Check if all required fields exist
    const requiredFields = ['min_pressure', 'max_pressure', 'mean_pressure', 'std_pressure', 'total_time', 'data_points'];
    const missingFields = requiredFields.filter(field => !(field in summary));
    if (missingFields.length > 0) {
        console.error('Missing fields in summary:', missingFields);
        return;
    }
    
    const stats = [
        { label: 'Min Pressure', value: formatPressure(summary.min_pressure), unit: 'bar', icon: 'fas fa-arrow-down' },
        { label: 'Max Pressure', value: formatPressure(summary.max_pressure), unit: 'bar', icon: 'fas fa-arrow-up' },
        { label: 'Mean Pressure', value: formatPressure(summary.mean_pressure), unit: 'bar', icon: 'fas fa-chart-line' },
        { label: 'Std Deviation', value: formatPressure(summary.std_pressure), unit: 'bar', icon: 'fas fa-chart-bar' },
        { label: 'Total Time', value: summary.total_time.toFixed(1), unit: 'min', icon: 'fas fa-clock' },
        { label: 'Data Points', value: summary.data_points.toLocaleString(), unit: '', icon: 'fas fa-database' }
    ];
    
    console.log('Generated stats:', stats);
    
    const html = stats.map(stat => `
        <div class="col-md-4 col-lg-2 mb-3">
            <div class="stat-card">
                <i class="${stat.icon} fa-2x text-primary mb-2"></i>
                <div class="stat-value">${stat.value}</div>
                <div class="stat-label">${stat.label}</div>
                <small class="text-muted">${stat.unit}</small>
            </div>
        </div>
    `).join('');
    
    console.log('Generated HTML:', html);
    summaryStats.innerHTML = html;
    console.log('Summary stats updated successfully');
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

// Pagination variables
let currentPage = 1;
let recordsPerPage = 50;
let totalPages = 1;
let totalRecords = 0;

function displayDataTable(data) {
    const tableBody = document.getElementById('dataTableBody');
    
    tableBody.innerHTML = data.map(row => {
        const pressure_bar = row.pressure_mbar * 0.001; // Convert mbar to bar
        return `
            <tr>
                <td>${row.retention_time.toFixed(2)}</td>
                <td>${formatPressure(pressure_bar)}</td>
                <td>${row.pressure_mbar.toFixed(4)}</td>
                <td>${row.pressure.toFixed(4)}</td>
                <td>${row.pressure_pa.toFixed(2)}</td>
            </tr>
        `;
    }).join('');
}

async function loadPaginatedData(page = 1, perPage = 50) {
    if (!currentFilename) {
        console.error('No filename available for pagination');
        return;
    }
    
    try {
        const response = await fetch('/get_paginated_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            },
            body: JSON.stringify({
                filename: currentFilename,
                page: page,
                per_page: perPage,
                timestamp: Date.now() // Cache-busting parameter
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayDataTable(result.data);
            updatePaginationControls(result.pagination);
            showPaginationContainer();
        } else {
            showMessage('Error loading data: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error loading paginated data:', error);
        showMessage('Error loading paginated data: ' + error.message, 'error');
    }
}

function updatePaginationControls(pagination) {
    currentPage = pagination.page;
    totalPages = pagination.total_pages;
    totalRecords = pagination.total_records;
    recordsPerPage = pagination.per_page;
    
    // Update pagination info
    const startRecord = (currentPage - 1) * recordsPerPage + 1;
    const endRecord = Math.min(currentPage * recordsPerPage, totalRecords);
    document.getElementById('paginationInfo').textContent = 
        `Showing ${startRecord}-${endRecord} of ${totalRecords} records`;
    
    // Update pagination controls
    const paginationControls = document.getElementById('paginationControls');
    paginationControls.innerHTML = '';
    
    // Previous button
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${!pagination.has_prev ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a>`;
    paginationControls.appendChild(prevLi);
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        const firstLi = document.createElement('li');
        firstLi.className = 'page-item';
        firstLi.innerHTML = '<a class="page-link" href="#" data-page="1">1</a>';
        paginationControls.appendChild(firstLi);
        
        if (startPage > 2) {
            const ellipsisLi = document.createElement('li');
            ellipsisLi.className = 'page-item disabled';
            ellipsisLi.innerHTML = '<span class="page-link">...</span>';
            paginationControls.appendChild(ellipsisLi);
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageLi = document.createElement('li');
        pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
        pageLi.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
        paginationControls.appendChild(pageLi);
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            const ellipsisLi = document.createElement('li');
            ellipsisLi.className = 'page-item disabled';
            ellipsisLi.innerHTML = '<span class="page-link">...</span>';
            paginationControls.appendChild(ellipsisLi);
        }
        
        const lastLi = document.createElement('li');
        lastLi.className = 'page-item';
        lastLi.innerHTML = `<a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a>`;
        paginationControls.appendChild(lastLi);
    }
    
    // Next button
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${!pagination.has_next ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#" data-page="${currentPage + 1}">Next</a>`;
    paginationControls.appendChild(nextLi);
    
    // Add click event listeners
    paginationControls.addEventListener('click', handlePaginationClick);
}

function handlePaginationClick(event) {
    event.preventDefault();
    
    if (event.target.classList.contains('page-link') && !event.target.closest('.disabled')) {
        const page = parseInt(event.target.getAttribute('data-page'));
        if (page && page !== currentPage) {
            loadPaginatedData(page, recordsPerPage);
        }
    }
}

function showPaginationContainer() {
    const container = document.getElementById('paginationContainer');
    container.style.display = 'flex';
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
            <div class="col-md-3">
                <strong>Retention Time:</strong><br>
                ${pressureInfo.retention_time.toFixed(2)} minutes
            </div>
            <div class="col-md-3">
                <strong>Pressure (bar):</strong><br>
                ${pressureInfo.pressure_bar.toFixed(6)}
            </div>
            <div class="col-md-3">
                <strong>Pressure (mbar):</strong><br>
                ${pressureInfo.pressure_mbar.toFixed(4)}
            </div>
            <div class="col-md-3">
                <strong>Pressure (Torr):</strong><br>
                ${pressureInfo.pressure_torr.toFixed(4)}
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