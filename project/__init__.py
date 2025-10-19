from flask import Flask

# Create Flask app instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # optional but recommended

# Import routes after creating the app
from project import views
