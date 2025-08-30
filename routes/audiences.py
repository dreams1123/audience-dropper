from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_login import login_required, current_user
from utils.audience_helpers import (
    get_user_audiences, create_audience, get_audience_by_id,
    simulate_llm_chatbot, extract_keywords_from_conversation,
    generate_phrases_from_keywords, search_social_platforms,
    analyze_and_filter_content, get_contact_information, generate_csv
)
from datetime import datetime

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
                
                # Store the processed data in the database for persistent access
                audience_data = {
                    'user_id': current_user.id,
                    'conversation_history': conversation_history,
                    'summary': result.get('summary', ''),
                    'keywords': keywords,
                    'status': 'processing',
                    'created_at': datetime.utcnow()
                }
                
                # Save to database
                from utils.audience_helpers import save_audience_conversation
                audience_id = save_audience_conversation(audience_data)
                
                # Store audience_id in session for future steps
                session['audience_creation']['audience_id'] = audience_id
                
                # Check if results are good enough to proceed
                results_quality = assess_results_quality(keywords, result.get('summary', ''))
                
                return jsonify({
                    'response': llm_response,
                    'keywords': keywords,
                    'summary': result.get('summary', ''),
                    'audience_id': audience_id,
                    'results_quality': results_quality,
                    'can_proceed': results_quality['score'] >= 7,  # Minimum quality score
                    'show_next_button': results_quality['score'] >= 7
                })
                
            except Exception as e:
                print(f"Error using LLM: {e}")
                llm_response = simulate_llm_chatbot(user_input, conversation_history)
                keywords = extract_keywords_from_conversation(conversation_history)
                
                return jsonify({
                    'response': llm_response,
                    'keywords': keywords,
                    'can_proceed': False,
                    'show_next_button': False,
                    'error': 'LLM processing failed, using fallback'
                })
        else:
            # Use regular chatbot for questions
            llm_response = simulate_llm_chatbot(user_input, conversation_history)
            keywords = []
            
            return jsonify({
                'response': llm_response,
                'keywords': keywords,
                'can_proceed': False,
                'show_next_button': False
            })
    
    return render_template('create_audience_step1.html')

def assess_results_quality(keywords, summary):
    """Assess the quality of generated keywords and summary"""
    score = 0
    feedback = []
    
    # Check keywords quality
    if len(keywords) >= 8:
        score += 3
        feedback.append("Good number of keywords generated")
    elif len(keywords) >= 5:
        score += 2
        feedback.append("Adequate number of keywords")
    else:
        score += 1
        feedback.append("Limited keywords generated")
    
    # Check summary quality
    if summary and len(summary) > 50:
        score += 3
        feedback.append("Detailed summary provided")
    elif summary and len(summary) > 20:
        score += 2
        feedback.append("Basic summary provided")
    else:
        score += 1
        feedback.append("Minimal summary")
    
    # Check keyword relevance (basic check)
    relevant_keywords = [kw for kw in keywords if len(kw) > 2 and not kw.isdigit()]
    if len(relevant_keywords) >= 6:
        score += 2
        feedback.append("Keywords appear relevant")
    else:
        score += 1
        feedback.append("Some keywords may need refinement")
    
    # Check for common marketing terms
    marketing_terms = ['audience', 'target', 'market', 'customer', 'business', 'product', 'service']
    marketing_matches = sum(1 for kw in keywords if any(term in kw.lower() for term in marketing_terms))
    if marketing_matches >= 2:
        score += 2
        feedback.append("Keywords align with marketing concepts")
    else:
        score += 1
        feedback.append("Consider more marketing-focused keywords")
    
    return {
        'score': min(score, 10),  # Max score of 10
        'feedback': feedback,
        'grade': 'A' if score >= 8 else 'B' if score >= 6 else 'C' if score >= 4 else 'D'
    }

@audiences_bp.route('/audiences/create/step2', methods=['GET', 'POST'])
@login_required
def create_audience_step2():
    """Step 2: Generate phrases based on keywords"""
    if request.method == 'POST':
        data = request.get_json()
        keywords = data.get('keywords', [])
        
        # Get audience_id from session
        audience_id = session.get('audience_creation', {}).get('audience_id')
        
        if audience_id:
            # Update the database with phrases
            from utils.audience_helpers import update_audience_conversation
            phrases = generate_phrases_from_keywords(keywords)
            
            update_data = {
                'phrases': phrases,
                'step2_completed': True,
                'step2_completed_at': datetime.utcnow()
            }
            update_audience_conversation(audience_id, update_data)
            
            return jsonify({'phrases': phrases})
        else:
            # Fallback to session storage
            if 'audience_creation' not in session:
                session['audience_creation'] = {}
            session['audience_creation']['keywords'] = keywords
            
            phrases = generate_phrases_from_keywords(keywords)
            return jsonify({'phrases': phrases})
    
    # Get data from database or session
    audience_id = session.get('audience_creation', {}).get('audience_id')
    
    if audience_id:
        # Get data from database
        from utils.audience_helpers import get_audience_conversation
        audience_data = get_audience_conversation(audience_id)
        
        if audience_data:
            keywords = audience_data.get('keywords', [])
            summary = audience_data.get('summary', '')
            return render_template('create_audience_step2.html', 
                                keywords=keywords, 
                                summary=summary,
                                audience_data=audience_data)
    
    # Fallback to session data
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
