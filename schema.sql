-- ============================================================
-- ProteinKart Database Schema
-- A protein delivery startup's complete data model
-- ============================================================

-- Products: The protein catalog
CREATE TABLE products (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT    NOT NULL,
    brand               TEXT    NOT NULL,
    type                TEXT    NOT NULL,       -- whey | casein | isolate | plant | blend
    flavour             TEXT    NOT NULL,
    weight_kg           REAL    NOT NULL,
    price               INTEGER NOT NULL,       -- MRP in ₹
    protein_per_serving INTEGER NOT NULL,
    servings            INTEGER NOT NULL,
    rating              REAL    NOT NULL CHECK(rating BETWEEN 1 AND 5),
    rating_count        INTEGER NOT NULL DEFAULT 0,
    certified           BOOLEAN NOT NULL DEFAULT 0,
    made_in             TEXT    NOT NULL,
    veg                 BOOLEAN NOT NULL DEFAULT 1,
    image_url           TEXT,
    in_stock            BOOLEAN NOT NULL DEFAULT 1
);

-- Orders: Placed by users via agent chat
CREATE TABLE orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name   TEXT    NOT NULL,
    customer_email  TEXT    NOT NULL,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    quantity        INTEGER NOT NULL CHECK(quantity > 0),
    total_price     INTEGER NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'placed',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Seed Data: 20 real-market protein products
-- ============================================================

INSERT INTO products (name, brand, type, flavour, weight_kg, price, protein_per_serving, servings, rating, rating_count, certified, made_in, veg, image_url, in_stock) VALUES

-- Optimum Nutrition
('Gold Standard 100% Whey',          'Optimum Nutrition', 'whey',    'Double Rich Chocolate', 2.27, 4999, 24, 73, 4.6, 18420, 1, 'USA', 1, 'https://images.unsplash.com/photo-1593095948071-474c5cc2989d?auto=format&fit=crop&q=80&w=400', 1),
('Gold Standard 100% Whey',          'Optimum Nutrition', 'whey',    'Vanilla Ice Cream',     2.27, 4999, 24, 73, 4.5, 12300, 1, 'USA', 1, 'https://images.unsplash.com/photo-1579722820308-d74e57198c7b?auto=format&fit=crop&q=80&w=400', 1),
('Gold Standard 100% Casein',        'Optimum Nutrition', 'casein',  'Chocolate Supreme',     1.82, 4599, 24, 52, 4.3, 4200,  1, 'USA', 1, 'https://images.unsplash.com/photo-1546483875-ad9014c88eba?auto=format&fit=crop&q=80&w=400', 1),

-- MuscleBlaze
('Biozyme Performance Whey',         'MuscleBlaze',       'whey',    'Rich Chocolate',        2.0,  3499, 25, 57, 4.4, 32100, 1, 'India', 1, 'https://images.unsplash.com/photo-1610725664338-235d92828334?auto=format&fit=crop&q=80&w=400', 1),
('Raw Whey Protein',                 'MuscleBlaze',       'whey',    'Unflavoured',           1.0,   999, 24, 33, 4.1, 45600, 1, 'India', 1, 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&q=80&w=400', 1),
('Biozyme Iso-Zero',                 'MuscleBlaze',       'isolate', 'Strawberry Shake',      2.0,  4299, 27, 57, 4.5, 8700,  1, 'India', 1, 'https://images.unsplash.com/photo-1572449043416-55f4685c9bb7?auto=format&fit=crop&q=80&w=400', 1),

-- Dymatize
('ISO 100 Hydrolyzed',               'Dymatize',          'isolate', 'Gourmet Chocolate',     2.27, 5999, 25, 71, 4.7, 9800,  1, 'USA', 1, 'https://images.unsplash.com/photo-1594882645126-14020914d58d?auto=format&fit=crop&q=80&w=400', 1),
('Elite 100% Whey',                  'Dymatize',          'whey',    'Rich Chocolate',        2.27, 4199, 25, 63, 4.3, 6500,  1, 'USA', 1, 'https://p.vitalabo.com/it/dymatize-elite-100-whey-2.1-kg.jpg', 1),

-- MyProtein
('Impact Whey Protein',              'MyProtein',         'whey',    'Chocolate Smooth',      1.0,  1499, 21, 40, 4.4, 28900, 1, 'UK', 1, 'https://static.thcdn.com/images/large/webp//productimg/1600/1600/10530743-1624869275091216.jpg', 1),
('Impact Whey Isolate',              'MyProtein',         'isolate', 'Vanilla',               1.0,  1999, 23, 40, 4.5, 11200, 1, 'UK', 1, 'https://static.thcdn.com/images/large/webp//productimg/1600/1600/10530911-3964890253457199.jpg', 1),

-- Nakpro
('Perform Whey Protein',             'Nakpro',            'whey',    'Mango',                 2.0,  2699, 24, 57, 4.2, 15300, 1, 'India', 1, 'https://m.media-amazon.com/images/I/71r9W41FqZL._SL1500_.jpg', 1),
('Raw Whey Protein',                 'Nakpro',            'whey',    'Unflavoured',           1.0,   849, 24, 33, 4.0, 22100, 0, 'India', 1, 'https://m.media-amazon.com/images/I/61M6K5J6IqL._SL1500_.jpg', 1),

-- Plant-Based
('Plant Protein (Pea + Brown Rice)', 'OZiva',             'plant',   'Chocolate',             1.0,  1299, 25, 30, 4.2, 7800,  1, 'India', 1, 'https://m.media-amazon.com/images/I/61s0O52tK0L._SL1200_.jpg', 1),
('Strength Daily Protein',           'Plix',              'plant',   'Cafe Mocha',            1.0,  1599, 25, 30, 4.3, 5400,  1, 'India', 1, 'https://m.media-amazon.com/images/I/61gR7m2-ZVL._SL1500_.jpg', 1),

-- Premium / Niche
('Nitro-Tech Whey Gold',             'MuscleTech',        'whey',    'Double Rich Chocolate', 2.27, 4799, 24, 71, 4.4, 11000, 1, 'USA', 1, 'https://m.media-amazon.com/images/I/71+699H9KzL._SL1500_.jpg', 1),
('Prostar 100% Whey',                'Ultimate Nutrition','whey',    'Chocolate Creme',       2.27, 3999, 25, 67, 4.1, 9100,  1, 'USA', 1, 'https://m.media-amazon.com/images/I/617v12-fWfL._SL1200_.jpg', 0),
('100% Whey Protein Professional',   'Scitec Nutrition',  'whey',    'Chocolate Hazelnut',    2.35, 4499, 22, 78, 4.2, 3200,  1, 'Hungary', 1, 'https://m.media-amazon.com/images/I/61GoyH6+MhL._SL1500_.jpg', 1),
('Nutrilite All Plant Protein',      'Amway',             'plant',   'Unflavoured',           0.5,  1680, 8,  33, 3.9, 6700,  1, 'India', 1, 'https://m.media-amazon.com/images/I/51HSt2N1wWL._SL1000_.jpg', 1),

-- Blend
('Syntha-6 Protein Blend',           'BSN',               'blend',   'Chocolate Milkshake',   2.27, 4299, 22, 51, 4.3, 7400,  1, 'USA', 1, 'https://m.media-amazon.com/images/I/71Xm3zLgPcL._SL1500_.jpg', 1),
('Bigmuscles Nutrition Premium Gold','Big Muscles',       'blend',   'Rich Chocolate',        2.0,  2199, 25, 60, 4.0, 19800, 1, 'India', 1, 'https://m.media-amazon.com/images/I/71MscIeI0vL._SL1500_.jpg', 1);
