/**
 * Crop Zen Frontend - Main Script
 * Handles form submission and API communication
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

// API Configuration (use environment variable or default)
const API_CONFIG = {
    BASE_URL: window.ENV?.API_URL || 'http://localhost:5000',
    TIMEOUT: 30000, // 30 seconds
    ENDPOINTS: {
        PREDICT: '/api/predict',
        CROPS: '/api/crops',
        HEALTH: '/health'
    }
};

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

let isLoading = false;

// ============================================================================
// DOM REFERENCES
// ============================================================================

const form = document.getElementById("crop-form");
const resultDiv = document.getElementById("result");
const soilPhInput = document.getElementById("soilPH");
const moistureInput = document.getElementById("moisture");
const imageInput = document.getElementById("image");

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Show loading spinner
 */
function showLoading() {
    isLoading = true;
    resultDiv.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Analyzing soil conditions...</p>
        </div>
    `;
}

/**
 * Hide loading spinner
 */
function hideLoading() {
    isLoading = false;
}

/**
 * Display error message to user
 */
function showError(message, details = null) {
    hideLoading();
    let errorHTML = `
        <div class="result-error">
            <h3>⚠️ Error</h3>
            <p>${escapeHtml(message)}</p>
    `;
    
    if (details) {
        errorHTML += `<details><summary>Details</summary><pre>${escapeHtml(JSON.stringify(details, null, 2))}</pre></details>`;
    }
    
    errorHTML += `</div>`;
    resultDiv.innerHTML = errorHTML;
    resultDiv.style.display = 'block';
}

/**
 * Display success result
 */
function showResult(data) {
    hideLoading();
    
    if (!data || !data.predictions || data.predictions.length === 0) {
        showError("No predictions available");
        return;
    }
    
    const topPrediction = data.predictions[0];
    const alternatives = data.predictions.slice(1);
    
    let resultHTML = `
        <div class="result-card">
            <div class="result-header">
                <h2>🌾 Recommended Crop</h2>
                <div class="confidence-badge">${Math.round(topPrediction.confidence * 100)}% Confidence</div>
            </div>
            
            <div class="result-main">
                <div class="crop-icon">🌱</div>
                <h3>${escapeHtml(topPrediction.crop)}</h3>
            </div>
    `;
    
    if (Array.isArray(topPrediction.reasons) && topPrediction.reasons.length > 0) {
        resultHTML += `
            <div class="reason-section">
                <h4>Why this crop fits</h4>
                <ul>
                    ${topPrediction.reasons.map(reason => `<li>${escapeHtml(reason)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Add alternative crops if available
    if (alternatives.length > 0) {
        resultHTML += `<div class="alternatives"><h4>Alternative Crops:</h4><div class="crop-list">`;
        alternatives.forEach(pred => {
            const widthPercent = Math.round(pred.confidence * 100);
            resultHTML += `
                <div class="crop-item">
                    <span class="crop-name">${escapeHtml(pred.crop)}</span>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${widthPercent}%"></div>
                    </div>
                    <span class="crop-score">${widthPercent}%</span>
                </div>
            `;
        });
        resultHTML += `</div></div>`;
    }
    
    // Add disease detection results if available
    if (data.disease_detection && data.disease_detection.status !== 'skipped') {
        resultHTML += `
            <div class="disease-section">
                <h4>🔬 Disease Detection</h4>
                <p>${escapeHtml(data.disease_detection.message)}</p>
        `;
        if (data.disease_detection.disease) {
            resultHTML += `<p><strong>Disease:</strong> ${escapeHtml(data.disease_detection.disease)}</p>`;
        }
        resultHTML += `</div>`;
    }
    
    resultHTML += `</div>`;
    resultDiv.innerHTML = resultHTML;
    resultDiv.style.display = 'block';
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Validate form inputs
 */
function validateForm() {
    const soilPh = parseFloat(soilPhInput.value);
    const moisture = parseFloat(moistureInput.value);
    
    const errors = [];
    
    if (isNaN(soilPh)) {
        errors.push("Soil pH must be a valid number");
    } else if (soilPh < 3.0 || soilPh > 10.0) {
        errors.push("Soil pH must be between 3.0 and 10.0");
    }
    
    if (isNaN(moisture)) {
        errors.push("Soil moisture must be a valid number");
    } else if (moisture < 0 || moisture > 100) {
        errors.push("Soil moisture must be between 0 and 100%");
    }
    
    if (errors.length > 0) {
        showError(errors.join("<br>"));
        return false;
    }
    
    return true;
}

/**
 * Make API request with timeout and error handling
 */
async function makeAPIRequest(url, options = {}) {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);
        
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
            headers: {
                'Accept': 'application/json',
                ...options.headers
            }
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error(`Request timeout after ${API_CONFIG.TIMEOUT}ms`);
        }
        throw error;
    }
}

/**
 * Build FormData for multipart requests
 */
function buildFormData() {
    const formData = new FormData();
    formData.append("soilPH", soilPhInput.value);
    formData.append("moisture", moistureInput.value);
    
    if (imageInput.files && imageInput.files[0]) {
        formData.append("image", imageInput.files[0]);
    }
    
    return formData;
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

/**
 * Form submission handler
 */
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    // Validate inputs
    if (!validateForm()) {
        return;
    }
    
    // Show loading state
    showLoading();
    
    try {
        // Build request
        const formData = buildFormData();
        const url = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.PREDICT}`;
        
        console.log(`[Crop Zen] Sending prediction request to: ${url}`);
        
        // Make API request
        const data = await makeAPIRequest(url, {
            method: "POST",
            body: formData
        });
        
        console.log("[Crop Zen] Prediction received:", data);
        
        // Display results
        showResult(data);
        
    } catch (error) {
        console.error("[Crop Zen] Error:", error);
        
        let errorMessage = "Failed to get crop recommendation";
        
        if (error.message.includes("Failed to fetch")) {
            errorMessage = "Cannot connect to server. Make sure the backend is running at " + API_CONFIG.BASE_URL;
        } else if (error.message.includes("timeout")) {
            errorMessage = "Request timeout. Server is taking too long to respond.";
        } else if (error.message.includes("HTTP Error")) {
            errorMessage = `Server error: ${error.message}`;
        }
        
        showError(errorMessage, {
            error: error.message,
            endpoint: API_CONFIG.BASE_URL + API_CONFIG.ENDPOINTS.PREDICT,
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * Real-time input validation
 */
soilPhInput.addEventListener("blur", () => {
    const value = parseFloat(soilPhInput.value);
    if (!isNaN(value)) {
        if (value < 3.0) {
            soilPhInput.setCustomValidity("pH too low (minimum 3.0)");
        } else if (value > 10.0) {
            soilPhInput.setCustomValidity("pH too high (maximum 10.0)");
        } else {
            soilPhInput.setCustomValidity("");
        }
    }
});

moistureInput.addEventListener("blur", () => {
    const value = parseFloat(moistureInput.value);
    if (!isNaN(value)) {
        if (value < 0) {
            moistureInput.setCustomValidity("Moisture cannot be negative");
        } else if (value > 100) {
            moistureInput.setCustomValidity("Moisture cannot exceed 100%");
        } else {
            moistureInput.setCustomValidity("");
        }
    }
});

/**
 * File input validation
 */
if (imageInput) {
    imageInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
            const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
            const maxSize = 5 * 1024 * 1024; // 5MB
            
            if (!validTypes.includes(file.type)) {
                imageInput.setCustomValidity("Only JPEG, PNG, and GIF images are allowed");
                imageInput.value = '';
            } else if (file.size > maxSize) {
                imageInput.setCustomValidity("Image size must be less than 5MB");
                imageInput.value = '';
            } else {
                imageInput.setCustomValidity("");
                console.log(`[Crop Zen] Image selected: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`);
            }
        }
    });
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log("[Crop Zen] Frontend initialized");
    console.log(`[Crop Zen] API Base URL: ${API_CONFIG.BASE_URL}`);
    console.log("[Crop Zen] Ready to receive predictions");
});

