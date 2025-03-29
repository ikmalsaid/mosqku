from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from ..models.mosque import Mosque
from ..models.prayer_time import PrayerTime
from ..models.announcement import Announcement
from ..models.user import User
from .. import db
from datetime import datetime, date
from werkzeug.security import generate_password_hash

mosque = Blueprint('mosque', __name__)

@mosque.route('/')
def root():
    return redirect(url_for('mosque.home'))

@mosque.route('/home')
def home():
    mosques = Mosque.query.all()
    return render_template("home.html", user=current_user, mosques=mosques)

@mosque.route('/mosque_info/<int:id>')
def mosque_info(id):
    mosque = Mosque.query.get_or_404(id)
    prayer_times = PrayerTime.query.filter_by(
        mosque_id=id,
        date=date.today()
    ).all()
    
    # Get active announcements
    all_announcements = Announcement.query.filter_by(mosque_id=id).all()
    active_announcements = [a for a in all_announcements if a.is_active]
    
    return render_template(
        "mosque/mosque_info.html",
        user=current_user,
        mosque=mosque,
        prayer_times=prayer_times,
        active_announcements=active_announcements,
        now=datetime.now()
    )

@mosque.route('/register_mosque', methods=['GET', 'POST'])
@login_required
def register_mosque():
    # Prevent users who already have a mosque from registering another one
    if current_user.mosque_id:
        flash('You are already an administrator of a mosque.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    # Prevent superadmins from registering mosques (they should use add_mosque)
    if current_user.role == 'superadmin':
        flash('Superadmins should use the admin dashboard to add mosques.', category='error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country')
        phone = request.form.get('phone')
        email = request.form.get('email')
        capacity = request.form.get('capacity')
        jakim_code = request.form.get('jakim_code')
        
        try:
            mosque = Mosque(
                name=name,
                address=address,
                city=city,
                state=state,
                country=country,
                phone=phone,
                email=email,
                capacity=capacity,
                jakim_code=jakim_code
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
    # Redirect superadmins to admin dashboard
    if current_user.role == 'superadmin':
        return redirect(url_for('admin.dashboard'))
        
    if current_user.mosque_id:
        mosque = Mosque.query.get(current_user.mosque_id)
        prayer_times = PrayerTime.query.filter_by(
            mosque_id=current_user.mosque_id,
            date=date.today()
        ).all()
        
        # Get all announcements and filter active ones using the property
        all_announcements = Announcement.query.filter_by(mosque_id=current_user.mosque_id).all()
        active_announcements = [a for a in all_announcements if a.is_active]
        
        # Get assigned admins for this mosque
        assigned_admins = User.query.filter_by(mosque_id=current_user.mosque_id, role='admin').all()
        
        # Get staff members for this mosque
        staff_members = User.query.filter_by(mosque_id=current_user.mosque_id, role='staff').all()
        
        return render_template(
            "mosque/dashboard.html",
            user=current_user,
            mosque=mosque,
            prayer_times=prayer_times,
            active_announcements=active_announcements,
            assigned_admins=assigned_admins,
            staff_members=staff_members,
            now=datetime.now()
        )
    return render_template("mosque/dashboard.html", user=current_user)

@mosque.route('/prayer_times/<int:mosque_id>', methods=['GET', 'POST'])
@login_required
def prayer_times(mosque_id):
    if current_user.mosque_id != mosque_id and current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    mosque = Mosque.query.get_or_404(mosque_id)
        
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
        mosque=mosque
    )

@mosque.route('/prayer_times/delete/<int:id>', methods=['POST'])
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

@mosque.route('/prayer_times/<int:mosque_id>/import', methods=['POST'])
@login_required
def import_prayer_times(mosque_id):
    if current_user.mosque_id != mosque_id and current_user.role != 'superadmin':
        return jsonify({'success': False, 'message': 'Unauthorized access.'}), 403
        
    mosque = Mosque.query.get_or_404(mosque_id)
    
    try:
        data = request.get_json()
        prayer_times = data.get('prayer_times', [])
        
        # Begin transaction
        duplicates = 0
        added = 0
        
        for prayer_data in prayer_times:
            # Check if prayer time already exists
            existing = PrayerTime.query.filter_by(
                mosque_id=mosque_id,
                prayer_name=prayer_data['prayer_name'],
                date=datetime.strptime(prayer_data['date'], '%Y-%m-%d').date()
            ).first()
            
            if not existing:
                prayer_time = PrayerTime(
                    prayer_name=prayer_data['prayer_name'],
                    time=datetime.strptime(prayer_data['time'], '%H:%M').time(),
                    date=datetime.strptime(prayer_data['date'], '%Y-%m-%d').date(),
                    mosque_id=mosque_id
                )
                db.session.add(prayer_time)
                added += 1
            else:
                duplicates += 1
        
        # Always commit if there are any additions
        if added > 0:
            db.session.commit()
            
        # Return appropriate response
        total = added + duplicates
        if added == 0 and duplicates > 0:
            return jsonify({
                'success': True,
                'status': 'no_changes',
                'message': f'All {duplicates} prayer times already exist for these dates.',
                'added': added,
                'duplicates': duplicates,
                'total': total
            })
        else:
            return jsonify({
                'success': True,
                'status': 'imported',
                'message': f'Successfully imported {added} prayer times. {duplicates} duplicates were skipped.',
                'added': added,
                'duplicates': duplicates,
                'total': total
            })
        
    except Exception as e:
        db.session.rollback()
        print('Error importing prayer times:', str(e))
        return jsonify({
            'success': False,
            'status': 'error',
            'message': 'Failed to import prayer times. Please try again.'
        }), 500

@mosque.route('/mosque_announcements', methods=['GET', 'POST'])
@login_required
def announcements():
    # If user is not a superadmin and has no mosque, redirect to register
    if not current_user.role == 'superadmin' and not current_user.mosque_id:
        flash('Please register a mosque first.', 'warning')
        return redirect(url_for('mosque.register_mosque'))

    # For superadmin, get mosque_id from query parameter
    if current_user.role == 'superadmin':
        mosque_id = request.args.get('mosque_id', type=int)
        if not mosque_id:
            flash('Please specify a mosque.', 'warning')
            return redirect(url_for('admin.dashboard'))
    else:
        mosque_id = current_user.mosque_id

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
        is_urgent = request.form.get('is_urgent') == 'on'

        if start_date > end_date or (start_date == end_date and start_time >= end_time):
            flash('End date/time must be after start date/time.', 'error')
            return redirect(url_for('mosque.announcements', mosque_id=mosque_id))

        announcement = Announcement(
            mosque_id=mosque_id,
            title=title,
            content=content,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            is_urgent=is_urgent
        )
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement added successfully.', 'success')
        if current_user.role == 'superadmin':
            return redirect(url_for('admin.mosque_announcements', mosque_id=mosque_id))
        return redirect(url_for('mosque.announcements'))

    announcements = Announcement.query.filter_by(mosque_id=mosque_id).all()
    mosque = Mosque.query.get_or_404(mosque_id)
    return render_template('mosque/announcements.html', 
                         announcements=announcements, 
                         user=current_user, 
                         mosque=mosque,
                         now=datetime.now())

@mosque.route('/mosque_announcements/delete/<int:id>', methods=['POST'])
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

@mosque.route('/mosque_announcements/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    
    # Check if user has permission to edit this announcement
    if current_user.mosque_id != announcement.mosque_id and current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
        end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
        is_urgent = request.form.get('is_urgent') == 'on'

        if start_date > end_date or (start_date == end_date and start_time >= end_time):
            flash('End date/time must be after start date/time.', 'error')
            return redirect(url_for('mosque.edit_announcement', id=id))

        try:
            announcement.title = title
            announcement.content = content
            announcement.start_date = start_date
            announcement.end_date = end_date
            announcement.start_time = start_time
            announcement.end_time = end_time
            announcement.is_urgent = is_urgent
            db.session.commit()
            flash('Announcement updated successfully.', 'success')
            if current_user.role == 'superadmin':
                return redirect(url_for('admin.mosque_announcements', mosque_id=announcement.mosque_id))
            return redirect(url_for('mosque.announcements'))
        except Exception as e:
            flash('Error updating announcement.', 'error')
            return redirect(url_for('mosque.edit_announcement', id=id))

    return render_template('mosque/edit_announcement.html', 
                         user=current_user, 
                         announcement=announcement, 
                         mosque=Mosque.query.get(announcement.mosque_id),
                         now=datetime.now())

@mosque.route('/add_another_admin', methods=['GET', 'POST'])
@login_required
def add_another_admin():
    # Only allow mosque admins to access this route
    if current_user.role != 'admin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    mosque = Mosque.query.get_or_404(current_user.mosque_id)
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        else:
            try:
                recovery_key = User.generate_recovery_key()
                new_admin = User(
                    email=email,
                    name=name,
                    password=generate_password_hash(password, method='scrypt'),
                    role='admin',
                    mosque_id=current_user.mosque_id,
                    recovery_key=recovery_key
                )
                db.session.add(new_admin)
                db.session.commit()
                flash(f'{name} added successfully!', category='success')
                return redirect(url_for('mosque.dashboard'))
            except Exception as e:
                flash('Error adding admin.', category='error')
                
    return render_template("mosque/add_another_admin.html", user=current_user, mosque=mosque)

@mosque.route('/add_another_staff', methods=['GET', 'POST'])
@login_required
def add_another_staff():
    # Only allow mosque admins to access this route
    if current_user.role != 'admin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    mosque = Mosque.query.get_or_404(current_user.mosque_id)
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        else:
            try:
                recovery_key = User.generate_recovery_key()
                new_staff = User(
                    email=email,
                    name=name,
                    password=generate_password_hash(password, method='scrypt'),
                    role='staff',
                    mosque_id=current_user.mosque_id,
                    recovery_key=recovery_key
                )
                db.session.add(new_staff)
                db.session.commit()
                flash(f'{name} added successfully!', category='success')
                return redirect(url_for('mosque.dashboard'))
            except Exception as e:
                flash('Error adding staff.', category='error')
                
    return render_template("mosque/add_another_staff.html", user=current_user, mosque=mosque) 