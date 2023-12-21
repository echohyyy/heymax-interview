import sqlite3
# this file will generate the empty database
# Open database
conn = sqlite3.connect('database.db')

# Drop the existing tables if necessary
conn.execute("DROP TABLE IF EXISTS Transactions")
conn.execute("DROP TABLE IF EXISTS Cart")
conn.execute("DROP TABLE IF EXISTS Products")
conn.execute("DROP TABLE IF EXISTS Customers")
conn.execute("DROP TABLE IF EXISTS categories")

conn.execute('''CREATE TABLE categories
            (categoryId INTEGER PRIMARY KEY,
            name TEXT)''')

conn.execute('''CREATE TABLE Products
             (productId INTEGER PRIMARY KEY,
              name TEXT,
              description TEXT,
              image TEXT,
              inventoryAmount INTEGER,
              price REAL,
              FOREIGN KEY(categoryId) REFERENCES categories(categoryId))''')


# Customer kind: Normal/Admin
conn.execute('''CREATE TABLE Customers
             (customerId INTEGER PRIMARY KEY,
              name TEXT,
			  password TEXT,
              email TEXT,
              kind TEXT)''')

conn.execute('''CREATE TABLE Transactions
             (orderNumber INTEGER PRIMARY KEY,
              quantity INTEGER,
              customerId INTEGER,
              productId INTEGER,
              FOREIGN KEY(customerId) REFERENCES Customers(customerId),
              FOREIGN KEY(productId) REFERENCES Products(productId))''')

conn.execute('''CREATE TABLE Cart
            (customerId INTEGER,
             productId INTEGER,
             inventoryAmount INTEGER,
             FOREIGN KEY(customerId) REFERENCES Customers(customerId),
             FOREIGN KEY(productId) REFERENCES Products(productId))''')

conn.commit()
conn.close()
