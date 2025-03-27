from .. import db
from datetime import datetime

class Mosque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    jakim_code = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    capacity = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    prayer_times = db.relationship('PrayerTime', backref='mosque', lazy=True)
    announcements = db.relationship('Announcement', backref='mosque', lazy=True)
    
    def __repr__(self):
        return f'<Mosque {self.name}>' 