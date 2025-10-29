from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from project import mysql
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import re
import base64

main = Blueprint('main', __name__)

# ---------------- DASHBOARDS ----------------
@main.route('/', endpoint='customer_dashboard')
def customer_dashboard():
    cur = mysql.connection.cursor()

    cur.execute("SELECT DATABASE();")
    db_name_row = cur.fetchone()
    db_name = db_name_row['DATABASE()'] if db_name_row else "Unknown"

    cur.execute("SELECT name FROM event ORDER BY name ASC")
    events = cur.fetchall() 

    cur.close()

    return render_template('customer_dashboard.html', db_name=db_name, events=events)


@main.route('/photographer_dashboard')
def photographer_dashboard():
    photographer_id = session.get('photographer_id')

    cur = mysql.connection.cursor()
    cur.execute("SELECT DATABASE();")
    db_row = cur.fetchone()
    cur.close()

    if db_row:
        if isinstance(db_row, dict):
            db_name = list(db_row.values())[0]
        else:
            db_name = db_row[0]
    else:
        db_name = "Unknown"

    return render_template('photographer_dashboard.html', db_name=db_name)

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

            session['event_added'] = True
            return redirect(url_for('main.admin_dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM event")
    events = cur.fetchall()
    cur.close()

    event_added = session.pop('event_added', None)
    if session.pop('show_event_success', False):
        flash("Event added successfully!", "success")


    return render_template('admin_dashboard.html', events=events)

# ---------------- Admin features ----------------

@main.route('/admin/handle_request/<int:request_id>/<string:action>', methods=['POST'])
def handle_request(request_id, action):
    cur = mysql.connection.cursor()

    if action == 'approve':
        cur.execute("SELECT event_name FROM event_request WHERE id = %s", (request_id,))
        row = cur.fetchone()
        if row:
            event_name = row[0]
            cur.execute("INSERT INTO event (name) VALUES (%s)", (event_name,))
            cur.execute("UPDATE event_request SET status='Approved' WHERE id=%s", (request_id,))
    elif action == 'reject':
        cur.execute("UPDATE event_request SET status='Rejected' WHERE id=%s", (request_id,))

    mysql.connection.commit()
    cur.close()

    flash("Event request has been processed.", "success")
    return redirect(url_for('main.admin_event_requests'))

@main.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM event WHERE id = %s", (event_id,))
        mysql.connection.commit()
        flash("Event deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting event: {str(e)}", "danger")
    finally:
        cur.close()

    return redirect(url_for('main.admin_dashboard'))

# @main.route('/admin_dashboard')
# def admin_dashboard():
#     return render_template('admin_dashboard.html')

# ---------------- Customer features ----------------
@main.route('/customer_profile')
def customer_profile():
    return render_template('customer_profile.html')

@main.route('/index_old')
def index_old():
    return render_template('index_old.html')

@main.route('/vendor_gallery')
def vendor_gallery():
    return render_template('vendor_gallery.html')

@main.route('/checkout')
def checkout():
    return render_template('checkout.html')

@main.route('/item_details')
def item_details():
    return render_template('item_details.html')

# ---------------- Photographer features ----------------
@main.route('/add_service', methods=['POST'])
def add_service():
    photographer_id = session.get('photographer_id')
    if not photographer_id:
        flash("Login required to add a service.", "danger")
        return redirect(url_for('photographer_dashboard'))

    event_id = request.form['event_id']
    hours = request.form['hours']
    price = request.form['price']
    description = request.form['description']
    photo = request.files.get('photo')

    photo_data = photo.read() if photo else None

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO package (photographer_id, event_id, package_image, description, price, photography_duration)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (photographer_id, event_id, photo_data, description, price, hours))

    mysql.connection.commit()
    cur.close()
    flash("Service added successfully!", "success")

    return redirect(url_for('photographer_dashboard'))

@main.route('/admin/event_requests')
def admin_event_requests():
    cur = mysql.connection.cursor(dictionary=True)
    cur.execute("""
        SELECT er.*, p.name AS photographer_name 
        FROM event_request er
        JOIN photographer p ON er.photographer_id = p.id
        ORDER BY er.created_at DESC
    """)
    requests = cur.fetchall()
    cur.close()
    return render_template('admin_event_requests.html', requests=requests)

# @main.route('/request_event', methods=['GET', 'POST'])
# def request_event():
#     photographer_id = session.get('photographer_id')

#     if request.method == 'POST':
#         event_name = request.form.get('event_name')

#         if not event_name:
#             flash("Please enter an event name.", "warning")
#             return redirect(url_for('main.request_event'))

#         cur = mysql.connection.cursor()
#         try:
#             cur.execute("""
#                 INSERT INTO event_request (photographer_id, event_name, status)
#                 VALUES (%s, %s, 'Pending')
#             """, (photographer_id, event_name))
#             mysql.connection.commit()
#             flash("Your event request has been sent to admin.", "info")
#         except Exception as e:
#             mysql.connection.rollback()
#             flash(f"Error submitting request: {e}", "danger")
#         finally:
#             cur.close()

#         return redirect(url_for('main.photographer_dashboard'))

#     return render_template('request_event.html')

# ---------------- ROUTES ----------------

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

        name_regex = r"^[A-Za-z]+(?: [A-Za-z]+)*$"
        if not re.match(name_regex, name):
            error_name = "Username must contain only letters and be 2–50 letters long."

        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            error_email = "Invalid email format."

        elif password != confirm_password:
            error_password = "Passwords do not match."

        else:
            cur = mysql.connection.cursor()
            try:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                existing_user = cur.fetchone()

                if existing_user:
                    error_email = "This email is already registered."
                else:
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()

                    cur.execute(
                        "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                        (name, email, hashed_password, role)
                    )
                    mysql.connection.commit()
                    user_id = cur.lastrowid

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

@main.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cur = mysql.connection.cursor()
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

        session['user_id'] = user_id
        session['user_name'] = user_name
        session['user_role'] = user_role
        session['logged_in'] = True

        print("User role is:", user_id, user_name, user_role)

        flash("Login successful!", "success")

        if user_role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        elif user_role == 'photographer':
            return redirect(url_for('main.photographer_dashboard'))
        else:
            return redirect(url_for('main.customer_dashboard'))  # customer home
    else:
        flash("Invalid email or password", "danger")
        return redirect(url_for('main.signin_login'))

@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('main.signin_login'))

@main.route('/signin_login.html')
def signin_login():
    return render_template('signin_login.html', hide_nav=True)

# ---------------- ERROR HANDLERS ----------------

@main.route('/error')
def error():
    return render_template('error.html')

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404), 404

@main.app_errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500), 500


