from .. import db
from datetime import datetime

# Prayer order dictionary for sorting
PRAYER_ORDER = {
    'Imsak': 1,
    'Subuh': 2,
    'Syuruk': 3,
    'Zuhur': 4,
    'Asar': 5,
    'Maghrib': 6,
    'Isyak': 7
}

class PrayerTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prayer_name = db.Column(db.String(20), nullable=False)  # Fajr, Dhuhr, Asr, Maghrib, Isha
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosque.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    @property
    def order(self):
        """Get the order of this prayer for sorting"""
        return PRAYER_ORDER.get(self.prayer_name, 999)  # Unknown prayers go to the end
    
    def __repr__(self):
        return f'<PrayerTime {self.prayer_name} at {self.time}>' 