/* ═══════════════════════════════════════════════════════════════
   ExamTrack AI — Main JavaScript Module
   ═══════════════════════════════════════════════════════════════ */

// ─── GLOBAL AUTH STATE ────────────────────────────────────────
window.isAdmin = false;

// ─── THEME TOGGLE ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('themeToggle');
    const html = document.documentElement;

    // Restore saved theme
    const saved = localStorage.getItem('examtrack-theme');
    if (saved) html.setAttribute('data-theme', saved);

    if (toggle) {
        toggle.addEventListener('click', () => {
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('examtrack-theme', next);
        });
    }

    // Highlight active nav link
    const path = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href') === path || 
            (path === '/' && link.getAttribute('href') === '/dashboard')) {
            link.classList.add('active');
        }
    });

    // Mobile menu toggle
    const mobileBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    if (mobileBtn) {
        mobileBtn.addEventListener('click', () => {
            navLinks.classList.toggle('mobile-open');
            mobileBtn.textContent = navLinks.classList.contains('mobile-open') ? '✕' : '☰';
        });
    }

    // Check auth status
    checkAuthStatus();

    // Check for near exams and send browser notifications
    checkExamNotifications();
});


// ─── AUTH STATUS ──────────────────────────────────────────────
async function checkAuthStatus() {
    try {
        const data = await apiGet('/api/auth/status');
        const loginBtn = document.getElementById('loginBtn');
        const logoutBtn = document.getElementById('logoutBtn');

        window.isAdmin = data.logged_in;

        if (data.logged_in) {
            if (loginBtn) loginBtn.classList.add('hidden');
            if (logoutBtn) logoutBtn.classList.remove('hidden');
            showAdminControls();
        } else {
            if (loginBtn) loginBtn.classList.remove('hidden');
            if (logoutBtn) logoutBtn.classList.add('hidden');
        }
    } catch(e) {
        console.error('Auth check failed:', e);
    }
}

/**
 * Show all .admin-only elements on the page.
 * Call this after dynamically rendering content that has admin controls.
 */
function showAdminControls() {
    if (!window.isAdmin) return;
    document.querySelectorAll('.admin-only').forEach(el => {
        el.classList.add('visible');
        el.style.display = '';
    });
}


// ─── TOAST NOTIFICATIONS ─────────────────────────────────────
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
        <span class="toast-message">${message}</span>
    `;

    toast.addEventListener('click', () => removeToast(toast));
    container.appendChild(toast);

    setTimeout(() => removeToast(toast), duration);
}

function removeToast(toast) {
    toast.classList.add('removing');
    setTimeout(() => toast.remove(), 300);
}


// ─── FETCH HELPERS ────────────────────────────────────────────
async function apiGet(url) {
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || `HTTP ${res.status}`);
    }
    return res.json();
}

async function apiPost(url, data) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.error || `HTTP ${res.status}`);
    }
    return res.json();
}

async function apiPut(url, data) {
    const res = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.error || `HTTP ${res.status}`);
    }
    return res.json();
}

async function apiDelete(url) {
    const res = await fetch(url, { method: 'DELETE' });
    if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.error || `HTTP ${res.status}`);
    }
    return res.json();
}


// ─── DATE HELPERS ─────────────────────────────────────────────
function formatDate(dateStr) {
    if (!dateStr) return 'TBD';
    return new Date(dateStr).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric'
    });
}

function daysUntil(dateStr) {
    if (!dateStr) return null;
    const target = new Date(dateStr);
    const now = new Date();
    target.setHours(0,0,0,0);
    now.setHours(0,0,0,0);
    return Math.ceil((target - now) / (1000 * 60 * 60 * 24));
}


// ─── BROWSER NOTIFICATIONS ───────────────────────────────────
function requestNotificationPermission() {
    if ('Notification' in window) {
        Notification.requestPermission();
    }
}

function showBrowserNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: body,
            icon: '📚',
            badge: '📚'
        });
    }
}

async function checkExamNotifications() {
    try {
        const exams = await apiGet('/api/exams/upcoming');
        exams.forEach(exam => {
            if (exam.exam_date) {
                const days = daysUntil(exam.exam_date);
                if (days !== null && days <= 3 && days >= 0) {
                    showBrowserNotification(
                        `📚 Exam Alert: ${exam.name}`,
                        `Only ${days} day(s) left! Exam on ${formatDate(exam.exam_date)}`
                    );
                }
            }
        });
    } catch(e) {
        // Silently fail
    }
}


// ─── SCROLL ANIMATIONS ───────────────────────────────────────
if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.animate-in').forEach(el => observer.observe(el));
    });
}

// ─── AUTO-REFRESH/POLLING FOR REAL-TIME UPDATES ────────────────
setInterval(() => {
    // Skip if user is actively focusing the search input to avoid UI jumpiness
    const searchInput = document.getElementById('searchInput');
    const isSearching = searchInput && document.activeElement === searchInput;

    // 1. Dashboard Page Polling
    if (typeof loadDashboard === 'function') {
        const modal = document.getElementById('dashExamModal');
        const deleteModal = document.getElementById('dashDeleteModal');
        const isModalOpen = (modal && modal.classList.contains('active')) || (deleteModal && deleteModal.classList.contains('active'));
        if (!isModalOpen && !isSearching) {
            loadDashboard();
        }
    }

    // 2. Exams Page Polling
    if (typeof loadExams === 'function') {
        const modal = document.getElementById('examModal');
        const deleteModal = document.getElementById('deleteModal');
        const isModalOpen = (modal && modal.classList.contains('active')) || (deleteModal && deleteModal.classList.contains('active'));
        if (!isModalOpen && !isSearching) {
            loadExams();
        }
    }

    // 3. Calendar Page Polling
    if (typeof calendarView !== 'undefined' && calendarView && typeof calendarView.loadExams === 'function') {
        const modal = document.getElementById('dayModal');
        const isModalOpen = modal && modal.classList.contains('active');
        if (!isModalOpen) {
            calendarView.loadExams().then(() => calendarView.render());
        }
    }
}, 5000);

