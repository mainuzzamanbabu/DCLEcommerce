/**
 * DCL E-Commerce - Main JavaScript
 * Interactive functionality for the premium e-commerce experience
 */

'use strict';

// ===== GLOBAL STATE =====
const DCL = {
    cart: JSON.parse(localStorage.getItem('dcl_cart')) || [],
    wishlist: JSON.parse(localStorage.getItem('dcl_wishlist')) || [],
    isLoggedIn: false
};

// ===== DOM READY =====
document.addEventListener('DOMContentLoaded', function() {
    initPageLoader();
    initNavbar();
    initScrollAnimations();
    initBackToTop();
    initProductCards();
    initCartFunctionality();
    initWishlist();
    initQuantitySelectors();
    initSearchToggle();
    initMobileMenu();
    initFormValidation();
    initTooltips();
    initSmoothScroll();
    initParallax();
    initCounters();
    updateCartCount();
});

// ===== PAGE LOADER =====
function initPageLoader() {
    const loader = document.querySelector('.page-loader');
    if (loader) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                loader.classList.add('loaded');
                document.body.classList.add('loaded');
            }, 500);
        });
    }
}

// ===== NAVBAR =====
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    const scrollThreshold = 50;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        // Add scrolled class for slight style change
        if (currentScroll > scrollThreshold) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        // Navbar always stays visible - no hide on scroll
    });
}

// ===== SCROLL ANIMATIONS =====
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('[data-animate]');
    
    if (!animatedElements.length) return;
    
    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -100px 0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    animatedElements.forEach(el => observer.observe(el));
}

// ===== BACK TO TOP =====
function initBackToTop() {
    const backToTopBtn = document.querySelector('.back-to-top');
    if (!backToTopBtn) return;
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 500) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });
    
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ===== PRODUCT CARDS =====
function initProductCards() {
    // Quick view buttons
    const quickViewBtns = document.querySelectorAll('.quick-view-btn');
    quickViewBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const productId = btn.dataset.productId;
            openQuickView(productId);
        });
    });
    
    // Add to cart buttons on product cards
    const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');
    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const productId = btn.dataset.productId;
            const productName = btn.dataset.productName;
            const productPrice = parseFloat(btn.dataset.productPrice);
            const productImage = btn.dataset.productImage;
            
            addToCart({
                id: productId,
                name: productName,
                price: productPrice,
                image: productImage,
                quantity: 1
            });
            
            // Visual feedback
            showAddedAnimation(btn);
        });
    });
}

// ===== CART FUNCTIONALITY =====
function initCartFunctionality() {
    // Cart page specific functionality
    const cartItemRemoveBtns = document.querySelectorAll('.cart-item-remove');
    cartItemRemoveBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = btn.dataset.productId;
            removeFromCart(productId);
            
            // Animate removal
            const cartItem = btn.closest('.cart-item');
            if (cartItem) {
                cartItem.style.animation = 'slideOutRight 0.3s ease forwards';
                setTimeout(() => cartItem.remove(), 300);
            }
        });
    });
}

function addToCart(product) {
    const existingItem = DCL.cart.find(item => item.id === product.id);
    
    if (existingItem) {
        existingItem.quantity += product.quantity;
    } else {
        DCL.cart.push(product);
    }
    
    saveCart();
    updateCartCount();
    showNotification(`${product.name} added to cart!`, 'success');
}

function removeFromCart(productId) {
    DCL.cart = DCL.cart.filter(item => item.id !== productId);
    saveCart();
    updateCartCount();
    showNotification('Item removed from cart', 'info');
}

function updateCartQuantity(productId, quantity) {
    const item = DCL.cart.find(item => item.id === productId);
    if (item) {
        item.quantity = Math.max(1, quantity);
        saveCart();
        updateCartCount();
    }
}

function saveCart() {
    localStorage.setItem('dcl_cart', JSON.stringify(DCL.cart));
}

function updateCartCount() {
    const cartCountElements = document.querySelectorAll('.cart-count');
    const totalCount = DCL.cart.reduce((sum, item) => sum + item.quantity, 0);
    
    cartCountElements.forEach(el => {
        el.textContent = totalCount;
        if (totalCount > 0) {
            el.style.display = 'flex';
            el.classList.add('animate-bounceIn');
        } else {
            el.style.display = 'none';
        }
    });
}

function getCartTotal() {
    return DCL.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}

// ===== WISHLIST =====
function initWishlist() {
    const wishlistBtns = document.querySelectorAll('.wishlist-btn');
    
    wishlistBtns.forEach(btn => {
        const productId = btn.dataset.productId;
        
        // Check if already in wishlist
        if (DCL.wishlist.includes(productId)) {
            btn.classList.add('active');
        }
        
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleWishlist(productId, btn);
        });
    });
}

function toggleWishlist(productId, btn) {
    const index = DCL.wishlist.indexOf(productId);
    
    if (index > -1) {
        DCL.wishlist.splice(index, 1);
        btn.classList.remove('active');
        showNotification('Removed from wishlist', 'info');
    } else {
        DCL.wishlist.push(productId);
        btn.classList.add('active');
        btn.classList.add('animate-heartbeat');
        setTimeout(() => btn.classList.remove('animate-heartbeat'), 500);
        showNotification('Added to wishlist!', 'success');
    }
    
    localStorage.setItem('dcl_wishlist', JSON.stringify(DCL.wishlist));
}

// ===== QUANTITY SELECTORS =====
function initQuantitySelectors() {
    const quantitySelectors = document.querySelectorAll('.quantity-selector');
    
    quantitySelectors.forEach(selector => {
        const minusBtn = selector.querySelector('.qty-minus');
        const plusBtn = selector.querySelector('.qty-plus');
        const input = selector.querySelector('.qty-input');
        
        if (!minusBtn || !plusBtn || !input) return;
        
        minusBtn.addEventListener('click', () => {
            const currentVal = parseInt(input.value) || 1;
            if (currentVal > 1) {
                input.value = currentVal - 1;
                input.dispatchEvent(new Event('change'));
            }
        });
        
        plusBtn.addEventListener('click', () => {
            const currentVal = parseInt(input.value) || 1;
            const maxVal = parseInt(input.max) || 99;
            if (currentVal < maxVal) {
                input.value = currentVal + 1;
                input.dispatchEvent(new Event('change'));
            }
        });
        
        input.addEventListener('change', () => {
            const productId = selector.dataset.productId;
            if (productId) {
                updateCartQuantity(productId, parseInt(input.value));
            }
        });
    });
}

// ===== SEARCH TOGGLE =====
function initSearchToggle() {
    const searchToggle = document.querySelector('.search-toggle');
    const searchOverlay = document.querySelector('.search-overlay');
    const searchClose = document.querySelector('.search-close');
    const searchInput = document.querySelector('.search-overlay input');
    
    if (!searchToggle || !searchOverlay) return;
    
    searchToggle.addEventListener('click', () => {
        searchOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        setTimeout(() => searchInput?.focus(), 300);
    });
    
    if (searchClose) {
        searchClose.addEventListener('click', () => {
            searchOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Close on ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
            searchOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}

// ===== MOBILE MENU =====
function initMobileMenu() {
    const menuToggle = document.querySelector('.navbar-toggler');
    const mobileMenu = document.querySelector('.navbar-collapse');
    
    if (!menuToggle || !mobileMenu) return;
    
    menuToggle.addEventListener('click', () => {
        mobileMenu.classList.toggle('show');
        menuToggle.classList.toggle('active');
    });
    
    // Close menu when clicking on a link
    const menuLinks = mobileMenu.querySelectorAll('.nav-link');
    menuLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('show');
            menuToggle.classList.remove('active');
        });
    });
}

// ===== FORM VALIDATION =====
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation feedback
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                validateInput(input);
            });
            
            input.addEventListener('input', () => {
                if (form.classList.contains('was-validated')) {
                    validateInput(input);
                }
            });
        });
    });
}

function validateInput(input) {
    if (input.checkValidity()) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
    }
}

// ===== PASSWORD STRENGTH =====
function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/)) strength++;
    if (password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;
    
    return strength;
}

function updatePasswordStrengthMeter(password, meterElement) {
    const strength = checkPasswordStrength(password);
    const percentage = (strength / 5) * 100;
    
    meterElement.style.width = `${percentage}%`;
    
    if (strength <= 1) {
        meterElement.className = 'password-strength-meter weak';
    } else if (strength <= 3) {
        meterElement.className = 'password-strength-meter medium';
    } else {
        meterElement.className = 'password-strength-meter strong';
    }
}

// ===== TOOLTIPS =====
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip-custom animate-fadeIn';
            tooltip.textContent = el.dataset.tooltip;
            document.body.appendChild(tooltip);
            
            const rect = el.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
            tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
        });
        
        el.addEventListener('mouseleave', () => {
            const tooltip = document.querySelector('.tooltip-custom');
            if (tooltip) tooltip.remove();
        });
    });
}

// ===== SMOOTH SCROLL =====
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ===== PARALLAX =====
function initParallax() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    
    if (!parallaxElements.length) return;
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        
        parallaxElements.forEach(el => {
            const speed = el.dataset.parallax || 0.5;
            const offset = scrolled * speed;
            el.style.transform = `translateY(${offset}px)`;
        });
    });
}

// ===== ANIMATED COUNTERS =====
function initCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    
    if (!counters.length) return;
    
    const observerOptions = {
        root: null,
        threshold: 0.5
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
    const target = parseInt(element.dataset.counter);
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    
    const updateCounter = () => {
        current += step;
        if (current < target) {
            element.textContent = Math.floor(current).toLocaleString();
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target.toLocaleString();
        }
    };
    
    updateCounter();
}

// ===== NOTIFICATIONS =====
function showNotification(message, type = 'info') {
    // Remove existing notifications
    document.querySelectorAll('.notification-toast').forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification-toast notification-${type} animate-slideInRight`;
    
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    
    notification.innerHTML = `
        <span class="notification-icon">${icons[type] || icons.info}</span>
        <span class="notification-message">${message}</span>
        <button class="notification-close">×</button>
    `;
    
    document.body.appendChild(notification);
    
    // Close button
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.classList.add('animate-slideOutRight');
        setTimeout(() => notification.remove(), 300);
    });
    
    // Auto remove
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.add('animate-slideOutRight');
            setTimeout(() => notification.remove(), 300);
        }
    }, 3000);
}

// ===== QUICK VIEW MODAL =====
function openQuickView(productId) {
    // This would typically fetch product data and show a modal
    console.log('Quick view for product:', productId);
    // Implementation depends on modal library or custom modal
}

// ===== ANIMATION HELPERS =====
function showAddedAnimation(button) {
    const originalContent = button.innerHTML;
    button.innerHTML = '<span class="animate-scaleIn">✓ Added</span>';
    button.classList.add('btn-success');
    button.disabled = true;
    
    setTimeout(() => {
        button.innerHTML = originalContent;
        button.classList.remove('btn-success');
        button.disabled = false;
    }, 1500);
}

// ===== IMAGE GALLERY =====
function initImageGallery(container) {
    const mainImage = container.querySelector('.main-image');
    const thumbnails = container.querySelectorAll('.thumbnail');
    
    if (!mainImage || !thumbnails.length) return;
    
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', () => {
            // Remove active class from all thumbnails
            thumbnails.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked thumbnail
            thumb.classList.add('active');
            
            // Update main image with fade effect
            mainImage.style.opacity = '0';
            setTimeout(() => {
                mainImage.src = thumb.dataset.fullImage || thumb.src;
                mainImage.style.opacity = '1';
            }, 200);
        });
    });
    
    // Image zoom on hover
    mainImage.addEventListener('mousemove', (e) => {
        const rect = mainImage.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        mainImage.style.transformOrigin = `${x}% ${y}%`;
    });
    
    mainImage.addEventListener('mouseenter', () => {
        mainImage.style.transform = 'scale(1.5)';
    });
    
    mainImage.addEventListener('mouseleave', () => {
        mainImage.style.transform = 'scale(1)';
    });
}

// ===== UTILITIES =====

// Format currency
function formatCurrency(amount, currency = 'BDT') {
    return new Intl.NumberFormat('en-BD', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Debounce function
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

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ===== NOTIFICATION STYLES (Injected) =====
const notificationStyles = `
    .notification-toast {
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 16px 24px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 9999;
        max-width: 400px;
    }
    
    .notification-success {
        border-left: 4px solid #10b981;
    }
    
    .notification-error {
        border-left: 4px solid #ef4444;
    }
    
    .notification-warning {
        border-left: 4px solid #f59e0b;
    }
    
    .notification-info {
        border-left: 4px solid #3b82f6;
    }
    
    .notification-icon {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: bold;
    }
    
    .notification-success .notification-icon { color: #10b981; }
    .notification-error .notification-icon { color: #ef4444; }
    .notification-warning .notification-icon { color: #f59e0b; }
    .notification-info .notification-icon { color: #3b82f6; }
    
    .notification-message {
        flex: 1;
        font-size: 14px;
        color: #1e293b;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        color: #94a3b8;
        padding: 0;
        line-height: 1;
    }
    
    .notification-close:hover {
        color: #1e293b;
    }
    
    .animate-slideInRight {
        animation: slideInRight 0.4s ease-out forwards;
    }
    
    .animate-slideOutRight {
        animation: slideOutRight 0.3s ease-in forwards;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .tooltip-custom {
        position: fixed;
        background: #1e293b;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        z-index: 9999;
        pointer-events: none;
    }
    
    .tooltip-custom::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border: 6px solid transparent;
        border-top-color: #1e293b;
    }
`;

// Inject notification styles
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// ===== EXPORT FOR MODULE USE =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DCL,
        addToCart,
        removeFromCart,
        updateCartQuantity,
        toggleWishlist,
        showNotification,
        formatCurrency
    };
}
