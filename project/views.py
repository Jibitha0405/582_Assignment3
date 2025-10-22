from flask import Blueprint, render_template, request, redirect, url_for, flash
from project import mysql
from werkzeug.security import generate_password_hash, check_password_hash


# Create a Blueprint instance
main = Blueprint('main', __name__)

# ---------------- ROUTES ----------------

@main.route('/', endpoint='index')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DATABASE();")
    db_name = cur.fetchone()
    cur.close()
    return render_template('index.html', db_name=db_name[0])



@main.route('/admin')
def admin():
    return render_template('admin.html')

@main.route('/vendor_gallery')
def vendor_gallery():
    return render_template('vendor_gallery.html')

@main.route('/vendor_management')
def vendor_management():
    return render_template('vendor_management.html')

@main.route('/checkout')
def checkout():
    return render_template('checkout.html')

@main.route('/item_details')
def item_details():
    return render_template('item_details.html')

@main.route('/error')
def error():
    return render_template('error.html')

@main.route('/signin_login.html')
def signin_login():
    return render_template('signin_login.html', hide_nav=True)

@main.route('/register')
def register():
    return render_template('register.html', hide_nav=True)

@main.route('/signin', methods=['GET', 'POST'])
def signin():
    error_email = None

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Password confirmation check
        if password != confirm_password:
            error_email = "Passwords do not match."
        else:
            cur = mysql.connection.cursor()
            try:
                # Check if user already exists
                cur.execute("SELECT * FROM user WHERE email = %s", (email,))
                existing_user = cur.fetchone()

                if existing_user:
                    error_email = "This email is already registered."
                else:
                    # Hash password and insert new user
                    hashed_password = generate_password_hash(password)
                    cur.execute(
                        "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)",
                        (name, email, hashed_password)
                    )
                    mysql.connection.commit()
                    flash("Sign up successful! You can now log in.", "success")
                    return redirect(url_for('main.signin_login'))
            finally:
                cur.close()

    return render_template('signin_login.html', error_email=error_email)



# Login
@main.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM user WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[0], password):
        flash("Login successful!", "success")
        return redirect(url_for('index'))
    else:
        flash("Invalid credentials", "danger")
        return redirect(url_for('login'))

# ---------------- ERROR HANDLERS ----------------

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404), 404

@main.app_errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500), 500
