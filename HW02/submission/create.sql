-- Drop existing tables if they exist
drop table if exists BIDS;
drop table if exists ITEM_CATEGORIES;
drop table if exists ITEM;
drop table if exists USERS;

-- Create USERS table
create table USERS (
    user_id TEXT PRIMARY KEY,
    rating INTEGER,
    location TEXT,
    country TEXT
);

-- Create ITEM table
create table ITEM (
    item_id INTEGER PRIMARY KEY,
    name TEXT,
    currently REAL,
    first_bid REAL,
    number_of_bids INTEGER,
    country TEXT,
    started DATETIME,
    ends DATETIME,
    seller_id TEXT,
    description TEXT,
    FOREIGN KEY (seller_id) REFERENCES USERS(user_id)
);

-- Create ITEM_CATEGORIES table
create table ITEM_CATEGORIES (
    item_id INTEGER,
    category TEXT,
    PRIMARY KEY (item_id, category),
    FOREIGN KEY (item_id) REFERENCES ITEM(item_id)
);

-- Create BIDS table
create table BIDS (
    user_id TEXT,
    item_id INTEGER,
    time DATETIME,
    amount REAL,
    PRIMARY KEY (user_id, item_id, time),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (item_id) REFERENCES ITEM(item_id)
);
