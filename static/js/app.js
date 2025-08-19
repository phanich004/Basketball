// Basketball AI Coach Web App JavaScript
class BasketballCoach {
    constructor() {
        this.currentSessionId = null;
        this.uploadForm = document.getElementById('uploadForm');
        this.fileInput = document.getElementById('videoFile');
        this.fileUploadArea = document.getElementById('fileUploadArea');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.processingStatus = document.getElementById('processingStatus');
        
        this.sections = {
            upload: document.getElementById('uploadSection'),
            processing: document.getElementById('processingSection'),
            results: document.getElementById('resultsSection'),
            error: document.getElementById('errorSection')
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
    }
    
    setupEventListeners() {
        // Form submission
        this.uploadForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleVideoUpload();
        });
        
        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });
        
        // Browse files link
        document.querySelector('.browse-link').addEventListener('click', () => {
            this.fileInput.click();
        });
        
        // Download button
        document.getElementById('downloadBtn')?.addEventListener('click', () => {
            this.downloadVideo();
        });
        
        // Analyze another button
        document.getElementById('analyzeAnotherBtn')?.addEventListener('click', () => {
            this.resetApp();
        });
        
        // Retry button
        document.getElementById('retryBtn')?.addEventListener('click', () => {
            this.resetApp();
        });
    }
    
    setupDragAndDrop() {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.fileUploadArea.addEventListener(eventName, this.preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            this.fileUploadArea.addEventListener(eventName, () => {
                this.fileUploadArea.classList.add('dragover');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            this.fileUploadArea.addEventListener(eventName, () => {
                this.fileUploadArea.classList.remove('dragover');
            }, false);
        });
        
        this.fileUploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        }, false);
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    handleFileSelect(file) {
        if (!file) return;
        
        // Validate file type
        const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime', 'video/x-msvideo'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('Please select a valid video file (MP4, AVI, MOV)');
            return;
        }
        
        // Validate file size (100MB max)
        const maxSize = 100 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('File size must be less than 100MB');
            return;
        }
        
        // Update UI to show selected file
        const placeholder = this.fileUploadArea.querySelector('.upload-placeholder');
        placeholder.innerHTML = `
            <i class="fas fa-video"></i>
            <p><strong>${file.name}</strong></p>
            <small>Size: ${this.formatFileSize(file.size)}</small>
            <p><span class="browse-link">Choose different file</span></p>
        `;
        
        // Enable upload button
        this.uploadBtn.disabled = false;
    }
    
    async handleVideoUpload() {
        const file = this.fileInput.files[0];
        if (!file) {
            this.showError('Please select a video file');
            return;
        }
        
        const apiKey = document.getElementById('apiKey').value.trim();
        
        // Create form data
        const formData = new FormData();
        formData.append('video', file);
        formData.append('api_key', apiKey);
        
        try {
            // Show processing section
            this.showSection('processing');
            this.updateProcessingStep(1, 'active');
            
            // Upload video
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Upload failed');
            }
            
            const result = await response.json();
            this.currentSessionId = result.session_id;
            
            // Start polling for status
            this.pollProcessingStatus();
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Failed to upload video. Please try again.');
        }
    }
    
    async pollProcessingStatus() {
        if (!this.currentSessionId) return;
        
        try {
            const response = await fetch(`/status/${this.currentSessionId}`);
            const status = await response.json();
            
            if (response.ok) {
                this.updateProgress(status);
                
                if (status.status === 'completed') {
                    this.showResults(status);
                } else if (status.status === 'error') {
                    this.showError(status.error || 'Processing failed');
                } else {
                    // Continue polling
                    setTimeout(() => this.pollProcessingStatus(), 2000);
                }
            } else {
                throw new Error('Status check failed');
            }
            
        } catch (error) {
            console.error('Status polling error:', error);
            this.showError('Failed to check processing status');
        }
    }
    
    updateProgress(status) {
        const progress = status.progress || 0;
        this.progressFill.style.width = `${progress}%`;
        this.progressText.textContent = `${Math.round(progress)}%`;
        
        // Update processing steps
        if (progress >= 20) this.updateProcessingStep(1, 'completed');
        if (progress >= 40) this.updateProcessingStep(2, 'active');
        if (progress >= 60) {
            this.updateProcessingStep(2, 'completed');
            this.updateProcessingStep(3, 'active');
        }
        if (progress >= 80) {
            this.updateProcessingStep(3, 'completed');
            this.updateProcessingStep(4, 'active');
        }
        if (progress >= 100) {
            this.updateProcessingStep(4, 'completed');
        }
        
        // Update status message
        if (progress < 20) {
            this.processingStatus.textContent = 'Uploading video...';
        } else if (progress < 40) {
            this.processingStatus.textContent = 'Extracting video frames...';
        } else if (progress < 70) {
            this.processingStatus.textContent = 'Generating AI commentary...';
        } else if (progress < 100) {
            this.processingStatus.textContent = 'Creating final video...';
        } else {
            this.processingStatus.textContent = 'Analysis complete!';
        }
    }
    
    updateProcessingStep(stepNumber, state) {
        const step = document.getElementById(`step${stepNumber}`);
        if (step) {
            step.className = `step ${state}`;
        }
    }
    
    showResults(status) {
        this.showSection('results');
        
        // Set up video preview
        const resultVideo = document.getElementById('resultVideo');
        resultVideo.src = `/preview/${this.currentSessionId}`;
        
        // Set up download button
        const downloadBtn = document.getElementById('downloadBtn');
        downloadBtn.onclick = () => {
            window.open(`/download/${this.currentSessionId}`, '_blank');
        };
        
        // Display commentary insights
        if (status.commentary && status.commentary.length > 0) {
            this.displayCommentaryInsights(status.commentary);
        }
    }
    
    displayCommentaryInsights(commentary) {
        const insightsList = document.getElementById('insightsList');
        insightsList.innerHTML = '';
        
        commentary.forEach((insight, index) => {
            const insightElement = document.createElement('div');
            insightElement.className = 'insight-item';
            insightElement.innerHTML = `
                <div class="insight-timestamp">
                    <i class="fas fa-clock"></i>
                    ${this.formatTimestamp(insight.timestamp)}
                </div>
                <div class="insight-action">
                    <i class="fas fa-basketball-ball"></i>
                    ${insight.action}
                </div>
                <div class="insight-feedback">
                    <i class="fas fa-comment"></i>
                    ${insight.feedback}
                </div>
            `;
            insightsList.appendChild(insightElement);
        });
    }
    
    showSection(sectionName) {
        // Hide all sections
        Object.values(this.sections).forEach(section => {
            section.classList.add('hidden');
        });
        
        // Show target section
        if (this.sections[sectionName]) {
            this.sections[sectionName].classList.remove('hidden');
        }
    }
    
    showError(message) {
        this.showSection('error');
        document.getElementById('errorMessage').textContent = message;
    }
    
    resetApp() {
        // Reset form
        this.uploadForm.reset();
        this.currentSessionId = null;
        
        // Reset file upload area
        const placeholder = this.fileUploadArea.querySelector('.upload-placeholder');
        placeholder.innerHTML = `
            <i class="fas fa-video"></i>
            <p>Drop your basketball video here or <span class="browse-link">browse files</span></p>
            <small>Supports MP4, AVI, MOV, MKV (Max: 100MB)</small>
        `;
        
        // Reset progress
        this.progressFill.style.width = '0%';
        this.progressText.textContent = '0%';
        
        // Reset processing steps
        for (let i = 1; i <= 4; i++) {
            this.updateProcessingStep(i, '');
        }
        
        // Show upload section
        this.showSection('upload');
        
        // Disable upload button
        this.uploadBtn.disabled = true;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatTimestamp(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BasketballCoach();
});

// Add some visual enhancements
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scrolling
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add loading animation to buttons
    const buttons = document.querySelectorAll('.btn, .upload-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            }
        });
    });
});