import bcrypt
from datetime import datetime, timezone
from flask_login import UserMixin
from models import db


class AdminUser(UserMixin, db.Model):
    """Admin user model with secure password hashing."""
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def __repr__(self):
        return f'<AdminUser {self.username}>'


class Exam(db.Model):
    """Exam model storing all exam details."""
    __tablename__ = 'exams'

    CATEGORIES = ['Banking', 'SSC', 'UPSC', 'TNPSC', 'Railway', 'Group', 'Other']
    STATUSES = ['Upcoming', 'Applied', 'Scheduled', 'Completed', 'Missed']
    PRIORITIES = ['High', 'Medium', 'Low']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    exam_date = db.Column(db.Date, nullable=True)
    application_start_date = db.Column(db.Date, nullable=True)
    application_deadline = db.Column(db.Date, nullable=True)
    official_website = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(30), default='Upcoming')
    priority = db.Column(db.String(20), default='Medium')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'exam_date': self.exam_date.isoformat() if self.exam_date else None,
            'application_start_date': self.application_start_date.isoformat() if self.application_start_date else None,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'official_website': self.official_website,
            'status': self.status,
            'priority': self.priority,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Exam {self.name}>'

class Subscriber(db.Model):
    """Stores phone numbers for SMS/WhatsApp notifications."""
    __tablename__ = 'subscribers'

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Subscriber {self.phone_number}>'
