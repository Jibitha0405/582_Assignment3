from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from project import mysql
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import re
import base64
import MySQLdb
import MySQLdb.cursors

main = Blueprint('main', __name__)


@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('main.signin_login'))


@main.app_context_processor
def cart_count_processor():
    """
    Returns cart_count for the navbar for both logged-in users and guests.
    """
    count = 0

    if session.get('logged_in'):
        user_id = session.get('user_id')
        if user_id:
            # Get customer_id
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT id FROM customer WHERE user_id=%s", (user_id,))
            customer_row = cur.fetchone()
            if customer_row:
                customer_id = customer_row['id']
                # Count cart items
                cur.execute("""
                    SELECT COUNT(*) AS cnt FROM cart_item ci
                    JOIN cart c ON ci.cart_id = c.id
                    WHERE c.customer_id = %s
                """, (customer_id,))
                row = cur.fetchone()
                if row:
                    count = row['cnt']
            cur.close()
    else:
        # Guest cart stored in session
        count = len(session.get('guest_cart', []))
    return dict(cart_count=count)

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


@main.route('/signin_login.html')
def signin_login():
    return render_template('signin_login.html', hide_nav=True)

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

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

     #  Get total customers
    cur.execute("SELECT COUNT(*) AS total_customers FROM users WHERE role = 'customer'")
    total_customers = cur.fetchone()['total_customers']

    #  Get total photographers
    cur.execute("SELECT COUNT(*) AS total_photographers FROM users WHERE role = 'photographer'")
    total_photographers = cur.fetchone()['total_photographers']

    #  Get total bookings
    cur.execute("SELECT COUNT(*) AS total_bookings FROM booking")
    total_bookings = cur.fetchone()['total_bookings']

    event_added = session.pop('event_added', None)
    if session.pop('show_event_success', False):
        flash("Event added successfully!", "success")

    

    # Get all events
    cur.execute("SELECT * FROM event")
    events = cur.fetchall()

    # Total counts
    cur.execute("SELECT COUNT(*) AS total_bookings FROM booking")
    total_bookings = cur.fetchone()['total_bookings']

    

    # Get 5 most recent bookings with joined details
    cur.execute("""
    SELECT 
        b.id,
        cu_user.name AS customer_name,
        ph_user.name AS photographer_name,
        e.name AS event_name,
        DATE_FORMAT(b.booking_date, '%d %b %Y') AS booking_date,
        b.status
    FROM booking b
    JOIN customer cu ON b.customer_id = cu.id
    JOIN users cu_user ON cu.user_id = cu_user.id
    JOIN photographer ph ON b.photographer_id = ph.id
    JOIN users ph_user ON ph.user_id = ph_user.id
    JOIN package pkg ON b.package_id = pkg.id
    JOIN event e ON pkg.event_id = e.id
    ORDER BY b.created_at DESC
    LIMIT 5
    """)
    recent_bookings = cur.fetchall()

    cur.close()

    return render_template(
        'admin_dashboard.html',
        events=events,
        total_customers=total_customers,
        total_photographers=total_photographers,
        total_bookings=total_bookings,
        recent_bookings=recent_bookings
    )

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

# Customer features
@main.route('/customer_profile')
def customer_profile():
    return render_template('customer_profile.html')

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

@main.route('/item_details')
def item_details():
    package_id = request.args.get('package_id', 1)
    cart_item_id = request.args.get('cart_item_id')
    edit_index = request.args.get('edit_index')

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


#Photographer features
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

#ROUTES

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

    # Use DictCursor for easier access by column names
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Check user credentials
        cur.execute(
            "SELECT id, name, role FROM users WHERE email=%s AND password_hash=%s",
            (email, hashed_password)
        )
        user = cur.fetchone()

        if not user:
            flash("Invalid email or password", "danger")
            return redirect(url_for('main.signin_login'))

        user_id = user['id']
        user_name = user['name']
        user_role = user['role']

        session['user_id'] = user_id
        session['user_name'] = user_name
        session['user_role'] = user_role
        session['logged_in'] = True

        flash("Login successful!", "success")
        print("User role is:", user_id, user_name, user_role)

        #Merge guest cart
        guest_cart = session.get('guest_cart', [])
        if guest_cart:
            # Get or create customer
            cur.execute("SELECT id FROM customer WHERE user_id=%s", (user_id,))
            customer_row = cur.fetchone()
            if not customer_row:
                cur.execute("INSERT INTO customer (user_id) VALUES (%s)", (user_id,))
                mysql.connection.commit()
                customer_id = cur.lastrowid
            else:
                customer_id = customer_row['id']

            # Get or create cart
            cur.execute("SELECT id FROM cart WHERE customer_id=%s", (customer_id,))
            cart_row = cur.fetchone()
            if not cart_row:
                cur.execute("INSERT INTO cart (customer_id) VALUES (%s)", (customer_id,))
                mysql.connection.commit()
                cart_id = cur.lastrowid
            else:
                cart_id = cart_row['id']

            # Insert guest cart items
            for item in guest_cart:
                location_name = item.get('location')
                photographer_name = item.get('photographer')
                location_id = None

                if location_name:
                    cur.execute(
                        "SELECT id FROM location WHERE region=%s OR address_line=%s LIMIT 1",
                        (location_name, location_name)
                    )
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

    finally:
        cur.close()  # Close cursor only once at the end

    # Redirect based on role
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

#ERROR HANDLERS
@main.route('/error')
def error():
    return render_template('error.html')

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404), 404

@main.app_errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500), 500


