// Mobile Navigation
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Close mobile menu when clicking on links
document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', () => {
    hamburger.classList.remove('active');
    navMenu.classList.remove('active');
}));

// Detection Page Functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const resultsContainer = document.getElementById('resultsContainer');
    const loadingElement = document.getElementById('loading');
    
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('drop', handleFileDrop);
        
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    function handleDragOver(e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#FF6B6B';
        uploadArea.style.background = '#f0f8ff';
    }
    
    function handleFileDrop(e) {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            processFile(files[0]);
        }
    }
    
    function handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            processFile(files[0]);
        }
    }
    
    function processFile(file) {
        // Show loading
        loadingElement.style.display = 'block';
        resultsContainer.innerHTML = '';
        
        const formData = new FormData();
        formData.append('file', file);
        
        fetch('/analyze_prescription', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingElement.style.display = 'none';
            displayResults(data);
        })
        .catch(error => {
            loadingElement.style.display = 'none';
            console.error('Error:', error);
            alert('Error processing file. Please try again.');
        });
    }
    
    function displayResults(data) {
        if (data.error) {
            resultsContainer.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Error</h3>
                    <p>${data.error}</p>
                </div>
            `;
            return;
        }
        
        const { prescription_analysis, diet_recommendations } = data;
        
        let resultsHTML = `
            <div class="results-header">
                <h2><i class="fas fa-file-medical-alt"></i> Prescription Analysis Complete!</h2>
                <p>Here's what we found in your dog's prescription:</p>
            </div>
        `;
        
        // Prescription Analysis
        if (prescription_analysis.medications.length > 0) {
            resultsHTML += `
                <div class="result-section">
                    <h3><i class="fas fa-pills"></i> Medications Detected</h3>
                    <div class="medications-grid">
                        ${prescription_analysis.medications.map(med => `
                            <div class="medication-card">
                                <h4>${med.name}</h4>
                                <span class="med-category">${med.category}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // Diet Recommendations
        if (diet_recommendations) {
            resultsHTML += `
                <div class="result-section">
                    <h3><i class="fas fa-utensils"></i> Tailored Diet Plan</h3>
                    
                    <div class="diet-section">
                        <h4><i class="fas fa-heart"></i> General Recommendations</h4>
                        <ul>
                            ${diet_recommendations.general_recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div class="diet-section">
                        <h4><i class="fas fa-thumbs-up"></i> Recommended Foods</h4>
                        <div class="food-grid">
                            ${diet_recommendations.food_suggestions.map(food => `
                                <div class="food-item">
                                    <i class="fas fa-check"></i>
                                    <span>${food}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    ${diet_recommendations.foods_to_avoid.length > 0 ? `
                    <div class="diet-section">
                        <h4><i class="fas fa-ban"></i> Foods to Avoid</h4>
                        <div class="food-grid">
                            ${diet_recommendations.foods_to_avoid.map(food => `
                                <div class="food-item avoid">
                                    <i class="fas fa-times"></i>
                                    <span>${food}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    <div class="diet-section">
                        <h4><i class="fas fa-clock"></i> Feeding Schedule</h4>
                        <div class="schedule-grid">
                            ${Object.entries(diet_recommendations.feeding_schedule).map(([time, desc]) => `
                                <div class="schedule-item">
                                    <strong>${time}:</strong> ${desc}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        }
        
        resultsContainer.innerHTML = resultsHTML;
    }
});

// Add some interactive animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe all feature cards and sections
    document.querySelectorAll('.feature-card, .result-section').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});
// Enhanced JavaScript for additional functionality

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form validation enhancement
function enhanceFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea');
        
        inputs.forEach(input => {
            // Add real-time validation
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    switch(field.type) {
        case 'email':
            if (!isValidEmail(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
            break;
        case 'text':
            if (field.required && value === '') {
                isValid = false;
                errorMessage = 'This field is required';
            }
            break;
        case 'textarea':
            if (field.required && value === '') {
                isValid = false;
                errorMessage = 'This field is required';
            }
            break;
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.style.borderColor = '#dc3545';
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.5rem';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.style.borderColor = '#e0e0e0';
    
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

// FAQ accordion functionality
function initFAQAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('h3');
        const answer = item.querySelector('p');
        
        // Initially hide answers
        answer.style.display = 'none';
        
        question.style.cursor = 'pointer';
        question.addEventListener('click', () => {
            const isVisible = answer.style.display === 'block';
            
            // Close all other FAQ items
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.querySelector('p').style.display = 'none';
                    otherItem.querySelector('i').className = 'fas fa-question-circle';
                }
            });
            
            // Toggle current item
            if (isVisible) {
                answer.style.display = 'none';
                question.querySelector('i').className = 'fas fa-question-circle';
            } else {
                answer.style.display = 'block';
                question.querySelector('i').className = 'fas fa-chevron-down';
            }
        });
    });
}

// Typing animation for hero text
function initTypingAnimation() {
    const heroText = document.querySelector('.hero h1');
    if (heroText) {
        const text = heroText.textContent;
        heroText.textContent = '';
        let i = 0;
        
        function typeWriter() {
            if (i < text.length) {
                heroText.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            }
        }
        
        // Start typing after a short delay
        setTimeout(typeWriter, 1000);
    }
}

// Parallax effect for hero sections
function initParallax() {
    const heroes = document.querySelectorAll('.hero, .about-hero, .contact-hero');
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        
        heroes.forEach(hero => {
            const rate = scrolled * -0.5;
            hero.style.transform = `translate3d(0px, ${rate}px, 0px)`;
        });
    });
}

// Initialize all enhancements when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    enhanceFormValidation();
    initFAQAccordion();
    initTypingAnimation();
    initParallax();
    
    // Add loading animation to images
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('load', function() {
            this.style.opacity = '1';
            this.style.transform = 'scale(1)';
        });
        
        img.style.opacity = '0';
        img.style.transform = 'scale(0.9)';
        img.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });
    
    // Add intersection observer for animated elements
    const animatedElements = document.querySelectorAll('.feature-card, .team-member, .value-card, .faq-item, .support-option');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(el => {
        el.style.animation = 'fadeInUp 0.6s ease forwards';
        el.style.animationPlayState = 'paused';
        observer.observe(el);
    });
});

// Utility function for debouncing
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

// Enhanced file upload with progress (for future implementation)
function enhanceFileUpload() {
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Show file info
                const fileInfo = document.createElement('div');
                fileInfo.className = 'file-info';
                fileInfo.innerHTML = `
                    <i class="fas fa-file"></i>
                    <span>${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                    <i class="fas fa-check"></i>
                `;
                
                const uploadArea = document.getElementById('uploadArea');
                const existingInfo = uploadArea.querySelector('.file-info');
                if (existingInfo) {
                    existingInfo.remove();
                }
                
                uploadArea.appendChild(fileInfo);
            }
        });
    }
}

// Initialize file upload enhancement
document.addEventListener('DOMContentLoaded', enhanceFileUpload);