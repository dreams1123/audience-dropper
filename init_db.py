#!/usr/bin/env python3
"""
Database initialization script for Audience Dropper
This script sets up the MongoDB collections and creates a test user.
"""

from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the database with required collections and test data"""
    
    # Connect to MongoDB
    try:
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        db = client['audience_dropper']
        
        print("✅ Connected to MongoDB successfully!")
        
        # Create collections if they don't exist
        collections = ['users', 'audiences', 'access_requests']
        
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"✅ Created collection: {collection_name}")
            else:
                print(f"ℹ️  Collection already exists: {collection_name}")
        
        # Create a test user if no users exist
        if db.users.count_documents({}) == 0:
            test_user = {
                'email': 'admin@audiencedropper.com',
                'password': generate_password_hash('admin123'),
                'name': 'Admin User',
                'role': 'admin',
                'company': 'Audience Dropper',
                'created_at': datetime.utcnow(),
                'last_login': datetime.utcnow()
            }
            
            db.users.insert_one(test_user)
            print("✅ Created test user:")
            print("   Email: admin@audiencedropper.com")
            print("   Password: admin123")
        else:
            print("ℹ️  Users already exist in database")
        
        # Create some sample audiences
        if db.audiences.count_documents({}) == 0:
            sample_audiences = [
                {
                    'user_id': 'admin',
                    'name': 'Tech Professionals',
                    'description': 'Software developers, IT professionals, and tech enthusiasts',
                    'category': 'technology',
                    'criteria': '{"interests": ["technology", "programming"], "age_range": [25, 45]}',
                    'status': 'active',
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                },
                {
                    'user_id': 'admin',
                    'name': 'E-commerce Buyers',
                    'description': 'Online shoppers and e-commerce customers',
                    'category': 'ecommerce',
                    'criteria': '{"behaviors": ["online_shopping"], "age_range": [18, 65]}',
                    'status': 'active',
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            ]
            
            db.audiences.insert_many(sample_audiences)
            print("✅ Created sample audiences")
        else:
            print("ℹ️  Audiences already exist in database")
        
        print("\n🎉 Database initialization completed successfully!")
        print("\nYou can now:")
        print("1. Run the application: python app.py")
        print("2. Sign in with: admin@audiencedropper.com / admin123")
        print("3. Or request access as a new user")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("\nPlease check your MongoDB connection string in the .env file")

if __name__ == '__main__':
    print("🚀 Initializing Audience Dropper Database...")
    print("=" * 50)
    init_database()
