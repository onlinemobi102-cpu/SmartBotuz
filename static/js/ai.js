// AI Functions for SmartBot.uz
// Handles all AI-related frontend interactions

// Global variables
let chatHistory = [];

// Initialize AI interface
document.addEventListener('DOMContentLoaded', function() {
    initializeAI();
});

function initializeAI() {
    // Add enter key listener for chat input
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
}

// ========================
// AI CHATBOT FUNCTIONS
// ========================

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';
    
    // Show typing indicator
    addTypingIndicator();
    
    try {
        const response = await fetch('/ai/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        if (data.success) {
            addMessageToChat(data.response, 'bot');
        } else {
            addMessageToChat(data.response || 'Xatolik yuz berdi', 'bot');
        }
        
    } catch (error) {
        removeTypingIndicator();
        addMessageToChat('Aloqa xatosi yuz berdi. Iltimos, qaytadan urinib ko\'ring.', 'bot');
        console.error('Chat error:', error);
    }
}

function addMessageToChat(message, sender) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `${sender}-message mb-2`;
    
    if (sender === 'bot') {
        messageDiv.innerHTML = `
            <small class="text-muted">SmartBot AI:</small>
            <div class="bg-light p-2 rounded">${message}</div>
        `;
    } else {
        messageDiv.innerHTML = `
            <small class="text-muted">Siz:</small>
            <div class="bg-primary text-white p-2 rounded ms-auto" style="max-width: 80%;">${message}</div>
        `;
    }
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addTypingIndicator() {
    const chatContainer = document.getElementById('chatContainer');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'bot-message mb-2';
    typingDiv.innerHTML = `
        <small class="text-muted">SmartBot AI:</small>
        <div class="bg-light p-2 rounded">
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// ========================
// BLOG GENERATION FUNCTIONS
// ========================

async function generateBlog() {
    const topicInput = document.getElementById('blogTopic');
    const topic = topicInput.value.trim();
    
    if (!topic) {
        showNotification('Mavzu kiritish majburiy', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/ai/blog', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic: topic })
        });
        
        const data = await response.json();
        hideLoading();
        
        const resultDiv = document.getElementById('blogResult');
        
        if (data.success) {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="fas fa-check me-2"></i>${data.message}</h6>
                    <small class="text-muted">Blog ID: ${data.blog.id}</small>
                </div>
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">${data.blog.title}</h6>
                    </div>
                    <div class="card-body">
                        <div style="max-height: 300px; overflow-y: auto;">
                            ${data.blog.content}
                        </div>
                        <hr>
                        <small class="text-muted">
                            <i class="fas fa-calendar me-1"></i>${data.blog.date} | 
                            <i class="fas fa-tag me-1"></i>${data.blog.category}
                        </small>
                    </div>
                </div>
            `;
            resultDiv.style.display = 'block';
            showNotification('Blog maqolasi muvaffaqiyatli yaratildi!', 'success');
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>${data.message}
                </div>
            `;
            resultDiv.style.display = 'block';
        }
        
    } catch (error) {
        hideLoading();
        showNotification('Blog yaratishda xatolik yuz berdi', 'error');
        console.error('Blog generation error:', error);
    }
}

// ========================
// MESSAGE ANALYSIS FUNCTIONS
// ========================

async function analyzeMessage() {
    const messageInput = document.getElementById('messageText');
    const message = messageInput.value.trim();
    
    if (!message) {
        showNotification('Xabar matnini kiriting', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/ai/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        hideLoading();
        
        const resultDiv = document.getElementById('analysisResult');
        
        if (data.success) {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="fas fa-brain me-2"></i>Tahlil Natijasi</h6>
                </div>
                <div class="card">
                    <div class="card-body">
                        <h6>Tavsiya qilingan xizmat:</h6>
                        <div class="bg-light p-3 rounded mb-3">
                            <h6 class="text-primary mb-1">${data.recommendation.service}</h6>
                            <p class="mb-2">${data.recommendation.description}</p>
                            <a href="${data.recommendation.url}" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-external-link-alt me-1"></i>Ko'proq ma'lumot
                            </a>
                        </div>
                        <small class="text-muted">
                            <strong>AI tahlili:</strong> ${data.analysis}
                        </small>
                    </div>
                </div>
            `;
            resultDiv.style.display = 'block';
            showNotification('Xabar muvaffaqiyatli tahlil qilindi!', 'success');
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>${data.error}
                </div>
            `;
            resultDiv.style.display = 'block';
        }
        
    } catch (error) {
        hideLoading();
        showNotification('Tahlil qilishda xatolik yuz berdi', 'error');
        console.error('Analysis error:', error);
    }
}

// ========================
// CASE STUDY GENERATION FUNCTIONS
// ========================

async function generateCaseStudy() {
    const projectInput = document.getElementById('projectInfo');
    const projectInfo = projectInput.value.trim();
    
    if (!projectInfo) {
        showNotification('Loyiha ma\'lumotlarini kiriting', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/ai/case-study', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ project_info: projectInfo })
        });
        
        const data = await response.json();
        hideLoading();
        
        const resultDiv = document.getElementById('caseStudyResult');
        
        if (data.success) {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="fas fa-check me-2"></i>${data.message}</h6>
                </div>
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Case Study</h6>
                    </div>
                    <div class="card-body">
                        <div style="max-height: 400px; overflow-y: auto;">
                            <div class="case-study-content">
                                ${data.case_study.split('\n').map(line => `<p>${line}</p>`).join('')}
                            </div>
                        </div>
                        <hr>
                        <button class="btn btn-sm btn-secondary" onclick="copyToClipboard('${data.case_study.replace(/'/g, "\\'")}')">
                            <i class="fas fa-copy me-1"></i>Nusxalash
                        </button>
                    </div>
                </div>
            `;
            resultDiv.style.display = 'block';
            showNotification('Case study muvaffaqiyatli yaratildi!', 'success');
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>${data.message}
                </div>
            `;
            resultDiv.style.display = 'block';
        }
        
    } catch (error) {
        hideLoading();
        showNotification('Case study yaratishda xatolik yuz berdi', 'error');
        console.error('Case study error:', error);
    }
}

// ========================
// DOCUMENT ANALYSIS FUNCTIONS
// ========================

async function analyzeDocument() {
    const fileInput = document.getElementById('documentFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Fayl tanlang', 'error');
        return;
    }
    
    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showNotification('Fayl hajmi 10MB dan kichik bo\'lishi kerak', 'error');
        return;
    }
    
    showLoading();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/ai/document', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        hideLoading();
        
        const resultDiv = document.getElementById('documentResult');
        
        if (data.success) {
            let content = `
                <div class="alert alert-success">
                    <h6><i class="fas fa-file me-2"></i>Hujjat tahlili</h6>
                </div>
                <div class="card">
                    <div class="card-body">
                        <h6>Fayl turi: ${data.file_type}</h6>
            `;
            
            if (data.extracted_text) {
                content += `
                    <h6>Ajratilgan matn:</h6>
                    <div class="bg-light p-2 rounded mb-3" style="max-height: 150px; overflow-y: auto;">
                        <small>${data.extracted_text}</small>
                    </div>
                `;
            }
            
            content += `
                        <h6>AI tahlili:</h6>
                        <div class="bg-primary bg-opacity-10 p-3 rounded">
                            ${data.analysis}
                        </div>
                    </div>
                </div>
            `;
            
            resultDiv.innerHTML = content;
            resultDiv.style.display = 'block';
            showNotification('Hujjat muvaffaqiyatli tahlil qilindi!', 'success');
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>${data.message || data.error}
                </div>
            `;
            resultDiv.style.display = 'block';
        }
        
    } catch (error) {
        hideLoading();
        showNotification('Hujjat tahlilida xatolik yuz berdi', 'error');
        console.error('Document analysis error:', error);
    }
}

// ========================
// UTILITY FUNCTIONS
// ========================

function showLoading() {
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    loadingModal.show();
}

function hideLoading() {
    const loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
    if (loadingModal) {
        loadingModal.hide();
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 100px; right: 20px; z-index: 9999; min-width: 300px; max-width: 400px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Matn nusxalandi!', 'success');
    }).catch(() => {
        showNotification('Nusxalashda xatolik yuz berdi', 'error');
    });
}

// CSS for typing animation
const style = document.createElement('style');
style.textContent = `
    .typing-dots {
        display: inline-flex;
        align-items: center;
    }
    
    .typing-dots span {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #6c757d;
        margin: 0 1px;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { 
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% { 
            transform: scale(1);
            opacity: 1;
        }
    }
    
    .case-study-content p {
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }
`;
document.head.appendChild(style);