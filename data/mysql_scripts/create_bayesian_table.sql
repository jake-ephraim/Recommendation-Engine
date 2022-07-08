use SakoDB;
CREATE TABLE bayesian_features(
id BIGINT NOT NULL AUTO_INCREMENT,
a DECIMAL(12, 3) NOT NULL,
b DECIMAL(12, 3) NOT NULL,
viewCount BIGINT NOT NULL,
clickedCount BIGINT NOT NULL,
added2cartCount BIGINT NOT NULL,
boughtCount BIGINT NOT NULL,
PRIMARY KEY (id)
)