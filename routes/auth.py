from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import re
from models import db
from models.exam import AdminUser, Subscriber

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('exams.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = AdminUser.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Welcome back, Admin!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('exams.dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the admin user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('exams.dashboard'))


@auth_bp.route('/api/auth/status')
def auth_status():
    """Check if user is logged in."""
    return jsonify({
        'logged_in': current_user.is_authenticated,
        'username': current_user.username if current_user.is_authenticated else None
    })

@auth_bp.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Subscribe a phone number for notifications."""
    data = request.get_json()
    if not data or not data.get('phone_number'):
        return jsonify({'error': 'Phone number is required'}), 400

    phone = data['phone_number'].strip()
    
    # Basic validation (allow digits, +, spaces, dashes)
    if not re.match(r'^[\d\+\-\s\(\)]{7,20}$', phone):
        return jsonify({'error': 'Invalid phone number format'}), 400

    # Check if exists
    existing = Subscriber.query.filter_by(phone_number=phone).first()
    if not existing:
        sub = Subscriber(phone_number=phone)
        db.session.add(sub)
        db.session.commit()
    
    return jsonify({'message': 'Subscribed successfully'})

