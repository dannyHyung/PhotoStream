from flask import Flask
import os

def create_app(config_class=None):
    # Create and configure the app
    app = Flask(__name__)
    
    # Load config
    if config_class is None:
        from config import Config
        config_class = Config
    
    app.config.from_object(config_class)
    
    if app.config.get('TEMP_UPLOAD_DIR') and not os.path.isdir(app.config['TEMP_UPLOAD_DIR']):
        os.makedirs(app.config['TEMP_UPLOAD_DIR'])
    
    # Ensure Supabase environment variables are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        app.logger.warning("Supabase environment variables (SUPABASE_URL and SUPABASE_KEY) must be set")
    
    # Register blueprints
    from app.routes import auth, main, photos, follows, tags, likes
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(photos.bp)
    app.register_blueprint(follows.bp)
    app.register_blueprint(tags.bp)
    app.register_blueprint(likes.bp)
    
    return app