"""
Database initialization script.
Creates tables and seeds default admin + sample exams.
Run: python init_db.py
"""
import os
import sys
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from models.exam import AdminUser, Exam


def init_database():
    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created!")

        # Create default admin user
        admin = AdminUser.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
        if not admin:
            admin = AdminUser(username=app.config['ADMIN_USERNAME'])
            admin.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            print(f"✅ Admin user created: {app.config['ADMIN_USERNAME']}")
        else:
            print(f"ℹ️  Admin user already exists: {admin.username}")

        # Seed sample exams (only if DB is empty)
        if Exam.query.count() == 0:
            sample_exams = [
                Exam(
                    name='SBI PO Prelims 2026',
                    category='Banking',
                    exam_date=date(2026, 8, 15),
                    application_deadline=date(2026, 7, 1),
                    official_website='https://sbi.co.in/web/careers',
                    status='Upcoming',
                    priority='High',
                    notes='State Bank of India Probationary Officer preliminary examination.'
                ),
                Exam(
                    name='SSC CGL Tier-I 2026',
                    category='SSC',
                    exam_date=date(2026, 9, 10),
                    application_deadline=date(2026, 7, 15),
                    official_website='https://ssc.nic.in',
                    status='Upcoming',
                    priority='High',
                    notes='Staff Selection Commission Combined Graduate Level examination.'
                ),
                Exam(
                    name='UPSC CSE Prelims 2026',
                    category='UPSC',
                    exam_date=date(2026, 6, 28),
                    application_deadline=date(2026, 4, 15),
                    official_website='https://upsc.gov.in',
                    status='Applied',
                    priority='High',
                    notes='Civil Services Examination preliminary stage.'
                ),
                Exam(
                    name='TNPSC Group 2 2026',
                    category='TNPSC',
                    exam_date=date(2026, 10, 20),
                    application_deadline=date(2026, 8, 30),
                    official_website='https://www.tnpsc.gov.in',
                    status='Upcoming',
                    priority='Medium',
                    notes='Tamil Nadu Public Service Commission Group 2 examination.'
                ),
                Exam(
                    name='RRB NTPC CBT-1 2026',
                    category='Railway',
                    exam_date=date(2026, 11, 5),
                    application_deadline=date(2026, 9, 15),
                    official_website='https://www.rrbcdg.gov.in',
                    status='Upcoming',
                    priority='Medium',
                    notes='Railway Recruitment Board Non-Technical Popular Categories.'
                ),
                Exam(
                    name='IBPS Clerk Prelims 2026',
                    category='Banking',
                    exam_date=date(2026, 12, 1),
                    application_deadline=date(2026, 10, 10),
                    official_website='https://www.ibps.in',
                    status='Upcoming',
                    priority='Low',
                    notes='Institute of Banking Personnel Selection Clerk examination.'
                ),
            ]
            db.session.add_all(sample_exams)
            print(f"✅ {len(sample_exams)} sample exams seeded!")
        else:
            print(f"ℹ️  Database already has {Exam.query.count()} exam(s)")

        db.session.commit()
        print("\n🚀 Database initialization complete!")
        print(f"   Admin Login: {app.config['ADMIN_USERNAME']} / {app.config['ADMIN_PASSWORD']}")


if __name__ == '__main__':
    init_database()
