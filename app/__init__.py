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
    
    # Ensure the static directory exists
    if not os.path.isdir(app.config['IMAGES_DIR']):
        os.makedirs(app.config['IMAGES_DIR'])
    
    # Register blueprints
    from app.routes import auth, main, photos, follows, tags
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(photos.bp)
    app.register_blueprint(follows.bp)
    app.register_blueprint(tags.bp)
    
    return app