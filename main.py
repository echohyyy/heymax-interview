from flask import *
import sqlite3
import os
from werkzeug.utils import secure_filename

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
    conn.close()
        
    return render_template('home.html', itemData=itemData, loggedIn=loggedIn, name=name, noOfItems=noOfItems)

@app.route("/logout")
def logout():
    session.pop('email', None)
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

@app.route('/cart',methods=['GET'])
def cart():
    return render_template('cart.html')

@app.route('/account/orders',methods=['GET'])
def orders():
    return render_template('orders.html')

@app.route("/productDescription")
def productDescription():
    loggedIn, name, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, inventoryAmount FROM products WHERE productId = ?', (productId, ))
        productData = cur.fetchone()
    conn.close()
    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, name = name, noOfItems = noOfItems)

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