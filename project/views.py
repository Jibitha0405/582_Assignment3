from flask import (
    render_template, request, session, redirect,
    url_for, flash
)
from datetime import datetime
from project import app
from project.models import db, Cart, CartItem, Package


# ------------------------
# BASIC PAGE ROUTES
# ------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/vendor_gallery')
def vendor_gallery():
    return render_template('vendor_gallery.html')


@app.route('/vendor_management')
def vendor_management():
    return render_template('vendor_management.html')


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


@app.route('/item_details')
def item_details():
    return render_template('item_details.html')


@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/login')
def login():
    return render_template('login.html', hide_nav=True)


@app.route('/register')
def register():
    return render_template('register.html', hide_nav=True)


# ------------------------
# ERROR HANDLERS
# ------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500), 500


# ------------------------
# CART ROUTES
# ------------------------
@app.route('/show_cart')
def show_cart():
    """Display user's or guest's cart."""
    user_id = session.get('user_id')

    if user_id:
        cart = Cart.query.filter_by(user_id=user_id).first()
        items = CartItem.query.filter_by(cart_id=cart.id).all() if cart else []
        total = float(cart.total_amount) if cart else 0
    else:
        items = session.get('guest_cart', [])
        total = sum(item['price'] for item in items)

    return render_template('cart.html', items=items, total=total)


@app.route('/add_to_cart/<int:package_id>', methods=['POST'])
def add_to_cart(package_id):
    """Add a package to the cart (works for both guest and logged-in users)."""

    # Get optional datetime and location from form
    selected_datetime = request.form.get('selected_datetime') or None
    location_id = request.form.get('location_id')
    location_id = int(location_id) if location_id else None

    package = Package.query.get(package_id)
    if not package:
        flash("Selected package not found.", "danger")
        return redirect(request.referrer or url_for('vendor_gallery'))

    user_id = session.get('user_id')

    # --------------------
    # Logged-in user -> save to DB
    # --------------------
    if user_id:
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id, total_amount=0)
            db.session.add(cart)
            db.session.commit()

        # Prevent duplicate items for same package + datetime
        existing_item = None
        if selected_datetime:
            dt_obj = datetime.strptime(selected_datetime, "%Y-%m-%d %H:%M:%S")
            existing_item = CartItem.query.filter_by(
                cart_id=cart.id,
                package_id=package.id,
                selected_datetime=dt_obj
            ).first()
        if existing_item:
            flash("This package is already in your cart for that time.", "info")
            return redirect(url_for('show_cart'))

        cart_item = CartItem(
            cart_id=cart.id,
            package_id=package.id,
            location_id=location_id,
            selected_datetime=datetime.strptime(selected_datetime, "%Y-%m-%d %H:%M:%S") if selected_datetime else None,
            price=package.price
        )
        db.session.add(cart_item)
        db.session.commit()

        # Update cart total
        cart.total_amount = db.session.query(db.func.sum(CartItem.price)).filter_by(cart_id=cart.id).scalar() or 0
        db.session.commit()

    # --------------------
    # Guest user -> store in session
    # --------------------
    else:
        if 'guest_cart' not in session:
            session['guest_cart'] = []

        # Prevent duplicate for same package + datetime in guest cart
        duplicate = False
        for item in session['guest_cart']:
            if item['package_id'] == package.id and item['selected_datetime'] == selected_datetime:
                duplicate = True
                break

        if duplicate:
            flash("This package is already in your cart for that time.", "info")
            return redirect(url_for('show_cart'))

        session['guest_cart'].append({
            'package_id': package.id,
            'name': package.name,  # now works since you added the column
            'price': float(package.price),
            'location': location_id if location_id else 'N/A',
            'selected_datetime': selected_datetime if selected_datetime else 'N/A'
        })
        session.modified = True

    flash(f"Added {package.name} to your cart!", "success")
    return redirect(url_for('show_cart'))
