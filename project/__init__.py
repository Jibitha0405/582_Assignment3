from flask import Flask
from flask_mysqldb import MySQL

# Initialize MySQL
mysql = MySQL()

def create_app():
    app = Flask(__name__)

    # MySQL Configuration
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'Seema@9908'  # Replace with your MySQL password
    app.config['MYSQL_DB'] = 'IFN582_a3_database'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    # Secret Key for Sessions (required for cart/checkout session data)
    app.secret_key = 'IFN582_a3'

    # Initialize MySQL with app
    mysql.init_app(app)

    # Register Blueprints
    from project.views import main
    app.register_blueprint(main)

    return app
