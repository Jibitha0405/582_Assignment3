from project import db  # <- import the db object from __init__.py

from project import db
from datetime import datetime

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_amount = db.Column(db.Numeric(10, 2))

class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    selected_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    price = db.Column(db.Numeric(10, 2))


class Package(db.Model):
    __tablename__ = 'package'
    id = db.Column(db.Integer, primary_key=True)
    photographer_id = db.Column(db.Integer, db.ForeignKey('photographer.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    name = db.Column(db.String(100))  # <-- NEW COLUMN
    package_image_url = db.Column(db.String(200))
    description = db.Column(db.String(200))
    price = db.Column(db.Numeric(10, 2))
    photography_duration = db.Column(db.String(50))

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    address_line = db.Column(db.String(100))
    region = db.Column(db.String(50))
    postcode = db.Column(db.String(10))