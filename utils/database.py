from pymongo import MongoClient
from config import Config

def get_database():
    """Get database connection"""
    client = MongoClient(Config.MONGODB_URI)
    return client[Config.DATABASE_NAME]

def init_database():
    """Initialize database with required collections and indexes"""
    db = get_database()
    
    # Create collections if they don't exist
    collections = ['users', 'audiences', 'access_requests']
    
    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
    
    # Create indexes
    db.users.create_index('email', unique=True)
    db.audiences.create_index('user_id')
    db.access_requests.create_index('email')
    
    print("Database initialized successfully!")
