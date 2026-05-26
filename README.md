# 📚 ExamTrack AI

> Your AI-Powered Personal Exam Tracker for Banking, SSC, UPSC, TNPSC, Railway & Group Exams

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-blue?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 🎨 **Modern Notebook-Style UI** — Glassmorphism design with dark/light mode
- 📊 **Dashboard** — Stats cards, category breakdown, upcoming exams
- ⏰ **Live Countdown Timers** — Real-time countdowns to exam dates
- 📅 **Calendar View** — Monthly calendar with exam markers
- 🔍 **Smart Search & Filters** — Filter by category, status, priority
- 🤖 **AI Chatbot** — Natural language commands to add, search, and manage exams
- 🔐 **Admin Login** — Secure bcrypt password-protected admin panel
- 📧 **Email Reminders** — Automatic daily email notifications for near exams
- 🔔 **Browser Notifications** — Push notifications for upcoming exams
- 📱 **Fully Responsive** — Works on desktop, tablet, and mobile

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Setup

```bash
# 1. Navigate to project directory
cd Desktop/ExamTrackAI

# 2. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux

# 5. Initialize database with sample data
python init_db.py

# 6. Run the application
python app.py
```

### Access
- 🌐 **App**: http://localhost:5000
- 🔐 **Admin Login**: `admin` / `admin123`

---

## 🤖 AI Chatbot Commands

| Command | Example |
|---------|---------|
| Add exam | "Add SBI PO exam on 2026-08-15 deadline 2026-07-01" |
| Search | "Search banking exams" |
| Upcoming | "Show upcoming exams" |
| Stats | "Show statistics" |
| Delete | "Delete SBI PO" |
| Tips | "Tips for UPSC preparation" |
| Help | "help" |

---

## 📁 Project Structure

```
ExamTrackAI/
├── app.py                    # Main Flask application
├── config.py                 # Configuration
├── init_db.py                # Database seeder
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── models/
│   ├── __init__.py           # SQLAlchemy instance
│   └── exam.py               # AdminUser & Exam models
├── routes/
│   ├── auth.py               # Login/logout routes
│   ├── exams.py              # Exam CRUD API
│   └── chatbot.py            # Chatbot API
├── utils/
│   ├── chatbot_ai.py         # AI chatbot engine
│   └── email_sender.py       # Email notifications
├── static/
│   ├── css/style.css         # All styles (700+ lines)
│   └── js/
│       ├── main.js           # Core JS (theme, auth, toasts)
│       ├── countdown.js      # Live countdown timers
│       ├── calendar.js       # Calendar view
│       └── chatbot.js        # Chatbot UI
└── templates/
    ├── base.html             # Base layout
    ├── login.html            # Admin login
    ├── dashboard.html        # Dashboard
    ├── exams.html            # Exam management
    └── calendar.html         # Calendar view
```

---

## 📧 Email Setup (Optional)

To enable email reminders, update your `.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
NOTIFICATION_EMAIL=your-email@gmail.com
```

> For Gmail, use [App Passwords](https://support.google.com/accounts/answer/185833)

---

## 🛠️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/exams` | List all exams (with filters) |
| GET | `/api/exams/<id>` | Get single exam |
| POST | `/api/exams` | Create exam (admin) |
| PUT | `/api/exams/<id>` | Update exam (admin) |
| DELETE | `/api/exams/<id>` | Delete exam (admin) |
| GET | `/api/exams/stats` | Dashboard statistics |
| GET | `/api/exams/upcoming` | Next 5 upcoming exams |
| POST | `/api/chat` | AI chatbot message |
| GET | `/api/auth/status` | Check login status |

---

## 📝 License

MIT License — feel free to use and modify!

---

Built with ❤️ for competitive exam aspirants 🇮🇳
