from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from flask import Flask, render_template, redirect, request, session, flash, jsonify
import pg, os, bcrypt, uuid
from time import time
import stripe


tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask('e-commerce', template_folder=tmp_dir)

db = pg.DB(
   dbname=os.environ.get('PG_DBNAME'),
   host=os.environ.get('PG_HOST'),
   user=os.environ.get('PG_USERNAME'),
   passwd=os.environ.get('PG_PASSWORD')
)
#All products
@app.route('/api/products')
def products():
    result = db.query('Select * from product')
    data = result.dictresult()
    return jsonify(data);

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
        'username' : req['username'],
        'email': req['email'],
        'password' : encrypted_password,
        'first_name' : req['first_name'],
        'last_name' : req['last_name']
    })
    # data = result.dictresult()
    return jsonify(req);

    #Login Route
@app.route('/api/user/login', methods=["POST"])
def login():
    req = request.get_json()
    print req
    username = req['username']
    password = req['password']
    query = db.query('select * from customer where username = $1', username).dictresult()[0]
    print query
    stored_enc_pword = query['password']
    del query['password']
    print stored_enc_pword
    rehash = bcrypt.hashpw(password.encode('utf-8'), stored_enc_pword)
    if (stored_enc_pword == rehash):
        print "Success"
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
