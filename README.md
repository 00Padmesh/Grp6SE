# 🎉 College Fest Management Portal

A robust, role-based web application designed to streamline the management of university events. This portal bridges the gap between Event Organizers and Student Participants, offering secure authentication, real-time data management, and logical validations.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Flask](https://img.shields.io/badge/Framework-Flask-green?style=flat&logo=flask)
![DB](https://img.shields.io/badge/Database-SQLite-lightgrey?style=flat&logo=sqlite)

## 🌟 Key Features

### 🔐 Security & Authentication
* **Role-Based Access Control (RBAC):** Distinct workflows for **Organizers** and **Students**.
* **Organizer Verification:** New organizers must provide a specific "Secret Code" to register.
* **Secure Password Hashing:** User passwords are hashed using `scrypt` before storage.
* **Cross-Admin Protection:** Admins can view events created by other admins (Read-Only) but can only **Edit** or **Delete** their own events.

### 📅 Event Management (Organizer)
* **CRUD Operations:** Create, Read, Update, and Delete events.
* **Logical Validations:** * Prevents creating events where the *End Date* is before the *Start Date*.
    * Validates image file types for event banners.
* **Data Export:** Download the list of registered participants as a **CSV file** with one click.
* **Dashboard:** View registered student counts in real-time.

### 🎓 Student Features
* **Unified Dashboard:** Browse all available events in a grid view.
* **Registration System:** One-click registration and cancellation.
* **Duplicate Prevention:** Prevents students from registering for the same event twice.
* **Visual Calendar:** (Optional) Integration with FullCalendar to view schedule.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Database:** SQLite (via SQLAlchemy ORM)
* **Frontend:** HTML5, CSS3, Jinja2 Templating
* **Utilities:** `csv` module (for export), `werkzeug` (for security)

---

## 📂 Project Structure

```text
CollegePortal/
├── app.py                  # Main application logic and routes
├── models.py               # Database models (User, Event, Registration)
├── config.py               # Configuration settings
├── instance/               # Contains the SQLite database (site.db)
├── static/
│   ├── style.css           # Global styling
│   └── uploads/            # Stores event banner images
├── templates/              # HTML files (Login, Dashboard, etc.)
└── requirements.txt        # List of dependencies
