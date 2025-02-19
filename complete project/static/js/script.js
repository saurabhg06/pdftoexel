// DOM elements
const uploadForm = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const convertBtn = document.getElementById('convert-btn');
const statusMsg = document.getElementById('status-message');
const downloadLink = document.getElementById('download-link');

// Event listeners
uploadForm.addEventListener('submit', handleFormSubmit);
fileInput.addEventListener('change', handleFileSelect);

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (!fileInput.files[0]) {
        showStatus('Please select a PDF file first.', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('pdf_file', fileInput.files[0]);

    showStatus('Converting...', 'info');
    convertBtn.disabled = true;

    try {
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Conversion failed');
        }

        const data = await response.json();
        showStatus('Conversion successful!', 'success');
        downloadLink.href = data.excel_url;
        downloadLink.style.display = 'block';
    } catch (error) {
        showStatus('Error during conversion. Please try again.', 'error');
        console.error('Error:', error);
    } finally {
        convertBtn.disabled = false;
    }
}

// Handle file selection
function handleFileSelect() {
    const file = fileInput.files[0];
    if (file) {
        if (file.type !== 'application/pdf') {
            showStatus('Please select a valid PDF file.', 'error');
            fileInput.value = '';
        } else {
            showStatus('File selected: ' + file.name, 'info');
        }
    }
}

// Show status message
function showStatus(message, type) {
    statusMsg.textContent = message;
    statusMsg.className = 'status-message ' + type;
}