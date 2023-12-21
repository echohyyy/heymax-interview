from flask import *
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            name = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, name FROM Users WHERE email = ?", (session['email'], ))
            userId, name = cur.fetchone()
            cur.execute("SELECT count(productId) FROM Cart WHERE userId = ?", (userId, ))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, name, noOfItems)

@app.route("/")
def root():
    loggedIn, name, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT productId, name, price, description, image, inventoryAmount FROM Products")
        itemData = cur.fetchall()
        if loggedIn:
            email = session['email'] if loggedIn else ' '
            app.logger.info(email)
            cur.execute("SELECT kind FROM users WHERE email = ?", (email,))
            kind = cur.fetchone()[0]
        else: 
            kind = 'none'
    conn.close()
        
    return render_template('home.html', userType = kind, itemData=itemData, loggedIn=loggedIn, name=name, noOfItems=noOfItems)

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

@app.route("/remove")
def remove():
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productId = ?', (productId, ))
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    return redirect(url_for('root'))



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        
        email = request.form['email']
        password = request.form['password']
        app.logger.info(email+password)

        if is_valid(email, password):
            session['email'] = email
            app.logger.info("post success")
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            app.logger.info(error)
            return render_template('login.html', error=error)
    else:
        if 'email' in session:
            return redirect(url_for('root'))
        else:
            return render_template('login.html', error='')
        


# admin method to additems
@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])
        #Uploading image
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO products (name, price, description, image, inventoryAmount, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, categoryId))
                conn.commit()
            except:
                conn.rollback()
        conn.close()
        return redirect(url_for('root'))
    else:
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT categoryId, name FROM Categories")
            categories = cur.fetchall()
            
        conn.close()
        return render_template('addItem.html',categories=categories)

@app.route('/cart',methods=['GET','POST'])
def cart():
    if 'email' not in session:
        return redirect(url_for('login'))
    loggedIn, name, noOfItems = getLoginDetails()
    email = session['email']

    if request.method == "GET":
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM Users WHERE email = ?", (email, ))
            userId = cur.fetchone()[0]
            cur.execute("SELECT products.productId, products.name, products.price, products.image, products.inventoryAmount, cart.inventoryAmount FROM products, cart WHERE products.productId = cart.productId AND cart.userId = ?", (userId, ))
            products = cur.fetchall()
        totalPrice = 0
        for row in products:
            totalPrice += row[2] * row[5]

        return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, name = name, noOfItems=noOfItems)
    else:
        # checkout
        shippingAddress = request.form['address']
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()

            cur.execute("SELECT userId FROM Users WHERE email = ?", (email,))
            userId = cur.fetchone()[0]

            
            cur.execute('''SELECT p.productId, p.inventoryAmount
                           FROM Products p
                           JOIN cart k ON p.productId = k.productId
                           WHERE k.userId = ?''', (userId,))
            products = cur.fetchall()

            cur.execute("SELECT productId, inventoryAmount FROM cart WHERE userId = ?", (userId,))
            cart_items = cur.fetchall()
            if not cart_items:
                return render_template('checkout.html',  loggedIn=loggedIn, name=name, message="Nothing to checkout.")

            for productId, quantity in cart_items:
                cur.execute("SELECT inventoryAmount, price FROM Products WHERE productId = ?", (productId,))
                productData = cur.fetchone()
                inventoryAmount = productData[0]
                price = productData[1] * quantity
                if quantity > inventoryAmount:
                    return render_template('checkout.html', loggedIn=loggedIn, name=name, message="Insufficient stock for one or more items.")
                else:
                    # Insert a transaction record
                    cur.execute('''INSERT INTO Transactions (date, userId, productId, quantity, shippingAddress, price) 
                                VALUES (?, ?, ?, ?, ?, ?)''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), userId, productId, quantity, shippingAddress, price))
                    
                    # Reduce the inventoryAmount by 1
                    cur.execute("UPDATE Products SET inventoryAmount = inventoryAmount - 1 WHERE productId = ?", (productId,))


            if any(inventoryAmount <= 0 for _, inventoryAmount in products):
                return render_template('checkout.html', loggedIn=loggedIn, name=name, message="Error: One or more products are out of stock.")

            # Clear the user's cart
            cur.execute("DELETE FROM cart WHERE userId = ?", (userId,))

            conn.commit()

        return render_template('checkout.html',  loggedIn=loggedIn, name=name, message="Transaction successfully made.")

@app.route('/updateCartItem/<int:product_id>', methods=['POST'])
def updateCartItem(product_id):
    new_quantity = int(request.form['quantity'])

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'],))
        user_id = cur.fetchone()[0]
        cur.execute("UPDATE cart SET inventoryAmount = ? WHERE userId = ? AND productId = ?", (new_quantity, user_id, product_id))
        conn.commit()
        flash("successfully update")

    return redirect(url_for('cart'))  # Redirect to the cart view page
    


@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        productId = int(request.args.get('productId'))
        quantity = max(int(request.args.get('quantity', 1)), 1)  # Ensure quantity is at least 1
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = ?", (session['email'], ))
            userId = cur.fetchone()[0]

            # Check if the product is already in the cart
            cur.execute("SELECT inventoryAmount FROM cart WHERE userId = ? AND productId = ?", (userId, productId))
            result = cur.fetchone()
            try:
                # Product is in the cart, update the quantity
                if result:
                    new_quantity = result[0] + quantity
                    cur.execute("UPDATE cart SET inventoryAmount = ? WHERE userId = ? AND productId = ?", (new_quantity, userId, productId))
                else:
                    # Product is not in the cart, insert a new row
                    cur.execute("INSERT INTO cart (userId, productId, inventoryAmount) VALUES (?, ?, ?)", (userId, productId, quantity))

                conn.commit()
                msg = "Added successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return redirect(url_for('cart'))

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('login'))
    email = session['email']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM Users WHERE email = ?", (email, ))
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM cart WHERE userId = ? AND productId = ?", (userId, productId))
            conn.commit()
            msg = "removed successfully"
        except:
            conn.rollback()
            msg = "error occured"
    conn.close()
    return redirect(url_for('cart'))

@app.route('/account/orders',methods=['GET'])
def orders():
    email = session.get('email')
    loggedIn, name, noOfItems = getLoginDetails()
    if not email:
        return redirect(url_for('login'))  
    
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        cur.execute("SELECT userId FROM users WHERE email = ?", (email,))
        userId = cur.fetchone()[0]

        cur.execute('''SELECT t.date
                       FROM Transactions t
                       WHERE t.userId = ?
                       GROUP BY t.date''', (userId,))
        dates = cur.fetchall()
        app.logger.info(type(dates[0][0]))
        transactions = []
        for date in dates:
            cur.execute('''SELECT t.orderNumber, t.date, t.price, p.name, t.quantity, t.shippingAddress
                        FROM Transactions t
                        JOIN Products p ON t.productId = p.productId
                        WHERE t.userId = ? AND t.date = ?''', (userId, date[0]))
            transactions.append(cur.fetchall())

    return render_template('orders.html', noOfItems = noOfItems, loggedIn=loggedIn, name=name, transactions=transactions)

@app.route("/productDescription")
def productDescription():
    loggedIn, name, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventoryAmount FROM products WHERE productId = ?', (productId, ))
        productData = cur.fetchone()
        if loggedIn:
            email = session['email'] if loggedIn else ' '
            app.logger.info(email)
            cur.execute("SELECT kind FROM users WHERE email = ?", (email,))
            kind = cur.fetchone()[0]
        else: 
            kind = 'none'
    conn.close()
    return render_template("productDescription.html", userType = kind, data=productData, loggedIn = loggedIn, name = name, noOfItems = noOfItems)

def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM Users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == password:
            return True
    return False

if __name__ == '__main__':
    app.run(debug=True)