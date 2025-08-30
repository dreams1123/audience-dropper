from bson import ObjectId
from pymongo import MongoClient
from config import Config

# MongoDB connection
client = MongoClient(Config.MONGODB_URI)
db = client[Config.DATABASE_NAME]

class User:
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.name = user_data.get('name', '')
        self.role = user_data.get('role', 'user')
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return self.id

def load_user(user_id):
    """Load user by ID for Flask-Login"""
    user_data = db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

def get_user_by_email(email):
    """Get user by email"""
    return db.users.find_one({'email': email})

def create_user(user_data):
    """Create a new user"""
    return db.users.insert_one(user_data)

def get_user_by_id(user_id):
    """Get user by ID"""
    return db.users.find_one({'_id': ObjectId(user_id)})
