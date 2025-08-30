from flask import Flask
from flask_login import LoginManager
from config import Config
from models.user import load_user

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.signin'
    login_manager.user_loader(load_user)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.audiences import audiences_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(audiences_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)
