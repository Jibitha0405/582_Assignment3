from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from project import mysql
import hashlib
import re
import MySQLdb.cursors

# Create a Blueprint instance
main = Blueprint('main', __name__)


def get_customer_id(user_id):
    """Return the customer_id for a logged-in user, or create one if missing."""
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id FROM customer WHERE user_id=%s", (user_id,))
    row = cur.fetchone()
    if row:
        customer_id = row['id']
    else:
        # Create customer row if missing
        cur.execute("INSERT INTO customer (user_id) VALUES (%s)", (user_id,))
        mysql.connection.commit()
        customer_id = cur.lastrowid
    cur.close()
    return customer_id

def get_cart_id(customer_id):
    """Return the cart_id for a customer, create if missing."""
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id FROM cart WHERE customer_id=%s", (customer_id,))
    row = cur.fetchone()
    if row:
        cart_id = row['id']
    else:
        cur.execute("INSERT INTO cart (customer_id) VALUES (%s)", (customer_id,))
        mysql.connection.commit()
        cart_id = cur.lastrowid
    cur.close()
    return cart_id


@main.route('/', endpoint='customer_dashboard')
def customer_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DATABASE();")
    db_name_row = cur.fetchone()
    cur.close()

    if db_name_row:
        db_name = db_name_row['DATABASE()']
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

@main.route('/index')
def index():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch all photographers and their info
    cur.execute("""
        SELECT p.id AS photographer_id,
               u.name AS photographer_name,
               CONCAT(l.address_line, ', ', l.region, ' ', l.postcode) AS location,
               pf.featured_image AS image
        FROM photographer p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN location l ON p.location_id = l.id
        LEFT JOIN portfolio pf ON pf.photographer_id = p.id
        JOIN package pkg ON pkg.photographer_id = p.id
    """)
    photographers = cur.fetchall()
    cur.close()

    # Pass filters and active badges
    locations = ['Brisbane', 'Sydney', 'Perth']
    events = ['Wedding', 'Engagement', 'Baptism', 'Birthday']
    price_ranges = ['$100 - $500', '$501 - $1000', '$1001 - $1500']
    active_filters = ['Sydney', 'Wedding', '$501 - $1000']  # example, can be dynamic later

    return render_template(
        'index.html',
        photographers=photographers,
        locations=locations,
        events=events,
        price_ranges=price_ranges,
        active_filters=active_filters
    )


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
    return redirect(url_for('main.customer_dashboard'))


@main.route('/index_old')
def index_old():
    return render_template('index_old.html')


@main.route('/vendor_gallery')
def vendor_gallery():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT p.id AS package_id,
               p.package_image_url,
               p.description,
               p.price,
               p.photography_duration,
               e.name AS event_name,
               ph.id AS photographer_id,
               u.name AS photographer_name
        FROM package p
        JOIN event e ON p.event_id = e.id
        JOIN photographer ph ON p.photographer_id = ph.id
        JOIN users u ON ph.user_id = u.id
    """)
    packages = cur.fetchall()
    cur.close()

    return render_template('vendor_gallery.html', packages=packages)


@main.route('/vendor_management')
def vendor_management():
    return render_template('vendor_management.html')


@main.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')
    
@main.route('/item_details')
def item_details():
    package_id = request.args.get('package_id', 1)
    cart_item_id = request.args.get('cart_item_id')
    edit_index = request.args.get('edit_index')  # for guest cart

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM package WHERE id=%s", (package_id,))
    item = cur.fetchone()
    if not item:
        flash("Package not found", "danger")
        cur.close()
        return redirect(url_for('main.index'))

    cart_item = None

    # Logged-in user
    if cart_item_id:
        cur.execute("SELECT * FROM cart_item WHERE id=%s", (cart_item_id,))
        cart_item = cur.fetchone()

    cur.close()

    # Guest user
    if not cart_item and edit_index is not None:
        guest_cart = session.get('guest_cart', [])
        try:
            edit_index = int(edit_index)
            cart_item = guest_cart[edit_index]
        except (IndexError, ValueError):
            flash("Invalid item to edit", "warning")
            return redirect(url_for('main.checkout'))

    photographers_list = [
        {"name": "Italo Melo"}, {"name": "Libuda Stephen"}, {"name": "Mohamed Sadiq"},
        {"name": "Nano Erdozain"}, {"name": "Rafan Barros"}, {"name": "Sindre Luis"},
        {"name": "Stefan Stefancik"}, {"name": "Suliman Sallehi"}, {"name": "Amberssona Lawrence"}
    ]
    locations_list = ["Perth", "Sydney", "Brisbane"]
    dynamic_hours = list(range(1, 13))

    return render_template(
        'item_details.html',
        item=item,
        cart_item=cart_item,
        photographers=photographers_list,
        locations=locations_list,
        dynamic_hours=dynamic_hours
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

        name_regex = r"^[A-Za-z]{2,50}$"
        if not re.match(name_regex, name):
            error_name = "Username must contain only letters and be 2–50 letters long."
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            error_email = "Invalid email format."
        elif password != confirm_password:
            error_password = "Passwords do not match."
        else:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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


# ---------------- LOGIN ----------------
@main.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(
        "SELECT id, name, role FROM users WHERE email=%s AND password_hash=%s",
        (email, hashed_password)
    )
    user = cur.fetchone()

    if user:
        user_id = user['id']
        user_name = user['name']
        user_role = user['role']

        session['user_id'] = user_id
        session['user_name'] = user_name
        session['user_role'] = user_role
        session['logged_in'] = True

        flash("Login successful!", "success")

        # ---------------- MERGE GUEST CART ----------------
        guest_cart = session.get('guest_cart', [])
        if guest_cart:
            cur.execute("SELECT id FROM customer WHERE user_id=%s", (user_id,))
            customer_row = cur.fetchone()
            if not customer_row:
                cur.execute("INSERT INTO customer (user_id) VALUES (%s)", (user_id,))
                mysql.connection.commit()
                customer_id = cur.lastrowid
            else:
                customer_id = customer_row['id']

            cur.execute("SELECT id FROM cart WHERE customer_id=%s", (customer_id,))
            cart = cur.fetchone()
            if not cart:
                cur.execute("INSERT INTO cart (customer_id) VALUES (%s)", (customer_id,))
                mysql.connection.commit()
                cart_id = cur.lastrowid
            else:
                cart_id = cart['id']

            for item in guest_cart:
                location_name = item.get('location')  # safely get location
                photographer_name = item.get('photographer')

                location_id = None
                if location_name:
                    cur.execute("SELECT id FROM location WHERE region=%s OR address_line=%s LIMIT 1", (location_name, location_name))
                    location_row = cur.fetchone()
                    location_id = location_row['id'] if location_row else None


                cur.execute("""
                    INSERT INTO cart_item (cart_id, package_id, price, hours, selected_datetime, location_id, photographer_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    cart_id,
                    item.get('package_id'),
                    item.get('price'),
                    item.get('hours', 1),
                    item.get('selected_datetime'),
                    location_id,
                    photographer_name
                ))


            mysql.connection.commit()
            session.pop('guest_cart', None)
    else:
        flash("Invalid email or password", "danger")
        cur.close()
        return redirect(url_for('main.signin_login'))

    cur.close()

    if user_role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    elif user_role == 'photographer':
        return redirect(url_for('main.photographer_dashboard'))
    else:
        return redirect(url_for('main.customer_dashboard'))
@main.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user_id = session.get('user_id')
    items = []

    if user_id:
        customer_id = get_customer_id(user_id)
        if customer_id:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT id FROM cart WHERE customer_id=%s", (customer_id,))
            cart_row = cur.fetchone()
            if cart_row:
                cart_id = cart_row['id']
                cur.execute("""
                    SELECT ci.id AS cart_item_id,
                           ci.price AS item_price,
                           ci.hours,
                           ci.selected_datetime,
                           ci.photographer_name AS photographer,
                           COALESCE(CONCAT(l.address_line, ', ', l.region, ' ', l.postcode), '') AS location,
                           p.id AS package_id,
                           p.package_image_url,
                           p.description
                    FROM cart_item ci
                    JOIN cart c ON ci.cart_id = c.id
                    JOIN package p ON ci.package_id = p.id
                    LEFT JOIN location l ON ci.location_id = l.id
                    WHERE c.customer_id = %s
                """, (customer_id,))
                fetched_items = cur.fetchall()
                
                # Convert dicts to objects
                class CartItemObj:
                    def __init__(self, d):
                        self.id = d['cart_item_id']
                        self.price = d['item_price']
                        self.hours = d['hours']
                        self.photographer = d['photographer']
                        self.location = d['location']
                        self.package_id = d['package_id']
                        self.package_image_url = d['package_image_url']
                        self.description = d['description']
                        self.selected_datetime = d['selected_datetime']
                
                items = [CartItemObj(item) for item in fetched_items]

            cur.close()
        total = sum(item.price * item.hours for item in items)

    else:
        # Guest cart
        guest_cart = session.get('guest_cart', [])
        class CartItem:
            def __init__(self, d):
                self.package_id = d.get('package_id')
                self.name = d.get('name')
                self.price = d.get('price')
                self.hours = d.get('hours', 1)
                self.duration = d.get('duration')
                self.photographer = d.get('photographer')
                self.location = d.get('location')
                self.selected_datetime = d.get('selected_datetime')
                self.package_image_url = d.get('package_image_url')
        items = [CartItem(item) for item in guest_cart]
        total = sum(item.price * item.hours for item in items)

    if request.method == 'POST':
        flash("Payment processed successfully!", "success")
        if user_id:
            cur = mysql.connection.cursor()
            cur.execute("""
                DELETE ci FROM cart_item ci
                JOIN cart c ON ci.cart_id = c.id
                WHERE c.customer_id = %s
            """, (customer_id,))
            mysql.connection.commit()
            cur.close()
        else:
            session['guest_cart'] = []
        return redirect(url_for('main.index'))

    return render_template('checkout.html', items=items, total=total)


@main.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_name = request.form.get('item_name')
    package_id = request.form.get('package_id')
    base_price = request.form.get('item_base_price', 0)

    # Optional fields
    hours = request.form.get('hours')  # may be None if from gallery
    photographer = request.form.get('photographer') or None
    location = request.form.get('location') or None
    selected_datetime = request.form.get('appointment_time') or None

    # Convert to correct types / defaults
    try:
        base_price = float(base_price)
    except ValueError:
        base_price = 0.0
    try:
        hours = float(hours) if hours else 1
    except ValueError:
        hours = 1

    total_price = base_price * hours

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT package_image_url FROM package WHERE id = %s", (package_id,))
    package = cur.fetchone()
    package_image_url = package['package_image_url'] if package else None
    cur.close()

    if session.get('logged_in'):
        user_id = session['user_id']
        customer_id = get_customer_id(user_id)
        cart_id = get_cart_id(customer_id)

        cart_item_id = request.form.get('cart_item_id')  # coming from item_details edit form
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        photographer_name = photographer or ""
        location_name = location or ""

        # Lookup location_id if selected
        location_id = None
        if location_name:
            cur.execute(
                "SELECT id FROM location WHERE region=%s OR address_line=%s LIMIT 1",
                (location_name, location_name)
            )
            row = cur.fetchone()
            location_id = row['id'] if row else None

        if cart_item_id:
            # UPDATE existing item
            cur.execute("""
                UPDATE cart_item
                SET price=%s, hours=%s, selected_datetime=%s, location_id=%s, photographer_name=%s
                WHERE id=%s
            """, (total_price, hours, selected_datetime, location_id, photographer_name, cart_item_id))
            flash("Item updated successfully!", "success")
        else:
            # INSERT new item
            cur.execute("""
                INSERT INTO cart_item 
                    (cart_id, package_id, price, hours, selected_datetime, location_id, photographer_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (cart_id, package_id, total_price, hours, selected_datetime, location_id, photographer_name))
            flash(f"{item_name} added to your booking! Total: ${total_price:.2f}", "success")

        mysql.connection.commit()
        cur.close()



    else:
        # Guest cart
        if 'guest_cart' not in session:
            session['guest_cart'] = []

        exists = any(i['package_id'] == package_id and i.get('selected_datetime') == selected_datetime
                     for i in session['guest_cart'])
        if not exists:
            session['guest_cart'].append({
                'package_id': package_id,
                'name': item_name,
                'price': total_price,
                'hours': hours,
                'duration': f"{hours} hour{'s' if hours > 1 else ''}" if hours else "",
                'photographer': photographer,
                'location': location,
                'selected_datetime': selected_datetime,
                'package_image_url': package_image_url
            })
            session.modified = True

    flash(f"{item_name} added to your booking! Total: ${total_price:.2f}", "success")
    return redirect(url_for('main.checkout'))



@main.route('/clear_cart', methods=['POST'])
def clear_cart():
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()
    if user_id:
        customer_id = get_customer_id(user_id)
        cur.execute("""
            DELETE ci FROM cart_item ci
            JOIN cart c ON ci.cart_id = c.id
            WHERE c.customer_id = %s
        """, (customer_id,))
        mysql.connection.commit()
    else:
        session.pop('guest_cart', None)
    cur.close()
    flash("Cart cleared successfully.", "info")
    return redirect(url_for('main.checkout'))

@main.route('/remove_cart_item', methods=['POST'])
def remove_cart_item():
    index = int(request.form.get('item_index', -1))  # for guest
    user_id = session.get('user_id')

    if user_id:
        # Signed-in user: remove from database
        customer_id = get_customer_id(user_id)
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Get the cart_id
        cur.execute("SELECT id FROM cart WHERE customer_id=%s", (customer_id,))
        cart = cur.fetchone()
        if not cart:
            flash("No cart found.", "warning")
            return redirect(url_for('main.checkout'))
        cart_id = cart['id']

        # Get the cart item ID by index
        cur.execute("""
            SELECT id FROM cart_item 
            WHERE cart_id=%s ORDER BY id ASC
        """, (cart_id,))
        items = cur.fetchall()

        if 0 <= index < len(items):
            cart_item_id = items[index]['id']
            cur.execute("DELETE FROM cart_item WHERE id=%s", (cart_item_id,))
            mysql.connection.commit()
            flash("Item removed from cart!", "info")
        else:
            flash("No item to remove.", "warning")
        cur.close()

    else:
        # Guest user: remove from session
        guest_cart = session.get('guest_cart', [])
        if guest_cart and 0 <= index < len(guest_cart):
            guest_cart.pop(index)
            session.modified = True
            flash("Item removed from cart!", "info")
        else:
            flash("No item to remove.", "warning")

    return redirect(url_for('main.checkout'))





# ---------------- ERROR HANDLERS ----------------
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_message="Page Not Found"), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_message="Internal Server Error"), 500
