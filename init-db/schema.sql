/* 최종 수정 : 2026-01-06 16:56 */
/* 수정 사항 : events 테이블에서 host 필드 -> VARCHAR(100) */

CREATE TABLE `user_activity_score` (
	`user_activity_score_id`	INT	NOT NULL   AUTO_INCREMENT,
	`user_id`			INT	NOT NULL,
	`badge_id`			INT	NOT NULL,
	`score`				INT	NOT NULL   DEFAULT 0,
	PRIMARY KEY (`user_activity_score_id`)
);

CREATE TABLE `post_reactions` (
	`reaction_id`	INT	NOT NULL   AUTO_INCREMENT,
	`post_id`	INT	NOT NULL,
	`user_id`	INT	NOT NULL,
	`type`		ENUM('like','dislike')	NOT NULL,
	PRIMARY KEY (`reaction_id`),
	UNIQUE KEY `unique_user_post_reaction` (`user_id`, `post_id`)
);

CREATE TABLE `users` (
	`user_id`			INT	NOT NULL   AUTO_INCREMENT,
	`email`				VARCHAR(255)	NOT NULL,
	`nickname`			VARCHAR(50)	NOT NULL,
	`provider`			VARCHAR(255)	NOT NULL,
	`provider_id`			VARCHAR(255)	NOT NULL,
	`created_at`			DATETIME	NOT NULL   DEFAULT CURRENT_TIMESTAMP,
	`is_email_sub`			TINYINT(1)	NOT NULL,
	`is_events_notification_sub`	TINYINT(1)	NOT NULL,
	`is_posts_notification_sub`	TINYINT(1)	NOT NULL,
	`is_admin`		TINYINT(1)	NOT NULL,
	`exp_now`		INT	NOT NULL   DEFAULT 0,
	`exp_total`		INT	NOT NULL   DEFAULT 0,
	`level`			INT	NOT NULL    DEFAULT 1,
	`reliability_score`	INT	NOT NULL    DEFAULT 50,
	PRIMARY KEY (`user_id`)
);

CREATE TABLE `badge` (
	`badge_id`		INT			NOT NULL   AUTO_INCREMENT,
	`name`			VARCHAR(100)	NOT NULL,
	`description`		VARCHAR(255)	NULL,
	`required_score`	INT			NOT NULL,
	PRIMARY KEY (`badge_id`)
);

CREATE TABLE `posts` (
	`post_id`	INT	NOT NULL   AUTO_INCREMENT,
	`event_id`	INT	NOT NULL,
	`user_id`	INT	NOT NULL,
	`category`	ENUM('후기','질문','정보')	NOT NULL,
	`title`		VARCHAR(255)	NOT NULL,
	`content`	TEXT		NOT NULL,
	`updated_at`	TIMESTAMP	NULL 		ON UPDATE CURRENT_TIMESTAMP,
	`created_at`	TIMESTAMP	NULL		DEFAULT CURRENT_TIMESTAMP,
	`like_count`	INT		NOT NULL	DEFAULT 0,
	`dislike_count`	INT		NOT NULL	DEFAULT 0,
	`views`		INT		NOT NULL	DEFAULT 0,
	`image_url`  VARCHAR(300)  NULL,
	PRIMARY KEY (`post_id`)
);

CREATE TABLE `events` (
	`event_id`	INT			NOT NULL   AUTO_INCREMENT,
	`kopis_id`	VARCHAR(20)	NOT NULL,
	`title`		VARCHAR(255)	NOT NULL,
	`artist`		VARCHAR(100)	NULL,
	`start_date`	DATE			NOT NULL,
	`end_date`	DATE			NOT NULL,
	`venue`	VARCHAR(100)	NULL,
	`age`		VARCHAR(20)	NULL,
	`poster`	VARCHAR(500)	NULL,
	`time`		VARCHAR(255)	NULL,
	`price`		VARCHAR(255)	NULL,
	`update_date`	TIMESTAMP		NOT NULL,
	`relate_url`       VARCHAR(255)	NOT NULL,
	`host`		VARCHAR(100)	NULL,
	`genre` 	VARCHAR(50)	DEFAULT '대중음악',
	PRIMARY KEY (`event_id`),
	UNIQUE KEY `unique_kopis_events` (`kopis_id`)
);

CREATE TABLE `bookmark` (
	`bookmark_id`	INT	NOT NULL   AUTO_INCREMENT,
	`user_id`	INT	NOT NULL,
	`event_id`	INT	NOT NULL,
	PRIMARY KEY (`bookmark_id`),
UNIQUE KEY `unique_user_event_bookmark` (`user_id`, `event_id`)
);

CREATE TABLE `notifications` (
	`notification_id`	INT	NOT NULL   AUTO_INCREMENT,
	`user_id`		INT	NOT NULL,
	`post_id`		INT	NOT NULL,
	`event_id`		INT	NOT NULL,
	`type`			VARCHAR(20)		NOT NULL,
	`is_read`		TINYINT(1)		NOT NULL	DEFAULT 0,
	`message`		VARCHAR(255)	NOT NULL,
	`created_at`	TIMESTAMP		NOT NULL	DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`notification_id`)
);


CREATE TABLE `comments` (
	`comment_id`	INT		NOT NULL   AUTO_INCREMENT,
	`user_id`	INT		NOT NULL,
	`post_id`	INT		NOT NULL,
	`content`	TEXT		NOT NULL,
	`created_at`	TIMESTAMP	NOT NULL	DEFAULT CURRENT_TIMESTAMP,
	`updated_at`	TIMESTAMP	NOT NULL	DEFAULT CURRENT_TIMESTAMP   ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`comment_id`)
);

CREATE TABLE `reports` (
	`report_id`		INT	NOT NULL   AUTO_INCREMENT,
	`post_id`		INT	NOT NULL,
	`user_id`		INT	NOT NULL,
	`reason_category`	ENUM('도배','욕설','허위정보')	NOT NULL,
	`reason_detail`	TEXT			NOT NULL,
	`created_at`		TIMESTAMP		NOT NULL	DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`report_id`)
);



ALTER TABLE `posts` ADD CONSTRAINT `FK_users_TO_posts` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;
ALTER TABLE `posts` ADD CONSTRAINT `FK_events_TO_posts` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`) ON DELETE CASCADE;


ALTER TABLE `post_reactions` ADD CONSTRAINT `FK_posts_TO_reactions` FOREIGN KEY (`post_id`) REFERENCES `posts` (`post_id`) ON DELETE CASCADE;
ALTER TABLE `post_reactions` ADD CONSTRAINT `FK_users_TO_reactions` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;


ALTER TABLE `comments` ADD CONSTRAINT `FK_users_TO_comments` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;
ALTER TABLE `comments` ADD CONSTRAINT `FK_posts_TO_comments` FOREIGN KEY (`post_id`) REFERENCES `posts` (`post_id`) ON DELETE CASCADE;


ALTER TABLE `bookmark` ADD CONSTRAINT `FK_users_TO_bookmark` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;
ALTER TABLE `bookmark` ADD CONSTRAINT `FK_events_TO_bookmark` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`) ON DELETE CASCADE;


ALTER TABLE `notifications` ADD CONSTRAINT `FK_users_TO_notifications` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;
ALTER TABLE `notifications` ADD CONSTRAINT `FK_posts_TO_notifications` FOREIGN KEY (`post_id`) REFERENCES `posts` (`post_id`) ON DELETE CASCADE; 
ALTER TABLE `notifications` ADD CONSTRAINT `FK_events_TO_notifications` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`) ON DELETE CASCADE; 

ALTER TABLE `reports` ADD CONSTRAINT `FK_posts_TO_reports` FOREIGN KEY (`post_id`) REFERENCES `posts` (`post_id`) ON DELETE CASCADE;
ALTER TABLE `reports` ADD CONSTRAINT `FK_users_TO_reports` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

ALTER TABLE `user_activity_score` ADD CONSTRAINT `FK_users_TO_score` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE; 
ALTER TABLE `user_activity_score` ADD CONSTRAINT `FK_badge_TO_score` FOREIGN KEY (`badge_id`) REFERENCES `badge` (`badge_id`) ON DELETE CASCADE;


