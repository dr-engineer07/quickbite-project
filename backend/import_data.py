import os
from pymongo import MongoClient
from dotenv import load_dotenv

# --- Step 1: Restaurant data ---
restaurants_data = [
    {
        "id": 1,
        "name": "Bella Italia",
        "cuisine": "italian",
        "image": "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/0163d622-dce8-41fc-a2c8-aa2af405d8f3.png",
        "rating": 4.8,
        "reviews": 245,
        "priceRange": "₹₹",
        "deliveryTime": "25-35 min",
        "offer": "50% OFF on main course",
        "menu": [
            {"id": 101, "name": "Margherita Pizza", "description": "Classic pizza with tomato sauce and mozzarella", "price": 399, "veg": True, "popular": True},
            {"id": 102, "name": "Pasta Carbonara", "description": "Creamy pasta with bacon and cheese", "price": 349, "veg": False, "popular": True},
            {"id": 103, "name": "Tiramisu", "description": "Classic Italian dessert", "price": 199, "veg": True, "popular": False},
            {"id": 104, "name": "Garlic Bread", "description": "Oven-baked bread with garlic butter", "price": 149, "veg": True, "popular": True}
        ]
    },
    {
        "id": 2,
        "name": "Dragon Wok",
        "cuisine": "chinese",
        "image": "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/79227f8b-54f7-4283-b420-67a51c0e2c55.png",
        "rating": 4.5,
        "reviews": 189,
        "priceRange": "₹",
        "deliveryTime": "20-30 min",
        "offer": "Free spring rolls above ₹299",
        "menu": [
            {"id": 201, "name": "Kung Pao Chicken", "description": "Spicy stir-fry with chicken and peanuts", "price": 329, "veg": False, "popular": True},
            {"id": 202, "name": "Vegetable Fried Rice", "description": "Stir-fried rice with mixed vegetables", "price": 249, "veg": True, "popular": True},
            {"id": 203, "name": "Dim Sum Platter", "description": "Assorted steamed dumplings", "price": 299, "veg": False, "popular": False},
            {"id": 204, "name": "Sweet and Sour Soup", "description": "Traditional Chinese soup", "price": 179, "veg": True, "popular": True}
        ]
    },
    {
        "id": 3,
        "name": "Burger Heaven",
        "cuisine": "american",
        "image": "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/1160f469-b0a2-479d-ad5b-828a7dcca179.png",
        "rating": 4.9,
        "reviews": 312,
        "priceRange": "₹₹",
        "deliveryTime": "15-25 min",
        "offer": "Buy 1 Get 1 on Wednesdays",
        "menu": [
            {"id": 301, "name": "Classic Cheeseburger", "description": "Beef patty with cheese and veggies", "price": 229, "veg": False, "popular": True},
            {"id": 302, "name": "Crispy Chicken Burger", "description": "Crispy fried chicken with special sauce", "price": 199, "veg": False, "popular": True},
            {"id": 303, "name": "Veggie Supreme", "description": "Plant-based patty with fresh vegetables", "price": 189, "veg": True, "popular": False},
            {"id": 304, "name": "French Fries", "description": "Crispy golden fries with seasoning", "price": 99, "veg": True, "popular": True}
        ]
    },
    {
        "id": 4,
        "name": "Taco Fiesta",
        "cuisine": "mexican",
        "image": "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/7be9fd5c-25e1-4622-8ffe-bfcabe9e3d3c.png",
        "rating": 4.6,
        "reviews": 176,
        "priceRange": "₹",
        "deliveryTime": "30-40 min",
        "offer": "Free guacamole with any order",
        "menu": [
            {"id": 401, "name": "Beef Tacos", "description": "Three soft tacos with seasoned beef", "price": 279, "veg": False, "popular": True},
            {"id": 402, "name": "Vegetable Quesadilla", "description": "Grilled tortilla with cheese and veggies", "price": 229, "veg": True, "popular": True},
            {"id": 403, "name": "Nachos Supreme", "description": "Crispy nachos with cheese and toppings", "price": 249, "veg": False, "popular": False},
            {"id": 404, "name": "Churros", "description": "Fried dough pastry with chocolate dip", "price": 149, "veg": True, "popular": True}
        ]
    },
    {
        "id": 5,
        "name": "Spice Garden",
        "cuisine": "indian",
        "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8aW5kaWFuJTIwcmVzdGF1cmFudHxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",
        "rating": 4.7,
        "reviews": 321,
        "priceRange": "₹₹",
        "deliveryTime": "20-30 min",
        "offer": "20% OFF on biryani",
        "menu": [
            {"id": 501, "name": "Butter Chicken", "description": "Tender chicken in creamy tomato sauce", "price": 349, "veg": False, "popular": True},
            {"id": 502, "name": "Paneer Tikka", "description": "Grilled cottage cheese with spices", "price": 279, "veg": True, "popular": True},
            {"id": 503, "name": "Vegetable Biryani", "description": "Fragrant rice with mixed vegetables", "price": 299, "veg": True, "popular": False},
            {"id": 504, "name": "Garlic Naan", "description": "Soft bread with garlic butter", "price": 79, "veg": True, "popular": True}
        ]
    },
    {
        "id": 6,
        "name": "Thai Orchid",
        "cuisine": "thai",
        "image": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8dGhhaSUyMHJlc3RhdXJhbnR8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=500&q=60",
        "rating": 4.4,
        "reviews": 198,
        "priceRange": "₹₹",
        "deliveryTime": "25-35 min",
        "offer": "Free Thai iced tea with main course",
        "menu": [
            {"id": 601, "name": "Pad Thai", "description": "Stir-fried rice noodles with tofu and peanuts", "price": 299, "veg": True, "popular": True},
            {"id": 602, "name": "Green Curry", "description": "Spicy coconut curry with vegetables", "price": 329, "veg": True, "popular": True},
            {"id": 603, "name": "Tom Yum Soup", "description": "Hot and sour soup with mushrooms", "price": 199, "veg": True, "popular": False},
            {"id": 604, "name": "Mango Sticky Rice", "description": "Sweet dessert with mango and coconut", "price": 179, "veg": True, "popular": True}
        ]
    },
    {
        "id": 7,
        "name": "Curry House",
        "cuisine": "indian",
        "image": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8aW5kaWFuJTIwZm9vZHxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=500&q=60",
        "rating": 4.3,
        "reviews": 167,
        "priceRange": "₹",
        "deliveryTime": "15-25 min",
        "offer": "Free delivery on orders above ₹199",
        "menu": [
            {"id": 701, "name": "Chicken Curry", "description": "Spicy chicken curry with gravy", "price": 279, "veg": False, "popular": True},
            {"id": 702, "name": "Dal Tadka", "description": "Lentils tempered with spices", "price": 149, "veg": True, "popular": True},
            {"id": 703, "name": "Aloo Gobi", "description": "Potato and cauliflower dry curry", "price": 199, "veg": True, "popular": False},
            {"id": 704, "name": "Roti", "description": "Whole wheat flatbread", "price": 25, "veg": True, "popular": True}
        ]
    },
    {
        "id": 8,
        "name": "Sweet Tooth",
        "cuisine": "desserts",
        "image": "https://images.unsplash.com/photo-1551024506-0bccd828d307?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZGVzc2VydCUyMHNob3B8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=500&q=60",
        "rating": 4.8,
        "reviews": 234,
        "priceRange": "₹",
        "deliveryTime": "15-20 min",
        "offer": "10% OFF on ice creams",
        "menu": [
            {"id": 801, "name": "Chocolate Brownie", "description": "Rich chocolate brownie with fudge", "price": 149, "veg": True, "popular": True},
            {"id": 802, "name": "New York Cheesecake", "description": "Creamy cheesecake with berry compote", "price": 199, "veg": True, "popular": True},
            {"id": 803, "name": "Ice Cream Sundae", "description": "Vanilla ice cream with hot fudge", "price": 179, "veg": True, "popular": False},
            {"id": 804, "name": "Macarons Box", "description": "Assorted French macarons", "price": 299, "veg": True, "popular": True}
        ]
    }
]


def import_data():
    print("Starting data import...")

    # --- Step 2: Load .env file ---
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        print("Error: MONGO_URI not found in .env file.")
        print("Please create a .env file in the 'backend' folder with your MongoDB connection string.")
        return

    # --- Step 3: Connect to MongoDB ---
    try:
        client = MongoClient(mongo_uri)
        db = client.quickbiteDB
        restaurants_collection = db.restaurants

        print(f"Connected to database: {db.name}")
        print(f"Target collection: {restaurants_collection.name}")

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return

    # --- Step 4: Clear existing data ---
    try:
        print("Clearing old restaurant data...")
        delete_result = restaurants_collection.delete_many({})
        print(f"Deleted {delete_result.deleted_count} old documents.")
    except Exception as e:
        print(f"Error clearing collection: {e}")
        client.close()
        return

    # --- Step 5: Insert new data ---
    if not restaurants_data:
        print("No restaurant data found.")
        client.close()
        return

    try:
        print(f"Inserting {len(restaurants_data)} new restaurant documents...")
        insert_result = restaurants_collection.insert_many(restaurants_data)
        print(f"Successfully inserted {len(insert_result.inserted_ids)} documents.")
    except Exception as e:
        print(f"Error inserting data: {e}")

    # --- Step 6: Close connection ---
    client.close()
    print("Data import finished. Connection closed.")


if __name__ == "__main__":
    import_data()
