CREATE TABLE IF NOT EXISTS tricenix(
id MEDIUMINT NOT NULL AUTO_INCREMENT,
timestamp TIMESTAMP,
reply_to_id varchar(32) DEFAULT NULL,
screen_name varchar(20) DEFAULT NULL,
message varchar(140) DEFAULT NULL,
new_messge varchar(140) DEFAULT NULL,
response varchar(140) DEFAULT NULL,
at_mentions varchar(140) DEFAULT NULL,
hash_tags varchar(140) DEFAULT NULL,
urls varchar(140) DEFAULT NULL,
PRIMARY KEY (id)
) ENGINE=InnoDB;
