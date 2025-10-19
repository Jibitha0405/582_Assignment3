from flask import render_template, request
from project import app

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