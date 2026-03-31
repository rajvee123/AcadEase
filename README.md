# AcadEase 🎓

> A college portal web application for academic scheduling and automation — enabling secure student-teacher interaction, result management, and event coordination.

---

## 📌 Overview

**AcadEase** is a role-based academic portal built for educational institutions. It streamlines day-to-day college operations including result uploads, event management, and secure communication between students and teachers — all from a single platform.

---

## ✨ Features

- 🔐 **Role-Based Access Control (RBAC)** — Separate access and permissions for students and teachers
- 📁 **File Upload/Download System** — Supports PDF and CSV for result storage and retrieval
- 🔍 **Dynamic Filtering** — Filter academic results by year, semester, and course
- 📅 **Event Management Module** — Create and manage institutional events
- 📧 **SMTP Email Broadcasting** — Automated bulk email notifications to students and teachers
- 🛡️ **JWT Authentication & Authorization** — Secure token-based login and session handling
- 🧩 **Modular Authorization Decorators** — Reusable decorators enforcing access control across all routes

---

## 🛠️ Tech Stack

| Layer         | Technology                         |
|---------------|------------------------------------|
| Backend       | Python, Flask                      |
| Frontend      | JavaScript (64%), HTML, CSS, SCSS  |
| Database      | SQLite (`events.db`)               |
| Auth          | JSON Web Tokens (JWT)              |
| Email         | SMTP                               |
| Templating    | Jinja2 (`/templates`)              |
| Static Assets | `/static` (JS, CSS, images)        |

---

## 📂 Project Structure

```
AcadEase/
├── instance/           # Flask instance config (secret keys, DB config)
├── static/             # Static assets — JS, CSS, SCSS, images
├── templates/          # Jinja2 HTML templates
├── try/                # UI experiments / sandbox
├── app.py              # Main Flask application entry point
├── events.db           # SQLite database
├── requirements.txt    # Python dependencies
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/rajvee123/AcadEase.git
cd AcadEase

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and fill in your values (see below)

# 5. Run the app
python app.py
```

The app will be available at `http://localhost:5000`

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_flask_secret_key
JWT_SECRET=your_jwt_secret_key

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
```

---

## 👥 Contributors

| GitHub | Role |
|--------|------|
| [@rajvee123](https://github.com/rajvee123) | Contributor |
| [@NisargWath](https://github.com/NisargWath) | Contributor |
| [@vaish-navi24](https://github.com/vaish-navi24) | Contributor |

---

## 📄 License

This project is for educational purposes. Feel free to fork and build upon it.

---

> Built with 💙 as part of an EdTech academic project | Apr 2025 – Jun 2025
