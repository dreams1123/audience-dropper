import csv
import io
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from config import Config

# MongoDB connection
client = MongoClient(Config.MONGODB_URI)
db = client[Config.DATABASE_NAME]

from utils.llm_server import get_llm_summary_and_keywords, test_llm_connection

def simulate_llm_chatbot(user_input, conversation_history):
    """LLM chatbot responses using hermes-3-llama-3.1-8b model"""
    questions = [
        "Who are you looking for?",
        "What type of conversations are you looking for?",
        "What topic in conversations are you looking for?",
        "What product or service do you offer?",
        "Describe the person you want to sell your product or service to?",
        "What are some things the person you are looking for would say if they were asking for your product or service?"
    ]
    
    # Check if we have enough conversation history to process with LLM
    if len(conversation_history) >= len(questions):
        # Use LLM to generate response based on conversation
        try:
            # Test LLM connection first
            if test_llm_connection():
                # Process conversation with LLM
                result = get_llm_summary_and_keywords(conversation_history)
                return f"Based on our conversation, I've analyzed your responses and generated keywords to help you find your target audience. Here's what I found: {result.get('summary', '')}"
            else:
                return "Based on our conversation, I'll now generate 10 keywords to help you find your target audience. (LLM server not available, using fallback)"
        except Exception as e:
            print(f"Error using LLM: {e}")
            return "Based on our conversation, I'll now generate 10 keywords to help you find your target audience."
    else:
        # Return the next question in the sequence
        return questions[len(conversation_history)]

def extract_keywords_from_conversation(conversation_history):
    """Extract keywords from conversation using LLM"""
    try:
        # Test LLM connection
        if test_llm_connection():
            # Use LLM to extract keywords
            result = get_llm_summary_and_keywords(conversation_history)
            return result.get('keywords', [])
        else:
            # Fallback to sample keywords if LLM is not available
            print("LLM server not available, using fallback keywords")
            sample_keywords = [
                "target audience", "social media", "marketing", "business", "customers",
                "online presence", "digital marketing", "lead generation", "sales", "growth"
            ]
            return sample_keywords[:10]
    except Exception as e:
        print(f"Error extracting keywords with LLM: {e}")
        # Fallback keywords
        sample_keywords = [
            "target audience", "social media", "marketing", "business", "customers",
            "online presence", "digital marketing", "lead generation", "sales", "growth"
        ]
        return sample_keywords[:10]

def generate_phrases_from_keywords(keywords):
    """Generate phrases based on keywords (simulated)"""
    # This would use LLM to generate relevant phrases
    phrases = []
    for keyword in keywords:
        phrases.extend([
            f"I need help with {keyword}",
            f"Looking for {keyword} solutions",
            f"Best {keyword} strategies",
            f"{keyword} recommendations"
        ])
    return phrases[:10]

def search_social_platforms(keywords, phrases):
    """Search social platforms (simulated)"""
    # This would integrate with actual APIs
    platforms = ['GoFundMe.com', 'x.com', 'reddit.com']
    results = []
    
    for platform in platforms:
        for keyword in keywords[:3]:  # Limit for demo
            results.append({
                'platform': platform,
                'content': f"Sample post about {keyword}",
                'author': f"User{len(results)}",
                'location': f"City{len(results)}, State{len(results)}"
            })
    
    return results

def analyze_and_filter_content(search_results, keywords):
    """Analyze and filter content (simulated)"""
    # This would use LLM to analyze relevance and extract contact info
    filtered = []
    for result in search_results:
        if any(keyword.lower() in result['content'].lower() for keyword in keywords):
            filtered.append({
                'first_name': result['author'].split()[0] if ' ' in result['author'] else result['author'],
                'last_name': result['author'].split()[1] if len(result['author'].split()) > 1 else '',
                'city': result['location'].split(',')[0],
                'state': result['location'].split(',')[1] if ',' in result['location'] else ''
            })
    
    return filtered

def get_contact_information(filtered_results):
    """Get contact information from truepeoplesearch.com (simulated)"""
    # This would integrate with truepeoplesearch.com API
    contacts = []
    for result in filtered_results:
        contacts.append({
            'first_name': result['first_name'],
            'last_name': result['last_name'],
            'city': result['city'],
            'state': result['state'],
            'email': f"{result['first_name'].lower()}.{result['last_name'].lower()}@example.com",
            'phone': f"555-{len(contacts):03d}-{len(contacts):04d}",
            'address': f"{len(contacts)} Main St, {result['city']}, {result['state']}"
        })
    
    return contacts

def generate_csv(contact_data):
    """Generate CSV data"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Address', 'City', 'State'])
    
    # Write data
    for contact in contact_data:
        writer.writerow([
            contact['first_name'],
            contact['last_name'],
            contact['email'],
            contact['phone'],
            contact['address'],
            contact['city'],
            contact['state']
        ])
    
    return output.getvalue()

def create_audience(user_id, audience_data):
    """Create a new audience in the database"""
    audience_data.update({
        'user_id': user_id,
        'status': 'active',
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    })
    return db.audiences.insert_one(audience_data)

def get_user_audiences(user_id):
    """Get all audiences for a user"""
    return list(db.audiences.find({'user_id': user_id}))

def get_audience_by_id(audience_id, user_id):
    """Get a specific audience by ID for a user"""
    return db.audiences.find_one({'_id': ObjectId(audience_id), 'user_id': user_id})
