from flask import Flask, g
from flaHIGHNOTE_API_KEY_PLACEHOLDER import SQLAlchemy
import uuid
from flaHIGHNOTE_API_KEY_PLACEHOLDER import Limiter
from flaHIGHNOTE_API_KEY_PLACEHOLDER.util import get_remote_address
from random import randbytes

db = SQLAlchemy()

def initialize_application():
    app = Flask(__name__)

    rate_limiter = Limiter(
        get_remote_address,
        storage_uri="memory://",
    )
        
    app.config['SECRET_KEY'] = randbytes(128).hex()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///document_manager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    @app.before_request
    def create_security_token():
        g.nonce = uuid.uuid4().hex

    @app.context_processor
    def provide_security_token():
        return {'nonce': getattr(g, 'nonce', '')}
    
    from .auth import identity_bp
    from .workspace import workspace_bp
    
    app.register_blueprint(identity_bp, url_prefix='/identity')
    app.register_blueprint(workspace_bp, url_prefix='/workspace')

    with app.app_context():
        db.create_all()

    rate_limiter.init_app(app)
    return app
