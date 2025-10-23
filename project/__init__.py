from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus

# ---------------------------
# CREATE FLASK APP
# ---------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # optional but recommended

# ---------------------------
# DATABASE CONFIGURATION
# ---------------------------
DB_USER = 'root'
DB_PASS = 'Seema@9908'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'IFN582_a3_database'

# Encode special characters in password
password_quoted = quote_plus(DB_PASS)

# Set the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{password_quoted}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ---------------------------
# INITIALIZE SQLALCHEMY
# ---------------------------
db = SQLAlchemy(app)

# ---------------------------
# IMPORT VIEWS AND MODELS
# ---------------------------
from project import views
from project import models
