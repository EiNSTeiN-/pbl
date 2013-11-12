-- MySQL dump 10.13  Distrib 5.1.61, for debian-linux-gnu (i486)
--
-- Host: localhost    Database: pbl
-- ------------------------------------------------------
-- Server version	5.1.61-0ubuntu0.10.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `leak_content`
--

DROP TABLE IF EXISTS `leak_content`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `leak_content` (
  `leak_content_id` int(11) NOT NULL AUTO_INCREMENT,
  `leak_id` int(11) DEFAULT NULL,
  `line_id` int(11) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `value` text,
  PRIMARY KEY (`leak_content_id`),
  KEY `leak_content_leak_id` (`leak_id`),
  KEY `leak_content_line_id` (`line_id`),
  KEY `leak_content_type` (`type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `leak_metadata`
--

DROP TABLE IF EXISTS `leak_metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `leak_metadata` (
  `leak_id` int(11) NOT NULL DEFAULT '0',
  `name` varchar(128) NOT NULL DEFAULT '',
  `value` text,
  PRIMARY KEY (`leak_id`,`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `leaks`
--

DROP TABLE IF EXISTS `leaks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `leaks` (
  `leak_id` int(11) NOT NULL AUTO_INCREMENT,
  `data` longblob,
  `htmldata` longblob,
  `nblines` int(11) DEFAULT NULL,
  `isbad` int(11) DEFAULT '0',
  `isparsed` int(11) DEFAULT '0',
  `filter` text,
  `comment` text,
  `date` int(11) NOT NULL,
  `reason` text,
  `source` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`leak_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pastebin_entry`
--

DROP TABLE IF EXISTS `pastebin_entry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pastebin_entry` (
  `pastebin_id` varchar(16) NOT NULL DEFAULT '',
  `leak_id` int(11) NOT NULL,
  `title` text,
  `user` varchar(255) DEFAULT NULL,
  `syntax` varchar(255) DEFAULT NULL,
  `isreported` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`pastebin_id`),
  KEY `pastebin_entry_leak_id` (`leak_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tweets`
--

DROP TABLE IF EXISTS `tweets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tweets` (
  `tweet_id` bigint(20) NOT NULL DEFAULT '0',
  `leak_id` int(11) DEFAULT NULL,
  `date` text,
  `tweet` text,
  `url` text,
  `category` text,
  `pastebin_id` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`tweet_id`),
  UNIQUE KEY `pbl_tweets_tweet_id` (`tweet_id`),
  UNIQUE KEY `pbl_tweets_pastebin_id` (`pastebin_id`),
  UNIQUE KEY `pbl_tweets_leak_id` (`leak_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_seen`
--

DROP TABLE IF EXISTS `user_seen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_seen` (
  `leak_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  UNIQUE KEY `user_seen_user_leak_unique` (`leak_id`,`user_id`),
  KEY `user_seen_leak_id` (`leak_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(128) DEFAULT NULL,
  `password` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-11-12 20:36:54
