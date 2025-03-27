from datetime import datetime, timedelta, time
import random
from werkzeug.security import generate_password_hash
from .user import User
from .mosque import Mosque
from .prayer_time import PrayerTime
from .inventory import Inventory
from .finance import Finance
from .announcement import Announcement
from .. import db

def generate_mosque_data(mosque_info):
    """Generate data for a specific mosque"""
    mosque = Mosque(
        name=mosque_info['name'],
        address=mosque_info['address'],
        city=mosque_info['city'],
        state=mosque_info['state'],
        country=mosque_info['country'],
        jakim_code=mosque_info['jakim_code'],
        phone=mosque_info['phone'],
        email=mosque_info['email'],
        capacity=mosque_info['capacity']
    )
    db.session.add(mosque)
    db.session.commit()
    print(f"Created mosque: {mosque.name}")

    # Create mosque admins and staff
    for user_data in mosque_info['users']:
        user = User(
            email=user_data["email"],
            name=user_data["name"],
            password=generate_password_hash("Demo@123", method='scrypt'),
            role=user_data["role"],
            mosque_id=mosque.id,
            recovery_key=User.generate_recovery_key()
        )
        db.session.add(user)
    db.session.commit()
    print(f"Created users for {mosque.name}")

    # Generate prayer times with mosque-specific variations
    prayer_names = ['Imsak', 'Subuh', 'Syuruk', 'Zuhur', 'Asar', 'Maghrib', 'Isyak']
    base_times = {
        'Imsak': time(5, 30),
        'Subuh': time(5, 45),
        'Syuruk': time(7, 0),
        'Zuhur': time(13, 15),
        'Asar': time(16, 30),
        'Maghrib': time(19, 20),
        'Isyak': time(20, 35)
    }
    
    # Add mosque-specific offset (each mosque slightly different timing)
    mosque_offset = random.randint(-10, 10)
    
    for i in range(7):
        date = datetime.now().date() + timedelta(days=i)
        for prayer_name in prayer_names:
            base_time = base_times[prayer_name]
            # Add mosque-specific variations to prayer times
            varied_time = (datetime.combine(date, base_time) + 
                         timedelta(minutes=mosque_offset + random.randint(-2, 2))).time()
            
            prayer_time = PrayerTime(
                prayer_name=prayer_name,
                time=varied_time,
                date=date,
                mosque_id=mosque.id
            )
            db.session.add(prayer_time)
    db.session.commit()
    print(f"Generated prayer times for {mosque.name}")

    # Generate inventory with mosque-specific quantities
    inventory_items = [
        ('Prayer Mats', 'Prayer Items', random.randint(300, 700)),
        ('Quran Copies', 'Prayer Items', random.randint(100, 300)),
        ('Cleaning Supplies', 'Cleaning', random.randint(30, 70)),
        ('Vacuum Cleaners', 'Cleaning', random.randint(3, 8)),
        ('Chairs', 'Office', random.randint(20, 50)),
        ('Tables', 'Office', random.randint(5, 15)),
        ('Water Dispensers', 'Kitchen', random.randint(5, 12)),
        ('Light Bulbs', 'Maintenance', random.randint(50, 150))
    ]
    
    for i, (item_name, category, qty) in enumerate(inventory_items, 1):
        inventory = Inventory(
            mosque_id=mosque.id,
            number=f'{mosque_info["code"]}-INV-{i:03d}',
            item_name=item_name,
            item_category=category,
            item_description=f'{item_name} for {mosque.name}',
            quantity=qty,
            remarks=f'Inventory item for {mosque.name}'
        )
        db.session.add(inventory)
    db.session.commit()
    print(f"Generated inventory for {mosque.name}")

    # Generate finance records with mosque-specific amounts
    finance_scale = random.uniform(0.8, 1.5)  # Each mosque has different financial scale
    finance_records = [
        ('Monthly Donation', 'Donation', 5000.00 * finance_scale),
        ('Electricity Bill', 'Utility', -800.00 * finance_scale),
        ('Water Bill', 'Utility', -200.00 * finance_scale),
        ('Building Maintenance', 'Maintenance', -1500.00 * finance_scale),
        ('Staff Salary', 'Salary', -2000.00 * finance_scale),
        ('Ramadan Event', 'Event', -1000.00 * finance_scale),
        ('Friday Collection', 'Donation', 3000.00 * finance_scale)
    ]
    
    for i, (name, category, amount) in enumerate(finance_records, 1):
        date = datetime.now() - timedelta(days=random.randint(0, 30))
        finance = Finance(
            mosque_id=mosque.id,
            number=f'{mosque_info["code"]}-FIN-{i:03d}',
            transaction_name=name,
            finance_category=category,
            description=f'{name} for {mosque.name}',
            amount=round(amount, 2),
            date_added=date,
            remarks=f'Finance record for {mosque.name}'
        )
        db.session.add(finance)
    db.session.commit()
    print(f"Generated finance records for {mosque.name}")

    # Generate mosque-specific announcements
    announcements = [
        {
            'title': f'Weekly Activities at {mosque.name}',
            'content': f'Join our weekly activities at {mosque.name}. We offer Quran classes, Islamic lectures, and community events.',
            'is_urgent': False,
            'days_duration': 30
        },
        {
            'title': f'Urgent: {mosque.name} Maintenance Day',
            'content': f'We need volunteers for mosque maintenance this weekend at {mosque.name}. Your help is greatly appreciated.',
            'is_urgent': True,
            'days_duration': 7
        },
        {
            'title': mosque_info['special_announcement']['title'],
            'content': mosque_info['special_announcement']['content'],
            'is_urgent': mosque_info['special_announcement']['is_urgent'],
            'days_duration': mosque_info['special_announcement']['days_duration']
        }
    ]
    
    current_date = datetime.now().date()
    for i, announcement_data in enumerate(announcements):
        start_date = current_date + timedelta(days=i)
        end_date = start_date + timedelta(days=announcement_data['days_duration'])
        
        announcement = Announcement(
            mosque_id=mosque.id,
            title=announcement_data['title'],
            content=announcement_data['content'],
            start_date=start_date,
            end_date=end_date,
            start_time=time(8, 0),
            end_time=time(22, 0),
            is_urgent=announcement_data['is_urgent']
        )
        db.session.add(announcement)
    db.session.commit()
    print(f"Generated announcements for {mosque.name}")

def generate_demo_data():
    """Generate demo data for multiple mosques"""
    print("Generating demo data for multiple mosques...")
    
    # Define multiple mosques with their specific data
    mosques_info = [
        {
            'name': "Masjid Al-Salam",
            'address': "123 Peace Street",
            'city': "Shah Alam",
            'state': "Selangor",
            'country': "Malaysia",
            'jakim_code': "SGR01",
            'phone': "+60123456789",
            'email': "info@masjidalsalam.com",
            'capacity': 1000,
            'code': 'MAS',
            'users': [
                {"email": "admin.salam@demo.com", "name": "Salam Admin", "role": "admin"},
                {"email": "staff1.salam@demo.com", "name": "Salam Staff 1", "role": "admin"},
                {"email": "staff2.salam@demo.com", "name": "Salam Staff 2", "role": "admin"}
            ],
            'special_announcement': {
                'title': 'Quran Competition Registration Open',
                'content': 'Register now for our annual Quran recitation competition. Open for all age groups.',
                'is_urgent': True,
                'days_duration': 14
            }
        },
        {
            'name': "Masjid An-Nur",
            'address': "456 Light Avenue",
            'city': "Petaling Jaya",
            'state': "Selangor",
            'country': "Malaysia",
            'jakim_code': "SGR01",
            'phone': "+60123456790",
            'email': "info@masjidannur.com",
            'capacity': 1500,
            'code': 'MAN',
            'users': [
                {"email": "admin.nur@demo.com", "name": "Nur Admin", "role": "admin"},
                {"email": "staff1.nur@demo.com", "name": "Nur Staff 1", "role": "admin"},
                {"email": "staff2.nur@demo.com", "name": "Nur Staff 2", "role": "admin"}
            ],
            'special_announcement': {
                'title': 'Youth Islamic Camp',
                'content': 'Join our weekend Islamic camp for youth aged 15-25. Activities include Islamic lectures, team building, and outdoor activities.',
                'is_urgent': False,
                'days_duration': 21
            }
        },
        {
            'name': "Masjid Al-Hidayah",
            'address': "789 Guidance Road",
            'city': "Subang Jaya",
            'state': "Selangor",
            'country': "Malaysia",
            'jakim_code': "SGR01",
            'phone': "+60123456791",
            'email': "info@masjidhidayah.com",
            'capacity': 800,
            'code': 'MAH',
            'users': [
                {"email": "admin.hidayah@demo.com", "name": "Hidayah Admin", "role": "admin"},
                {"email": "staff1.hidayah@demo.com", "name": "Hidayah Staff 1", "role": "admin"},
                {"email": "staff2.hidayah@demo.com", "name": "Hidayah Staff 2", "role": "admin"}
            ],
            'special_announcement': {
                'title': 'Community Iftar Program',
                'content': 'Join us for our weekly community iftar program every Saturday. All are welcome to join.',
                'is_urgent': True,
                'days_duration': 10
            }
        }
    ]
    
    # Generate data for each mosque
    for mosque_info in mosques_info:
        generate_mosque_data(mosque_info)
    
    print("Demo data generation completed successfully!") 