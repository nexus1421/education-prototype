// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initImageUpload();
    initScanButton();
});

// Image upload functionality
function initImageUpload() {
    const imageInput = document.getElementById('image-upload');
    const imagePreview = document.getElementById('image-preview');
    const uploadArea = document.getElementById('upload-area');
    const uploadPrompt = document.getElementById('upload-prompt');
    const scanButton = document.getElementById('scan-button');
    
    if (!imageInput || !imagePreview || !uploadArea) return;
    
    // Click to upload
    uploadArea.addEventListener('click', function() {
        imageInput.click();
    });
    
    // File selected
    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        handleImageFile(file);
    });
    
    // Drag and drop functionality
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function() {
        this.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            handleImageFile(e.dataTransfer.files[0]);
        }
    });
    
    function handleImageFile(file) {
        if (!file || !file.type.match('image.*')) {
            alert('Please select an image file (JPEG, PNG, etc.).');
            return;
        }
        
        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('Please select an image smaller than 10MB.');
            return;
        }
        
        const reader = new FileReader();
        
        reader.addEventListener('load', function() {
            imagePreview.src = reader.result;
            imagePreview.style.display = 'block';
            uploadPrompt.style.display = 'none';
            
            if (scanButton) {
                scanButton.disabled = false;
            }
        });
        
        reader.readAsDataURL(file);
    }
}

// Scan button functionality
function initScanButton() {
    const scanButton = document.getElementById('scan-button');
    const resultsContainer = document.getElementById('scan-results');
    const loadingOverlay = document.getElementById('loading');
    
    if (!scanButton) return;
    
    scanButton.addEventListener('click', function() {
        const imagePreview = document.getElementById('image-preview');
        if (!imagePreview || imagePreview.style.display === 'none') {
            alert('Please upload an image first.');
            return;
        }
        
        // Show loading state
        scanButton.disabled = true;
        const originalText = scanButton.textContent;
        scanButton.textContent = 'Scanning...';
        
        if (resultsContainer) {
            resultsContainer.classList.add('hidden');
        }
        
        if (loadingOverlay) {
            loadingOverlay.classList.remove('hidden');
        }
        
        // Convert image to base64 for API
        const imageData = getBase64Image(imagePreview);
        
        // Send to scan API
        fetch('/api/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                displayScanResults(data);
            } else {
                throw new Error(data.error || 'Scan failed');
            }
        })
        .catch(error => {
            alert('Scan failed: ' + error.message);
            console.error('Scan error:', error);
        })
        .finally(() => {
            // Reset button state
            scanButton.disabled = false;
            scanButton.textContent = originalText;
            
            if (loadingOverlay) {
                loadingOverlay.classList.add('hidden');
            }
        });
    });
}

// Convert image to base64
function getBase64Image(img) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    ctx.drawImage(img, 0, 0);
    
    // Get image data as JPEG with reasonable quality
    return canvas.toDataURL('image/jpeg', 0.8);
}

// Display scan results
function displayScanResults(data) {
    const resultsContainer = document.getElementById('scan-results');
    const resultsContent = document.getElementById('results-content');
    
    if (!resultsContainer || !resultsContent) return;
    
    // Clear previous results
    resultsContent.innerHTML = '';
    
    if (data.results.length === 0) {
        resultsContent.innerHTML = `
            <div class="no-results">
                <h3>No environmental elements detected</h3>
                <p>Try scanning plants, animals, bodies of water, or other natural elements.</p>
                <p>Make sure your image is clear and well-lit for best results.</p>
            </div>
        `;
// In the displayScanResults function, add this after displaying results:
if (data.note) {
    const noteElement = document.createElement('div');
    noteElement.className = 'api-note';
    noteElement.innerHTML = `
        <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mt-4">
            <div class="flex">
                <div class="ml-3">
                    <p class="text-sm text-yellow-700">${data.note}</p>
                </div>
            </div>
        </div>
    `;
    resultsContent.appendChild(noteElement);
}
    } else {
        // Add detected concepts
        const conceptsHtml = data.results.map(item => `
            <div class="concept-item">
                <span class="concept-name">${item.concept}</span>
                <span class="confidence">${Math.round(item.score * 100)}% match</span>
            </div>
        `).join('');
        
        // Add educational content
        const educationHtml = data.educational_content.map(item => `
            <div class="education-card">
                <h4>About ${item.concept}</h4>
                <p class="fact">${item.fact}</p>
                <p class="tip"><strong>Eco Tip:</strong> ${item.tip}</p>
            </div>
        `).join('');
        
        resultsContent.innerHTML = `
            <div class="scan-results-section">
                <h3>Detected Environmental Elements</h3>
                <div class="concepts-list">${conceptsHtml}</div>
            </div>
            <div class="education-section">
                <h3>Learn More</h3>
                <div class="education-cards">${educationHtml}</div>
            </div>
        `;
    }
    
    resultsContainer.classList.remove('hidden');
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// Add a global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});