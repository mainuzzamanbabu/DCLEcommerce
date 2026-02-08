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
document.addEventListener('DOMContentLoaded', function () {
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
    initCartPage();
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
    const isSolid = navbar.classList.contains('navbar-solid');

    const handleScroll = () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > scrollThreshold || isSolid) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Initialize on load
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
    // Use event delegation for buttons that might be loaded via AJAX
    document.addEventListener('click', (e) => {
        // Quick view buttons
        const quickViewBtn = e.target.closest('.quick-view-btn');
        if (quickViewBtn) {
            e.preventDefault();
            e.stopPropagation();
            const productId = quickViewBtn.dataset.productId;
            openQuickView(productId);
            return;
        }

        // Add to cart buttons
        const addToCartBtn = e.target.closest('.add-to-cart-btn');
        if (addToCartBtn) {
            e.preventDefault();
            e.stopPropagation();
            const variantId = addToCartBtn.dataset.variantId || addToCartBtn.dataset.productId;
            const productName = addToCartBtn.dataset.productName;
            const productPrice = parseFloat(addToCartBtn.dataset.productPrice);
            const productImage = addToCartBtn.dataset.productImage;

            // Store original classes if not already stored
            if (!addToCartBtn.dataset.originalClass) {
                addToCartBtn.dataset.originalClass = addToCartBtn.className;
            }

            // Find quantity if exists in the same container
            const container = addToCartBtn.closest('.d-flex') || addToCartBtn.closest('form');
            const qtyInput = container ? container.querySelector('.qty-input') : null;
            const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

            addToCart({
                id: variantId,
                name: productName,
                price: productPrice,
                image: productImage,
                quantity: quantity
            }, addToCartBtn);
            return;
        }

        // Wishlist buttons (moved from initWishlist to delegation for AJAX support)
        const wishlistBtn = e.target.closest('.wishlist-btn');
        if (wishlistBtn) {
            e.preventDefault();
            e.stopPropagation();
            const productId = wishlistBtn.dataset.productId;
            toggleWishlist(productId, wishlistBtn);
            return;
        }
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

function addToCart(product, button = null) {
    // We prioritize the backend cart, but keep localStorage for redundancy/UI responsiveness
    const formData = new FormData();
    formData.append('variant_id', product.id);
    formData.append('quantity', product.quantity);

    fetch('/cart/add/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update local state for legacy support if needed
                const existingItem = DCL.cart.find(item => item.id === product.id);
                if (existingItem) {
                    existingItem.quantity += product.quantity;
                } else {
                    DCL.cart.push(product);
                }
                saveCart();

                // Update UI with data from server
                updateCartCount(data.cart_count);
                showNotification(data.message, 'success');

                // Visual feedback on button
                if (button) showAddedAnimation(button);
            } else {
                showNotification(data.message || 'Error adding to cart', 'error');
            }
        })
        .catch(error => {
            console.error('Cart AJAX Error:', error);
            showNotification('Failed to add product to cart. Please try again.', 'error');
        });
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

function updateCartCount(count = null) {
    // Select both navbar badge and floating cart badge
    const cartCountElements = document.querySelectorAll('.cart-count, .floating-cart-count');
    // If we have a direct count from server, use it, otherwise stay with current
    if (count !== null) {
        cartCountElements.forEach(el => {
            el.textContent = count;
            // Logic for visibility might differ slightly, but generally:
            if (count > 0) {
                el.classList.remove('d-none');
                el.style.display = 'flex';
                el.classList.add('animate-bounceIn');
            } else {
                // Determine if we should hide the badge entirely or just show 0
                // For floating cart, maybe we always want to show it? 
                // Let's stick to current logic: hide badge if 0
                el.classList.add('d-none');
                el.style.display = 'none';
            }
        });
    }
}

// Global handle for cart updates to keep UI in sync
function updateCartUI(data) {
    if (data.cart_count !== undefined) updateCartCount(data.cart_count);

    // If on cart page, update totals
    const subtotalEl = document.querySelector('.summary-row .fw-semibold');
    const totalEl = document.querySelector('.summary-total .h4');
    const itemCountEl = document.getElementById('cartItemCount');
    const summaryCountEl = document.querySelector('.summary-row .text-muted'); // Subtotal (X items)

    if (subtotalEl) subtotalEl.textContent = formatCurrency(data.cart_total);
    if (totalEl) totalEl.textContent = formatCurrency(data.cart_total);
    if (itemCountEl && data.cart_count !== undefined) itemCountEl.textContent = data.cart_count;
    if (summaryCountEl && data.cart_count !== undefined) {
        summaryCountEl.textContent = `Subtotal (${data.cart_count} items)`;
    }
}

// Init Cart Page AJAX logic
function initCartPage() {
    // Select both classes to be safe, but main logic iterates over cart-items
    const cartItems = document.querySelectorAll('.cart-item');
    if (!cartItems.length) return;

    cartItems.forEach(item => {
        const variantId = item.dataset.itemId;
        const qtyInput = item.querySelector('.qty-input');
        const minusBtn = item.querySelector('.qty-minus');
        const plusBtn = item.querySelector('.qty-plus');
        const removeBtn = item.querySelector('.remove-item-btn');
        const itemPriceEl = item.querySelector('.text-primary.fw-bold');

        const updateItemQuantity = (newQty) => {
            const formData = new FormData();
            formData.append('variant_id', variantId);
            formData.append('quantity', newQty);

            fetch('/cart/update/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        if (itemPriceEl) itemPriceEl.textContent = formatCurrency(data.item_total);
                        updateCartUI(data);
                    } else {
                        showNotification(data.message || 'Error updating cart', 'error');
                        // Reset input if error
                    }
                })
                .catch(error => console.error('Error updating cart:', error));
        };

        minusBtn?.addEventListener('click', () => {
            const currentVal = parseInt(qtyInput.value);
            if (currentVal > 1) {
                qtyInput.value = currentVal - 1;
                updateItemQuantity(qtyInput.value);
            }
        });

        plusBtn?.addEventListener('click', () => {
            const currentVal = parseInt(qtyInput.value);
            if (currentVal < 10) {
                qtyInput.value = currentVal + 1;
                updateItemQuantity(qtyInput.value);
            }
        });

        qtyInput?.addEventListener('change', () => {
            updateItemQuantity(qtyInput.value);
        });

        // Handle AJAX removal
        const removeForm = removeBtn?.closest('form');
        if (removeForm) {
            removeForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(removeForm);

                fetch('/cart/remove/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            item.classList.add('animate-fadeOut');
                            setTimeout(() => {
                                item.remove();
                                updateCartUI(data);
                                if (document.querySelectorAll('.cart-item').length === 0) {
                                    location.reload(); // Show empty cart state
                                }
                            }, 400);
                            showNotification(data.message, 'success');
                        }
                    });
            });
        }
    });
}


// CSRF Token Helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getCartTotal() {
    return DCL.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}

// ===== WISHLIST =====
function initWishlist() {
    // No longer need to attach listeners here as it's handled by delegation in initProductCards
    // Just handle initial state for wishlist buttons if needed
    const wishlistBtns = document.querySelectorAll('.wishlist-btn');
    wishlistBtns.forEach(btn => {
        const productId = btn.dataset.productId;
        if (DCL.wishlist.includes(productId)) {
            btn.classList.add('active');
        }
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
        anchor.addEventListener('click', function (e) {
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
    // Create container if it doesn't exist
    let container = document.querySelector('.notification-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
    }

    const notification = document.createElement('div');
    notification.className = `notification-toast notification-${type} animate-slideInRight`;

    const icons = {
        success: '<i class="bi bi-check-circle-fill"></i>',
        error: '<i class="bi bi-exclamation-octagon-fill"></i>',
        warning: '<i class="bi bi-exclamation-triangle-fill"></i>',
        info: '<i class="bi bi-info-circle-fill"></i>'
    };

    notification.innerHTML = `
        <div class="notification-glass">
            <span class="notification-icon">${icons[type] || icons.info}</span>
            <div class="notification-content">
                <span class="notification-message">${message}</span>
            </div>
            <button class="notification-close" aria-label="Close">
                <i class="bi bi-x"></i>
            </button>
        </div>
    `;

    container.appendChild(notification);

    // Close button
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        hideNotification(notification);
    });

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            hideNotification(notification);
        }
    }, 5000);
}

function hideNotification(notification) {
    notification.classList.add('animate-fadeOut');
    notification.style.transform = 'translateX(100%)';
    notification.style.opacity = '0';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
            // Remove container if empty
            const container = document.querySelector('.notification-container');
            if (container && !container.hasChildNodes()) {
                container.remove();
            }
        }
    }, 400);
}

// ===== QUICK VIEW MODAL =====
// ===== QUICK VIEW =====
function openQuickView(productId) {
    const modalElement = document.getElementById('quickViewModal');
    const modalContent = document.getElementById('qv-modal-content');
    if (!modalElement || !modalContent) return;

    // Show loading spinner first (modal content already has it by default)
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    // Reset content to loader
    modalContent.innerHTML = `
        <div class="col-12 p-5 text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>`;

    // Fetch quick view partial
    fetch(`/catalog/product/${productId}/quickview/`)
        .then(response => {
            if (!response.ok) throw new Error('Product not found');
            return response.text();
        })
        .then(html => {
            modalContent.innerHTML = html;
            // Re-init any specific listeners if needed, though delegation handles most
        })
        .catch(error => {
            console.error('Quick View Error:', error);
            modalContent.innerHTML = `
                <div class="col-12 p-5 text-center">
                    <i class="bi bi-exclamation-circle text-danger mb-3 display-4"></i>
                    <h4>Oops! Something went wrong</h4>
                    <p class="text-muted">We couldn't load the product details. Please try again.</p>
                </div>`;
        });
}

// ===== ANIMATION HELPERS =====
function showAddedAnimation(button) {
    const originalContent = button.innerHTML;
    button.innerHTML = '<span class="animate-scaleIn"><i class="bi bi-check-lg me-1"></i>Added</span>';
    button.classList.remove('btn-primary', 'btn-secondary', 'btn-outline-primary', 'btn-outline-secondary');
    button.classList.add('btn-added');
    button.disabled = true;

    setTimeout(() => {
        button.innerHTML = originalContent;
        button.classList.remove('btn-added');
        // Restore appropriate class if needed, or rely on original classes still being there if not removed
        // Actually it's better to just toggle back
        if (button.dataset.originalClass) {
            button.className = button.dataset.originalClass;
        } else {
            button.classList.add('btn-primary'); // Default fallback
        }
        button.disabled = false;
    }, 2000);
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
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ===== NOTIFICATION STYLES (Injected) =====
const notificationStyles = `
    .notification-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        gap: 12px;
        pointer-events: none;
    }
    
    .notification-toast {
        pointer-events: auto;
        min-width: 320px;
        max-width: 450px;
        transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    .notification-glass {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        padding: 16px 20px;
        gap: 16px;
    }
    
    .notification-icon {
        font-size: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .notification-content {
        flex: 1;
    }
    
    .notification-message {
        font-size: 14px;
        font-weight: 500;
        color: #1e293b;
        line-height: 1.4;
    }
    
    .notification-close {
        background: rgba(0, 0, 0, 0.05);
        border: none;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: #64748b;
        transition: all 0.2s;
        margin-left: 8px;
    }
    
    .notification-close:hover {
        background: rgba(0, 0, 0, 0.1);
        color: #1e293b;
        transform: rotate(90deg);
    }
    
    /* Notification Variations */
    .notification-success .notification-icon { color: #10b981; }
    .notification-success .notification-glass { border-left: 4px solid #10b981; }
    
    .notification-error .notification-icon { color: #ef4444; }
    .notification-error .notification-glass { border-left: 4px solid #ef4444; }
    
    .notification-warning .notification-icon { color: #f59e0b; }
    .notification-warning .notification-glass { border-left: 4px solid #f59e0b; }
    
    .notification-info .notification-icon { color: #3b82f6; }
    .notification-info .notification-glass { border-left: 4px solid #3b82f6; }
    
    /* Animations */
    @keyframes slideInRight {
        from { transform: translateX(100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    
    .animate-slideInRight {
        animation: slideInRight 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
    }
    
    .animate-fadeOut {
        animation: fadeOut 0.3s ease forwards;
    }
    
    .animate-scaleIn {
        animation: scaleIn 0.3s ease forwards;
    }
    
    @keyframes scaleIn {
        from { transform: scale(0.8); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    
    /* Tooltip Styles */
    .tooltip-custom {
        position: fixed;
        background: rgba(15, 23, 42, 0.9);
        backdrop-filter: blur(8px);
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 500;
        z-index: 10000;
        pointer-events: none;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
`;

// Inject notification styles
if (typeof document !== 'undefined') {
    const styleSheet = document.createElement('style');
    styleSheet.textContent = notificationStyles;
    document.head.appendChild(styleSheet);
}

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
