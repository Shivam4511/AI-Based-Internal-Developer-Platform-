/* ═══════════════════════════════════════════════════════════════
   IDP Platform — Shared JavaScript Module
   API client, utilities, and navigation state
   ═══════════════════════════════════════════════════════════════ */

const API_BASE = window.location.origin;

// ─── API Client ────────────────────────────────────────────────
const api = {
    async get(endpoint) {
        try {
            const res = await fetch(`${API_BASE}${endpoint}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error(`API Error [${endpoint}]:`, err);
            return null;
        }
    },

    async post(endpoint, data) {
        try {
            const res = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error(`API Error [${endpoint}]:`, err);
            return null;
        }
    },

    getStats: () => api.get('/api/stats'),
    getProjects: (status) => api.get(`/api/projects${status ? `?status=${status}` : ''}`),
    getActivity: (type, limit) => {
        const params = new URLSearchParams();
        if (type) params.set('event_type', type);
        if (limit) params.set('limit', limit);
        const qs = params.toString();
        return api.get(`/api/activity${qs ? '?' + qs : ''}`);
    },
    getCodebase: (query) => api.get(`/api/codebase${query ? `?q=${encodeURIComponent(query)}` : ''}`),
    getRepo: (name) => api.get(`/api/codebase/${name}`),
    chat: (message) => api.post('/chat', { message })
};

// ─── Utility Functions ─────────────────────────────────────────
function timeAgo(dateStr) {
    const now = new Date();
    const date = new Date(dateStr);
    const diffMs = now - date;
    const diffMin = Math.floor(diffMs / 60000);
    const diffHr = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHr / 24);

    if (diffMin < 1) return 'just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHr < 24) return `${diffHr}h ago`;
    if (diffDay < 7) return `${diffDay}d ago`;
    return date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
}

function formatNumber(num) {
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num.toString();
}

function getActivityIcon(type) {
    const icons = {
        deploy: '🚀',
        pr_merged: '🔀',
        incident: '🔥',
        code_review: '👁️'
    };
    return icons[type] || '📌';
}

function getStatusBadge(status) {
    return `<span class="badge ${status}">${status}</span>`;
}

function getLanguageColor(lang) {
    const colors = {
        'Python': '#3572A5',
        'JavaScript': '#f1e05a',
        'TypeScript': '#3178c6',
        'Go': '#00ADD8',
        'HCL': '#844FBA',
        'Java': '#b07219',
        'Rust': '#dea584'
    };
    return colors[lang] || '#64748b';
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ─── Sidebar Generator ────────────────────────────────────────
function renderSidebar(activePage) {
    return `
    <div class="sidebar" id="sidebar">
        <div class="sidebar-logo">
            <div class="logo-icon">⚡</div>
            <div>
                <div class="logo-text">IDP Platform</div>
                <div class="logo-sub">Developer Portal</div>
            </div>
        </div>
        <nav class="sidebar-nav">
            <div class="nav-section-title">Main</div>
            <a href="/static/index.html" class="nav-item ${activePage === 'home' ? 'active' : ''}">
                <span class="nav-icon">🏠</span> Dashboard
            </a>
            <a href="/static/chatbot.html" class="nav-item ${activePage === 'chatbot' ? 'active' : ''}">
                <span class="nav-icon">🤖</span> AI Chatbot
                <span class="nav-badge">AI</span>
            </a>
            <div class="nav-section-title">Platform</div>
            <a href="/static/codebase.html" class="nav-item ${activePage === 'codebase' ? 'active' : ''}">
                <span class="nav-icon">📁</span> Codebase
            </a>
            <a href="/static/projects.html" class="nav-item ${activePage === 'projects' ? 'active' : ''}">
                <span class="nav-icon">📦</span> Projects
            </a>
            <a href="/static/activity.html" class="nav-item ${activePage === 'activity' ? 'active' : ''}">
                <span class="nav-icon">📊</span> Activity
                <span class="nav-badge warning">12</span>
            </a>
            <div class="nav-section-title">Tools</div>
            <a href="/static/upload.html" class="nav-item ${activePage === 'upload' ? 'active' : ''}">
                <span class="nav-icon">📤</span> Upload Codebase
                <span class="nav-badge">NEW</span>
            </a>
        </nav>
        <div class="sidebar-footer">
            <div class="user-info">
                <div class="user-avatar">SK</div>
                <div>
                    <div class="user-name">Shiva K.</div>
                    <div class="user-role">Platform Engineer</div>
                </div>
            </div>
        </div>
    </div>`;
}
