from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from project import mysql
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import re

# Create a Blueprint instance
main = Blueprint('main', __name__)

# ---------------- DASHBOARDS ----------------

@main.route('/', endpoint='customer_dashboard')
def customer_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DATABASE();")
    db_name_row = cur.fetchone()  # Returns a tuple like ('your_db_name',)
    cur.close()

    if db_name_row:
        db_name = db_name_row['DATABASE()']  # Access the first element of the tuple
    else:
        db_name = "Unknown"

    return render_template('customer_dashboard.html', db_name=db_name)


@main.route('/photographer_dashboard')
def photographer_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DATABASE();")
    db_name_row = cur.fetchone()
    cur.close()

    if db_name_row:
        db_name = db_name_row['DATABASE()']
    else:
        db_name = "Unknown"

    return render_template('photographer_dashboard.html', db_name=db_name)


# ---------------- ROUTES ----------------


@main.route('/customer_profile')
def customer_profile():
    return render_template('customer_profile.html')

@main.route('/logout')
def logout():
    # Clear all session data
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('main.customer_dashboard'))

@main.route('/index_old')
def index_old():
    return render_template('index_old.html')


@main.route('/vendor_gallery')
def vendor_gallery():
    return render_template('vendor_gallery.html')

# @main.route('/admin_dashboard')
# def admin_dashboard():
#     return render_template('admin_dashboard.html')

@main.route('/checkout')
def checkout():
    return render_template('checkout.html')

@main.route('/item_details')
def item_details():
    return render_template('item_details.html')

@main.route('/error')
def error():
    return render_template('error.html')

# Signin/Login Page
@main.route('/signin_login.html')
def signin_login():
    return render_template('signin_login.html', hide_nav=True)

# ---------------- SIGN UP ----------------
@main.route('/signin', methods=['GET', 'POST'])
def signin():
    error_email = None
    error_password = None
    error_name = None

    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role_signup')

        # --- NAME VALIDATION (Only letters, 2–50 chars) ---
        name_regex = r"^[A-Za-z]{2,50}$"
        if not re.match(name_regex, name):
            error_name = "Username must contain only letters and be 2–50 letters long."

        # --- EMAIL FORMAT VALIDATION ---
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            error_email = "Invalid email format."

        # --- PASSWORD MATCH VALIDATION ---
        elif password != confirm_password:
            error_password = "Passwords do not match."

        else:
            cur = mysql.connection.cursor()
            try:
                # Check if email already exists
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                existing_user = cur.fetchone()

                if existing_user:
                    error_email = "This email is already registered."
                else:
                    # Hash password
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()

                    # Insert into users table
                    cur.execute(
                        "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                        (name, email, hashed_password, role)
                    )
                    mysql.connection.commit()
                    user_id = cur.lastrowid

                    # Role-specific table
                    if role == 'customer':
                        cur.execute("INSERT INTO customer (user_id) VALUES (%s)", (user_id,))
                    elif role == 'photographer':
                        cur.execute("INSERT INTO photographer (user_id) VALUES (%s)", (user_id,))

                    mysql.connection.commit()
                    flash("Sign up successful! You can now log in.", "success")
                    return redirect(url_for('main.signin_login'))
            finally:
                cur.close()

    return render_template(
        'signin_login.html',
        error_email=error_email,
        error_password=error_password,
        error_name=error_name
    )





# ---------------- LOGIN ----------------
@main.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Hash the input password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cur = mysql.connection.cursor()
    # Query to check email and password
    cur.execute(
        "SELECT id, name, role FROM users WHERE email=%s AND password_hash=%s",
        (email, hashed_password)
    )
    user = cur.fetchone()
    cur.close()

    if user:
        user_id = user['id']
        user_name = user['name']
        user_role = user['role']

        # Save session info
        session['user_id'] = user_id
        session['user_name'] = user_name
        session['user_role'] = user_role
        session['logged_in'] = True

        print("User role is:", user_id, user_name, user_role)

        flash("Login successful!", "success")

        # Redirect based on role
        if user_role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        elif user_role == 'photographer':
            return redirect(url_for('main.photographer_dashboard'))
        else:
            return redirect(url_for('main.customer_dashboard'))  # customer home
    else:
        flash("Invalid email or password", "danger")
        return redirect(url_for('main.signin_login'))

@main.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        event_name = request.form.get('event_name', '').strip()

        if not event_name:
            flash("Event name cannot be empty.", "danger")
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO event (name) VALUES (%s)", (event_name,))
            mysql.connection.commit()
            cur.close()

            # Use session flag to track successful add
            session['event_added'] = True
            return redirect(url_for('main.admin_dashboard'))

    # Retrieve events
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM event")
    events = cur.fetchall()
    cur.close()

    # Check session flag
    event_added = session.pop('event_added', None)
        # Show success only when redirected from event submission
    if session.pop('show_event_success', False):
        flash("Event added successfully!", "success")


    return render_template('admin_dashboard.html', events=events)




# ---------------- ERROR HANDLERS ----------------

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404), 404

@main.app_errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500), 500


