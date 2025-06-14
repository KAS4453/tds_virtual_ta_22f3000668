// TDS Virtual TA - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const questionForm = document.getElementById('questionForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingCard = document.getElementById('loadingCard');
    const responseCard = document.getElementById('responseCard');
    const errorAlert = document.getElementById('errorAlert');
    
    // Load stats on page load
    loadStats();
    
    // Form submission
    questionForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const question = document.getElementById('question').value.trim();
        const imageFile = document.getElementById('imageFile').files[0];
        
        if (!question) {
            showError('Please enter a question');
            return;
        }
        
        await submitQuestion(question, imageFile);
    });
    
    async function submitQuestion(question, imageFile) {
        const startTime = Date.now();
        
        try {
            // Show loading state
            showLoading();
            
            // Prepare request data
            const requestData = { question };
            
            // Convert image to base64 if provided
            if (imageFile) {
                requestData.image = await fileToBase64(imageFile);
            }
            
            // Submit to API
            const response = await fetch('/api/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            const responseTime = Date.now() - startTime;
            
            if (response.ok) {
                showResponse(data, responseTime);
                loadStats(); // Refresh stats
            } else {
                showError(data.error || 'An error occurred');
            }
            
        } catch (error) {
            console.error('Error:', error);
            showError('Network error: ' + error.message);
        } finally {
            hideLoading();
        }
    }
    
    function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                // Remove data URL prefix to get just base64
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
    
    function showLoading() {
        hideAll();
        loadingCard.classList.remove('d-none');
        submitBtn.disabled = true;
    }
    
    function hideLoading() {
        loadingCard.classList.add('d-none');
        submitBtn.disabled = false;
    }
    
    function showResponse(data, responseTime) {
        hideAll();
        
        // Show answer
        document.getElementById('answerText').innerHTML = formatAnswer(data.answer);
        document.getElementById('responseTime').textContent = (responseTime / 1000).toFixed(2) + 's';
        
        // Show links if available
        if (data.links && data.links.length > 0) {
            const linksSection = document.getElementById('linksSection');
            const linksList = document.getElementById('linksList');
            
            linksList.innerHTML = data.links.map(link => `
                <div class="mb-2">
                    <a href="${escapeHtml(link.url)}" target="_blank" class="text-decoration-none">
                        <i class="fas fa-external-link-alt me-2"></i>
                        ${escapeHtml(link.text)}
                    </a>
                </div>
            `).join('');
            
            linksSection.classList.remove('d-none');
        }
        
        responseCard.classList.remove('d-none');
    }
    
    function showError(message) {
        hideAll();
        document.getElementById('errorText').textContent = message;
        errorAlert.classList.remove('d-none');
    }
    
    function hideAll() {
        loadingCard.classList.add('d-none');
        responseCard.classList.add('d-none');
        errorAlert.classList.add('d-none');
    }
    
    function formatAnswer(answer) {
        // Simple text formatting - convert newlines to <br> and preserve spacing
        return escapeHtml(answer).replace(/\n/g, '<br>');
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    async function loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            if (response.ok) {
                document.getElementById('totalQuestions').textContent = stats.total_questions;
                document.getElementById('avgResponseTime').textContent = stats.average_response_time + 's';
                document.getElementById('questionsWithImages').textContent = stats.questions_with_images;
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
});

function showCurlExample() {
    const curlExample = document.getElementById('curlExample');
    curlExample.classList.toggle('d-none');
}
