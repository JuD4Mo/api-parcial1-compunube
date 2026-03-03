USE `productsDB`;

CREATE TABLE IF NOT EXISTS `products` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `quantity` INT NOT NULL DEFAULT 0,
  `priceU` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `products` (name, quantity, priceU) VALUES
('Laptop Lenovo IdeaPad 4', 6, 100.00),
('Mouse Wireless', 25, 15.50);
