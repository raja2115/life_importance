"""
ExamTrack AI — Main Application
Run: python app.py
"""
import os
import sys
from datetime import datetime, timezone

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS

from config import Config
from models import db
from models.exam import AdminUser

# Global extensions
login_manager = LoginManager()
mail = Mail()


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    CORS(app)

    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access admin features.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # Handle unauthorized API requests
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request, jsonify, redirect, url_for
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for('auth.login'))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.exams import exams_bp
    from routes.chatbot import chatbot_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(chatbot_bp)

    # Create tables and default admin on startup
    with app.app_context():
        db.create_all()

        # Create default admin if not exists
        admin = AdminUser.query.filter_by(
            username=app.config.get('ADMIN_USERNAME', 'admin')
        ).first()

        if not admin:
            admin = AdminUser(username=app.config.get('ADMIN_USERNAME', 'admin'))
            admin.set_password(app.config.get('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Default admin user created: {admin.username}")

    # Setup scheduler for daily reminders
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from utils.email_sender import check_and_send_reminders

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=lambda: check_and_send_reminders(app, mail),
            trigger='cron',
            hour=8,
            minute=0,
            id='daily_reminders'
        )
        scheduler.start()
        print("✅ Daily reminder scheduler started (8:00 AM)")
    except Exception as e:
        print(f"⚠️  Scheduler setup skipped: {e}")

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 50)
    print("  📚 ExamTrack AI — Running!")
    print("  🌐 http://localhost:5000")
    print("  🔐 Admin: admin / admin123")
    print("=" * 50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
