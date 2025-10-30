/*
SQL schema for Assignment 3 project
Database: IFN582_a3_database
*/

DROP DATABASE IF EXISTS IFN582_a3_database;
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

USE IFN582_a3_database;

-- 1. location
INSERT INTO location (address_line, region, postcode) VALUES
('12 King St', 'Sydney', '2000'),
('45 Queen Ave', 'Melbourne', '3000'),
('78 River Rd', 'Brisbane', '4000'),
('90 Lake View', 'Perth', '6000'),
('22 Garden Ln', 'Adelaide', '5000');

-- 2. users
INSERT INTO users (name, email, password_hash, role) VALUES
('Admin User', 'admin@gmail.com', 'e86f78a8a3caf0b60d8e74e5942aa6d86dc150cd3c03338aef25b7d2d7e3acc7', 'admin'),
('Alice Johnson', 'alice@example.com', 'hash1', 'customer'),
('Bob Smith', 'bob@example.com', 'hash2', 'customer'),
('Charlie Lens', 'charlie@example.com', 'hash3', 'photographer'),
('Diana Frames', 'diana@example.com', 'hash4', 'photographer'),
('Ethan Click', 'ethan@example.com', 'hash5', 'photographer');

-- 3. customer
INSERT INTO customer (user_id, phone, address) VALUES
(2, '0412345678', '12 Ocean St, Sydney'),
(3, '0498765432', '90 High Rd, Melbourne');

-- 4. photographer
INSERT INTO photographer (user_id, location_id, phone, portfolio_id) VALUES
(4, 1, '0411000001', NULL),
(5, 2, '0411000002', NULL),
(6, 3, '0411000003', NULL);

-- 5. event
INSERT INTO event (name) VALUES
('Wedding'),
('Birthday Party'),
('Corporate Event'),
('Graduation'),
('Family Portrait');

-- 6. package
INSERT INTO package (photographer_id, event_id, package_image_url, description, price, photography_duration) VALUES
(1, 1, 'wedding_pkg.jpg', 'Full-day wedding coverage with album', 1200.00, '8 hours'),
(1, 2, 'birthday_pkg.jpg', 'Birthday event coverage', 400.00, '3 hours'),
(2, 3, 'corporate_pkg.jpg', 'Corporate event photo session', 800.00, '5 hours'),
(3, 4, 'graduation_pkg.jpg', 'Graduation day photo shoot', 500.00, '4 hours'),
(3, 5, 'family_pkg.jpg', 'Family portrait session', 300.00, '2 hours');

-- 7. portfolio
INSERT INTO portfolio (photographer_id, featured_image) VALUES
(1, 'charlie_portfolio1.jpg'),
(2, 'diana_portfolio1.jpg'),
(3, 'ethan_portfolio1.jpg'),
(1, 'charlie_portfolio2.jpg'),
(2, 'diana_portfolio2.jpg');

-- 8. cart
INSERT INTO cart (customer_id, total_amount) VALUES
(1, 1200.00),
(1, 400.00),
(2, 800.00),
(2, 500.00),
(1, 300.00);

-- 9. cart_item
INSERT INTO cart_item (cart_id, package_id, location_id, selected_datetime, price) VALUES
(1, 1, 1, '2025-11-10 10:00:00', 1200.00),
(2, 2, 2, '2025-11-15 14:00:00', 400.00),
(3, 3, 3, '2025-11-20 09:00:00', 800.00),
(4, 4, 4, '2025-11-25 11:00:00', 500.00),
(5, 5, 5, '2025-11-30 13:00:00', 300.00);

-- 10. payment_method
INSERT INTO payment_method (customer_id, type, provider, last_four_digits, expiry_date, billing_name) VALUES
(1, 'Credit Card', 'Visa', '1234', '2026-05-01', 'Alice Johnson'),
(1, 'PayPal', 'PayPal', '0000', '2027-03-01', 'Alice Johnson'),
(2, 'Debit Card', 'MasterCard', '5678', '2026-08-01', 'Bob Smith'),
(2, 'Credit Card', 'Amex', '4321', '2025-12-01', 'Bob Smith'),
(1, 'Credit Card', 'MasterCard', '6789', '2026-10-01', 'Alice Johnson');

-- 11. receipt
INSERT INTO receipt (billing_address, receipt_items, issued_to_customer_id, total_amount) VALUES
('12 Ocean St, Sydney', 'Wedding Package', 1, 1200.00),
('12 Ocean St, Sydney', 'Birthday Package', 1, 400.00),
('90 High Rd, Melbourne', 'Corporate Package', 2, 800.00),
('90 High Rd, Melbourne', 'Graduation Package', 2, 500.00),
('12 Ocean St, Sydney', 'Family Package', 1, 300.00);

-- 12. checkout
INSERT INTO checkout (cart_id, customer_id, payment_method_id, confirmation_code, receipt_id) VALUES
(1, 1, 1, 'CONF1001', 1),
(2, 1, 2, 'CONF1002', 2),
(3, 2, 3, 'CONF1003', 3),
(4, 2, 4, 'CONF1004', 4),
(5, 1, 5, 'CONF1005', 5);

-- 13. booking_request
INSERT INTO booking_request (customer_id, photographer_id, package_id, requested_date, location_id, status) VALUES
(1, 1, 1, '2025-12-01', 1, 'Pending'),
(1, 1, 2, '2025-12-05', 2, 'Approved'),
(2, 2, 3, '2025-12-10', 3, 'Pending'),
(2, 3, 4, '2025-12-12', 4, 'Rejected'),
(1, 3, 5, '2025-12-15', 5, 'Pending');

-- 14. booking
INSERT INTO booking (request_id, customer_id, photographer_id, package_id, booking_date, location_id, payment_method_id, status, confirmation_note, booking_address_snapshot) VALUES
(1, 1, 1, 1, '2025-12-01', 1, 1, 'Confirmed', 'See you on your wedding day!', '12 King St, Sydney'),
(2, 1, 1, 2, '2025-12-05', 2, 2, 'Confirmed', 'Birthday shoot confirmed.', '45 Queen Ave, Melbourne'),
(3, 2, 2, 3, '2025-12-10', 3, 3, 'Pending', 'Awaiting payment confirmation', '78 River Rd, Brisbane'),
(4, 2, 3, 4, '2025-12-12', 4, 4, 'Cancelled', 'Request rejected by photographer', '90 Lake View, Perth'),
(5, 1, 3, 5, '2025-12-15', 5, 5, 'Confirmed', 'Family session booked', '22 Garden Ln, Adelaide');

-- 15. notification
INSERT INTO notification (user_id, request_id, booking_id, message, response_status, is_read) VALUES
(2, 1, 1, 'Your wedding booking is confirmed!', 'Approved', FALSE),
(2, 2, 2, 'Your birthday session has been scheduled.', 'Approved', TRUE),
(3, 3, 3, 'Corporate booking awaiting confirmation.', 'Pending', FALSE),
(3, 4, 4, 'Your request has been declined.', 'Rejected', TRUE),
(2, 5, 5, 'Your family shoot is confirmed.', 'Approved', FALSE);

