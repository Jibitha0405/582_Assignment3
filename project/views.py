from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from project import mysql
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import re
import MySQLdb.cursors


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


@main.route('/')
def index():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM package")
    packages = cur.fetchall()
    return render_template('index.html', packages=packages)



@main.route('/admin')
def admin():
    return render_template('admin.html')

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

@main.route('/vendor_management')
def vendor_management():
    return render_template('vendor_management.html')

@main.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@main.route('/item_details')
def item_details():
    package_id = request.args.get('package_id', 1)  # default to 1

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM package WHERE id = %s", (package_id,))
    item = cur.fetchone()
    cur.close()

    if not item:
        flash("Package not found", "danger")
        return redirect(url_for('main.index'))

    photographers_list = [
        {"name": "Italo Melo"}, {"name": "Libuda Stephen"}, {"name": "Mohamed Sadiq"},
        {"name": "Nano Erdozain"}, {"name": "Rafan Barros"}, {"name": "Sindre Luis"},
        {"name": "Stefan Stefancik"}, {"name": "Suliman Sallehi"}, {"name": "Amberssona Lawrence"}
    ]
    locations_list = ["Perth", "Sydney", "Brisbane"]

    return render_template(
        'item_details.html',
        item=item,
        photographers=photographers_list,
        locations=locations_list
    )


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



# ---------------- ERROR HANDLERS ----------------

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404), 404

@main.app_errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500), 500


@main.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_name = request.form.get('item_name')
    base_price = float(request.form.get('item_base_price', 0))
    hours = float(request.form.get('hours', 1))
    total_price = base_price * hours
    package_id = request.form.get('package_id')
    selected_datetime = request.form.get('appointment_time')
    photographer = request.form.get('photographer')
    location = request.form.get('location')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT package_image_url FROM package WHERE id = %s", (package_id,))
    package = cur.fetchone()
    package_image_url = package['package_image_url'] if package else None
    cur.close()

    # Guest cart (session)
    if 'guest_cart' not in session:
        session['guest_cart'] = []

    session['guest_cart'].append({
        'package_id': package_id,
        'name': item_name,
        'price': total_price,
        'hours': hours,
        'duration': f"{hours} hour{'s' if hours > 1 else ''}",
        'photographer': photographer,
        'location': location,
        'selected_datetime': selected_datetime,
        'package_image_url': package_image_url
    })
    session.modified = True

    flash(f"{item_name} added to your booking! Total: ${total_price:.2f}", "success")
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
        # Update duration
        session['guest_cart'][index]['duration'] = new_duration
        
        # Recalculate price based on hours
        base_price = float(session['guest_cart'][index].get('base_price', 0))
        hours = int(session['guest_cart'][index].get('hours', 1))
        session['guest_cart'][index]['price'] = base_price * hours

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
            SELECT ci.id AS cart_item_id,
                   ci.price AS item_price,
                   ci.selected_datetime,
                   l.region AS location_name,
                   p.id AS package_id,
                   p.package_image_url,
                   p.description,
                   p.price AS base_price,
                   p.photography_duration,
                   ph.id AS photographer_id,
                   ph.name AS photographer_name
            FROM cart_item ci
            JOIN package p ON ci.package_id = p.id
            JOIN photographer ph ON p.photographer_id = ph.id
            LEFT JOIN location l ON ci.location_id = l.id
            JOIN cart c ON ci.cart_id = c.id
            WHERE c.user_id = %s
        """, (user_id,))
        items = cur.fetchall()
        total = sum(float(item['item_price']) for item in items) if items else 0
    else:
        # Guest: fetch cart from session and convert dicts to objects
        guest_cart = session.get('guest_cart', [])
        class CartItem:
            def __init__(self, d):
                self.package_id = d.get('package_id')
                self.name = d.get('name')
                self.price = d.get('price')
                self.hours = d.get('hours')
                self.duration = d.get('duration')
                self.photographer = d.get('photographer')
                self.location = d.get('location')
                self.selected_datetime = d.get('selected_datetime')
                self.package_image_url = d.get('package_image_url')
        items = [CartItem(item) for item in guest_cart]
        total = sum(float(item.price) for item in items) if items else 0

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
