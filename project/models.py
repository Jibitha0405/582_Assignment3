from project import db
from datetime import datetime

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    address_line = db.Column(db.String(100))
    region = db.Column(db.String(50))
    postcode = db.Column(db.String(10))
    
    users = db.relationship('User', backref='location', lazy=True)
    photographers = db.relationship('Photographer', backref='location', lazy=True)
    cart_items = db.relationship('CartItem', backref='location', lazy=True)
    booking_requests = db.relationship('BookingRequest', backref='location', lazy=True)
    bookings = db.relationship('Booking', backref='location', lazy=True)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))

    carts = db.relationship('Cart', backref='user', lazy=True)
    booking_requests = db.relationship('BookingRequest', backref='user', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    receipts = db.relationship('Receipt', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)


class Photographer(db.Model):
    __tablename__ = 'photographer'
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'))

    packages = db.relationship('Package', backref='photographer', lazy=True)
    booking_requests = db.relationship('BookingRequest', backref='photographer', lazy=True)
    bookings = db.relationship('Booking', backref='photographer', lazy=True)


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    packages = db.relationship('Package', backref='event', lazy=True)


class Package(db.Model):
    __tablename__ = 'package'
    id = db.Column(db.Integer, primary_key=True)
    photographer_id = db.Column(db.Integer, db.ForeignKey('photographer.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    package_image_url = db.Column(db.String(200))
    description = db.Column(db.String(200))
    price = db.Column(db.Numeric(10,2))
    photography_duration = db.Column(db.String(50))

    cart_items = db.relationship('CartItem', backref='package', lazy=True)
    booking_requests = db.relationship('BookingRequest', backref='package', lazy=True)
    bookings = db.relationship('Booking', backref='package', lazy=True)


class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True)
    photographer_id = db.Column(db.Integer, db.ForeignKey('photographer.id'))
    featured_image = db.Column(db.String(200))


class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_amount = db.Column(db.Numeric(10,2))

    cart_items = db.relationship('CartItem', backref='cart', lazy=True)


class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    selected_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    price = db.Column(db.Numeric(10,2))


class PaymentMethod(db.Model):
    __tablename__ = 'payment_method'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    provider = db.Column(db.String(100))
    last_four_digits = db.Column(db.String(4))
    expiry_date = db.Column(db.Date)
    billing_name = db.Column(db.String(100))

    checkouts = db.relationship('Checkout', backref='payment_method', lazy=True)
    bookings = db.relationship('Booking', backref='payment_method', lazy=True)


class Receipt(db.Model):
    __tablename__ = 'receipt'
    id = db.Column(db.Integer, primary_key=True)
    billing_address = db.Column(db.String(200))
    receipt_items = db.Column(db.String(200))
    issued_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    issued_at = db.Column(db.DateTime)
    total_amount = db.Column(db.Numeric(10,2))

    checkouts = db.relationship('Checkout', backref='receipt', lazy=True)


class Checkout(db.Model):
    __tablename__ = 'checkout'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'))
    confirmation_code = db.Column(db.String(50))
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipt.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class BookingRequest(db.Model):
    __tablename__ = 'booking_request'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photographer_id = db.Column(db.Integer, db.ForeignKey('photographer.id'))
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    requested_date = db.Column(db.Date)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime)
    responded_at = db.Column(db.DateTime, nullable=True)

    bookings = db.relationship('Booking', backref='request', lazy=True)
    notifications = db.relationship('Notification', backref='request', lazy=True)


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('booking_request.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photographer_id = db.Column(db.Integer, db.ForeignKey('photographer.id'))
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    booking_date = db.Column(db.Date)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'))
    status = db.Column(db.String(50))
    confirmation_note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime)
    booking_address_snapshot = db.Column(db.String(200))

    notifications = db.relationship('Notification', backref='booking', lazy=True)


class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    request_id = db.Column(db.Integer, db.ForeignKey('booking_request.id'))
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=True)
    message = db.Column(db.String(200))
    response_status = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
