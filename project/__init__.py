from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'Seema@9908'   # Replace with your MySQL password
    app.config['MYSQL_DB'] = 'IFN582_a3_database'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    app.secret_key = 'IFN582_a3'

    mysql.init_app(app)

    # Import and register blueprint
    from project.views import main
    app.register_blueprint(main)


    return app
