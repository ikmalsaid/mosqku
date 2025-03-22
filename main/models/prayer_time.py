from .. import db
from datetime import datetime

class PrayerTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prayer_name = db.Column(db.String(20), nullable=False)  # Fajr, Dhuhr, Asr, Maghrib, Isha
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosque.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PrayerTime {self.prayer_name} at {self.time}>' 