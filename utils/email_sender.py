from flask_mail import Message
from datetime import date, timedelta
from models.exam import Exam, Subscriber
import os


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


def send_sms(phone, message):
    """Mock SMS sending function. Replace with Twilio/Meta API in production."""
    # Write to a mock log file instead of sending real SMS for free testing
    with open('sms_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"[{date.today().isoformat()}] TO {phone}:\n{message}\n{'-'*30}\n")
    print(f"📱 [SMS Mock] Sent to {phone}:\n{message}")
    return True

def check_and_send_reminders(app, mail):
    """Check for exams and send email/SMS reminders."""
    try:
        with app.app_context():
            today = date.today()
            in_3_days = today + timedelta(days=3)
            in_7_days = today + timedelta(days=7)

            exams = Exam.query.filter(Exam.status.in_(['Upcoming', 'Applied', 'Scheduled'])).all()
            subscribers = Subscriber.query.all()

            for exam in exams:
                alerts = []
                
                # 1. Application Starts Today
                if exam.application_start_date == today:
                    alerts.append(f"🟢 APPLICATION OPEN TODAY: {exam.name}")
                
                # 2. Application Deadline in 3 days
                if exam.application_deadline == in_3_days:
                    alerts.append(f"⏰ DEADLINE APPROACHING: {exam.name} ends in 3 days!")
                
                # 3. Exam in 7 days
                if exam.exam_date == in_7_days:
                    alerts.append(f"📚 EXAM IN 1 WEEK: {exam.name} is on {exam.exam_date.strftime('%b %d')}")

                # Send email (original logic)
                if exam.exam_date and exam.exam_date <= (today + timedelta(days=3)) and exam.exam_date >= today:
                    send_reminder_email(app, mail, exam)

                # Send SMS/WhatsApp alerts if any triggers matched
                if alerts and subscribers:
                    message = "\n".join(alerts)
                    for sub in subscribers:
                        send_sms(sub.phone_number, message)

    except Exception as e:
        print(f"[Scheduler] Error checking reminders: {e}")
