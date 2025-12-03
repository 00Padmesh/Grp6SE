import os
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, Event, Registration

app = Flask(__name__)
app.config.from_object(Config)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route("/")
def index():
    return render_template("index.html")

ORGANIZER_CODE = "fest2025"

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]         # NEW
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]
        
        # Logic for ID: Required for Students, Optional for Organizers
        unique_id = request.form.get("unique_id") 
        if role == "participant" and not unique_id:
            flash("Student ID is required for participants")
            return redirect(url_for("signup"))

        if role == "organizer":
            if request.form.get("secret_code") != ORGANIZER_CODE:
                flash("Wrong Organizer Code!")
                return redirect(url_for("signup"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists")
            return redirect(url_for("signup"))
            
        user = User(name=name, unique_id=unique_id, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please login.")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == "organizer":
                return redirect(url_for("dashboard_organizer"))
            else:
                return redirect(url_for("dashboard_student"))
        else:
            flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# --- ORGANIZER DASHBOARD ---
@app.route("/dashboard/organizer", methods=["GET", "POST"])
@login_required
def dashboard_organizer():
    if current_user.role != "organizer":
        return "Access Denied"
    
    if request.method == "POST":
        name = request.form["name"]
        start_date = request.form["start_date"] # CHANGED
        end_date = request.form["end_date"]     # NEW
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        desc = request.form["description"]
        
        # Image Upload Handling (Optional now)
        image_filename = 'default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            # Check if user actually uploaded a file (filename will be empty if not)
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        new_event = Event(
            name=name, start_date=start_date, end_date=end_date, 
            start_time=start_time, end_time=end_time,
            description=desc, image_file=image_filename, organizer_id=current_user.id
        )
        db.session.add(new_event)
        db.session.commit()
        flash("Event Created Successfully!")
    
    my_events = Event.query.filter_by(organizer_id=current_user.id).all()
    return render_template("dashboard_organizer.html", events=my_events)

# --- VIEW PARTICIPANTS ROUTE (NEW) ---
@app.route("/participants/<int:event_id>")
@login_required
def view_participants(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        return "Access Denied"
    return render_template("view_participants.html", event=event)

# --- DOWNLOAD CSV ROUTE (NEW) ---
@app.route("/download_participants/<int:event_id>")
@login_required
def download_participants(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        return "Access Denied"

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow(['Name', 'Student ID', 'Email'])
    
    # Data rows
    for reg in event.registrations:
        writer.writerow([reg.student.name, reg.student.unique_id, reg.student.email])
    
    # Prepare response
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=participants_{event.id}.csv"}
    )

# --- STUDENT DASHBOARD ---
@app.route("/dashboard/student")
@login_required
def dashboard_student():
    if current_user.role != "participant":
        return "Access Denied"
    
    all_events = Event.query.all()
    my_registrations = Registration.query.filter_by(student_id=current_user.id).all()
    my_event_ids = [r.event_id for r in my_registrations]
    
    return render_template("dashboard_student.html", events=all_events, my_event_ids=my_event_ids)

@app.route("/register/<int:event_id>")
@login_required
def register_event(event_id):
    if current_user.role != "participant":
        return "Access Denied"
        
    exists = Registration.query.filter_by(student_id=current_user.id, event_id=event_id).first()
    if exists:
        flash("You are already registered!")
    else:
        new_reg = Registration(student_id=current_user.id, event_id=event_id)
        db.session.add(new_reg)
        db.session.commit()
        flash("Successfully registered!")
        
    return redirect(url_for("dashboard_student"))

@app.route("/unregister/<int:event_id>")
@login_required
def unregister_event(event_id):
    if current_user.role != "participant":
        return "Access Denied"
    reg = Registration.query.filter_by(student_id=current_user.id, event_id=event_id).first()
    if reg:
        db.session.delete(reg)
        db.session.commit()
        flash("Registration revoked successfully.")
    else:
        flash("You were not registered for this event.")
    return redirect(url_for("dashboard_student"))

@app.route("/event/delete/<int:event_id>", methods=["POST"])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        return "Access Denied"
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted")
    return redirect(url_for("dashboard_organizer"))

if __name__ == "__main__":
    app.run(debug=True)