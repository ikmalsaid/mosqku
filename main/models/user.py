from .. import db
from flask_login import UserMixin
from datetime import datetime
import secrets
import string

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user', 'admin', 'staff', 'superadmin'
    recovery_key = db.Column(db.String(16), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosque.id'))
    mosque = db.relationship('Mosque', backref='admins')
    
    def __repr__(self):
        return f'<User {self.email}>'
        
    @staticmethod
    def generate_recovery_key():
        """Generate a 16-character recovery key using uppercase letters and numbers"""
        alphabet = string.ascii_uppercase + string.digits
        while True:
            key = ''.join(secrets.choice(alphabet) for i in range(16))
            # Check if key already exists
            if not User.query.filter_by(recovery_key=key).first():
                return key 