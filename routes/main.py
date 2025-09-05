from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.user import get_user_by_id

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/profile')
@login_required
def profile():
    user_data = get_user_by_id(current_user.id)
    return render_template('profile.html', user=user_data)

@main_bp.route('/account')
@login_required
def account():
    user_data = get_user_by_id(current_user.id)
    return render_template('account.html', user=user_data)

@main_bp.route('/support')
def support():
    return render_template('support.html')

@main_bp.route('/faq')
def faq():
    return render_template('faq.html')

@main_bp.route('/instructions')
def instructions():
    return render_template('instructions.html')

@main_bp.route('/map')
@login_required
def map():
    return render_template('map.html')