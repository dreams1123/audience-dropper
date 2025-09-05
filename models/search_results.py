from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from config import Config

# MongoDB connection
client = MongoClient(Config.MONGODB_URI)
db = client[Config.DATABASE_NAME]

class SearchResult:
    def __init__(self, data):
        self.id = str(data['_id'])
        self.platform = data.get('platform', '')
        self.name = data.get('name', '')
        self.creator = data.get('creator', '')
        self.location = data.get('location', '')
        self.date = data.get('date', '')
        self.description = data.get('description', '')
        self.url = data.get('url', '')
        self.relevance_score = data.get('relevance_score', 0)
        self.keywords_matched = data.get('keywords_matched', [])
        self.user_id = data.get('user_id', '')
        self.audience_id = data.get('audience_id', '')
        self.created_at = data.get('created_at', datetime.utcnow())
        self.status = data.get('status', 'active')

def save_search_results(user_id, audience_id, results):
    """Save search results to database"""
    for result in results:
        result['user_id'] = user_id
        result['audience_id'] = audience_id
        result['created_at'] = datetime.utcnow()
        result['status'] = 'active'
    
    if results:
        return db.search_results.insert_many(results)
    return None

def get_search_results_by_audience(audience_id, user_id):
    """Get search results for a specific audience"""
    return list(db.search_results.find({
        'audience_id': audience_id,
        'user_id': user_id
    }).sort('created_at', -1))

def update_search_status(result_id, status):
    """Update the status of a search result"""
    return db.search_results.update_one(
        {'_id': ObjectId(result_id)},
        {'$set': {'status': status}}
    )

def delete_search_results(audience_id, user_id):
    """Delete all search results for an audience"""
    return db.search_results.delete_many({
        'audience_id': audience_id,
        'user_id': user_id
    })

def get_search_stats(audience_id, user_id):
    """Get statistics for search results"""
    pipeline = [
        {'$match': {'audience_id': audience_id, 'user_id': user_id}},
        {'$group': {
            '_id': '$platform',
            'count': {'$sum': 1},
            'avg_relevance': {'$avg': '$relevance_score'}
        }}
    ]
    return list(db.search_results.aggregate(pipeline))
