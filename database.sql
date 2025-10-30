CREATE DATABASE  IF NOT EXISTS `ifn582_a3_database` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `ifn582_a3_database`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: ifn582_a3_database
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `booking`
--

DROP TABLE IF EXISTS `booking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking` (
  `id` int NOT NULL AUTO_INCREMENT,
  `request_id` int NOT NULL,
  `customer_id` int NOT NULL,
  `photographer_id` int NOT NULL,
  `package_id` int NOT NULL,
  `booking_date` date DEFAULT NULL,
  `location_id` int DEFAULT NULL,
  `payment_method_id` int DEFAULT NULL,
  `status` varchar(50) DEFAULT 'Confirmed',
  `confirmation_note` varchar(200) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `booking_address_snapshot` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `request_id` (`request_id`),
  KEY `customer_id` (`customer_id`),
  KEY `photographer_id` (`photographer_id`),
  KEY `package_id` (`package_id`),
  KEY `location_id` (`location_id`),
  KEY `payment_method_id` (`payment_method_id`),
  CONSTRAINT `booking_ibfk_1` FOREIGN KEY (`request_id`) REFERENCES `booking_request` (`id`),
  CONSTRAINT `booking_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`),
  CONSTRAINT `booking_ibfk_3` FOREIGN KEY (`photographer_id`) REFERENCES `photographer` (`id`),
  CONSTRAINT `booking_ibfk_4` FOREIGN KEY (`package_id`) REFERENCES `package` (`id`),
  CONSTRAINT `booking_ibfk_5` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `booking_ibfk_6` FOREIGN KEY (`payment_method_id`) REFERENCES `payment_method` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking`
--

LOCK TABLES `booking` WRITE;
/*!40000 ALTER TABLE `booking` DISABLE KEYS */;
INSERT INTO `booking` VALUES (1,1,1,1,1,'2025-12-01',1,1,'Confirmed','See you on your wedding day!','2025-10-30 18:15:30','12 King St, Sydney'),(2,2,1,1,2,'2025-12-05',2,2,'Confirmed','Birthday shoot confirmed.','2025-10-30 18:15:30','45 Queen Ave, Melbourne'),(3,3,2,2,3,'2025-12-10',3,3,'Pending','Awaiting payment confirmation','2025-10-30 18:15:30','78 River Rd, Brisbane'),(4,4,2,3,4,'2025-12-12',4,4,'Cancelled','Request rejected by photographer','2025-10-30 18:15:30','90 Lake View, Perth'),(5,5,1,3,5,'2025-12-15',5,5,'Confirmed','Family session booked','2025-10-30 18:15:30','22 Garden Ln, Adelaide');
/*!40000 ALTER TABLE `booking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booking_request`
--

DROP TABLE IF EXISTS `booking_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking_request` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `photographer_id` int NOT NULL,
  `package_id` int NOT NULL,
  `requested_date` date DEFAULT NULL,
  `location_id` int DEFAULT NULL,
  `status` varchar(50) DEFAULT 'Pending',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `responded_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  KEY `photographer_id` (`photographer_id`),
  KEY `package_id` (`package_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `booking_request_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`),
  CONSTRAINT `booking_request_ibfk_2` FOREIGN KEY (`photographer_id`) REFERENCES `photographer` (`id`),
  CONSTRAINT `booking_request_ibfk_3` FOREIGN KEY (`package_id`) REFERENCES `package` (`id`),
  CONSTRAINT `booking_request_ibfk_4` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking_request`
--

LOCK TABLES `booking_request` WRITE;
/*!40000 ALTER TABLE `booking_request` DISABLE KEYS */;
INSERT INTO `booking_request` VALUES (1,1,1,1,'2025-12-01',1,'Pending','2025-10-30 18:15:30',NULL),(2,1,1,2,'2025-12-05',2,'Approved','2025-10-30 18:15:30',NULL),(3,2,2,3,'2025-12-10',3,'Pending','2025-10-30 18:15:30',NULL),(4,2,3,4,'2025-12-12',4,'Rejected','2025-10-30 18:15:30',NULL),(5,1,3,5,'2025-12-15',5,'Pending','2025-10-30 18:15:30',NULL);
/*!40000 ALTER TABLE `booking_request` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart`
--

DROP TABLE IF EXISTS `cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `total_amount` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
INSERT INTO `cart` VALUES (1,1,1200.00),(2,1,400.00),(3,2,800.00),(4,2,500.00),(5,1,300.00),(6,3,0.00),(7,4,0.00);
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_item`
--

DROP TABLE IF EXISTS `cart_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cart_id` int NOT NULL,
  `package_id` int NOT NULL,
  `location_id` int DEFAULT NULL,
  `selected_datetime` datetime DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `hours` decimal(5,2) DEFAULT '1.00',
  `photographer_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cart_id` (`cart_id`),
  KEY `package_id` (`package_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `cart_item_ibfk_1` FOREIGN KEY (`cart_id`) REFERENCES `cart` (`id`),
  CONSTRAINT `cart_item_ibfk_2` FOREIGN KEY (`package_id`) REFERENCES `package` (`id`),
  CONSTRAINT `cart_item_ibfk_3` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_item`
--

LOCK TABLES `cart_item` WRITE;
/*!40000 ALTER TABLE `cart_item` DISABLE KEYS */;
INSERT INTO `cart_item` VALUES (1,1,1,1,'2025-11-10 10:00:00',1200.00,1.00,NULL),(2,2,2,2,'2025-11-15 14:00:00',400.00,1.00,NULL),(3,3,3,3,'2025-11-20 09:00:00',800.00,1.00,NULL),(4,4,4,4,'2025-11-25 11:00:00',500.00,1.00,NULL),(5,5,5,5,'2025-11-30 13:00:00',300.00,1.00,NULL),(6,6,1,NULL,NULL,1200.00,1.00,'Charlie Lens'),(7,6,3,NULL,NULL,800.00,1.00,'Diana Frames'),(8,7,1,NULL,NULL,1200.00,1.00,'Charlie Lens');
/*!40000 ALTER TABLE `cart_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `checkout`
--

DROP TABLE IF EXISTS `checkout`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `checkout` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cart_id` int NOT NULL,
  `customer_id` int NOT NULL,
  `payment_method_id` int NOT NULL,
  `confirmation_code` varchar(50) DEFAULT NULL,
  `receipt_id` int DEFAULT NULL,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `cart_id` (`cart_id`),
  KEY `customer_id` (`customer_id`),
  KEY `payment_method_id` (`payment_method_id`),
  KEY `receipt_id` (`receipt_id`),
  CONSTRAINT `checkout_ibfk_1` FOREIGN KEY (`cart_id`) REFERENCES `cart` (`id`),
  CONSTRAINT `checkout_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`),
  CONSTRAINT `checkout_ibfk_3` FOREIGN KEY (`payment_method_id`) REFERENCES `payment_method` (`id`),
  CONSTRAINT `checkout_ibfk_4` FOREIGN KEY (`receipt_id`) REFERENCES `receipt` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `checkout`
--

LOCK TABLES `checkout` WRITE;
/*!40000 ALTER TABLE `checkout` DISABLE KEYS */;
INSERT INTO `checkout` VALUES (1,1,1,1,'CONF1001',1,'2025-10-30 18:15:30'),(2,2,1,2,'CONF1002',2,'2025-10-30 18:15:30'),(3,3,2,3,'CONF1003',3,'2025-10-30 18:15:30'),(4,4,2,4,'CONF1004',4,'2025-10-30 18:15:30'),(5,5,1,5,'CONF1005',5,'2025-10-30 18:15:30');
/*!40000 ALTER TABLE `checkout` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `customer_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES (1,2,'0412345678','12 Ocean St, Sydney'),(2,3,'0498765432','90 High Rd, Melbourne'),(3,7,NULL,NULL),(4,8,NULL,NULL);
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event`
--

LOCK TABLES `event` WRITE;
/*!40000 ALTER TABLE `event` DISABLE KEYS */;
INSERT INTO `event` VALUES (1,'Wedding'),(2,'Birthday Party'),(3,'Corporate Event'),(4,'Graduation'),(5,'Family Portrait');
/*!40000 ALTER TABLE `event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `location`
--

DROP TABLE IF EXISTS `location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `location` (
  `id` int NOT NULL AUTO_INCREMENT,
  `address_line` varchar(100) DEFAULT NULL,
  `region` varchar(50) DEFAULT NULL,
  `postcode` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `location`
--

LOCK TABLES `location` WRITE;
/*!40000 ALTER TABLE `location` DISABLE KEYS */;
INSERT INTO `location` VALUES (1,'12 King St','Sydney','2000'),(2,'45 Queen Ave','Melbourne','3000'),(3,'78 River Rd','Brisbane','4000'),(4,'90 Lake View','Perth','6000'),(5,'22 Garden Ln','Adelaide','5000');
/*!40000 ALTER TABLE `location` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `request_id` int DEFAULT NULL,
  `booking_id` int DEFAULT NULL,
  `message` varchar(200) DEFAULT NULL,
  `response_status` varchar(50) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `request_id` (`request_id`),
  KEY `booking_id` (`booking_id`),
  CONSTRAINT `notification_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `notification_ibfk_2` FOREIGN KEY (`request_id`) REFERENCES `booking_request` (`id`),
  CONSTRAINT `notification_ibfk_3` FOREIGN KEY (`booking_id`) REFERENCES `booking` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification`
--

LOCK TABLES `notification` WRITE;
/*!40000 ALTER TABLE `notification` DISABLE KEYS */;
INSERT INTO `notification` VALUES (1,2,1,1,'Your wedding booking is confirmed!','Approved',0,'2025-10-30 18:15:30'),(2,2,2,2,'Your birthday session has been scheduled.','Approved',1,'2025-10-30 18:15:30'),(3,3,3,3,'Corporate booking awaiting confirmation.','Pending',0,'2025-10-30 18:15:30'),(4,3,4,4,'Your request has been declined.','Rejected',1,'2025-10-30 18:15:30'),(5,2,5,5,'Your family shoot is confirmed.','Approved',0,'2025-10-30 18:15:30');
/*!40000 ALTER TABLE `notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `package`
--

DROP TABLE IF EXISTS `package`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `package` (
  `id` int NOT NULL AUTO_INCREMENT,
  `photographer_id` int NOT NULL,
  `event_id` int NOT NULL,
  `package_image_url` varchar(200) DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `photography_duration` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `photographer_id` (`photographer_id`),
  KEY `event_id` (`event_id`),
  CONSTRAINT `package_ibfk_1` FOREIGN KEY (`photographer_id`) REFERENCES `photographer` (`id`),
  CONSTRAINT `package_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `event` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `package`
--

LOCK TABLES `package` WRITE;
/*!40000 ALTER TABLE `package` DISABLE KEYS */;
INSERT INTO `package` VALUES (1,1,1,'img/wedding.jpg','Full-day wedding coverage with album',1200.00,'8 hours'),(2,1,2,'img/birthdaycelebration.jpg','Birthday event coverage',400.00,'3 hours'),(3,2,3,'img/nature.jpg','Corporate event photo session',800.00,'5 hours'),(4,3,4,'img/wedding.jpg','Graduation day photo shoot',500.00,'4 hours'),(5,3,5,'img/engagement.jpg','Family portrait session',300.00,'2 hours');
/*!40000 ALTER TABLE `package` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_method`
--

DROP TABLE IF EXISTS `payment_method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_method` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  `provider` varchar(100) DEFAULT NULL,
  `last_four_digits` varchar(4) DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `billing_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `payment_method_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_method`
--

LOCK TABLES `payment_method` WRITE;
/*!40000 ALTER TABLE `payment_method` DISABLE KEYS */;
INSERT INTO `payment_method` VALUES (1,1,'Credit Card','Visa','1234','2026-05-01','Alice Johnson'),(2,1,'PayPal','PayPal','0000','2027-03-01','Alice Johnson'),(3,2,'Debit Card','MasterCard','5678','2026-08-01','Bob Smith'),(4,2,'Credit Card','Amex','4321','2025-12-01','Bob Smith'),(5,1,'Credit Card','MasterCard','6789','2026-10-01','Alice Johnson');
/*!40000 ALTER TABLE `payment_method` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photographer`
--

DROP TABLE IF EXISTS `photographer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `photographer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `location_id` int DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `portfolio_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `photographer_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `photographer_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photographer`
--

LOCK TABLES `photographer` WRITE;
/*!40000 ALTER TABLE `photographer` DISABLE KEYS */;
INSERT INTO `photographer` VALUES (1,4,1,'0411000001',NULL),(2,5,2,'0411000002',NULL),(3,6,3,'0411000003',NULL);
/*!40000 ALTER TABLE `photographer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `portfolio`
--

DROP TABLE IF EXISTS `portfolio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `portfolio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `photographer_id` int NOT NULL,
  `featured_image` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `photographer_id` (`photographer_id`),
  CONSTRAINT `portfolio_ibfk_1` FOREIGN KEY (`photographer_id`) REFERENCES `photographer` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `portfolio`
--

LOCK TABLES `portfolio` WRITE;
/*!40000 ALTER TABLE `portfolio` DISABLE KEYS */;
INSERT INTO `portfolio` VALUES (1,1,'charlie_portfolio1.jpg'),(2,2,'diana_portfolio1.jpg'),(3,3,'ethan_portfolio1.jpg'),(4,1,'charlie_portfolio2.jpg'),(5,2,'diana_portfolio2.jpg');
/*!40000 ALTER TABLE `portfolio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receipt`
--

DROP TABLE IF EXISTS `receipt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receipt` (
  `id` int NOT NULL AUTO_INCREMENT,
  `billing_address` varchar(200) DEFAULT NULL,
  `receipt_items` varchar(200) DEFAULT NULL,
  `issued_to_customer_id` int NOT NULL,
  `issued_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `total_amount` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `issued_to_customer_id` (`issued_to_customer_id`),
  CONSTRAINT `receipt_ibfk_1` FOREIGN KEY (`issued_to_customer_id`) REFERENCES `customer` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receipt`
--

LOCK TABLES `receipt` WRITE;
/*!40000 ALTER TABLE `receipt` DISABLE KEYS */;
INSERT INTO `receipt` VALUES (1,'12 Ocean St, Sydney','Wedding Package',1,'2025-10-30 18:15:30',1200.00),(2,'12 Ocean St, Sydney','Birthday Package',1,'2025-10-30 18:15:30',400.00),(3,'90 High Rd, Melbourne','Corporate Package',2,'2025-10-30 18:15:30',800.00),(4,'90 High Rd, Melbourne','Graduation Package',2,'2025-10-30 18:15:30',500.00),(5,'12 Ocean St, Sydney','Family Package',1,'2025-10-30 18:15:30',300.00);
/*!40000 ALTER TABLE `receipt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('customer','photographer','admin') NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Admin User','admin@example.com','e86f78a8a3caf0b60d8e74e5942aa6d86dc150cd3c03338aef25b7d2d7e3acc7','admin','2025-10-30 18:15:30'),(2,'Alice Johnson','alice@example.com','hash1','customer','2025-10-30 18:15:30'),(3,'Bob Smith','bob@example.com','hash2','customer','2025-10-30 18:15:30'),(4,'Charlie Lens','charlie@example.com','hash3','photographer','2025-10-30 18:15:30'),(5,'Diana Frames','diana@example.com','hash4','photographer','2025-10-30 18:15:30'),(6,'Ethan Click','ethan@example.com','hash5','photographer','2025-10-30 18:15:30'),(7,'Jibitha','jibitha01@gmail.com','b85d1d7b85d1720187a8e61267a12d31e0b5dba790d3e72b3bbaced0e8bff69b','customer','2025-10-30 18:16:28'),(8,'Jibitha','jibitha02@gmail.com','b85d1d7b85d1720187a8e61267a12d31e0b5dba790d3e72b3bbaced0e8bff69b','customer','2025-10-30 18:19:06');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-30 18:52:03
