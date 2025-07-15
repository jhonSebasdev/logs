/**
 * Volt Dashboard JavaScript
 * Core functionality for the Volt Dashboard template
 */

class VoltDashboard {
    constructor() {
        this.sidebarCollapsed = false;
        this.init();
    }

    init() {
        this.setupSidebarToggle();
        this.setupMobileNavigation();
        this.setupTooltips();
        this.setupAnimations();
        this.setupSearchFunctionality();
        this.setupModalHandling();
        this.setupFormValidation();
        this.setupLogViewer();
        this.setupAutoRefresh();
    }

    setupSidebarToggle() {
        const toggler = document.querySelector('.volt-navbar-toggler');
        const sidebar = document.querySelector('.volt-sidebar');
        const mainContent = document.querySelector('.volt-main-content');

        if (toggler && sidebar && mainContent) {
            toggler.addEventListener('click', () => {
                this.sidebarCollapsed = !this.sidebarCollapsed;
                
                if (this.sidebarCollapsed) {
                    sidebar.classList.add('collapsed');
                    mainContent.classList.add('expanded');
                } else {
                    sidebar.classList.remove('collapsed');
                    mainContent.classList.remove('expanded');
                }
                
                // Store preference
                localStorage.setItem('volt-sidebar-collapsed', this.sidebarCollapsed);
            });

            // Restore sidebar state
            const savedState = localStorage.getItem('volt-sidebar-collapsed');
            if (savedState === 'true') {
                sidebar.classList.add('collapsed');
                mainContent.classList.add('expanded');
                this.sidebarCollapsed = true;
            }
        }
    }

    setupMobileNavigation() {
        const toggler = document.querySelector('.volt-navbar-toggler');
        const sidebar = document.querySelector('.volt-sidebar');
        
        if (window.innerWidth <= 768) {
            document.addEventListener('click', (e) => {
                if (!sidebar.contains(e.target) && !toggler.contains(e.target)) {
                    sidebar.classList.remove('show');
                }
            });

            if (toggler) {
                toggler.addEventListener('click', () => {
                    sidebar.classList.toggle('show');
                });
            }
        }
    }

    setupTooltips() {
        const tooltipElements = document.querySelectorAll('[data-volt-tooltip]');
        
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.getAttribute('data-volt-tooltip'));
            });
            
            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'volt-tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: var(--volt-gray-800);
            color: var(--volt-white);
            padding: 0.5rem 0.75rem;
            border-radius: var(--volt-border-radius);
            font-size: 0.75rem;
            z-index: 10000;
            pointer-events: none;
            white-space: nowrap;
            box-shadow: var(--volt-box-shadow);
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
    }

    hideTooltip() {
        const tooltip = document.querySelector('.volt-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    setupAnimations() {
        // Intersection Observer for fade-in animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('volt-fade-in');
                }
            });
        }, { threshold: 0.1 });

        // Observe cards and other elements
        document.querySelectorAll('.volt-card, .volt-stats-card, .volt-server-card').forEach(el => {
            observer.observe(el);
        });

        // Add staggered animation delays
        document.querySelectorAll('.volt-card').forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
        });
    }

    setupSearchFunctionality() {
        const searchInput = document.querySelector('.volt-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                this.filterContent(searchTerm);
            });
        }
    }

    filterContent(searchTerm) {
        const searchableElements = document.querySelectorAll('.volt-log-line, .volt-server-card');
        
        searchableElements.forEach(element => {
            const text = element.textContent.toLowerCase();
            if (text.includes(searchTerm) || searchTerm === '') {
                element.style.display = '';
                if (searchTerm !== '') {
                    this.highlightText(element, searchTerm);
                } else {
                    this.removeHighlight(element);
                }
            } else {
                element.style.display = 'none';
            }
        });
    }

    highlightText(element, searchTerm) {
        element.classList.add('volt-highlight');
    }

    removeHighlight(element) {
        element.classList.remove('volt-highlight');
    }

    setupModalHandling() {
        // Modal triggers
        document.querySelectorAll('[data-volt-modal]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-volt-modal');
                this.showModal(modalId);
            });
        });

        // Modal close buttons
        document.querySelectorAll('[data-volt-modal-close]').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                this.hideModal();
            });
        });

        // Close modal on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('volt-modal-backdrop')) {
                this.hideModal();
            }
        });

        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideModal();
            }
        });
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
            
            // Focus first input
            const firstInput = modal.querySelector('input, textarea, select');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }
    }

    hideModal() {
        const activeModal = document.querySelector('.volt-modal.show');
        if (activeModal) {
            activeModal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form[data-volt-validate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });

            // Real-time validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        
        // Remove existing error styling
        field.classList.remove('volt-is-invalid');
        this.removeFieldError(field);
        
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            this.showFieldError(field, 'Este campo es requerido');
        } else if (field.type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            this.showFieldError(field, 'Ingrese un email válido');
        }
        
        if (!isValid) {
            field.classList.add('volt-is-invalid');
        }
        
        return isValid;
    }

    showFieldError(field, message) {
        const error = document.createElement('div');
        error.className = 'volt-field-error';
        error.textContent = message;
        error.style.cssText = `
            color: var(--volt-danger);
            font-size: 0.75rem;
            margin-top: 0.25rem;
        `;
        
        field.parentNode.appendChild(error);
    }

    removeFieldError(field) {
        const error = field.parentNode.querySelector('.volt-field-error');
        if (error) {
            error.remove();
        }
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    setupLogViewer() {
        const logViewer = document.querySelector('.volt-log-viewer');
        if (logViewer) {
            // Add line numbers
            const lines = logViewer.querySelectorAll('.volt-log-line');
            lines.forEach((line, index) => {
                const lineNumber = document.createElement('span');
                lineNumber.className = 'volt-line-number';
                lineNumber.textContent = (index + 1).toString().padStart(3, '0');
                lineNumber.style.cssText = `
                    color: var(--volt-gray-500);
                    margin-right: 1rem;
                    font-family: monospace;
                    user-select: none;
                    min-width: 40px;
                    display: inline-block;
                `;
                line.insertBefore(lineNumber, line.firstChild);
            });

            // Copy functionality
            const copyBtn = document.querySelector('[data-volt-copy-logs]');
            if (copyBtn) {
                copyBtn.addEventListener('click', () => {
                    const text = Array.from(lines).map(line => line.textContent).join('\n');
                    navigator.clipboard.writeText(text).then(() => {
                        this.showNotification('Logs copiados al portapapeles', 'success');
                    }).catch(() => {
                        this.showNotification('Error al copiar', 'danger');
                    });
                });
            }
        }
    }

    setupAutoRefresh() {
        const autoRefreshToggle = document.querySelector('[data-volt-auto-refresh]');
        if (autoRefreshToggle) {
            let refreshInterval;
            
            autoRefreshToggle.addEventListener('change', () => {
                if (autoRefreshToggle.checked) {
                    refreshInterval = setInterval(() => {
                        window.location.reload();
                    }, 30000);
                    this.showNotification('Auto-refresh activado (30s)', 'info');
                } else {
                    clearInterval(refreshInterval);
                    this.showNotification('Auto-refresh desactivado', 'info');
                }
            });
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `volt-notification volt-notification-${type}`;
        notification.innerHTML = `
            <div class="volt-notification-content">
                ${this.getNotificationIcon(type)}
                <span>${message}</span>
            </div>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            min-width: 250px;
            padding: 1rem;
            border-radius: var(--volt-border-radius);
            box-shadow: var(--volt-box-shadow-lg);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;

        this.setNotificationColors(notification, type);
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            danger: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    setNotificationColors(notification, type) {
        const colors = {
            success: { bg: 'var(--volt-success)', text: 'white' },
            danger: { bg: 'var(--volt-danger)', text: 'white' },
            warning: { bg: 'var(--volt-warning)', text: 'white' },
            info: { bg: 'var(--volt-info)', text: 'white' }
        };
        
        const color = colors[type] || colors.info;
        notification.style.backgroundColor = color.bg;
        notification.style.color = color.text;
    }

    // Utility methods
    static ready(fn) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fn);
        } else {
            fn();
        }
    }
}

// Custom CSS additions for enhanced functionality
const additionalStyles = `
.volt-highlight {
    background: rgba(63, 77, 181, 0.1) !important;
    border-left-color: var(--volt-primary) !important;
}

.volt-is-invalid {
    border-color: var(--volt-danger) !important;
    box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
}

.volt-modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
    z-index: 2000;
    align-items: center;
    justify-content: center;
}

.volt-modal.show {
    display: flex;
}

.volt-modal-content {
    background: var(--volt-white);
    border-radius: var(--volt-border-radius);
    padding: 2rem;
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    animation: volt-modal-slide-in 0.3s ease;
}

@keyframes volt-modal-slide-in {
    from {
        opacity: 0;
        transform: translateY(-50px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.volt-notification-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

@media (max-width: 480px) {
    .volt-server-actions {
        flex-direction: column;
    }
    
    .volt-server-actions .volt-btn {
        width: 100%;
    }
}
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Initialize Volt Dashboard when DOM is ready
VoltDashboard.ready(() => {
    window.voltDashboard = new VoltDashboard();
});