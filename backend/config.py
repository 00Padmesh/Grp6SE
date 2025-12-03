import os

class Config:
    SECRET_KEY = "supersecretkey123"
    SQLALCHEMY_DATABASE_URI = "sqlite:///college_portal.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')