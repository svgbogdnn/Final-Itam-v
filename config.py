import os

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:1234@localhost/dbitam"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret")