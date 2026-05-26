from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models import db
from models.exam import Exam

exams_bp = Blueprint('exams', __name__)


@exams_bp.route('/')
@exams_bp.route('/dashboard')
def dashboard():
    """Render the main dashboard page."""
    return render_template('dashboard.html')


@exams_bp.route('/exams')
def exams_page():
    """Render the exams list page."""
    return render_template('exams.html')


@exams_bp.route('/calendar')
def calendar_page():
    """Render the calendar view page."""
    return render_template('calendar.html')


# ─── API ENDPOINTS ───────────────────────────────────────────────

@exams_bp.route('/api/exams', methods=['GET'])
def get_exams():
    """Get all exams with optional filtering."""
    query = Exam.query

    # Search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            db.or_(
                Exam.name.ilike(f'%{search}%'),
                Exam.category.ilike(f'%{search}%'),
                Exam.notes.ilike(f'%{search}%')
            )
        )

    # Category filter
    category = request.args.get('category', '').strip()
    if category and category != 'All':
        query = query.filter(Exam.category == category)

    # Status filter
    status = request.args.get('status', '').strip()
    if status and status != 'All':
        query = query.filter(Exam.status == status)

    # Priority filter
    priority = request.args.get('priority', '').strip()
    if priority and priority != 'All':
        query = query.filter(Exam.priority == priority)

    exams = query.order_by(Exam.exam_date.asc().nullslast()).all()
    return jsonify([exam.to_dict() for exam in exams])


@exams_bp.route('/api/exams/<int:exam_id>', methods=['GET'])
def get_exam(exam_id):
    """Get a single exam by ID."""
    exam = Exam.query.get_or_404(exam_id)
    return jsonify(exam.to_dict())


@exams_bp.route('/api/exams', methods=['POST'])
@login_required
def create_exam():
    """Create a new exam (admin only)."""
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'error': 'Exam name is required'}), 400

    exam = Exam(
        name=data['name'],
        category=data.get('category', 'Banking'),
        exam_date=_parse_date(data.get('exam_date')),
        application_deadline=_parse_date(data.get('application_deadline')),
        official_website=data.get('official_website', ''),
        status=data.get('status', 'Upcoming'),
        priority=data.get('priority', 'Medium'),
        notes=data.get('notes', '')
    )

    db.session.add(exam)
    db.session.commit()
    return jsonify({'message': 'Exam created successfully', 'exam': exam.to_dict()}), 201


@exams_bp.route('/api/exams/<int:exam_id>', methods=['PUT'])
@login_required
def update_exam(exam_id):
    """Update an existing exam (admin only)."""
    exam = Exam.query.get_or_404(exam_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    exam.name = data.get('name', exam.name)
    exam.category = data.get('category', exam.category)
    exam.exam_date = _parse_date(data.get('exam_date')) if 'exam_date' in data else exam.exam_date
    exam.application_deadline = _parse_date(data.get('application_deadline')) if 'application_deadline' in data else exam.application_deadline
    exam.official_website = data.get('official_website', exam.official_website)
    exam.status = data.get('status', exam.status)
    exam.priority = data.get('priority', exam.priority)
    exam.notes = data.get('notes', exam.notes)

    db.session.commit()
    return jsonify({'message': 'Exam updated successfully', 'exam': exam.to_dict()})


@exams_bp.route('/api/exams/<int:exam_id>', methods=['DELETE'])
@login_required
def delete_exam(exam_id):
    """Delete an exam (admin only)."""
    exam = Exam.query.get_or_404(exam_id)
    db.session.delete(exam)
    db.session.commit()
    return jsonify({'message': 'Exam deleted successfully'})


@exams_bp.route('/api/exams/stats', methods=['GET'])
def exam_stats():
    """Get exam statistics for the dashboard."""
    today = date.today()
    first_of_month = today.replace(day=1)
    if today.month == 12:
        last_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    total = Exam.query.count()
    upcoming = Exam.query.filter(Exam.status == 'Upcoming').count()
    high_priority = Exam.query.filter(Exam.priority == 'High').count()

    this_month = Exam.query.filter(
        Exam.exam_date >= first_of_month,
        Exam.exam_date <= last_of_month
    ).count()

    # Category counts
    category_counts = {}
    for cat in Exam.CATEGORIES:
        category_counts[cat] = Exam.query.filter(Exam.category == cat).count()

    # Priority counts
    priority_counts = {}
    for pri in Exam.PRIORITIES:
        priority_counts[pri] = Exam.query.filter(Exam.priority == pri).count()

    # Nearest upcoming exam
    nearest = Exam.query.filter(
        Exam.exam_date >= today,
        Exam.status.in_(['Upcoming', 'Applied', 'Scheduled'])
    ).order_by(Exam.exam_date.asc()).first()

    return jsonify({
        'total_exams': total,
        'upcoming_count': upcoming,
        'high_priority': high_priority,
        'this_month': this_month,
        'category_counts': category_counts,
        'priority_counts': priority_counts,
        'nearest_exam': nearest.to_dict() if nearest else None
    })


@exams_bp.route('/api/exams/upcoming', methods=['GET'])
def upcoming_exams():
    """Get the next 5 upcoming exams."""
    today = date.today()
    exams = Exam.query.filter(
        Exam.exam_date >= today,
        Exam.status.in_(['Upcoming', 'Applied', 'Scheduled'])
    ).order_by(Exam.exam_date.asc()).limit(10).all()

    return jsonify([exam.to_dict() for exam in exams])


def _parse_date(date_str):
    """Parse a date string (YYYY-MM-DD) to a date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None
