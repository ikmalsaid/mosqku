from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.mosque import Mosque
from ..models.prayer_time import PrayerTime
from ..models.announcement import Announcement
from .. import db
from datetime import datetime, date

mosque = Blueprint('mosque', __name__)

@mosque.route('/')
@mosque.route('/home')
def home():
    mosques = Mosque.query.all()
    return render_template("mosque/home.html", user=current_user, mosques=mosques)

@mosque.route('/register-mosque', methods=['GET', 'POST'])
@login_required
def register_mosque():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country')
        phone = request.form.get('phone')
        email = request.form.get('email')
        capacity = request.form.get('capacity')
        
        try:
            mosque = Mosque(
                name=name,
                address=address,
                city=city,
                state=state,
                country=country,
                phone=phone,
                email=email,
                capacity=capacity
            )
            db.session.add(mosque)
            db.session.commit()
            
            # Update the current user to be an admin of this mosque
            current_user.role = 'admin'
            current_user.mosque_id = mosque.id
            db.session.commit()
            
            flash('Mosque registered successfully! You are now the administrator.', category='success')
            return redirect(url_for('mosque.dashboard'))
        except Exception as e:
            flash('Error registering mosque.', category='error')
            
    return render_template("mosque/register_mosque.html", user=current_user)

@mosque.route('/dashboard')
@login_required
def dashboard():
    if current_user.mosque_id:
        mosque = Mosque.query.get(current_user.mosque_id)
        prayer_times = PrayerTime.query.filter_by(
            mosque_id=current_user.mosque_id,
            date=date.today()
        ).all()
        announcements = Announcement.query.filter_by(
            mosque_id=current_user.mosque_id,
            is_active=True
        ).all()
        return render_template(
            "mosque/dashboard.html",
            user=current_user,
            mosque=mosque,
            prayer_times=prayer_times,
            announcements=announcements
        )
    return render_template("mosque/dashboard.html", user=current_user)

@mosque.route('/mosque/<int:id>')
def mosque_details(id):
    mosque = Mosque.query.get_or_404(id)
    prayer_times = PrayerTime.query.filter_by(
        mosque_id=id,
        date=date.today()
    ).all()
    announcements = Announcement.query.filter_by(
        mosque_id=id,
        is_active=True
    ).all()
    return render_template(
        "mosque/details.html",
        user=current_user,
        mosque=mosque,
        prayer_times=prayer_times,
        announcements=announcements
    )

@mosque.route('/prayer-times/<int:mosque_id>', methods=['GET', 'POST'])
@login_required
def prayer_times(mosque_id):
    if current_user.mosque_id != mosque_id and current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    if request.method == 'POST':
        prayer_name = request.form.get('prayer_name')
        time = request.form.get('time')
        date_str = request.form.get('date')
        
        try:
            prayer_time = PrayerTime(
                prayer_name=prayer_name,
                time=datetime.strptime(time, '%H:%M').time(),
                date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                mosque_id=mosque_id
            )
            db.session.add(prayer_time)
            db.session.commit()
            flash('Prayer time added successfully!', category='success')
        except Exception as e:
            flash('Error adding prayer time.', category='error')
            
    prayer_times = PrayerTime.query.filter_by(mosque_id=mosque_id).all()
    return render_template(
        "mosque/prayer_times.html",
        user=current_user,
        prayer_times=prayer_times,
        mosque_id=mosque_id
    )

@mosque.route('/prayer-times/delete/<int:id>', methods=['POST'])
@login_required
def delete_prayer_time(id):
    prayer_time = PrayerTime.query.get_or_404(id)
    
    # Check if user has permission to delete this prayer time
    if current_user.mosque_id != prayer_time.mosque_id and current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
    
    try:
        mosque_id = prayer_time.mosque_id  # Store mosque_id before deletion
        db.session.delete(prayer_time)
        db.session.commit()
        flash('Prayer time deleted successfully!', category='success')
    except Exception as e:
        flash('Error deleting prayer time.', category='error')
    
    return redirect(url_for('mosque.prayer_times', mosque_id=mosque_id))

@mosque.route('/announcements', methods=['GET', 'POST'])
@login_required
def announcements():
    if not current_user.mosque_id:
        flash('Please register a mosque first.', 'warning')
        return redirect(url_for('mosque.register_mosque'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()

        if start_date > end_date or (start_date == end_date and start_time >= end_time):
            flash('End date/time must be after start date/time.', 'error')
            return redirect(url_for('mosque.announcements'))

        announcement = Announcement(
            mosque_id=current_user.mosque_id,
            title=title,
            content=content,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement added successfully.', 'success')
        return redirect(url_for('mosque.announcements'))

    announcements = Announcement.query.filter_by(mosque_id=current_user.mosque_id).all()
    return render_template('mosque/announcements.html', announcements=announcements, user=current_user)

@mosque.route('/announcements/delete/<int:id>', methods=['POST'])
@login_required
def delete_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    
    # Check if user has permission to delete this announcement
    if current_user.mosque_id != announcement.mosque_id and current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
    
    try:
        mosque_id = announcement.mosque_id  # Store mosque_id before deletion
        db.session.delete(announcement)
        db.session.commit()
        flash('Announcement deleted successfully!', category='success')
    except Exception as e:
        flash('Error deleting announcement.', category='error')
    
    return redirect(url_for('mosque.announcements', mosque_id=mosque_id)) 