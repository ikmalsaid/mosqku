from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
import sqlite3

# Initialize SQLAlchemy
db = SQLAlchemy()
DB_NAME = "mosque.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    db.init_app(app)

    from .models.user import User
    from .models.mosque import Mosque
    from .models.prayer_time import PrayerTime
    from .models.announcement import Announcement

    # Import blueprints
    from .controllers.auth import auth
    from .controllers.mosque import mosque
    from .controllers.admin import admin
    from .controllers.inventory import inventory
    
    # Register blueprints - Note that mosque blueprint is registered first to handle root URL
    app.register_blueprint(mosque)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(inventory)

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Create database
    create_database(app)
    
    return app

def create_database(app):
    if not path.exists('instance/' + DB_NAME):
        with app.app_context():
            db.create_all()
            
            # Create default superadmin account
            from werkzeug.security import generate_password_hash
            from .models.user import User
            
            default_admin = User.query.filter_by(email='admin@mosqku.com').first()
            if not default_admin:
                default_admin = User(
                    email='admin@mosqku.com',
                    name='Super Admin',
                    password=generate_password_hash('Admin@123', method='scrypt'),
                    role='superadmin'
                )
                db.session.add(default_admin)
                db.session.commit()
                print('Created default superadmin account!')
            
            print('Created Database!') 