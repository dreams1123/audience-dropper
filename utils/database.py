from pymongo import MongoClient
from config import Config

def get_database():
    """Get database connection"""
    client = MongoClient(Config.MONGODB_URI)
    return client[Config.DATABASE_NAME]

def init_database():
    """Initialize database with required collections and indexes"""
    try:
        # Create collections if they don't exist
        if 'users' not in db.list_collection_names():
            db.create_collection('users')
            print("✅ Created 'users' collection")
        
        if 'audiences' not in db.list_collection_names():
            db.create_collection('audiences')
            print("✅ Created 'audiences' collection")
            
        if 'audience_conversations' not in db.list_collection_names():
            db.create_collection('audience_conversations')
            print("✅ Created 'audience_conversations' collection")
        
        # Create indexes for better performance
        db.users.create_index('email', unique=True)
        db.users.create_index('user_id')
        
        db.audiences.create_index('user_id')
        db.audiences.create_index('created_at')
        
        db.audience_conversations.create_index('user_id')
        db.audience_conversations.create_index('created_at')
        db.audience_conversations.create_index('status')
        
        print("✅ Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
