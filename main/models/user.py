from .. import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user', 'admin', 'superadmin'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosque.id'))
    mosque = db.relationship('Mosque', backref='admins')
    
    def __repr__(self):
        return f'<User {self.email}>' 