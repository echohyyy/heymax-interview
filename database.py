import sqlite3
# this file will generate the empty database
# Open database
conn = sqlite3.connect('database.db')

# Drop the existing tables if necessary
conn.execute("DROP TABLE IF EXISTS Transactions")
conn.execute("DROP TABLE IF EXISTS Cart")
conn.execute("DROP TABLE IF EXISTS Products")
conn.execute("DROP TABLE IF EXISTS Users")
conn.execute("DROP TABLE IF EXISTS Categories")

conn.execute('''CREATE TABLE Categories
            (categoryId INTEGER PRIMARY KEY,
            name TEXT)''')

conn.execute('''CREATE TABLE Products
             (productId INTEGER PRIMARY KEY,
              name TEXT,
              description TEXT,
              image TEXT,
              inventoryAmount INTEGER,
              price REAL,
              categoryId INTEGER,
              FOREIGN KEY(categoryId) REFERENCES Categories(categoryId))''')


# User kind: customer/admin
conn.execute('''CREATE TABLE Users
             (userId INTEGER PRIMARY KEY,
              name TEXT,
			  password TEXT,
              email TEXT,
              kind TEXT)''')

conn.execute('''CREATE TABLE Transactions
             (orderNumber INTEGER PRIMARY KEY,
              quantity INTEGER,
              userId INTEGER,
              productId INTEGER,
              shippingAddress TEXT,
              FOREIGN KEY(userId) REFERENCES Users(userId),
              FOREIGN KEY(productId) REFERENCES Products(productId))''')

conn.execute('''CREATE TABLE Cart
            (userId INTEGER,
             productId INTEGER,
             inventoryAmount INTEGER,
             FOREIGN KEY(userId) REFERENCES Users(userId),
             FOREIGN KEY(productId) REFERENCES Products(productId))''')

conn.commit()
conn.close()
