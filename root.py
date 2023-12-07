import mysql.connector
from flask import Flask, render_template
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify
app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Establish a database connection
# Database configuration
session = {}
def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host='localhost',
            user='root',
            #password='your_db_password',
            database='fs_dn_200'
        )
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Redirect to the login page
        return f(*args, **kwargs)
    return decorated_function


# Function to retrieve featured products from the database
def get_featured_products():
    # Get the database connection and cursor
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Execute a query to retrieve featured products
    cursor.execute("SELECT * FROM products")

    # Fetch the results
    featured_products = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    db.close()

    return featured_products


def get_product_by_id(product_id):
    try:
        # Connect to the database
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Query the database to get product details by ID
        query = "SELECT product_name, price FROM products WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()

        return product  # Return product details as a dictionary
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        db.close()

@app.route('/')
def index():
    # Retrieve featured products
    cart = session.get('cart', {})
    featured_products = get_featured_products()
    return render_template('index.html', featured_products=featured_products, session=session, cart=cart)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Initialize the cart with an empty object or retrieve it from the session
    
    error_message = None  # Initialize error message as None

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Get the database connection and cursor
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Check user credentials against the database
        query = "SELECT * FROM customers WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        if user:
            # Store user_id in session upon successful login
            session['user_id'] = user['customer_id']
            session['username'] = user['first_name']
            return redirect(url_for('index'))  # Redirect to the homepage or desired page
        else:
            error_message = 'Invalid credentials. Please try again.'

    return render_template('login.html',  error=error_message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Get the database connection and cursor
    db = get_db()
    cursor = db.cursor(dictionary=True)
    error_message = None  # Initialize error message as None
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if the password and confirm password match
        if password != confirm_password:
            error_message = 'Passwords do not match. Please try again.'
        else:
            # Insert the new user into the database
            try:
                cursor.execute("INSERT INTO customers (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)",
                               (first_name, last_name, email, password))
                db.commit()
                return redirect(url_for('login'))  # Redirect to login after successful registration
            except mysql.connector.Error as err:
                error_message = 'Error: {}'.format(err)

    return render_template('register.html', error=error_message)

@app.route('/add-to-cart/<int:product_id>', methods=['POST','GET'])
def add_to_cart(product_id):
    # Retrieve the cart from the session or initialize it if it doesn't exist
    cart = session.get('cart', {})
    
    # Check if the product is already in the cart, and if not, add it
    if product_id in cart:
        cart[product_id]['quantity'] += 1
    else:
        # Fetch the product details from the database (replace this with your logic)
        product = get_product_by_id(product_id)

        if product:
            cart[product_id] = {
                'product_name': product['product_name'],
                'price': float(product['price']),
                'quantity': 1,
            }

    # Update the cart data in the session
    session['cart'] = cart
    for i in session['cart']:
        session['cart'][i]['price']= float(session['cart'][i]['price'])
    print(session['cart'])

    # Calculate the total quantity and price in the cart
    total_quantity = sum(item['quantity'] for item in cart.values())
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
    print(session['cart'])
    print(total_quantity)
    print(total_price)
    # Return the updated cart data as JSON
    print({'quantity': int(total_quantity), 'total': float(total_price)})
    return jsonify({'quantity': int(total_quantity), 'total': float(total_price)})


@app.route('/products', methods=['GET', 'POST'])
def products():
    # Get the database connection and cursor
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # Calculate the total quantity and price in the cart
    cart = session.get('cart', {})
    
    print("PRODUCTS",cart)
    # Retrieve all products from the database
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    filtered_products = []

    if request.method == 'POST':
        # Get the search query from the form
        search_query = request.form.get('search_query').strip()

        if search_query:
            # Filter products by name based on the search query
            filtered_products = [product for product in products if search_query.lower() in product['product_name'].lower()]
        else:
            # If no search query provided, show all products
            filtered_products = products

    return render_template('products.html', products=filtered_products, session=session, cart=cart)



@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart = session.get('cart', {})

    if not cart:
        return redirect(url_for('products'))

    if request.method == 'POST':
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            try:
                user_id = session['user_id']
            except KeyError:
                return redirect(url_for('login'))
            total_price = calculate_total_price(cart)

            cursor.execute("INSERT INTO orders (customer_id, total_price) VALUES (%s, %s)",
                           (user_id, total_price))
            db.commit()
            order_id = cursor.lastrowid

            for product_id, item in cart.items():
                cursor.execute("INSERT INTO order_details (order_id, product_id, quantity, subtotal_price) VALUES (%s, %s, %s, %s)",
                               (order_id, product_id, item['quantity'], item['quantity'] * item['price']))
                db.commit()

                cursor.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                               (item['quantity'], product_id))
                db.commit()

            session['cart'] = {}
            success_message = 'Purchase successful! Your order has been placed.'
            return render_template('checkout.html', cart={}, success_message=success_message)

        except mysql.connector.Error as err:
            error_message = f'Database error: {err}'
            return render_template('checkout.html', cart=cart, error_message=error_message)

        finally:
            cursor.close()

    return render_template('checkout.html', cart=cart, cart_total=calculate_total_price(cart))

def calculate_total_price(cart):
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    return round(total_price, 2)

@app.route('/logout')
def logout():
    # Clear the user's session to log them out
    session.pop('user_id', None)
    return redirect(url_for('index'))  # Redirect to the homepage or desired page after logout


if __name__ == '__main__':
    app.run(debug=True)
