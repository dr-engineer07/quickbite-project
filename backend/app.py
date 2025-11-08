import os
import datetime
import jwt
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from bson import ObjectId
from functools import wraps  # <-- STEP 6: Added this import

# --- Step 1: Load Environment Variables ---
load_dotenv()
print(f"--- 1. MONGO_URI from .env: {os.getenv('MONGO_URI')}")
print(f"--- 2. SECRET_KEY from .env: {os.getenv('SECRET_KEY')}")

# --- Step 2: Initialize the App ---
app = Flask(__name__)

# --- Step 3: Configure the App ---
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

print(f"--- 3. MONGO_URI in Flask Config: {app.config.get('MONGO_URI')}")

# Check if the MONGO_URI was loaded correctly
if not app.config["MONGO_URI"]:
    print("Error: MONGO_URI is not set. Please check your .env file.")
    exit(1)

# --- Step 4: Initialize Extensions ---
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- ADDING A CONNECTION TEST ---
try:
    print("--- 4. Testing MongoDB Connection... ---")
    mongo.cx.server_info()
    print("--- 5. MongoDB Connection SUCCESSFUL! ---")
except Exception as e:
    print("--- 5. MongoDB Connection FAILED! ---")
    print(f"--- ERROR DETAILS: {e} ---")
    exit(1)
# --- END OF CONNECTION TEST ---

print("Flask App Initialized with MongoDB and CORS")

# --- Step 5: Define Database Collections ---
print("--- 6. Accessing mongo.db collections... ---")
users_collection = mongo.db.users
restaurants_collection = mongo.db.restaurants
orders_collection = mongo.db.orders
messages_collection = mongo.db.messages
tips_collection = mongo.db.tips

print(f"Connected to MongoDB. DB: {mongo.db.name}")


# ==========================================================
# --- STEP 6: Helper Function: Token Decorator ("The Bouncer") ---
# ==========================================================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 1. Check if the 'Authorization' header is present
        if 'Authorization' in request.headers:
            # 2. Get the token. It comes in the format "Bearer <token>"
            auth_header = request.headers['Authorization']
            if ' ' in auth_header:
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        # 3. Try to decode the token to see if it's valid
        try:
            # This checks the signature AND the expiration time
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # 4. Pass the user's data to the route
            current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': f'Token error: {e}'}), 401


        # 5. If everything is good, run the original route function
        #    (e.g., checkout(), get_orders(), etc.)
        return f(current_user, *args, **kwargs)

    return decorated


# ==========================================================
# AUTHENTICATION ROUTES (From Step 4)
# ==========================================================

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Username, email, and password are required"}), 400

    if users_collection.find_one({"username": username}):
        return jsonify({"message": "Username already exists"}), 409
    
    if users_collection.find_one({"email": email}):
        return jsonify({"message": "Email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        users_collection.insert_one({
            "username": username,
            "email": email,
            "password_hash": hashed_password
        })
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"message": f"An error occurred: {e}"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user = users_collection.find_one({"username": username})

    if user and bcrypt.check_password_hash(user["password_hash"], password):
        
        token = jwt.encode({
            'user_id': str(user['_id']),
            'username': user['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({"message": "Login successful", "token": token}), 200
    
    return jsonify({"message": "Invalid username or password"}), 401

# ==========================================================
# PUBLIC ROUTES (From Step 5)
# ==========================================================

@app.route("/api/restaurants", methods=["GET"])
def get_all_restaurants():
    try:
        # Find all documents in the restaurants_collection
        restaurants = list(restaurants_collection.find())
        
        # Convert the ObjectId to a string for each restaurant
        for restaurant in restaurants:
            restaurant['_id'] = str(restaurant['_id'])

        return jsonify(restaurants), 200
    
    except Exception as e:
        return jsonify({"message": f"An error occurred: {e}"}), 500

@app.route("/api/restaurants/<id>", methods=["GET"])
def get_one_restaurant(id):
    try:
        # Convert the ID string from the URL into a MongoDB ObjectId
        restaurant_id = ObjectId(id)

        # Find one restaurant that matches that _id
        restaurant = restaurants_collection.find_one({"_id": restaurant_id})

        # If no restaurant is found, return a 404 error
        if not restaurant:
            return jsonify({"message": "Restaurant not found"}), 404

        # If we found it, convert its _id to a string to send as JSON
        restaurant['_id'] = str(restaurant['_id'])

        # Return the single restaurant's data
        return jsonify(restaurant), 200

    except Exception as e:
        # This will catch errors like an invalid ID format
        return jsonify({"message": f"An error occurred or ID is invalid: {e}"}), 400

# ==========================================================
# PROTECTED ROUTES (Login Required) (From Step 6)
# ==========================================================

@app.route("/api/checkout", methods=["POST"])
@token_required  # <-- Our "bouncer" is in action!
def checkout(current_user):
    try:
        data = request.get_json()
        items = data.get('items')
        total = data.get('total')

        if not items or not total:
            return jsonify({"message": "Cart items and total are required"}), 400

        # Get the user_id from the token
        user_id = current_user['user_id']

        # Create the new order document
        new_order = {
            "user_id": ObjectId(user_id), # Store as ObjectId
            "items": items,
            "total": total,
            "status": "Preparing",
            "date": datetime.datetime.utcnow()
        }
        
        # Insert the order into the database
        orders_collection.insert_one(new_order)
        
        return jsonify({"message": "Order placed successfully"}), 201

    except Exception as e:
        return jsonify({"message": f"An error occurred: {e}"}), 500

@app.route("/api/orders", methods=["GET"])
@token_required  # <-- The bouncer is on duty here too
def get_orders(current_user):
    try:
        # Get the user_id from the token
        user_id = current_user['user_id']

        # Find all orders in the database that match this user's ID
        user_orders = list(orders_collection.find({
            "user_id": ObjectId(user_id)
        }))

        # Convert ObjectIds to strings so they can be sent as JSON
        for order in user_orders:
            order['_id'] = str(order['_id'])
            order['user_id'] = str(order['user_id'])
            # We sort by date, newest first
            order['date'] = order['date'].strftime('%B %d, %Y')
            
        # Sort the orders by date (newest first)
        user_orders.sort(key=lambda x: x['date'], reverse=True)
            
        return jsonify(user_orders), 200

    except Exception as e:
        return jsonify({"message": f"An error occurred: {e}"}), 500
        
# ==========================================================
# RUN THE APP
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)