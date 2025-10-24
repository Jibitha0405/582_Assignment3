from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from project import mysql
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

main = Blueprint('main', __name__)

@main.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DATABASE();")
    db_name_row = cur.fetchone()
    cur.close()
    db_name = db_name_row['DATABASE()'] if db_name_row else "Unknown"
    return render_template('index.html', db_name=db_name)

@main.route('/admin')
def admin():
    return render_template('admin.html')

@main.route('/customer_profile')
def customer_profile():
    return render_template('customer_profile.html')

@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('main.index'))

@main.route('/index_old')
def index_old():
    return render_template('index_old.html')

@main.route('/vendor_gallery')
def vendor_gallery():
    return render_template('vendor_gallery.html')

@main.route('/vendor_management')
def vendor_management():
    return render_template('vendor_management.html')

@main.route('/item_details')
def item_details():
    return render_template('item_details.html')

@main.route('/error')
def error():
    return render_template('error.html')

@main.route('/signin', methods=['GET', 'POST'])
def signin():
    error_email = None
    error_password = None

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            error_password = "Passwords do not match."
        else:
            cur = mysql.connection.cursor()
            try:
                cur.execute("SELECT * FROM user WHERE email = %s", (email,))
                existing_user = cur.fetchone()
                if existing_user:
                    error_email = "This email is already registered."
                else:
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    cur.execute(
                        "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)",
                        (name, email, hashed_password)
                    )
                    mysql.connection.commit()
                    flash("Sign up successful! You can now log in.", "success")
                    return redirect(url_for('main.signin_login'))
            finally:
                cur.close()

    return render_template('signin_login.html', error_email=error_email, error_password=error_password)


@main.route('/signin_login.html')
def signin_login():
    return render_template('signin_login.html', hide_nav=True)


@main.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM user WHERE email=%s AND password=%s", (email, hashed_password))
    user = cur.fetchone()
    cur.close()

    if user:
        user_id, user_name = user
        session['user_id'] = user_id
        session['user_name'] = user_name
        session['logged_in'] = True
        flash("Login successful!", "success")
        return redirect(url_for('main.index'))
    else:
        flash("Invalid email or password", "danger")
        return redirect(url_for('main.signin_login'))

@main.route('/checkout')
def checkout():
    """
    Instead of showing a cart, directly show checkout.
    """
    cur = mysql.connection.cursor()

    # Get user's cart items if needed (optional)
    user_id = session.get('user_id')
    items = []
    total = 0

    if user_id:
        cur.execute("""
            SELECT p.name, p.price, l.region, c.id AS cart_id
            FROM cart_item ci
            JOIN package p ON ci.package_id = p.id
            LEFT JOIN location l ON ci.location_id = l.id
            JOIN cart c ON ci.cart_id = c.id
            WHERE c.user_id = %s
        """, (user_id,))
        items = cur.fetchall()
        total = sum([float(item['price']) for item in items]) if items else 0

    cur.close()

    return render_template('checkout.html', items=items, total=total)

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404), 404

@main.app_errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500), 500
