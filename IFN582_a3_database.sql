/*
SQL schema for Assignment 3 project
Database: IFN582_a3_database
*/

CREATE DATABASE IF NOT EXISTS IFN582_a3_database;
USE IFN582_a3_database;

-- 1. location
CREATE TABLE location (
    id INT AUTO_INCREMENT PRIMARY KEY,
    address_line VARCHAR(100),
    region VARCHAR(50),
    postcode VARCHAR(10)
);

-- 2. users (main login table)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('customer', 'photographer', 'admin') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. customer profile
CREATE TABLE customer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(200),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. photographer profile
CREATE TABLE photographer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    location_id INT,
    phone VARCHAR(20),
    portfolio_id INT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES location(id)
);

-- 5. event
CREATE TABLE event (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- 6. package
CREATE TABLE package (
    id INT AUTO_INCREMENT PRIMARY KEY,
    photographer_id INT NOT NULL,
    event_id INT NOT NULL,
    package_image_url VARCHAR(200),
    description VARCHAR(200),
    price DECIMAL(10,2),
    photography_duration VARCHAR(50),
    FOREIGN KEY (photographer_id) REFERENCES photographer(id),
    FOREIGN KEY (event_id) REFERENCES event(id)
);

-- 7. portfolio
CREATE TABLE portfolio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    photographer_id INT NOT NULL,
    featured_image VARCHAR(200),
    FOREIGN KEY (photographer_id) REFERENCES photographer(id)
);

-- 8. cart
CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    total_amount DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customer(id)
);

-- 9. cart_item
CREATE TABLE cart_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    package_id INT NOT NULL,
    location_id INT,
    selected_datetime DATETIME,
    price DECIMAL(10,2),
    FOREIGN KEY (cart_id) REFERENCES cart(id),
    FOREIGN KEY (package_id) REFERENCES package(id),
    FOREIGN KEY (location_id) REFERENCES location(id)
);

-- 10. payment_method
CREATE TABLE payment_method (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    type VARCHAR(50),
    provider VARCHAR(100),
    last_four_digits VARCHAR(4),
    expiry_date DATE,
    billing_name VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES customer(id)
);

-- 11. receipt
CREATE TABLE receipt (
    id INT AUTO_INCREMENT PRIMARY KEY,
    billing_address VARCHAR(200),
    receipt_items VARCHAR(200),
    issued_to_customer_id INT NOT NULL,
    issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (issued_to_customer_id) REFERENCES customer(id)
);

-- 12. checkout
CREATE TABLE checkout (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    customer_id INT NOT NULL,
    payment_method_id INT NOT NULL,
    confirmation_code VARCHAR(50),
    receipt_id INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES cart(id),
    FOREIGN KEY (customer_id) REFERENCES customer(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(id),
    FOREIGN KEY (receipt_id) REFERENCES receipt(id)
);

-- 13. booking_request
CREATE TABLE booking_request (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    photographer_id INT NOT NULL,
    package_id INT NOT NULL,
    requested_date DATE,
    location_id INT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    responded_at DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(id),
    FOREIGN KEY (photographer_id) REFERENCES photographer(id),
    FOREIGN KEY (package_id) REFERENCES package(id),
    FOREIGN KEY (location_id) REFERENCES location(id)
);

-- 14. booking
CREATE TABLE booking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    customer_id INT NOT NULL,
    photographer_id INT NOT NULL,
    package_id INT NOT NULL,
    booking_date DATE,
    location_id INT,
    payment_method_id INT,
    status VARCHAR(50) DEFAULT 'Confirmed',
    confirmation_note VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    booking_address_snapshot VARCHAR(200),
    FOREIGN KEY (request_id) REFERENCES booking_request(id),
    FOREIGN KEY (customer_id) REFERENCES customer(id),
    FOREIGN KEY (photographer_id) REFERENCES photographer(id),
    FOREIGN KEY (package_id) REFERENCES package(id),
    FOREIGN KEY (location_id) REFERENCES location(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(id)
);

-- 15. notification
CREATE TABLE notification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    request_id INT NULL,
    booking_id INT NULL,
    message VARCHAR(200),
    response_status VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (request_id) REFERENCES booking_request(id),
    FOREIGN KEY (booking_id) REFERENCES booking(id)
);
