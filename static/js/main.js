// Darwin-Gödel Voice Agent - Common Utilities

// API base URL
const API_BASE = window.location.origin;

// Common API functions
const API = {
    // GET request
    async get(endpoint) {
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }
        return await response.json();
    },

    // POST request
    async post(endpoint, data) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || response.statusText);
        }
        return await response.json();
    },

    // WebSocket connection
    createWebSocket(endpoint) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${protocol}//${window.location.host}${endpoint}`;
        return new WebSocket(url);
    }
};

// UI utilities
const UI = {
    // Show loading spinner
    showLoading(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '<div class="spinner"></div>';
        }
    },

    // Hide loading spinner
    hideLoading(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }
    },

    // Show alert
    showAlert(message, type = 'info', containerId = 'alerts') {
        const container = document.getElementById(containerId);
        if (!container) return;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        container.appendChild(alert);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    },

    // Show error
    showError(error, containerId = 'alerts') {
        console.error(error);
        this.showAlert(error.message || error, 'error', containerId);
    },

    // Format timestamp
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    },

    // Format score
    formatScore(score) {
        return typeof score === 'number' ? score.toFixed(1) : '0.0';
    },

    // Create badge
    createBadge(text, type = 'info') {
        return `<span class="badge badge-${type}">${text}</span>`;
    },

    // Create progress bar
    updateProgressBar(barId, progress, label = '') {
        const bar = document.getElementById(barId);
        if (bar) {
            bar.style.width = `${progress}%`;
            bar.textContent = label || `${progress}%`;
        }
    }
};

// Data formatting utilities
const Format = {
    // Format persona name
    personaName(name) {
        return name.split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    },

    // Format outcome badge
    outcomeBadge(outcome) {
        const badges = {
            'success': UI.createBadge('✓ Success', 'success'),
            'failure': UI.createBadge('✗ Failed', 'danger'),
            'incomplete': UI.createBadge('⊘ Incomplete', 'warning'),
        };
        return badges[outcome] || UI.createBadge(outcome, 'info');
    },

    // Format score with color
    scoreWithColor(score) {
        let type = 'danger';
        if (score >= 85) type = 'success';
        else if (score >= 70) type = 'warning';
        return `<span style="color: var(--${type}); font-weight: 600;">${score.toFixed(1)}</span>`;
    }
};

// Set active navigation link
function setActiveNav(pageName) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href').includes(pageName)) {
            link.classList.add('active');
        }
    });
}

// Initialize page
function initPage() {
    // Set active nav based on current page
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    setActiveNav(currentPage.replace('.html', ''));

    // Load system status
    loadSystemStatus();
}

// Load system status
async function loadSystemStatus() {
    try {
        const status = await API.get('/api/status');

        // Update status indicator if exists
        const indicator = document.getElementById('status-indicator');
        if (indicator) {
            indicator.className = 'status-indicator status-' + status.status;
            indicator.title = `Status: ${status.status}`;
        }

        // Update stats if containers exist
        if (document.getElementById('total-agents')) {
            document.getElementById('total-agents').textContent = status.agents.total;
        }
        if (document.getElementById('best-score')) {
            document.getElementById('best-score').textContent =
                UI.formatScore(status.agents.best_score);
        }
        if (document.getElementById('llm-provider')) {
            document.getElementById('llm-provider').textContent =
                status.config.llm_provider.toUpperCase();
        }
    } catch (error) {
        console.error('Failed to load system status:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initPage);
