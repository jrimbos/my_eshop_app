-- Insert data into the Category Table
INSERT INTO categories (category_name) VALUES
    ('Smartphones'),
    ('Gaming Consoles'),
    ('Wearable Tech');

-- Insert data into the Product Table
INSERT INTO products (product_name, description, price, stock_quantity, category_id, image_url) VALUES
    ('iPhone 15', 'The latest iPhone with amazing features', 999.99, 100, 1, 'https://www.apple.com/newsroom/images/2023/09/apple-unveils-iphone-15-pro-and-iphone-15-pro-max/article/Apple-iPhone-15-Pro-lineup-hero-230912_Full-Bleed-Image.jpg.xlarge.jpg'),
    ('PS5', 'Next-gen gaming console from Sony', 499.99, 50, 2, 'https://media.4rgos.it/i/Argos/8349024_R_Z001A?w=1500&h=880&qlt=70&fmt=webp'),
    ('Huawei Watch', 'Stylish smartwatch with fitness tracking', 199.99, 30, 3, 'https://c8n.tradeling.com/img/plain/pim/rs:auto:800::0/f:webp/q:95/up/62fb59a6f0ea157f3d1e7257/f2d1f21966c0d185aad3d54f27acc300.jpg');

-- Insert data into the Customer Table
INSERT INTO customers (first_name, last_name, email, password, address, phone_number) VALUES
    ('John', 'Doe', 'john@example.com', 'hashed_password', '123 Main St, City', '123-456-7890'),
    ('Jane', 'Smith', 'jane@example.com', 'hashed_password', '456 Elm St, Town', '987-654-3210');

-- Insert data into the Order Table
INSERT INTO orders (customer_id, total_price) VALUES
    (1, 999.99),
    (2, 499.99);

-- Insert data into the Order Details Table
INSERT INTO order_details (order_id, product_id, quantity, subtotal_price) VALUES
    (1, 1, 2, 1999.98),
    (2, 2, 1, 499.99);

-- Insert data into the Cart Table
INSERT INTO carts (customer_id) VALUES
    (1),
    (2);

-- Insert data into the Cart Item Table
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES
    (1, 1, 1),
    (2, 3, 2);
