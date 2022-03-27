DROP TABLE IF EXISTS `visitors`;

CREATE TABLE `visitors`
(
    `vid` INTEGER AUTO_INCREMENT PRIMARY KEY,
    `v_name` VARCHAR(128) NOT NULL,
    `v_address` VARCHAR(512) NOT NULL,
    `phone_number` VARCHAR(16),
    `v_email` VARCHAR(128),
    `device_id` VARCHAR(64) NOT NULL UNIQUE,
    `infected` TINYINT(1) NOT NULL DEFAULT 0
);


DROP TABLE IF EXISTS `places`;

CREATE TABLE `places`
(
	`pid` INTEGER AUTO_INCREMENT PRIMARY KEY,
	`p_name` VARCHAR(128) NOT NULL,
	`p_address` VARCHAR(512) NOT NULL,
	`QRcode` VARCHAR(128) NOT NULL
);


DROP TABLE IF EXISTS `agents`;

CREATE TABLE `agents`
(
	`aid` INTEGER AUTO_INCREMENT PRIMARY KEY,
	`a_username` VARCHAR(64) NOT NULL UNIQUE,
	`a_password` VARCHAR(128) NOT NULL 
);


DROP TABLE IF EXISTS `hospitals`;

CREATE TABLE `hospitals`
(
	`hid` INTEGER AUTO_INCREMENT PRIMARY KEY,
    `h_name` VARCHAR(128) NOT NULL,
    `h_email` VARCHAR(128) NOT NULL,
	`h_username` VARCHAR(64) UNIQUE,
	`h_password` VARCHAR(128)
);



DROP TABLE IF EXISTS `visit`; 

CREATE TABLE `visit`
(
    `visit_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
	`place_id` INTEGER NOT NULL,
	`device` VARCHAR(64) NOT NULL,
	`entry_date` DATE, 
	`entry_time` TIME(0),
	`exit_date` DATE,
	`exit_time` TIME(0),
	FOREIGN KEY (`device`) REFERENCES `visitors`(`device_id`) ON DELETE CASCADE,
	FOREIGN KEY (`place_id`) REFERENCES `places`(`pid`) ON DELETE CASCADE
);
