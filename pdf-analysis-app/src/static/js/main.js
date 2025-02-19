// main.js

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const resultContainer = document.getElementById('result-container');

    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData(uploadForm);
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    function displayResults(data) {
        resultContainer.innerHTML = '';
        if (data.success) {
            const analysisResults = document.createElement('div');
            analysisResults.innerHTML = `<h3>Analysis Results:</h3><pre>${JSON.stringify(data.results, null, 2)}</pre>`;
            resultContainer.appendChild(analysisResults);
        } else {
            resultContainer.innerHTML = '<p>Error analyzing the PDF. Please try again.</p>';
        }
    }
});