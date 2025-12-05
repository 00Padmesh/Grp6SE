# College Fest Management Portal

> A lightweight Flask web application to manage college fests — organizers can create events and view/export participant lists; students can sign up and register for events.

---

## Table of Contents
1. [Demo / Overview](#demo--overview)
2. [Key Features](#key-features)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Setup & Installation](#setup--installation)
6. [Running the App](#running-the-app)
7. [Usage (Quick Guide)](#usage-quick-guide)
8. [Important Configuration & Defaults](#important-configuration--defaults)
9. [Security Notes & To‑Dos](#security-notes--to-dos)
10. [Extending the Project](#extending-the-project)
11. [License](#license)

---

## Demo / Overview
This portal provides two primary roles:

- **Organizer** — can create, edit, delete events, upload banners, view and export participant lists (CSV) for events they manage.
- **Student** — can sign up (with a unique student ID), browse events and register/unregister for events.

Screenshots are available in `backend/static/uploads/`.

---

## Key Features
- Role-based access control (Organizers vs Students).
- Organizer registration protected by a secret code.
- Password hashing (Werkzeug) before storing credentials.
- Create / Edit / Delete events with optional banner image upload.
- Student event registration and organizer view/export of participants as CSV.
- SQLite database, simple and portable.

---

## Tech Stack
- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLite (file `college_portal.db`)



---

## Project Structure
```
Grp6SE-master/
├─ backend/
│  ├─ app.py                 # Main Flask app and routes
│  ├─ config.py              # App configuration (SECRET_KEY, DB uri, upload folder)
│  ├─ models.py              # SQLAlchemy models: User, Event, Registration
│  ├─ requirements.txt       # Python dependencies
│  ├─ instance/              # Contains shipped sqlite DB (college_portal.db)
│  ├─ static/                # CSS, images, uploaded banners
│  │  └─ uploads/
│  └─ templates/             # Jinja2 templates (index, login, dashboards...)
└─ README.md                 # (This file)
```

> Note: A virtual environment (`venv/`) is included inside `backend/` in this repository. It's recommended to remove it from the repo and re-create a fresh virtual environment locally.

---

## Setup & Installation
Follow these steps to run the app locally.

1. Make sure you have Python 3.8+ installed.
2. Unzip / extract the repository and open a terminal in the `Grp6SE-master/backend` folder.

```bash
# optional: create and activate a virtual environment
python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# install dependencies
pip install flask flask-sqlalchemy flask-login
```

3. (Optional) Inspect `config.py`. By default the app uses the bundled configuration:
```py
SECRET_KEY = "supersecretkey123"
SQLALCHEMY_DATABASE_URI = "sqlite:///college_portal.db"
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
```
You may prefer to set environment variables or edit `config.py` for production.

---

## Running the App
From the `backend/` folder run:

```bash
python app.py
```

By default the server will start in debug mode on `http://127.0.0.1:5000`.

---

## Usage (Quick Guide)
1. Open `http://127.0.0.1:5000/` in your browser.
2. **Organizer signup**
   - Go to Sign Up and choose role **Organizer**.
   - You will be prompted for the organizer secret code. The default code in the project is `fest2025`.
   - After signing up, log in and use the Organizer dashboard to create events, upload banners, or view participants.
3. **Student signup**
   - Students should provide a **Unique ID** (student ID) when signing up. This ID is used in participant lists.
   - Students can log in and register for events from the Student dashboard.
4. **Exporting participants**
   - Organizers can view participants for an event and export them to CSV via the dashboard.

---

## Important Configuration & Defaults
- **Organizer secret code**: `ORGANIZER_CODE = "fest2025"` (defined in `app.py`). Change this in code or move to a secure environment variable.
- **Database**: `instance/college_portal.db` — the app will create tables automatically (`db.create_all()`) when first run.
- **Allowed upload types**: PNG, JPG, JPEG, GIF. Uploaded images are stored in `static/uploads/`.

---

## Security Notes & To‑Dos
This repository is a learning/demo application. If you plan to deploy or share it publicly, consider the following improvements:

- **Never store `SECRET_KEY` or organizer codes in source**. Use environment variables.
- The included `venv/` directory should be removed from version control (`.gitignore` it).
- Use stronger password hashing and configure Werkzeug/Bcrypt parameters explicitly.
- Turn off `debug=True` in production and run behind a production-grade WSGI server (Gunicorn / uWSGI).
- Validate & sanitize all user inputs more thoroughly (file size limits, image scanning).
- Add tests and role-based access unit tests to ensure only organizers can access organizer-only routes.

---

## Extending the Project (Ideas)
- Add email verification for signups.
- Add pagination and search/filter for events.
- Add RSVP limits and waitlists for events that fill up.
- Add an admin role to manage organizers.
- Move configuration to `env` variables and use Flask-Migrate for DB migrations.

---

## License
This project does not include a license file. If you intend to open-source it, add a LICENSE (e.g., MIT) and attribute contributors.

---

If you want, I can:
- generate a polished `README.md` file saved into the repository (I already created this file for you),
- create a `.gitignore` that excludes `venv/` and `instance/college_portal.db`, or
- produce a `Procfile` / simple `gunicorn` command for deploying to Heroku-like services.

Tell me which one you want next.

