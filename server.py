from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from flask import Flask, render_template, redirect, request, session, flash, jsonify
import pg, os, bcrypt, uuid
from time import time
import stripe


tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask('e-commerce', static_url_path='')

db = pg.DB(
   dbname=os.environ.get('PG_DBNAME'),
   host=os.environ.get('PG_HOST'),
   user=os.environ.get('PG_USERNAME'),
   passwd=os.environ.get('PG_PASSWORD')
)
#route to index.html
@app.route('/')
def home():
    return app.send_static_file('index.html')

#All products
@app.route('/api/products')
def products():
    result = db.query('Select * from product')
    data = result.dictresult()
    return jsonify(data)

#Product by ID
@app.route('/api/products/<id>')
def product(id):
    result = db.query('Select * from product where id = $1', id)
    data = result.dictresult()
    return jsonify(data);

#Sign Up Route
@app.route('/api/user/signup', methods=["POST"])
def signup():
    req = request.get_json()
    print req
    password = req['password']
    salt = bcrypt.gensalt()
    encrypted_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    db.insert('customer', {
        'username' : req['uname'],
        'email': req['email'],
        'password' : encrypted_password,
        'first_name' : req['fname'],
        'last_name' : req['lname']
    })
    # data = result.dictresult()
    return jsonify(req);

#shopping cart POST
@app.route('/api/shopping_cart', methods=["POST"])
def shopping_cart():
    req = request.get_json()
    auth = req['auth_token']
    result = db.query('select id from customer inner join auth_token on auth_token.customer_id = customer.id where auth_token.token = $1',auth).dictresult()
    print req
    if(len(result) > 0):
        print result[0]['id']
        db.insert('product_in_shopping_cart',{
        'product_id' : req['product_id'],
        'customer_id': result[0]['id']
        })
        return jsonify(req);
    else:
        return "Access Forbidden", 403

#Shopping Cart GET
@app.route('/api/shopping_cart', methods=['GET'])
def shopping_cart_get():
    req = request.args
    auth = req.get('auth_token')
    result = db.query('select id from customer inner join auth_token on auth_token.customer_id = customer.id where auth_token.token = $1',auth).dictresult()
    if(len(result) > 0):
        cart_items = db.query('select product.name, product.price, product.description, product.image_path from product_in_shopping_cart inner join product on product_in_shopping_cart.product_id = product.id where customer_id = $1', result[0]['id']).dictresult()
        cart_total = db.query('select sum(product.price) from product_in_shopping_cart inner join product on product_in_shopping_cart.product_id = product.id where customer_id = $1', result[0]['id']).dictresult()
        dict = {'cart_items' : cart_items, 'cart_total' : cart_total}
        return jsonify(dict)
    else:
        return "Access Forbidden", 403

#checkout API
@app.route('/api/shopping_cart/checkout', methods=['POST'])
def checkout():
    print "In Python"
    shopitems = []
    jreq = request.get_json()
    auth = jreq['auth_token']
    address = jreq['address']
    city = jreq['city']
    zipcode = jreq['zip']
    state = jreq['state']
    total_price = jreq['total_price']
    print state
    print city
    print total_price
    result = db.query('select id from customer inner join auth_token on auth_token.customer_id = customer.id where auth_token.token = $1',auth).dictresult()
    if(len(result) > 0):
        print result[0]['id']
        #calculating the total_price
        # for product in jreq:
        #     # result1 = db.query('select price from product where id = $1',product['product_id']).dictresult()[0]
        #     # total_price += result1['price']
        #     shopitems.append(product['product_id'])
        # # making an entry on the purchase table
        db.insert('purchase',{
        'customer_id' : result[0]['id'],
        'total_price' : total_price,
        'city' : city,
        'zipcode' : zipcode,
        'state' : state,
        'address' : address
        })
        #updating the product_in_purchase table
        purchase_id = db.query('select max(id) from purchase where customer_id = $1',result[0]['id']).dictresult()[0]['max']
        product_id = db.query('select product_id from product_in_shopping_cart where customer_id = $1',result[0]['id']).dictresult()
        for product in product_id:
            db.insert('product_in_purchase',{
            'product_id' : product['product_id'],
            'purchase_id': purchase_id
            })
        #deleting the cart_items for that customer
        db.query('Delete from product_in_shopping_cart where customer_id = $1',result[0]['id'])

        return jsonify(jreq)
    else:
        return "Access Forbidden", 403


    #Login Route
@app.route('/api/user/login', methods=["POST"])
def login():
    req = request.get_json()
    print req
    username = req['uname']
    password = req['pass']
    query = db.query('select * from customer where username = $1', username).dictresult()
    if(len(query)>0):
        query = query[0]
        stored_enc_pword = query['password']
        del query['password']
        rehash = bcrypt.hashpw(password.encode('utf-8'), stored_enc_pword)

        if (stored_enc_pword == rehash):
            print "Success"
            db_token = db.query('select token from auth_token where customer_id = $1',query['id']).dictresult()
            print db_token

            if(len(db_token) > 0):
                token = db_token[0]
                print "token exist"
            else:
                token = uuid.uuid4()
                db.insert('auth_token',{
                    'token' : token,
                    'token_expires' : '2016-12-31',
                    'customer_id' : query['id']
                })
            return jsonify({
            "user" : query,
            "auth_token" :
                token
            })
    else:
        return "login failed",401
    # data = result.dictresult()
    return "jsonify(password)";

app.run(debug=True)
