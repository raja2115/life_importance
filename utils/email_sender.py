from flask_mail import Message
from datetime import date, timedelta
from models.exam import Exam


def send_reminder_email(app, mail, exam):
    """Send a reminder email for an upcoming exam."""
    try:
        if not app.config.get('MAIL_USERNAME'):
            print(f"[Mail] Skipping email — MAIL_USERNAME not configured")
            return False

        days_left = (exam.exam_date - date.today()).days
        recipient = app.config.get('NOTIFICATION_EMAIL', app.config.get('MAIL_USERNAME'))

        html_body = f"""
        <div style="font-family: 'Inter', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 16px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #6c63ff, #3f3d9e); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">📚 ExamTrack AI Reminder</h1>
            </div>
            <div style="padding: 30px; color: #e0e0ff;">
                <h2 style="color: #6c63ff; margin-top: 0;">⏰ Exam Alert!</h2>
                <div style="background: rgba(108, 99, 255, 0.1); border: 1px solid rgba(108, 99, 255, 0.3); border-radius: 12px; padding: 20px; margin: 20px 0;">
                    <p style="margin: 8px 0;"><strong>📝 Exam:</strong> {exam.name}</p>
                    <p style="margin: 8px 0;"><strong>📂 Category:</strong> {exam.category}</p>
                    <p style="margin: 8px 0;"><strong>📅 Date:</strong> {exam.exam_date.strftime('%B %d, %Y')}</p>
                    <p style="margin: 8px 0; color: {'#ef4444' if days_left <= 3 else '#f59e0b'};">
                        <strong>⏳ Days Remaining:</strong> {days_left} day(s)
                    </p>
                </div>
                <p style="color: #a0a0c0; font-size: 14px; text-align: center; margin-top: 30px;">
                    — ExamTrack AI | Your Personal Exam Tracker —
                </p>
            </div>
        </div>
        """

        msg = Message(
            subject=f'🔔 ExamTrack AI: {exam.name} in {days_left} day(s)!',
            recipients=[recipient],
            html=html_body
        )

        with app.app_context():
            mail.send(msg)

        print(f"[Mail] Reminder sent for: {exam.name}")
        return True

    except Exception as e:
        print(f"[Mail] Error sending reminder for {exam.name}: {e}")
        return False


def check_and_send_reminders(app, mail):
    """Check for exams within the next 3 days and send reminders."""
    try:
        with app.app_context():
            today = date.today()
            target = today + timedelta(days=3)

            exams = Exam.query.filter(
                Exam.exam_date >= today,
                Exam.exam_date <= target,
                Exam.status.in_(['Upcoming', 'Applied', 'Scheduled'])
            ).all()

            for exam in exams:
                send_reminder_email(app, mail, exam)

            if exams:
                print(f"[Scheduler] Sent reminders for {len(exams)} exam(s)")
            else:
                print(f"[Scheduler] No upcoming exams within 3 days")

    except Exception as e:
        print(f"[Scheduler] Error checking reminders: {e}")
