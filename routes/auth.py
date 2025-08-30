from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from datetime import datetime
from models.user import get_user_by_email, create_user
from pymongo import MongoClient
from config import Config

# MongoDB connection
client = MongoClient(Config.MONGODB_URI)
db = client[Config.DATABASE_NAME]

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user_data = get_user_by_email(email)
        if user_data and check_password_hash(user_data['password'], password):
            from models.user import User
            user = User(user_data)
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('signin.html')

@auth_bp.route('/request-access', methods=['GET', 'POST'])
def request_access():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        company = request.form['company']
        reason = request.form['reason']
        
        # Check if user already exists
        existing_user = get_user_by_email(email)
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
            return redirect(url_for('auth.signin'))
    
    return render_template('request_access.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
