// Work Order Management System - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Confirm delete actions
    document.querySelectorAll('[data-confirm]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });

    // Search functionality
    var searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        var searchInput = searchForm.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.addEventListener('keyup', function(e) {
                if (e.key === 'Enter') {
                    searchForm.submit();
                }
            });
        }
    }

    // Auto-refresh functionality for dashboard
    if (window.location.pathname === '/dashboard' || window.location.pathname === '/') {
        setInterval(function() {
            // Update timestamp
            var timestampElement = document.querySelector('#last-updated');
            if (timestampElement) {
                timestampElement.textContent = new Date().toLocaleTimeString();
            }
        }, 30000); // Update every 30 seconds
    }

    // Table sorting
    document.querySelectorAll('.sortable th').forEach(function(header) {
        header.addEventListener('click', function() {
            var table = this.closest('table');
            var column = Array.from(this.parentElement.children).indexOf(this);
            var rows = Array.from(table.querySelectorAll('tbody tr'));
            var isAscending = this.classList.contains('sort-asc');
            
            // Remove sorting classes from all headers
            table.querySelectorAll('th').forEach(function(th) {
                th.classList.remove('sort-asc', 'sort-desc');
            });
            
            // Add sorting class to current header
            this.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
            
            // Sort rows
            rows.sort(function(a, b) {
                var aText = a.children[column].textContent.trim();
                var bText = b.children[column].textContent.trim();
                
                // Try to parse as numbers
                var aNum = parseFloat(aText);
                var bNum = parseFloat(bText);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAscending ? bNum - aNum : aNum - bNum;
                } else {
                    return isAscending ? bText.localeCompare(aText) : aText.localeCompare(bText);
                }
            });
            
            // Reorder table rows
            var tbody = table.querySelector('tbody');
            rows.forEach(function(row) {
                tbody.appendChild(row);
            });
        });
    });

    // Filter form auto-submit
    document.querySelectorAll('.auto-submit').forEach(function(element) {
        element.addEventListener('change', function() {
            this.form.submit();
        });
    });

    // Date range picker
    var dateInputs = document.querySelectorAll('input[type="datetime-local"]');
    dateInputs.forEach(function(input) {
        // Set min date to today for due dates
        if (input.name === 'due_date') {
            var today = new Date();
            var minDate = today.toISOString().slice(0, 16);
            input.min = minDate;
        }
    });

    // Chart.js default configuration
    if (typeof Chart !== 'undefined') {
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        Chart.defaults.plugins.legend.position = 'bottom';
    }

    // Loading states for buttons
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function() {
            var submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ' + submitBtn.textContent;
            }
        });
    });

    // Work order status color coding
    document.querySelectorAll('.status-badge').forEach(function(badge) {
        var status = badge.textContent.toLowerCase().replace(' ', '-');
        badge.classList.add('status-' + status);
    });

    // Priority color coding
    document.querySelectorAll('.priority-badge').forEach(function(badge) {
        var priority = badge.textContent.toLowerCase();
        badge.classList.add('priority-' + priority);
    });

    // Real-time updates (if WebSocket is available)
    if (typeof WebSocket !== 'undefined') {
        // This would be implemented with a WebSocket server
        // for real-time notifications and updates
    }
});

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function showNotification(message, type = 'info') {
    var alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    var container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

// Export functions for use in other scripts
window.WOManager = {
    formatDate: formatDate,
    formatCurrency: formatCurrency,
    showNotification: showNotification
};
