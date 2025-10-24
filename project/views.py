from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from project import mysql
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

main = Blueprint('main', __name__)


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
    
@main.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    # Get data from the form
    item_name = request.form.get('item_name')
    item_price = float(request.form.get('item_price', 0))
    item_duration = request.form.get('item_duration')
    package_id = request.form.get('package_id')  # for DB cart if logged-in

    user_id = session.get('user_id')
    cur = mysql.connection.cursor()

    if user_id:
        # Logged-in user: ensure cart exists
        cur.execute("SELECT id FROM cart WHERE user_id=%s", (user_id,))
        cart = cur.fetchone()
        if not cart:
            cur.execute("INSERT INTO cart (user_id) VALUES (%s)", (user_id,))
            mysql.connection.commit()
            cart_id = cur.lastrowid
        else:
            cart_id = cart['id']

        # Add item to cart_item table
        cur.execute(
            "INSERT INTO cart_item (cart_id, package_id) VALUES (%s, %s)",
            (cart_id, package_id)
        )
        mysql.connection.commit()
    else:
        # Guest cart stored in session
        if 'guest_cart' not in session:
            session['guest_cart'] = []
        session['guest_cart'].append({
            'name': item_name,
            'price': item_price,
            'duration': item_duration
        })
        session.modified = True

    cur.close()
    flash(f"{item_name} added to your booking!", "success")
    return redirect(url_for('main.checkout'))

@main.route('/remove_cart_item', methods=['POST'])
def remove_cart_item():
    index = int(request.form.get('item_index'))

    if 'guest_cart' in session:
        session['guest_cart'].pop(index)
        session.modified = True
        flash("Item removed from cart!", "info")

    return redirect(url_for('main.checkout'))

@main.route('/update_cart_item', methods=['POST'])
def update_cart_item():
    index = int(request.form.get('item_index'))
    new_duration = request.form.get('item_duration')

    if 'guest_cart' in session:
        session['guest_cart'][index]['duration'] = new_duration
        session.modified = True
        flash("Item updated successfully!", "success")

    return redirect(url_for('main.checkout'))

# Clear basket
@main.route('/clear_cart', methods=['POST'])
def clear_cart():
    session['guest_cart'] = []
    session.modified = True
    flash("Cart cleared.", "info")
    return redirect(url_for('main.checkout'))

@main.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user_id = session.get('user_id')
    items = []
    total = 0
    cur = mysql.connection.cursor()

    if user_id:
        # Logged-in user: fetch cart from database
        cur.execute("""
            SELECT p.id AS package_id, p.name, p.price, p.description,
                   l.region, ci.selected_datetime
            FROM cart_item ci
            JOIN package p ON ci.package_id = p.id
            LEFT JOIN location l ON ci.location_id = l.id
            JOIN cart c ON ci.cart_id = c.id
            WHERE c.user_id = %s
        """, (user_id,))
        items = cur.fetchall()
        total = sum(float(item['price']) for item in items) if items else 0
    else:
        # Guest: fetch cart from session
        guest_cart = session.get('guest_cart', [])
        items = guest_cart
        total = sum(float(item['price']) for item in items) if items else 0

    if request.method == 'POST':
        # Process checkout
        full_name = request.form.get('full_name')
        address = request.form.get('address')
        suburb = request.form.get('suburb')
        region = request.form.get('region')
        postcode = request.form.get('postcode')
        email = request.form.get('email')
        country_code = request.form.get('country_code')
        phone = request.form.get('phone')
        payment_method = request.form.get('payment_method')
        total_amount = total  # no service fee

        # Insert order into database
        cur.execute("""
            INSERT INTO orders 
            (user_id, full_name, address, suburb, region, postcode, email, phone, payment_method, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id if user_id else None, full_name, address, suburb, region, postcode,
              email, f"{country_code} {phone}", payment_method, total_amount))
        mysql.connection.commit()

        # Clear cart
        if user_id:
            cur.execute("""
                DELETE ci FROM cart_item ci
                JOIN cart c ON ci.cart_id = c.id
                WHERE c.user_id = %s
            """, (user_id,))
            mysql.connection.commit()
        else:
            session['guest_cart'] = []

        flash("Payment processed successfully! Thank you for your order.", "success")
        cur.close()
        return redirect(url_for('main.index'))

    cur.close()
    return render_template('checkout.html', items=items, total=total)

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404), 404

@main.app_errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500), 500
