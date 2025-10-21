/**
 * SecureBank Main JavaScript File
 * Handles common functionality across the application
 */

// Global variables
let currentUser = null;
let apiBaseURL = '/api/v1';

// Initialize when DOM is ready
$(document).ready(function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Check authentication status
    checkAuthStatus();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
    
    // Setup global event listeners
    setupEventListeners();
    
    // Initialize real-time updates
    initializeRealTimeUpdates();
    
    console.log('SecureBank initialized successfully');
}

/**
 * Check user authentication status
 */
function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    if (token) {
        // Verify token with server
        $.ajax({
            url: `${apiBaseURL}/auth/user/`,
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            success: function(response) {
                currentUser = response;
                updateUIForAuthenticatedUser();
            },
            error: function() {
                // Token is invalid, remove it
                localStorage.removeItem('authToken');
                updateUIForUnauthenticatedUser();
            }
        });
    } else {
        updateUIForUnauthenticatedUser();
    }
}

/**
 * Update UI for authenticated users
 */
function updateUIForAuthenticatedUser() {
    // Show user-specific elements
    $('.authenticated-only').show();
    $('.unauthenticated-only').hide();
    
    // Update user info in navbar
    if (currentUser) {
        $('.user-email').text(currentUser.email);
        $('.user-name').text(currentUser.first_name);
    }
}

/**
 * Update UI for unauthenticated users
 */
function updateUIForUnauthenticatedUser() {
    // Show login/register elements
    $('.authenticated-only').hide();
    $('.unauthenticated-only').show();
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap modals
 */
function initializeModals() {
    // Auto-focus first input in modals
    $('.modal').on('shown.bs.modal', function() {
        $(this).find('input:first').focus();
    });
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Handle logout
    $(document).on('click', '.logout-btn', function(e) {
        e.preventDefault();
        logout();
    });
    
    // Handle form submissions with AJAX
    $(document).on('submit', '.ajax-form', function(e) {
        e.preventDefault();
        handleAjaxFormSubmit($(this));
    });
    
    // Handle copy to clipboard
    $(document).on('click', '.copy-btn', function() {
        copyToClipboard($(this).data('copy'));
    });
    
    // Handle refresh buttons
    $(document).on('click', '.refresh-btn', function() {
        const target = $(this).data('target');
        refreshData(target);
    });
}

/**
 * Initialize real-time updates
 */
function initializeRealTimeUpdates() {
    // Update dashboard data every 30 seconds
    setInterval(function() {
        if (window.location.pathname.includes('dashboard')) {
            refreshDashboardData();
        }
    }, 30000);
}

/**
 * Handle AJAX form submission
 */
function handleAjaxFormSubmit($form) {
    const url = $form.attr('action');
    const method = $form.attr('method') || 'POST';
    const data = $form.serialize();
    const submitBtn = $form.find('button[type="submit"]');
    
    // Show loading state
    const originalText = submitBtn.html();
    submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Loading...');
    
    $.ajax({
        url: url,
        method: method,
        data: data,
        success: function(response) {
            showAlert(response.message || 'Operation successful', 'success');
            
            // Handle redirect if specified
            if (response.redirect) {
                setTimeout(() => {
                    window.location.href = response.redirect;
                }, 1500);
            }
            
            // Reset form on success
            $form[0].reset();
        },
        error: function(xhr) {
            const error = xhr.responseJSON ? xhr.responseJSON.message : 'An error occurred';
            showAlert(error, 'danger');
        },
        complete: function() {
            // Restore button state
            submitBtn.prop('disabled', false).html(originalText);
        }
    });
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info', duration = 5000) {
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Add alert to top of container
    $('.alert-container').prepend(alertHtml);
    
    // Auto-dismiss after duration
    setTimeout(() => {
        $(`#${alertId}`).alert('close');
    }, duration);
}

/**
 * Get appropriate icon for alert type
 */
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('Copied to clipboard!', 'success', 2000);
    }).catch(function() {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showAlert('Copied to clipboard!', 'success', 2000);
    });
}

/**
 * Format currency
 */
function formatCurrency(amount, currency = 'NGN') {
    return new Intl.NumberFormat('en-NG', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Format date/time
 */
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-NG', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format relative time
 */
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return formatDateTime(dateString);
}

/**
 * Refresh dashboard data
 */
function refreshDashboardData() {
    $.ajax({
        url: `${apiBaseURL}/dashboard/`,
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        success: function(response) {
            updateDashboardUI(response);
        },
        error: function() {
            console.log('Failed to refresh dashboard data');
        }
    });
}

/**
 * Update dashboard UI with fresh data
 */
function updateDashboardUI(data) {
    // Update balances
    $('.total-balance').text(formatCurrency(data.total_balance));
    $('.available-balance').text(formatCurrency(data.available_balance));
    $('.crypto-value').text(formatCurrency(data.crypto_value, 'USD'));
    
    // Update recent transactions
    if (data.recent_transactions) {
        updateRecentTransactions(data.recent_transactions);
    }
    
    // Update notifications
    if (data.notifications) {
        updateNotifications(data.notifications);
    }
}

/**
 * Update recent transactions list
 */
function updateRecentTransactions(transactions) {
    const container = $('.recent-transactions');
    container.empty();
    
    if (transactions.length === 0) {
        container.html('<p class="text-muted">No recent transactions</p>');
        return;
    }
    
    transactions.forEach(transaction => {
        const transactionHtml = `
            <div class="transaction-item ${transaction.transaction_type.toLowerCase()}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${transaction.description || transaction.transaction_type}</h6>
                        <small class="text-muted">${formatRelativeTime(transaction.created_at)}</small>
                    </div>
                    <div class="text-end">
                        <h6 class="mb-0 ${transaction.transaction_type === 'DEPOSIT' ? 'text-success' : 'text-danger'}">
                            ${transaction.transaction_type === 'DEPOSIT' ? '+' : '-'}${formatCurrency(transaction.amount)}
                        </h6>
                    </div>
                </div>
            </div>
        `;
        container.append(transactionHtml);
    });
}

/**
 * Update notifications list
 */
function updateNotifications(notifications) {
    const container = $('.notifications');
    container.empty();
    
    if (notifications.length === 0) {
        container.html('<p class="text-muted">No new notifications</p>');
        return;
    }
    
    notifications.forEach(notification => {
        const notificationHtml = `
            <div class="alert alert-${notification.type || 'info'} alert-sm mb-2">
                <small>${notification.message}</small>
                <div class="text-muted mt-1">
                    <small>${formatRelativeTime(notification.created_at)}</small>
                </div>
            </div>
        `;
        container.append(notificationHtml);
    });
}

/**
 * Logout user
 */
function logout() {
    $.ajax({
        url: `${apiBaseURL}/auth/logout/`,
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        success: function() {
            localStorage.removeItem('authToken');
            window.location.href = '/login/';
        },
        error: function() {
            // Force logout even if API call fails
            localStorage.removeItem('authToken');
            window.location.href = '/login/';
        }
    });
}

/**
 * Refresh specific data
 */
function refreshData(target) {
    switch(target) {
        case 'dashboard':
            refreshDashboardData();
            break;
        case 'transactions':
            // Refresh transactions
            break;
        case 'crypto':
            // Refresh crypto data
            break;
        default:
            console.log('Unknown refresh target:', target);
    }
}

/**
 * Validate form
 */
function validateForm($form) {
    let isValid = true;
    
    $form.find('input[required], select[required], textarea[required]').each(function() {
        if (!$(this).val().trim()) {
            $(this).addClass('is-invalid');
            isValid = false;
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    
    return isValid;
}

/**
 * Show loading spinner
 */
function showLoading(element, text = 'Loading...') {
    const originalContent = $(element).html();
    $(element).data('original-content', originalContent);
    $(element).html(`<i class="fas fa-spinner fa-spin me-2"></i>${text}`);
    $(element).prop('disabled', true);
}

/**
 * Hide loading spinner
 */
function hideLoading(element) {
    const originalContent = $(element).data('original-content');
    $(element).html(originalContent);
    $(element).prop('disabled', false);
}

// Export functions for global use
window.SecureBank = {
    showAlert,
    formatCurrency,
    formatDateTime,
    formatRelativeTime,
    copyToClipboard,
    refreshData,
    validateForm,
    showLoading,
    hideLoading
};