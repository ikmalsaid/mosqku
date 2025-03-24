from .. import db
from datetime import datetime

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    mosque_id = db.Column(db.Integer, db.ForeignKey('mosque.id'), nullable=False)
    
    def __repr__(self):
        return f'<Announcement {self.title}>'

    def __init__(self, id=None, mosque_id=None, title=None, content=None, start_date=None, end_date=None, start_time=None, end_time=None):
        self.id = id
        self.mosque_id = mosque_id
        self.title = title
        self.content = content
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time

    @staticmethod
    def create_table():
        db.execute('''
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mosque_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                FOREIGN KEY (mosque_id) REFERENCES mosques (id)
            )
        ''')
        db.commit()

    @staticmethod
    def get_all(mosque_id):
        announcements = db.execute(
            'SELECT * FROM announcements WHERE mosque_id = ? ORDER BY start_date DESC, start_time DESC',
            (mosque_id,)
        ).fetchall()
        return [Announcement(
            id=row[0],
            mosque_id=row[1],
            title=row[2],
            content=row[3],
            start_date=datetime.strptime(row[4], '%Y-%m-%d').date(),
            end_date=datetime.strptime(row[5], '%Y-%m-%d').date(),
            start_time=datetime.strptime(row[6], '%H:%M').time(),
            end_time=datetime.strptime(row[7], '%H:%M').time()
        ) for row in announcements]

    def save(self):
        if self.id is None:
            db.execute(
                '''INSERT INTO announcements (mosque_id, title, content, start_date, end_date, start_time, end_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (self.mosque_id, self.title, self.content, self.start_date, self.end_date, self.start_time, self.end_time)
            )
        else:
            db.execute(
                '''UPDATE announcements
                SET title = ?, content = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?
                WHERE id = ? AND mosque_id = ?''',
                (self.title, self.content, self.start_date, self.end_date, self.start_time, self.end_time, self.id, self.mosque_id)
            )
        db.commit()

    def delete(self):
        if self.id:
            db.execute('DELETE FROM announcements WHERE id = ? AND mosque_id = ?', (self.id, self.mosque_id))
            db.commit()

    @property
    def is_active(self):
        now = datetime.now()
        current_date = now.date()
        current_time = now.time()
        
        if current_date < self.start_date:
            return False
        if current_date > self.end_date:
            return False
        if current_date == self.start_date and current_time < self.start_time:
            return False
        if current_date == self.end_date and current_time > self.end_time:
            return False
        return True 