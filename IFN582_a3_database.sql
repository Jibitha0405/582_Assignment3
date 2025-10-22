/*
SQL schema for Assignment 3 project: 14 tables
Database: assignment3_db
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

-- 2. user
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    location_id INT,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20)
);

-- 3. photographer
CREATE TABLE photographer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    portfolio_id INT,
    FOREIGN KEY (location_id) REFERENCES location(id)
);

-- 4. event
CREATE TABLE event (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50)
);

-- 5. package
CREATE TABLE package (
    id INT AUTO_INCREMENT PRIMARY KEY,
    photographer_id INT,
    event_id INT,
    package_image_url VARCHAR(200),
    description VARCHAR(200),
    price DECIMAL(10,2),
    photography_duration VARCHAR(50),
    FOREIGN KEY (photographer_id) REFERENCES photographer(id),
    FOREIGN KEY (event_id) REFERENCES event(id)
);

-- 6. portfolio
CREATE TABLE portfolio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    photographer_id INT,
    featured_image VARCHAR(200),
    FOREIGN KEY (photographer_id) REFERENCES photographer(id)
);

-- 7. cart
CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- 8. cart_item
CREATE TABLE cart_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT,
    package_id INT,
    location_id INT,
    selected_datetime DATETIME,
    price DECIMAL(10,2),
    FOREIGN KEY (cart_id) REFERENCES cart(id),
    FOREIGN KEY (package_id) REFERENCES package(id),
    FOREIGN KEY (location_id) REFERENCES location(id)
);

-- 9. payment_method
CREATE TABLE payment_method (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50),
    provider VARCHAR(100),
    last_four_digits VARCHAR(4),
    expiry_date DATE,
    billing_name VARCHAR(100)
);

-- 10. receipt
CREATE TABLE receipt (
    id INT AUTO_INCREMENT PRIMARY KEY,
    billing_address VARCHAR(200),
    receipt_items VARCHAR(200),
    issued_to INT,
    issued_at DATETIME,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (issued_to) REFERENCES user(id)
);

-- 11. checkout
CREATE TABLE checkout (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT,
    user_id INT,
    payment_method_id INT,
    confirmation_code VARCHAR(50),
    receipt_id INT,
    timestamp DATETIME,
    FOREIGN KEY (cart_id) REFERENCES cart(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(id),
    FOREIGN KEY (receipt_id) REFERENCES receipt(id)
);

-- 12. booking_request
CREATE TABLE booking_request (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    photographer_id INT,
    package_id INT,
    requested_date DATE,
    location_id INT,
    status VARCHAR(50),
    created_at DATETIME,
    responded_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (photographer_id) REFERENCES photographer(id),
    FOREIGN KEY (package_id) REFERENCES package(id),
    FOREIGN KEY (location_id) REFERENCES location(id)
);

-- 13. booking
CREATE TABLE booking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT,
    user_id INT,
    photographer_id INT,
    package_id INT,
    booking_date DATE,
    location_id INT,
    payment_method_id INT,
    status VARCHAR(50),
    confirmation_note VARCHAR(200),
    created_at DATETIME,
    booking_address_snapshot VARCHAR(200),
    FOREIGN KEY (request_id) REFERENCES booking_request(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (photographer_id) REFERENCES photographer(id),
    FOREIGN KEY (package_id) REFERENCES package(id),
    FOREIGN KEY (location_id) REFERENCES location(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(id)
);

-- 14. notification
CREATE TABLE notification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    request_id INT,
    booking_id INT NULL,
    message VARCHAR(200),
    response_status VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    timestamp DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (request_id) REFERENCES booking_request(id),
    FOREIGN KEY (booking_id) REFERENCES booking(id)
);