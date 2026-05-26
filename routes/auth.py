from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.exam import AdminUser

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
