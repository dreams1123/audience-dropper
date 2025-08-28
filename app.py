from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
import os
import csv
import io
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client['audience_dropper']

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

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

@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user_data = db.users.find_one({'email': email})
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('signin.html')

@app.route('/request-access', methods=['GET', 'POST'])
def request_access():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        company = request.form['company']
        reason = request.form['reason']
        
        # Check if user already exists
        existing_user = db.users.find_one({'email': email})
        if existing_user:
            flash('An account with this email already exists', 'error')
        else:
            # Create pending user
            db.access_requests.insert_one({
                'name': name,
                'email': email,
                'company': company,
                'reason': reason,
                'status': 'pending',
                'created_at': datetime.utcnow()
            })
            flash('Access request submitted successfully! We will review and get back to you.', 'success')
            return redirect(url_for('signin'))
    
    return render_template('request_access.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/profile')
@login_required
def profile():
    user_data = db.users.find_one({'_id': ObjectId(current_user.id)})
    return render_template('profile.html', user=user_data)

@app.route('/account')
@login_required
def account():
    user_data = db.users.find_one({'_id': ObjectId(current_user.id)})
    return render_template('account.html', user=user_data)

@app.route('/audiences')
@login_required
def audiences():
    user_audiences = list(db.audiences.find({'user_id': current_user.id}))
    return render_template('audiences.html', audiences=user_audiences)

@app.route('/audiences/create', methods=['GET', 'POST'])
@login_required
def create_audience():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        criteria = request.form['criteria']
        
        audience_data = {
            'user_id': current_user.id,
            'name': name,
            'description': description,
            'criteria': criteria,
            'status': 'active',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        db.audiences.insert_one(audience_data)
        flash('Audience created successfully!', 'success')
        return redirect(url_for('audiences'))
    
    return render_template('create_audience.html')

# New 4-step audience creation workflow
@app.route('/audiences/create/step1', methods=['GET', 'POST'])
@login_required
def create_audience_step1():
    """Step 1: Chatbot interaction to gather information and generate keywords"""
    if request.method == 'POST':
        data = request.get_json()
        user_input = data.get('user_input', '')
        conversation_history = data.get('conversation_history', [])
        
        # Save conversation to session
        if 'audience_creation' not in session:
            session['audience_creation'] = {}
        
        session['audience_creation']['step1_conversation'] = conversation_history
        
        # Simulate LLM response (replace with actual local LLM integration)
        llm_response = simulate_llm_chatbot(user_input, conversation_history)
        
        return jsonify({
            'response': llm_response,
            'keywords': extract_keywords_from_conversation(conversation_history)
        })
    
    return render_template('create_audience_step1.html')

@app.route('/audiences/create/step2', methods=['GET', 'POST'])
@login_required
def create_audience_step2():
    """Step 2: Generate phrases based on keywords"""
    if request.method == 'POST':
        data = request.get_json()
        keywords = data.get('keywords', [])
        
        # Save keywords to session
        if 'audience_creation' not in session:
            session['audience_creation'] = {}
        session['audience_creation']['keywords'] = keywords
        
        # Generate phrases based on keywords
        phrases = generate_phrases_from_keywords(keywords)
        
        return jsonify({'phrases': phrases})
    
    # Get keywords from session
    keywords = session.get('audience_creation', {}).get('keywords', [])
    return render_template('create_audience_step2.html', keywords=keywords)

@app.route('/audiences/create/step3', methods=['GET', 'POST'])
@login_required
def create_audience_step3():
    """Step 3: Search social platforms and analyze content"""
    if request.method == 'POST':
        data = request.get_json()
        keywords = data.get('keywords', [])
        phrases = data.get('phrases', [])
        
        # Save phrases to session
        if 'audience_creation' not in session:
            session['audience_creation'] = {}
        session['audience_creation']['phrases'] = phrases
        
        # Search social platforms (simulated)
        search_results = search_social_platforms(keywords, phrases)
        
        # Analyze and filter results
        filtered_results = analyze_and_filter_content(search_results, keywords)
        
        return jsonify({
            'search_results': search_results,
            'filtered_results': filtered_results
        })
    
    # Get data from session
    audience_data = session.get('audience_creation', {})
    keywords = audience_data.get('keywords', [])
    phrases = audience_data.get('phrases', [])
    
    return render_template('create_audience_step3.html', keywords=keywords, phrases=phrases)

@app.route('/audiences/create/step4', methods=['GET', 'POST'])
@login_required
def create_audience_step4():
    """Step 4: Get contact information and download CSV"""
    if request.method == 'POST':
        data = request.get_json()
        filtered_results = data.get('filtered_results', [])
        
        # Get contact information (simulated)
        contact_data = get_contact_information(filtered_results)
        
        # Save audience data
        audience_name = session.get('audience_creation', {}).get('audience_name', 'New Audience')
        audience_data = {
            'user_id': current_user.id,
            'name': audience_name,
            'keywords': session.get('audience_creation', {}).get('keywords', []),
            'phrases': session.get('audience_creation', {}).get('phrases', []),
            'contacts': contact_data,
            'status': 'active',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        audience_id = db.audiences.insert_one(audience_data).inserted_id
        
        # Generate CSV
        csv_data = generate_csv(contact_data)
        
        return jsonify({
            'audience_id': str(audience_id),
            'csv_data': csv_data,
            'contact_count': len(contact_data)
        })
    
    # Get data from session
    audience_data = session.get('audience_creation', {})
    return render_template('create_audience_step4.html', audience_data=audience_data)

@app.route('/audiences/create/download/<audience_id>')
@login_required
def download_audience_csv(audience_id):
    """Download CSV file for the created audience"""
    audience = db.audiences.find_one({'_id': ObjectId(audience_id), 'user_id': current_user.id})
    if not audience:
        flash('Audience not found', 'error')
        return redirect(url_for('audiences'))
    
    csv_data = generate_csv(audience.get('contacts', []))
    
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=audience_{audience_id}.csv'
    
    return response

# Helper functions for the audience creation process
def simulate_llm_chatbot(user_input, conversation_history):
    """Simulate LLM chatbot responses"""
    # This would be replaced with actual local LLM integration
    questions = [
        "Who are you looking for?",
        "What type of conversations are you looking for?",
        "What topic in conversations are you looking for?",
        "What product or service do you offer?",
        "Describe the person you want to sell your product or service to?",
        "What are some things the person you are looking for would say if they were asking for your product or service?"
    ]
    
    # Simple logic to determine next question or generate keywords
    if len(conversation_history) < len(questions):
        return questions[len(conversation_history)]
    else:
        return "Based on our conversation, I'll now generate 10 keywords to help you find your target audience."

def extract_keywords_from_conversation(conversation_history):
    """Extract keywords from conversation (simulated)"""
    # This would use actual LLM to extract keywords
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

@app.route('/audiences/manage')
@login_required
def manage_audiences():
    user_audiences = list(db.audiences.find({'user_id': current_user.id}))
    return render_template('manage_audiences.html', audiences=user_audiences)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
