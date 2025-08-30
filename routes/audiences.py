from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_login import login_required, current_user
from utils.audience_helpers import (
    get_user_audiences, create_audience, get_audience_by_id,
    simulate_llm_chatbot, extract_keywords_from_conversation,
    generate_phrases_from_keywords, search_social_platforms,
    analyze_and_filter_content, get_contact_information, generate_csv
)

audiences_bp = Blueprint('audiences', __name__)

@audiences_bp.route('/audiences')
@login_required
def audiences():
    user_audiences = get_user_audiences(current_user.id)
    return render_template('audiences.html', audiences=user_audiences)

@audiences_bp.route('/audiences/create', methods=['GET', 'POST'])
@login_required
def create_audience_simple():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        criteria = request.form['criteria']
        
        audience_data = {
            'name': name,
            'description': description,
            'criteria': criteria
        }
        
        create_audience(current_user.id, audience_data)
        flash('Audience created successfully!', 'success')
        return redirect(url_for('audiences.audiences'))
    
    return render_template('create_audience.html')

@audiences_bp.route('/audiences/create/step1', methods=['GET', 'POST'])
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
        
        # Check if we have enough conversation history to process with LLM
        if len(conversation_history) >= 6:  # After all 6 questions are answered
            # Use LLM to process the conversation
            from utils.llm_server import get_llm_summary_and_keywords
            
            try:
                result = get_llm_summary_and_keywords(conversation_history)
                llm_response = f"Based on our conversation, I've analyzed your responses and generated keywords to help you find your target audience. Here's what I found: {result.get('summary', '')}"
                keywords = result.get('keywords', [])
            except Exception as e:
                print(f"Error using LLM: {e}")
                llm_response = simulate_llm_chatbot(user_input, conversation_history)
                keywords = extract_keywords_from_conversation(conversation_history)
        else:
            # Use regular chatbot for questions
            llm_response = simulate_llm_chatbot(user_input, conversation_history)
            keywords = []
        
        return jsonify({
            'response': llm_response,
            'keywords': keywords
        })
    
    return render_template('create_audience_step1.html')

@audiences_bp.route('/audiences/create/step2', methods=['GET', 'POST'])
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

@audiences_bp.route('/audiences/create/step3', methods=['GET', 'POST'])
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

@audiences_bp.route('/audiences/create/step4', methods=['GET', 'POST'])
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
            'name': audience_name,
            'keywords': session.get('audience_creation', {}).get('keywords', []),
            'phrases': session.get('audience_creation', {}).get('phrases', []),
            'contacts': contact_data
        }
        
        audience_id = create_audience(current_user.id, audience_data).inserted_id
        
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

@audiences_bp.route('/audiences/create/download/<audience_id>')
@login_required
def download_audience_csv(audience_id):
    """Download CSV file for the created audience"""
    audience = get_audience_by_id(audience_id, current_user.id)
    if not audience:
        flash('Audience not found', 'error')
        return redirect(url_for('audiences.audiences'))
    
    csv_data = generate_csv(audience.get('contacts', []))
    
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=audience_{audience_id}.csv'
    
    return response

@audiences_bp.route('/audiences/manage')
@login_required
def manage_audiences():
    user_audiences = get_user_audiences(current_user.id)
    return render_template('manage_audiences.html', audiences=user_audiences)
