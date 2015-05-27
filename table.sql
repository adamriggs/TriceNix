CREATE TABLE IF NOT EXISTS tricenix(
id MEDIUMINT NOT NULL AUTO_INCREMENT,
timestamp TIMESTAMP,
reply_to_id varchar(32) DEFAULT NULL,
screen_name varchar(20) DEFAULT NULL,
message varchar(140) DEFAULT NULL,
response varchar(140) DEFAULT NULL,
PRIMARY KEY (id)
) ENGINE=InnoDB;
