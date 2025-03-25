from .. import db
from datetime import datetime

class Finance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosque.id'), nullable=True)
    number = db.Column(db.String(50), nullable=False)
    transaction_name = db.Column(db.String(100), nullable=False)
    finance_category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    remarks = db.Column(db.Text)
    
    # Relationship with Mosque model (optional)
    mosque = db.relationship('Mosque', backref=db.backref('finance_items', lazy=True)) 