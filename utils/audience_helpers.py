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
        "Describe the person you want to sell your product or service to?"
    ]
    
    # Calculate how many questions have been asked and answered
    # Each question-answer pair takes 2 messages in conversation_history
    questions_answered = len(conversation_history) // 2
    
    # Debug logging
    print(f"Chatbot debug - Conversation history length: {len(conversation_history)}")
    print(f"Chatbot debug - Questions answered: {questions_answered}")
    print(f"Chatbot debug - User input: {user_input}")
    
    # Check if we have answered all 5 questions (10 messages: 5 questions + 5 answers)
    if len(conversation_history) >= 10:
        print("Chatbot debug - All questions answered, generating summary")
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
        # If we have 0, 2, 4, 6, 8, 10 messages, we need questions 0, 1, 2, 3, 4, 5
        next_question = questions[questions_answered]
        print(f"Chatbot debug - Asking next question: {next_question}")
        return next_question

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
                "I need help with", "looking for solutions", "my business is struggling",
                "need support", "anyone know a good", "recommendations for",
                "just started", "trying to find", "need advice", "help me with"
            ]
            return sample_keywords[:10]
    except Exception as e:
        print(f"Error extracting keywords with LLM: {e}")
        # Fallback keywords
        sample_keywords = [
            "I need help with", "looking for solutions", "my business is struggling",
            "need support", "anyone know a good", "recommendations for",
            "just started", "trying to find", "need advice", "help me with"
        ]
        return sample_keywords[:10]

def generate_phrases_from_keywords(keywords):
    """Generate 10 phrases based on keywords using LLM"""
    try:
        # Test LLM connection
        if test_llm_connection():
            # Use LLM to generate phrases
            from utils.llm_server import get_llm_phrases_from_keywords
            phrases = get_llm_phrases_from_keywords(keywords)
            print(f"LLM generated {len(phrases)} phrases: {phrases}")
            return phrases[:10]  # Ensure exactly 10 phrases
        else:
            print("LLM server not available, using fallback phrases")
            return generate_fallback_phrases(keywords)
    except Exception as e:
        print(f"Error generating phrases with LLM: {e}")
        return generate_fallback_phrases(keywords)

def generate_fallback_phrases(keywords):
    """Generate intelligent fallback phrases using prompt-based logic when LLM is not available"""
    if not keywords:
        return []
    
    # Create a prompt-based approach for generating natural phrases
    phrases = []
    
    # Analyze keywords to understand context
    keywords_text = ", ".join(keywords[:5])  # Use first 5 keywords for context
    
    # Generate phrases using intelligent prompting logic
    phrases = generate_phrases_from_prompt_logic(keywords, keywords_text)
    
    return phrases[:10]  # Ensure exactly 10 phrases

def generate_phrases_from_prompt_logic(keywords, keywords_text):
    """Generate phrases using prompt-based logic instead of static templates"""
    phrases = []
    
    # Define different phrase categories based on social media patterns
    phrase_patterns = [
        # Personal experience patterns
        {
            "pattern": "personal_struggle",
            "examples": [
                f"I'm dealing with {keywords[0].lower()}",
                f"Just found out about {keywords[0].lower()}",
                f"Been struggling with {keywords[0].lower()}",
            ]
        },
        # Family/relationship patterns
        {
            "pattern": "family_concern", 
            "examples": [
                f"My mom has {keywords[0].lower()}" if len(keywords) > 0 else "My family member needs help",
                f"My wife is dealing with {keywords[1].lower()}" if len(keywords) > 1 else "My partner needs support",
                f"My dad was diagnosed with {keywords[0].lower()}" if len(keywords) > 0 else "My father needs help",
            ]
        },
        # Help-seeking patterns
        {
            "pattern": "seeking_help",
            "examples": [
                f"Looking for help with {keywords[0].lower()}" if len(keywords) > 0 else "Need help and advice",
                f"Does anyone know about {keywords[1].lower()}?" if len(keywords) > 1 else "Anyone have experience with this?",
                f"Need advice on {keywords[2].lower()}" if len(keywords) > 2 else "Seeking guidance and support",
            ]
        },
        # Community/support patterns
        {
            "pattern": "community_support",
            "examples": [
                f"Support group for {keywords[0].lower()}?" if len(keywords) > 0 else "Looking for support group",
                f"Anyone else going through {keywords[1].lower()}?" if len(keywords) > 1 else "Others in similar situation?",
            ]
        }
    ]
    
    # Generate phrases from each pattern category
    for pattern_group in phrase_patterns:
        for example in pattern_group["examples"]:
            if len(phrases) < 10:
                phrases.append(example)
    
    # If we still need more phrases, generate additional ones
    while len(phrases) < 10:
        remaining_needed = 10 - len(phrases)
        additional_phrases = generate_additional_contextual_phrases(keywords, remaining_needed)
        phrases.extend(additional_phrases)
        break  # Avoid infinite loop
    
    return phrases[:10]

def generate_additional_contextual_phrases(keywords, count_needed):
    """Generate additional contextual phrases when more are needed"""
    additional = []
    
    # Create more natural variations based on keywords
    for i in range(count_needed):
        if i < len(keywords):
            keyword = keywords[i]
            
            # Generate contextual phrases based on keyword analysis
            if any(word in keyword.lower() for word in ['cancer', 'disease', 'illness', 'sick']):
                additional.append(f"Recently diagnosed with {keyword.lower()}")
            elif any(word in keyword.lower() for word in ['help', 'support', 'need']):
                additional.append(f"Looking for {keyword.lower()} in my area")
            elif any(word in keyword.lower() for word in ['treatment', 'therapy', 'doctor']):
                additional.append(f"Best {keyword.lower()} recommendations?")
            else:
                # Generic but natural fallback
                additional.append(f"Anyone have experience with {keyword.lower()}?")
        else:
            # Use remaining keywords cyclically
            keyword = keywords[i % len(keywords)]
            additional.append(f"Need guidance on {keyword.lower()}")
    
    return additional

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

def save_audience_conversation(audience_data):
    """
    Save audience conversation data to database for persistent access
    
    Args:
        audience_data: Dictionary containing conversation data
        
    Returns:
        audience_id: The ID of the saved audience record
    """
    try:
        # Insert into audience_conversations collection
        result = db.audience_conversations.insert_one(audience_data)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error saving audience conversation: {e}")
        return None

def get_audience_conversation(audience_id):
    """
    Retrieve audience conversation data from database
    
    Args:
        audience_id: The ID of the audience record
        
    Returns:
        audience_data: Dictionary containing conversation data
    """
    try:
        audience_data = db.audience_conversations.find_one({'_id': ObjectId(audience_id)})
        if audience_data:
            audience_data['_id'] = str(audience_data['_id'])
        return audience_data
    except Exception as e:
        print(f"Error retrieving audience conversation: {e}")
        return None

def update_audience_conversation(audience_id, update_data):
    """
    Update audience conversation data in database
    
    Args:
        audience_id: The ID of the audience record
        update_data: Dictionary containing fields to update
        
    Returns:
        success: Boolean indicating if update was successful
    """
    try:
        result = db.audience_conversations.update_one(
            {'_id': ObjectId(audience_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating audience conversation: {e}")
        return False

def get_user_latest_conversation(user_id):
    """
    Get the most recent conversation for a user
    
    Args:
        user_id: The user ID
        
    Returns:
        conversation_data: Dictionary containing conversation data or None
    """
    try:
        conversation_data = db.audience_conversations.find_one(
            {'user_id': user_id},
            sort=[('created_at', -1)]  # Sort by creation date, newest first
        )
        return conversation_data
    except Exception as e:
        print(f"Error retrieving user's latest conversation: {e}")
        return None

def get_user_conversation_audiences(user_id):
    """
    Get all conversation-based audiences for a user
    
    Args:
        user_id: The user ID
        
    Returns:
        conversation_audiences: List of conversation data
    """
    try:
        conversation_audiences = list(db.audience_conversations.find(
            {'user_id': user_id},
            sort=[('created_at', -1)]  # Sort by creation date, newest first
        ))
        return conversation_audiences
    except Exception as e:
        print(f"Error retrieving user's conversation audiences: {e}")
        return []
