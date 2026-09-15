from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
from . import db

class Account(db.Model):
    __tablename__ = 'user'  # Keep original table name for compatibility
    id = db.Column(db.Integer, primary_key=True)
    login_name = db.Column(db.String(80), unique=True, nullable=False)
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    secret_hash = db.Column(db.String(255), nullable=False)
    has_admin_rights = db.Column(db.Boolean, default=False)
    registration_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    documents = db.relationship('Document', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def update_secret(self, secret):
        self.secret_hash = generate_password_hash(secret)
    
    def verify_secret(self, secret):
        return check_password_hash(self.secret_hash, secret)
    
    def __repr__(self):
        return f'<Account {self.login_name}>'

class Document(db.Model):
    __tablename__ = 'note'  # Keep original table name for compatibility
    id = db.Column(db.String(36), primary_key=True, default=lambda: str("".join(random.choices("abcdef01234567890", k=25))))
    heading = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    modified_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Document {self.heading}>'
