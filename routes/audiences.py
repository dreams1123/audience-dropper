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

@audiences_bp.route('/audiences/')
@audiences_bp.route('/audiences')
@login_required
def audiences():
    # Get both traditional audiences and conversation-based audiences
    user_audiences = get_user_audiences(current_user.id)
    
    # Get conversation-based audiences
    from utils.audience_helpers import get_user_conversation_audiences
    conversation_audiences = get_user_conversation_audiences(current_user.id)
    
    # Combine and format audiences for display
    all_audiences = []
    
    # Add conversation-based audiences
    for conv_audience in conversation_audiences:
        all_audiences.append({
            '_id': conv_audience['_id'],
            'name': f"AI Generated - {conv_audience.get('created_at', '').strftime('%b %d, %Y') if conv_audience.get('created_at') else 'Unknown'}",
            'description': conv_audience.get('summary', 'AI-generated audience based on conversation')[:100] + '...' if conv_audience.get('summary') else 'AI-generated audience',
            'category': 'AI Generated',
            'status': conv_audience.get('status', 'unknown'),
            'created_at': conv_audience.get('created_at'),
            'keywords_count': len(conv_audience.get('keywords', [])),
            'type': 'conversation'
        })
    
    # Add traditional audiences
    for audience in user_audiences:
        audience['type'] = 'traditional'
        all_audiences.append(audience)
    
    # Sort by creation date (newest first)
    all_audiences.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template('audiences.html', audiences=all_audiences)


@audiences_bp.route('/audiences/create', methods=['GET', 'POST'])
@audiences_bp.route('/audiences/create/<audience_id>', methods=['GET', 'POST'])
@login_required
def create_audience(audience_id=None):
    """Step 1: Chatbot interaction to gather information and generate keywords"""
    if request.method == 'POST':
        data = request.get_json()
        user_input = data.get('user_input', '')
        conversation_history = data.get('conversation_history', [])
        # Use audience_id from URL parameter or from request data
        request_audience_id = data.get('audience_id')
        if audience_id:
            request_audience_id = audience_id
        
        # Save conversation to database
        if request_audience_id:
            from utils.audience_helpers import update_audience_conversation
            update_data = {
                'conversation_history': conversation_history,
                'updated_at': datetime.utcnow()
            }
            update_audience_conversation(request_audience_id, update_data)
        
        # Check if we have enough conversation history to process with LLM
        if len(conversation_history) >= 10:  # After all 5 questions are answered (5 questions * 2 = 10 messages)
            # Use LLM to process the conversation
            from utils.llm_server import get_llm_summary_and_keywords
            
            try:
                result = get_llm_summary_and_keywords(conversation_history)
                llm_response = f"Based on our conversation, I've analyzed your responses and generated keywords to help you find your target audience. Here's what I found: {result.get('summary', '')}"
                keywords = result.get('keywords', [])
                print(f"Step 1 Debug - Generated {len(keywords)} keywords from LLM: {keywords}")
                
                # Store the processed data in the database for persistent access
                audience_data = {
                    'user_id': current_user.id,
                    'conversation_history': conversation_history,
                    'summary': result.get('summary', ''),
                    'keywords': keywords,
                    'status': 'completed',
                    'completed_at': datetime.utcnow()
                }
                
                # Save to database
                from utils.audience_helpers import save_audience_conversation, update_audience_conversation
                if request_audience_id:
                    update_audience_conversation(request_audience_id, audience_data)
                    final_audience_id = request_audience_id
                else:
                    final_audience_id = save_audience_conversation(audience_data)
                
                # Store audience_id in session for future steps
                if 'audience_creation' not in session:
                    session['audience_creation'] = {}
                session['audience_creation']['audience_id'] = final_audience_id
                session['audience_creation']['keywords'] = keywords  # Also store keywords as backup
                session['audience_creation']['summary'] = result.get('summary', '')
                # Debug logging (can be removed in production)
                print(f"Step 1 Debug - Stored audience_id in session: {final_audience_id}")
                print(f"Step 1 Debug - Session data: {session.get('audience_creation', {})}")
                
                print(f"Step 1 Debug - Keywords count: {len(keywords)}")
                print(f"Step 1 Debug - Summary length: {len(result.get('summary', ''))}")
                
                return jsonify({
                    'response': llm_response,
                    'keywords': keywords,
                    'summary': result.get('summary', ''),
                    'audience_id': final_audience_id
                })
                
            except Exception as e:
                print(f"Error using LLM: {e}")
                llm_response = simulate_llm_chatbot(user_input, conversation_history)
                keywords = extract_keywords_from_conversation(conversation_history)
                print(f"Step 1 Debug - Generated {len(keywords)} keywords from fallback: {keywords}")
                
                # Save fallback data to database and session
                audience_data = {
                    'user_id': current_user.id,
                    'conversation_history': conversation_history,
                    'summary': 'Generated using fallback method',
                    'keywords': keywords,
                    'status': 'completed_fallback',
                    'completed_at': datetime.utcnow()
                }
                
                from utils.audience_helpers import save_audience_conversation, update_audience_conversation
                if request_audience_id:
                    update_audience_conversation(request_audience_id, audience_data)
                    final_audience_id = request_audience_id
                else:
                    final_audience_id = save_audience_conversation(audience_data)
                
                # Store in session as backup
                if 'audience_creation' not in session:
                    session['audience_creation'] = {}
                session['audience_creation']['audience_id'] = final_audience_id
                session['audience_creation']['keywords'] = keywords
                session['audience_creation']['summary'] = 'Generated using fallback method'
                
                return jsonify({
                    'response': llm_response,
                    'keywords': keywords,
                    'audience_id': final_audience_id,
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
    
    # Handle GET request - load existing audience if ID provided
    if audience_id:
        from utils.audience_helpers import get_audience_conversation
        audience_data = get_audience_conversation(audience_id)
        if audience_data and audience_data.get('user_id') == current_user.id:
            return render_template('create_audience.html', 
                                 audience_id=audience_id,
                                 audience_data=audience_data)
        else:
            flash('Audience not found or access denied', 'error')
            return redirect(url_for('audiences.audiences'))
    
    return render_template('create_audience.html', audience_id=audience_id)

@audiences_bp.route('/audiences/save-conversation', methods=['POST'])
@login_required
def save_conversation():
    """Save conversation to database"""
    data = request.get_json()
    conversation_history = data.get('conversation_history', [])
    audience_id = data.get('audience_id')
    
    if audience_id:
        # Update existing conversation
        from utils.audience_helpers import update_audience_conversation
        update_data = {
            'conversation_history': conversation_history,
            'updated_at': datetime.utcnow()
        }
        success = update_audience_conversation(audience_id, update_data)
        return jsonify({'success': success, 'audience_id': audience_id})
    else:
        # Create new conversation
        audience_data = {
            'user_id': current_user.id,
            'conversation_history': conversation_history,
            'status': 'in_progress',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        from utils.audience_helpers import save_audience_conversation
        new_audience_id = save_audience_conversation(audience_data)
        return jsonify({'success': True, 'audience_id': new_audience_id})

@audiences_bp.route('/audiences/get-saved-conversation', methods=['GET'])
@login_required
def get_saved_conversation():
    """Get saved conversation from database"""
    # Get the most recent in-progress conversation for this user
    from utils.audience_helpers import get_user_latest_conversation
    conversation_data = get_user_latest_conversation(current_user.id)
    
    if conversation_data:
        return jsonify({
            'conversation_history': conversation_data.get('conversation_history', []),
            'audience_id': str(conversation_data['_id'])
        })
    else:
        return jsonify({
            'conversation_history': [],
            'audience_id': None
        })

@audiences_bp.route('/audiences/get-conversation-results', methods=['POST'])
@login_required
def get_conversation_results():
    """Get results for a completed conversation"""
    data = request.get_json()
    audience_id = data.get('audience_id')
    
    if audience_id:
        from utils.audience_helpers import get_audience_conversation
        conversation_data = get_audience_conversation(audience_id)
        
        if conversation_data and conversation_data.get('keywords'):
            return jsonify({
                'keywords': conversation_data.get('keywords', []),
                'summary': conversation_data.get('summary', ''),
                'audience_id': audience_id
            })
    
    return jsonify({'error': 'No results found'})

@audiences_bp.route('/audiences/<audience_id>/details')
@login_required
def audience_details(audience_id):
    """View detailed information about an audience including conversation history"""
    from utils.audience_helpers import get_audience_conversation
    conversation_data = get_audience_conversation(audience_id)
    
    if not conversation_data:
        flash('Audience not found', 'error')
        return redirect(url_for('audiences.audiences'))
    
    # Check if user owns this audience
    if conversation_data.get('user_id') != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('audiences.audiences'))
    
    return render_template('audience_details.html', 
                         audience=conversation_data)






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

@audiences_bp.route('/audiences/search/status/<audience_id>')
@login_required
def get_search_status(audience_id):
    """Get current search status for an audience"""
    from utils.search_engine import search_engine
    status = search_engine.get_search_status()
    
    # Add audience-specific information
    if audience_id:
        from models.search_results import get_search_results_by_audience, get_search_stats
        results = get_search_results_by_audience(audience_id, current_user.id)
        stats = get_search_stats(audience_id, current_user.id)
        
        status['results_count'] = len(results)
        status['stats'] = stats
    
    return jsonify(status)

@audiences_bp.route('/audiences/search/start', methods=['POST'])
@login_required
def start_background_search():
    """Start a background search process"""
    data = request.get_json()
    keywords = data.get('keywords', [])
    phrases = data.get('phrases', [])
    audience_id = data.get('audience_id')
    
    if not audience_id:
        return jsonify({'error': 'No audience ID provided'}), 400
    
    # Start search in background
    from utils.search_engine import search_engine
    from models.search_results import save_search_results
    
    try:
        # Start the search process
        search_results = search_engine.start_search(keywords, phrases, current_user.id, audience_id)
        
        # Save results to database
        if search_results:
            save_search_results(current_user.id, audience_id, search_results)
        
        return jsonify({
            'status': 'success',
            'message': 'Search completed successfully',
            'results_count': len(search_results)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Search failed: {str(e)}'
        }), 500

@audiences_bp.route('/audiences/search/test-page')
@login_required
def test_search_page():
    """Serve the test search page"""
    return render_template('test_search.html')

@audiences_bp.route('/audiences/search/test', methods=['POST'])
@login_required
def test_search_engine():
    """Test the search engine without database operations"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', ['test'])
        phrases = data.get('phrases', ['test phrase'])
        
        print(f"Test Search - Keywords: {keywords}, Phrases: {phrases}")
        
        # Test search engine only
        from utils.search_engine import search_engine
        search_results = search_engine.start_search(keywords, phrases, 'test_user', 'test_audience')
        
        return jsonify({
            'status': 'success',
            'message': 'Test search completed',
            'results_count': len(search_results),
            'search_results': search_results
        })
        
    except Exception as e:
        print(f"Test Search Error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Test search failed: {str(e)}'
        }), 500
