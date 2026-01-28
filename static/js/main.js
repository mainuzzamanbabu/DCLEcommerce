/**
 * DCL Ecommerce - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
  // Initialize all Bootstrap tooltips
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

  // Quantity selector buttons
  setupQuantityButtons();
});

function setupQuantityButtons() {
  document.querySelectorAll('.qty-btn-minus').forEach(btn => {
    btn.addEventListener('click', function () {
      const input = this.parentNode.querySelector('input[type=number]');
      if (input.value > 1) {
        input.value = parseInt(input.value) - 1;
        input.dispatchEvent(new Event('change'));
      }
    });
  });

  document.querySelectorAll('.qty-btn-plus').forEach(btn => {
    btn.addEventListener('click', function () {
      const input = this.parentNode.querySelector('input[type=number]');
      if (input.value < 99) {
        input.value = parseInt(input.value) + 1;
        input.dispatchEvent(new Event('change'));
      }
    });
  });
}

/**
 * Toast Notification Utility
 */
function showToast(message, type = 'success') {
  const toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
  }

  const toastId = 'toast-' + Date.now();
  const bgClass = type === 'success' ? 'bg-success' : (type === 'error' ? 'bg-danger' : 'bg-primary');

  const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

  document.getElementById('toast-container').insertAdjacentHTML('beforeend', toastHtml);
  const toastEl = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
  toast.show();

  toastEl.addEventListener('hidden.bs.toast', function () {
    toastEl.remove();
  });
}

/**
 * Cart AJAX Operations
 */

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

function addToCart(variantId, quantity = 1) {
  if (!variantId) {
    showToast('Please select a variant first.', 'error');
    return;
  }

  const formData = new FormData();
  formData.append('variant_id', variantId);
  formData.append('quantity', quantity);
  formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

  fetch('/cart/add/', {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        showToast(data.message, 'success');
        // Update cart count badges
        document.querySelectorAll('.cart-badge').forEach(badge => {
          badge.textContent = data.cart_count;
          badge.classList.remove('d-none');
        });
      } else {
        showToast(data.message || 'Error adding product to cart.', 'error');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showToast('Something went wrong. Please try again.', 'error');
    });
}

function removeFromCart(variantId) {
  if (!confirm('Are you sure you want to remove this item?')) return;

  const formData = new FormData();
  formData.append('variant_id', variantId);
  formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

  fetch('/cart/remove/', {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        const itemRow = document.getElementById(`cart-item-${variantId}`);
        if (itemRow) {
          itemRow.style.transition = 'all 0.3s';
          itemRow.style.opacity = '0';
          itemRow.style.transform = 'translateX(20px)';
          setTimeout(() => {
            itemRow.remove();
            if (document.querySelectorAll('tbody tr').length === 0) {
              location.reload(); // Reload to show empty cart state
            }
          }, 300);
        }
        updateCartTotals(data);
        showToast(data.message);
      }
    });
}

function updateCartItem(variantId, action) {
  const input = document.getElementById(`qty-${variantId}`);
  let quantity = parseInt(input.value);

  if (action === 'increase') {
    quantity += 1;
  } else if (action === 'decrease' && quantity > 1) {
    quantity -= 1;
  } else {
    return;
  }

  const formData = new FormData();
  formData.append('variant_id', variantId);
  formData.append('quantity', quantity);
  formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

  fetch('/cart/update/', {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        input.value = quantity;
        document.getElementById(`total-${variantId}`).textContent = data.item_total.toFixed(2);
        updateCartTotals(data);
      } else {
        showToast(data.message, 'error');
      }
    });
}

function updateCartTotals(data) {
  // Update labels in summary
  const subtotalEl = document.getElementById('cart-subtotal');
  const totalEl = document.getElementById('cart-total');
  if (subtotalEl) subtotalEl.textContent = data.cart_total.toFixed(2);
  if (totalEl) totalEl.textContent = data.cart_total.toFixed(2);

  // Update navbar badges
  document.querySelectorAll('.cart-badge').forEach(badge => {
    badge.textContent = data.cart_count;
    if (data.cart_count === 0) {
      badge.classList.add('d-none');
    } else {
      badge.classList.remove('d-none');
    }
  });
}

function addToWishlist(variantId) {
  if (!variantId || variantId === '0') {
    showToast('Please select a variation first.', 'info');
    return;
  }
  // Phase G implementation
  showToast('Wishlist feature coming soon!', 'info');
}
