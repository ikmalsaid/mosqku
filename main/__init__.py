from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from colorpaws import ColorPaws
import os

logger = ColorPaws(__name__)
db = SQLAlchemy()

def get_db_name(demo_mode=False):
    """Return the appropriate database name based on demo mode"""
    return "mosqku_demo.db" if demo_mode else "mosqku_client.db"

def start_server(demo_mode=False, custom_error_handler=True,
                 launch=True, host='0.0.0.0', port=7860):
    """
    Starts the Mosqku web service.

    Parameters:
    - demo_mode: Starts in demo mode with pre-defined database.
    - custom_error_handler: Handles web errors with custom responses.
    - launch: Launch the web server automatically.
    - host: Specify host address.
    - port: Specify port number.
    """
    logger.info(f"Starting Mosqku ({'Demo' if demo_mode else 'Client'} Mode)...")
    logger.info(f'In loving memory of my beloved cat and kitten, Niddy and Nimi!')

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('MOSQKU_SECRET_KEY', 'mosqku-key-2025')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{get_db_name(demo_mode)}'
    app.config['DEMO_MODE'] = demo_mode

    if custom_error_handler:
        app.config['DEBUG'] = False
        app.config['PROPAGATE_EXCEPTIONS'] = False
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    
    db.init_app(app)

    from .models.user import User
    from .models.mosque import Mosque
    from .models.prayer_time import PrayerTime
    from .models.announcement import Announcement

    # Import blueprints
    from .controllers.auth import auth as auth_blueprint
    from .controllers.admin import admin as admin_blueprint
    from .controllers.mosque import mosque as mosque_blueprint
    from .controllers.inventory import inventory as inventory_blueprint
    from .controllers.finance import finance as finance_blueprint
    
    # Register blueprints - Note that mosque blueprint is registered first to handle root URL
    app.register_blueprint(mosque_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(inventory_blueprint)
    app.register_blueprint(finance_blueprint)

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    if custom_error_handler:
        @app.errorhandler(404)
        def page_not_found(e):
            return render_template('errors/error.html',
                                error_code=404,
                                error_title="Page Not Found",
                                error_description="The page you're looking for doesn't exist.",
                                user=current_user,
                                hide_breadcrumbs=True), 404

        @app.errorhandler(403)
        def forbidden(e):
            return render_template('errors/error.html',
                                error_code=403,
                                error_title="Access Forbidden",
                                error_description="You don't have permission to access this resource.",
                                user=current_user,
                                hide_breadcrumbs=True), 403

        @app.errorhandler(500)
        def internal_server_error(e):
            return render_template('errors/error.html',
                                error_code=500,
                                error_title="Internal Server Error",
                                error_description="Something went wrong on our end. Please try again later.",
                                user=current_user,
                                hide_breadcrumbs=True), 500

        @app.errorhandler(401)
        def unauthorized(e):
            return render_template('errors/error.html',
                                error_code=401,
                                error_title="Unauthorized Access",
                                error_description="Please log in to access this page.",
                                user=current_user,
                                hide_breadcrumbs=True), 401

        # Handle all other exceptions
        @app.errorhandler(Exception)
        def handle_exception(e):
            # Log the error here if you want
            return render_template('errors/error.html',
                                error_code=500,
                                error_title="Internal Server Error",
                                error_description="Something went wrong on our end. Please try again later.",
                                user=current_user,
                                hide_breadcrumbs=True), 500

    # Create database and optionally add demo data
    create_database(app, demo_mode)
    
    if launch:
        app.run(host=host, port=port)
    else:
        return app

def create_database(app, demo_mode=False):
    db_name = get_db_name(demo_mode)
    if not os.path.exists('instance/' + db_name):
        with app.app_context():
            db.create_all()
            
            # Create default superadmin account
            from werkzeug.security import generate_password_hash
            from .models.user import User
            
            default_admin = User.query.filter_by(email='admin@mosqku.com').first()
            if not default_admin:
                recovery_key = User.generate_recovery_key()
                default_admin = User(
                    email='admin@mosqku.com',
                    name='superadmin',
                    password=generate_password_hash('Admin@123', method='scrypt'),
                    role='superadmin',
                    recovery_key=recovery_key
                )
                db.session.add(default_admin)
                db.session.commit()
                logger.info(f'Created superadmin account: {default_admin.email}')
                logger.info(f'Default superadmin recovery key: {recovery_key}')
            
            # Generate demo data if requested
            if demo_mode:
                from .models.demo import generate_demo_data
                generate_demo_data(logger=logger)
            
            logger.info(f'Created database: {os.path.join(app.instance_path, db_name)}')