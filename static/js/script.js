// SmartBot.uz Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initSmoothScrolling();
    initCounterAnimation();
    initNavbarEffects();
    initPortfolioFilter();
    initBlogFilter();
    initFormValidation();
    initLoadingStates();
    initTooltips();
    initAnimationOnScroll();
});

// Smooth Scrolling for Anchor Links
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const headerOffset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Counter Animation
function initCounterAnimation() {
    const counters = document.querySelectorAll('.counter');
    
    const animateCounter = (counter) => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const stepTime = Math.abs(Math.floor(duration / target));
        let current = 0;
        
        const timer = setInterval(() => {
            current += Math.ceil(target / 50);
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = current + (target === 24 ? '/7' : '+');
        }, stepTime);
    };

    // Intersection Observer for counter animation
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => {
        counterObserver.observe(counter);
    });
}

// Navbar Effects
function initNavbarEffects() {
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Add shadow on scroll
        if (scrollTop > 50) {
            navbar.classList.add('shadow');
        } else {
            navbar.classList.remove('shadow');
        }
        
        // Hide/show navbar on scroll (optional)
        if (scrollTop > lastScrollTop && scrollTop > 200) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    });
}

// Portfolio Filter
function initPortfolioFilter() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const portfolioItems = document.querySelectorAll('.portfolio-item');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Update active button
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const filter = this.getAttribute('data-filter');

            // Filter portfolio items with animation
            portfolioItems.forEach((item, index) => {
                setTimeout(() => {
                    if (filter === 'all' || item.getAttribute('data-category') === filter) {
                        item.style.display = 'block';
                        item.classList.add('fade-in');
                        setTimeout(() => item.classList.remove('fade-in'), 600);
                    } else {
                        item.style.display = 'none';
                    }
                }, index * 50);
            });
        });
    });
}

// Blog Filter
function initBlogFilter() {
    const categoryBtns = document.querySelectorAll('.category-btn');
    const blogItems = document.querySelectorAll('.blog-item');

    categoryBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Update active button
            categoryBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const category = this.getAttribute('data-category');

            // Filter blog items with staggered animation
            blogItems.forEach((item, index) => {
                setTimeout(() => {
                    if (category === 'all' || item.getAttribute('data-category') === category) {
                        item.style.display = 'block';
                        item.classList.add('fade-in');
                        setTimeout(() => item.classList.remove('fade-in'), 600);
                    } else {
                        item.style.display = 'none';
                    }
                }, index * 30);
            });
        });
    });
}

// Form Validation and Enhancement
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Phone number formatting
        const phoneInput = form.querySelector('input[type="tel"]');
        if (phoneInput) {
            phoneInput.addEventListener('input', function() {
                let value = this.value.replace(/\D/g, '');
                if (value.startsWith('998')) {
                    value = '+998 ' + value.slice(3, 5) + ' ' + value.slice(5, 8) + ' ' + value.slice(8, 10) + ' ' + value.slice(10, 12);
                }
                this.value = value;
            });
        }
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
        
        // Form submission
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showNotification('Iltimos, barcha maydonlarni to\'g\'ri to\'ldiring.', 'error');
                return;
            }
            
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Yuborilmoqda...';
                submitBtn.disabled = true;
                
                // Re-enable after form processes (handled by Flask)
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    });
}

// Field validation function
function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        errorMessage = 'Bu maydon majburiy';
        isValid = false;
    }
    
    // Email validation
    if (type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            errorMessage = 'Email manzili noto\'g\'ri';
            isValid = false;
        }
    }
    
    // Phone validation
    if (type === 'tel' && value) {
        const phoneRegex = /^\+998\s\d{2}\s\d{3}\s\d{2}\s\d{2}$/;
        if (!phoneRegex.test(value)) {
            errorMessage = 'Telefon raqami noto\'g\'ri formatda';
            isValid = false;
        }
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

// Show field error
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

// Clear field error
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Loading States
function initLoadingStates() {
    const loadMoreBtn = document.getElementById('loadMore');
    
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Yuklanmoqda...';
            this.disabled = true;
            
            // Simulate loading
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-check me-2"></i>Barcha maqolalar yuklandi';
                this.classList.replace('btn-outline-primary', 'btn-success');
            }, 2000);
        });
    }
}

// Initialize Tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Animation on Scroll
function initAnimationOnScroll() {
    const animatedElements = document.querySelectorAll('.feature-card, .service-card, .team-card, .why-choose-card');
    
    const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                animationObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    animatedElements.forEach(element => {
        animationObserver.observe(element);
    });
}

// Notification System
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
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

// Newsletter Subscription
function initNewsletterSubscription() {
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[type="email"]').value;
            
            if (email) {
                // Show loading state
                const submitBtn = this.querySelector('button[type="submit"]');
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Obuna bo\'linyapti...';
                submitBtn.disabled = true;
                
                // Simulate API call
                setTimeout(() => {
                    showNotification('Obuna uchun rahmat! Tez orada yangiliklar yuboramiz.', 'success');
                    this.reset();
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 2000);
            }
        });
    }
}

// Initialize newsletter after DOM load
document.addEventListener('DOMContentLoaded', function() {
    initNewsletterSubscription();
});

// Scroll to Top Functionality
function initScrollToTop() {
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.className = 'btn btn-primary position-fixed';
    scrollBtn.style.cssText = 'bottom: 20px; right: 20px; z-index: 999; border-radius: 50%; width: 50px; height: 50px; display: none;';
    scrollBtn.setAttribute('aria-label', 'Yuqoriga chiqish');
    
    document.body.appendChild(scrollBtn);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    });
    
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Initialize scroll to top
document.addEventListener('DOMContentLoaded', function() {
    initScrollToTop();
});

// Performance Optimization
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Optimize scroll events
window.addEventListener('scroll', debounce(function() {
    // Scroll-dependent functions can be called here
}, 10));

// Preload critical images
function preloadImages() {
    const imageUrls = [
        // Add any critical image URLs here
    ];
    
    imageUrls.forEach(url => {
        const img = new Image();
        img.src = url;
    });
}

// Initialize preloading
document.addEventListener('DOMContentLoaded', function() {
    preloadImages();
});

// Handle form submission with AJAX (for better UX)
function handleAjaxForm(form) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const action = this.action || window.location.href;
        
        fetch(action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                this.reset();
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            showNotification('Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.', 'error');
        });
    });
}

// Error Handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // You can add error reporting here
});

// Handle offline/online status
window.addEventListener('online', function() {
    showNotification('Internet aloqasi tiklandi', 'success');
});

window.addEventListener('offline', function() {
    showNotification('Internet aloqasi yo\'q', 'warning');
});
