CREATE DATABASE  IF NOT EXISTS `centralbankdata` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `centralbankdata`;
-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    Database: centralbankdata
-- ------------------------------------------------------
-- Server version	8.3.0

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
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS admin;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  id int NOT NULL AUTO_INCREMENT,
  admin_user varchar(45) NOT NULL,
  admin_pass varchar(45) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES admin WRITE;
/*!40000 ALTER TABLE admin DISABLE KEYS */;
INSERT INTO admin VALUES (1,'Reza_Admin','Gorgan_0173'),(2,'Reza_Admin','Gorgan_0173'),(3,'Reza_Admin','Gorgan_0173');
/*!40000 ALTER TABLE admin ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `card`
--

DROP TABLE IF EXISTS card;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE card (
  id int NOT NULL AUTO_INCREMENT,
  typeOfCards varchar(45) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `card`
--

LOCK TABLES card WRITE;
/*!40000 ALTER TABLE card DISABLE KEYS */;
INSERT INTO card VALUES (1,'مهر گستر'),(2,'ایران بانو'),(3,'هدیه'),(4,'کودک و نوجوان'),(5,'خرید'),(6,'نهاده'),(7,'تنخواه'),(8,'اسمارت 50'),(9,'اسمارت 51'),(10,'جلد کارت عادی'),(11,'جلد کارت هدیه');
/*!40000 ALTER TABLE card ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `property`
--

DROP TABLE IF EXISTS property;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE property (
  id int NOT NULL AUTO_INCREMENT,
  user_code varchar(45) NOT NULL,
  cardType varchar(45) NOT NULL,
  supply int NOT NULL DEFAULT '0',
  date_add date DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=164 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `property`
--

LOCK TABLES property WRITE;
/*!40000 ALTER TABLE property DISABLE KEYS */;
INSERT INTO property VALUES (109,'1234','مهر گستر',0,'1402-12-18'),(110,'1234','ایران بانو',10,'1402-12-18'),(111,'1234','هدیه',0,'1402-12-18'),(112,'1234','کودک و نوجوان',15,'1402-12-18'),(113,'1234','خرید',0,'1402-12-18'),(114,'1234','نهاده',0,'1402-12-18'),(115,'1234','تنخواه',0,'1402-12-18'),(116,'1234','اسمارت 50',0,'1402-12-18'),(117,'1234','اسمارت 51',0,'1402-12-18'),(118,'1234','جلد کارت عادی',0,'1402-12-18'),(119,'1234','جلد کارت هدیه',0,'1402-12-18'),(120,'4567','مهر گستر',0,'1402-12-18'),(121,'4567','ایران بانو',0,'1402-12-18'),(122,'4567','هدیه',0,'1402-12-18'),(123,'4567','کودک و نوجوان',0,'1402-12-18'),(124,'4567','خرید',0,'1402-12-18'),(125,'4567','نهاده',0,'1402-12-18'),(126,'4567','تنخواه',0,'1402-12-18'),(127,'4567','اسمارت 50',0,'1402-12-18'),(128,'4567','اسمارت 51',5,'1402-12-18'),(129,'4567','جلد کارت عادی',0,'1402-12-18'),(130,'4567','جلد کارت هدیه',0,'1402-12-18'),(131,'5678','مهر گستر',0,'1402-12-18'),(132,'5678','ایران بانو',0,'1402-12-18'),(133,'5678','هدیه',0,'1402-12-18'),(134,'5678','کودک و نوجوان',0,'1402-12-18'),(135,'5678','خرید',0,'1402-12-18'),(136,'5678','نهاده',0,'1402-12-18'),(137,'5678','تنخواه',0,'1402-12-18'),(138,'5678','اسمارت 50',0,'1402-12-18'),(139,'5678','اسمارت 51',0,'1402-12-18'),(140,'5678','جلد کارت عادی',0,'1402-12-18'),(141,'5678','جلد کارت هدیه',0,'1402-12-18'),(142,'7890','مهر گستر',0,'1402-12-18'),(143,'7890','ایران بانو',0,'1402-12-18'),(144,'7890','هدیه',0,'1402-12-18'),(145,'7890','کودک و نوجوان',0,'1402-12-18'),(146,'7890','خرید',0,'1402-12-18'),(147,'7890','نهاده',0,'1402-12-18'),(148,'7890','تنخواه',0,'1402-12-18'),(149,'7890','اسمارت 50',0,'1402-12-18'),(150,'7890','اسمارت 51',0,'1402-12-18'),(151,'7890','جلد کارت عادی',0,'1402-12-18'),(152,'7890','جلد کارت هدیه',0,'1402-12-18'),(153,'7654','مهر گستر',0,'1402-12-18'),(154,'7654','ایران بانو',0,'1402-12-18'),(155,'7654','هدیه',0,'1402-12-18'),(156,'7654','کودک و نوجوان',0,'1402-12-18'),(157,'7654','خرید',0,'1402-12-18'),(158,'7654','نهاده',0,'1402-12-18'),(159,'7654','تنخواه',0,'1402-12-18'),(160,'7654','اسمارت 50',0,'1402-12-18'),(161,'7654','اسمارت 51',0,'1402-12-18'),(162,'7654','جلد کارت عادی',0,'1402-12-18'),(163,'7654','جلد کارت هدیه',0,'1402-12-18');
/*!40000 ALTER TABLE property ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recieve`
--

DROP TABLE IF EXISTS recieve;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE recieve (
  id int NOT NULL AUTO_INCREMENT,
  admin_supply int NOT NULL DEFAULT '0',
  recieve_date date DEFAULT NULL,
  _type varchar(45) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recieve`
--

LOCK TABLES recieve WRITE;
/*!40000 ALTER TABLE recieve DISABLE KEYS */;
INSERT INTO recieve VALUES (1,10,'1402-12-18','مهر گستر');
/*!40000 ALTER TABLE recieve ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS user;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  id int NOT NULL AUTO_INCREMENT,
  CenterName varchar(100) NOT NULL,
  CenterCode varchar(45) NOT NULL,
  username varchar(45) NOT NULL,
  `password` varchar(45) NOT NULL,
  sum_supply int NOT NULL DEFAULT '0',
  date_added date DEFAULT NULL,
  `status` int NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES user WRITE;
/*!40000 ALTER TABLE user DISABLE KEYS */;
INSERT INTO user VALUES (17,'شهرداری','1234','shahrdari','1234',15,'1402-12-18',0),(18,'مرکزی','4567','markazi','4567',5,'1402-12-18',0),(19,'عدالت 16','5678','edalat16','5678',0,'1402-12-18',0),(20,'ناهارخوران','7890','naharkhoran','7890',0,'1402-12-18',0),(21,'ترمینال','7654','terminal','7654',0,'1402-12-18',0);
/*!40000 ALTER TABLE user ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-03-08 18:54:50
