/* ═══════════════════════════════════════════════════════════════
   ExamTrack AI — Calendar View Module
   ═══════════════════════════════════════════════════════════════ */

class CalendarView {
    constructor() {
        const now = new Date();
        this.currentMonth = now.getMonth();
        this.currentYear = now.getFullYear();
        this.exams = [];
    }

    async init() {
        await this.loadExams();
        this.render();
    }

    async loadExams() {
        try {
            this.exams = await apiGet('/api/exams');
        } catch(e) {
            console.error('Failed to load exams for calendar:', e);
            this.exams = [];
        }
    }

    render() {
        const grid = document.getElementById('calendarGrid');
        const title = document.getElementById('calendarTitle');
        if (!grid || !title) return;

        const months = ['January','February','March','April','May','June',
                       'July','August','September','October','November','December'];
        title.textContent = `${months[this.currentMonth]} ${this.currentYear}`;

        // Remove existing day cells (keep the 7 headers)
        const headers = grid.querySelectorAll('.calendar-day-header');
        grid.innerHTML = '';
        headers.forEach(h => grid.appendChild(h));

        const daysInMonth = new Date(this.currentYear, this.currentMonth + 1, 0).getDate();
        const firstDay = new Date(this.currentYear, this.currentMonth, 1).getDay();
        const daysInPrevMonth = new Date(this.currentYear, this.currentMonth, 0).getDate();
        
        const today = new Date();
        const todayStr = today.toISOString().split('T')[0];

        // Previous month days
        for (let i = firstDay - 1; i >= 0; i--) {
            const day = daysInPrevMonth - i;
            const cell = this._createDayCell(day, true, null);
            grid.appendChild(cell);
        }

        // Current month days
        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${this.currentYear}-${String(this.currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const isToday = dateStr === todayStr;
            const dayExams = this.exams.filter(e => e.exam_date === dateStr);
            const deadlineExams = this.exams.filter(e => e.application_deadline === dateStr);

            const cell = this._createDayCell(day, false, [...dayExams, ...deadlineExams.map(e => ({...e, _isDeadline: true}))], isToday, dateStr);
            grid.appendChild(cell);
        }

        // Next month days to fill the grid
        const totalCells = firstDay + daysInMonth;
        const remaining = (7 - (totalCells % 7)) % 7;
        for (let day = 1; day <= remaining; day++) {
            const cell = this._createDayCell(day, true, null);
            grid.appendChild(cell);
        }
    }

    _createDayCell(day, isOtherMonth, exams, isToday = false, dateStr = null) {
        const cell = document.createElement('div');
        cell.className = 'calendar-day';
        if (isOtherMonth) cell.classList.add('other-month');
        if (isToday) cell.classList.add('today');

        let html = `<span class="day-number">${day}</span>`;

        if (exams && exams.length > 0) {
            cell.classList.add('has-exam');
            html += '<div class="exam-dots">';
            exams.forEach(exam => {
                const catColors = {
                    'Banking': '#6c63ff', 'SSC': '#f59e0b', 'UPSC': '#ef4444',
                    'TNPSC': '#10b981', 'Railway': '#3b82f6', 'Group': '#8b5cf6'
                };
                const color = catColors[exam.category] || '#6c63ff';
                html += `<span class="exam-dot" style="background:${color};" title="${exam.name}"></span>`;
            });
            html += '</div>';

            // Show first exam name
            const displayExam = exams[0];
            const prefix = displayExam._isDeadline ? '⏰' : '📝';
            html += `<span class="exam-name-mini">${prefix} ${displayExam.name}</span>`;

            cell.style.cursor = 'pointer';
            cell.addEventListener('click', () => this._showDayExams(dateStr, exams));
        }

        cell.innerHTML = html;
        return cell;
    }

    _showDayExams(dateStr, exams) {
        const modal = document.getElementById('dayModal');
        const title = document.getElementById('dayModalTitle');
        const content = document.getElementById('dayModalContent');

        const dateObj = new Date(dateStr);
        title.textContent = `📅 ${dateObj.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}`;

        content.innerHTML = exams.map(exam => {
            const catClass = exam.category.toLowerCase();
            const type = exam._isDeadline ? '⏰ Application Deadline' : '📝 Exam Day';
            return `
                <div class="card" style="margin-bottom: 12px; padding: 16px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <strong>${exam.name}</strong>
                        <span class="exam-category ${catClass}" style="font-size:0.7rem;padding:2px 8px;border-radius:999px;color:#fff;">${exam.category}</span>
                    </div>
                    <div style="font-size:0.85rem;color:var(--text-secondary);">
                        <div>${type}</div>
                        <div>Status: <span class="status-badge ${exam.status.toLowerCase()}">${exam.status}</span></div>
                        <div>Priority: <span class="priority-dot ${exam.priority.toLowerCase()}">${exam.priority}</span></div>
                        ${exam.official_website ? `<a href="${exam.official_website}" target="_blank" class="exam-link" style="margin-top:8px;display:block;">🔗 Official Website</a>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        modal.classList.add('active');
    }

    prevMonth() {
        this.currentMonth--;
        if (this.currentMonth < 0) {
            this.currentMonth = 11;
            this.currentYear--;
        }
        this.render();
    }

    nextMonth() {
        this.currentMonth++;
        if (this.currentMonth > 11) {
            this.currentMonth = 0;
            this.currentYear++;
        }
        this.render();
    }
}
