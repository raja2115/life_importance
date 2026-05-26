/* ═══════════════════════════════════════════════════════════════
   ExamTrack AI — Countdown Timer Module
   ═══════════════════════════════════════════════════════════════ */

/**
 * Initialize a live countdown timer for an exam.
 * @param {string} examDate - ISO date string (YYYY-MM-DD)
 * @param {HTMLElement} container - Container element for the countdown
 */
function createCountdown(examDate, container) {
    if (!examDate || !container) return;

    const target = new Date(examDate + 'T00:00:00').getTime();

    function update() {
        const now = Date.now();
        const diff = target - now;

        if (diff <= 0) {
            container.innerHTML = '<div class="countdown-expired">✅ Exam day has arrived!</div>';
            container.classList.remove('urgent');
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const secs = Math.floor((diff % (1000 * 60)) / 1000);

        // Add urgent class if less than 3 days
        if (days < 3) {
            container.classList.add('urgent');
        } else {
            container.classList.remove('urgent');
        }

        container.innerHTML = `
            <div class="countdown-unit">
                <span class="number">${days}</span>
                <span class="label">Days</span>
            </div>
            <div class="countdown-unit">
                <span class="number">${String(hours).padStart(2, '0')}</span>
                <span class="label">Hrs</span>
            </div>
            <div class="countdown-unit">
                <span class="number">${String(mins).padStart(2, '0')}</span>
                <span class="label">Min</span>
            </div>
            <div class="countdown-unit">
                <span class="number">${String(secs).padStart(2, '0')}</span>
                <span class="label">Sec</span>
            </div>
        `;

        requestAnimationFrame(() => setTimeout(update, 1000));
    }

    update();
}

/**
 * Initialize all countdown timers on the page.
 */
function initAllCountdowns() {
    document.querySelectorAll('.countdown-container[data-exam-date]').forEach(container => {
        const examDate = container.getAttribute('data-exam-date');
        createCountdown(examDate, container);
    });
}

// Auto-init on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initAllCountdowns);
