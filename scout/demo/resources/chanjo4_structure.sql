-- MySQL dump 10.13  Distrib 5.5.47, for Linux (x86_64)
--
-- Host: localhost    Database: chanjo4
-- ------------------------------------------------------
-- Server version	5.5.47

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
-- Table structure for table `sample`
--

DROP TABLE IF EXISTS `sample`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sample` (
  `id` varchar(32) NOT NULL,
  `group_id` varchar(128) DEFAULT NULL,
  `source` varchar(256) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  `group_name` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_sample_group_id` (`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transcript`
--

DROP TABLE IF EXISTS `transcript`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transcript` (
  `id` varchar(32) NOT NULL,
  `gene_id` int(11) NOT NULL,
  `gene_name` varchar(32) DEFAULT NULL,
  `chromosome` varchar(10) DEFAULT NULL,
  `length` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_transcript_gene_name` (`gene_name`),
  KEY `ix_transcript_gene_id` (`gene_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transcript_stat`
--

DROP TABLE IF EXISTS `transcript_stat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transcript_stat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mean_coverage` float NOT NULL,
  `completeness_10` float DEFAULT NULL,
  `completeness_15` float DEFAULT NULL,
  `completeness_20` float DEFAULT NULL,
  `completeness_50` float DEFAULT NULL,
  `completeness_100` float DEFAULT NULL,
  `threshold` int(11) DEFAULT NULL,
  `_incomplete_exons` text,
  `sample_id` varchar(32) NOT NULL,
  `transcript_id` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `_sample_transcript_uc` (`sample_id`,`transcript_id`),
  KEY `transcript_id` (`transcript_id`),
  CONSTRAINT `transcript_stat_ibfk_1` FOREIGN KEY (`sample_id`) REFERENCES `sample` (`id`),
  CONSTRAINT `transcript_stat_ibfk_2` FOREIGN KEY (`transcript_id`) REFERENCES `transcript` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=132347652 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-03-02 13:27:53
