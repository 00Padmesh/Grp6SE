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
        
        
        unique_id = request.form.get("unique_id") 
        if not unique_id:
            unique_id = None
        if role == "participant":
            if not unique_id:
                flash("Student ID is required for participants")
                return redirect(url_for("signup"))
            
            
            existing_student = User.query.filter_by(unique_id=unique_id).first()
            if existing_student:
                flash("This Student ID is already registered! Please login.")
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


@app.route("/dashboard/organizer", methods=["GET", "POST"])
@login_required
def dashboard_organizer():
    if current_user.role != "organizer":
        return "Access Denied"
    
    if request.method == "POST":
        name = request.form["name"]
        start_date = request.form["start_date"] 
        end_date = request.form["end_date"]     
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        desc = request.form["description"]
        if end_date < start_date:
            flash("Error: End date cannot be before Start date!")
            return redirect(url_for("dashboard_organizer"))
       
        image_filename = 'default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            
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
    
    
    all_events = Event.query.all()
    return render_template("dashboard_organizer.html", events=all_events)


@app.route("/participants/<int:event_id>")
@login_required
def view_participants(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        return "Access Denied"
    return render_template("view_participants.html", event=event)


@app.route("/download_participants/<int:event_id>")
@login_required
def download_participants(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        return "Access Denied"

    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Name', 'Student ID', 'Email'])
    
    for reg in event.registrations:
        writer.writerow([reg.student.name, reg.student.unique_id, reg.student.email])
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=participants_{event.id}.csv"}
    )

@app.route("/dashboard/student")
@login_required
def dashboard_student():
    if current_user.role != "participant":
        return "Access Denied"
    
    all_events = Event.query.all()
    
    my_registrations = Registration.query.filter_by(student_id=current_user.id).all()
    my_event_ids = [r.event_id for r in my_registrations]
    my_events_list = [Event.query.get(id) for id in my_event_ids]
    
    return render_template("dashboard_student.html", 
                         events=all_events, 
                         my_event_ids=my_event_ids, 
                         my_events_list=my_events_list)

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




@app.route("/event/edit/<int:event_id>", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    
    if event.organizer_id != current_user.id:
        return "Access Denied"

    if request.method == "POST":
        
        event.name = request.form["name"]
        event.start_date = request.form["start_date"]
        event.end_date = request.form["end_date"]
        event.start_time = request.form["start_time"]
        event.end_time = request.form["end_time"]
        event.description = request.form["description"]

        
        if event.end_date < event.start_date:
            flash("Error: End date cannot be before Start date!")
            return redirect(url_for('edit_event', event_id=event.id))

        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                event.image_file = filename

        db.session.commit()
        flash("Event Updated Successfully!")
        return redirect(url_for("dashboard_organizer"))

    return render_template("edit_event.html", event=event)
if __name__ == "__main__":
    app.run(debug=True)