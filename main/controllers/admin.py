from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.user import User
from ..models.mosque import Mosque
from ..models.announcement import Announcement
from ..models.prayer_time import PrayerTime
from .. import db
from werkzeug.security import generate_password_hash
from datetime import datetime

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
    
    mosques = Mosque.query.all()
    admins = User.query.filter_by(role='admin').all()
        
    # Get mosque names for all admins in one query to avoid N+1 problem
    mosque_dict = {m.id: m.name for m in Mosque.query.all()}
        
    return render_template(
        "admin/dashboard.html",
        user=current_user,
        mosques=mosques,
        admins=admins,
        mosque_dict=mosque_dict
    )

@admin.route('/add_mosque', methods=['GET', 'POST'])
@login_required
def add_mosque():
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
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
            flash('Mosque added successfully!', category='success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash('Error adding mosque.', category='error')
            
    return render_template("admin/add_mosque.html", user=current_user)

@admin.route('/add_admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        mosque_id = request.form.get('mosque_id')
        
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
                    mosque_id=mosque_id,
                    recovery_key=recovery_key
                )
                db.session.add(new_admin)
                db.session.commit()
                flash(f'Admin added successfully! Recovery key is: {recovery_key} - Please save this in a secure place.', category='success')
                return redirect(url_for('admin.dashboard'))
            except Exception as e:
                flash('Error adding admin.', category='error')
                
    mosques = Mosque.query.all()
    return render_template("admin/add_admin.html", user=current_user, mosques=mosques)

@admin.route('/mosque/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_mosque(id):
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    mosque = Mosque.query.get_or_404(id)
    
    if request.method == 'POST':
        mosque.name = request.form.get('name')
        mosque.address = request.form.get('address')
        mosque.city = request.form.get('city')
        mosque.state = request.form.get('state')
        mosque.country = request.form.get('country')
        mosque.phone = request.form.get('phone')
        mosque.email = request.form.get('email')
        mosque.capacity = request.form.get('capacity')
        mosque.jakim_code = request.form.get('jakim_code')
        
        try:
            db.session.commit()
            flash('Mosque updated successfully!', category='success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash('Error updating mosque.', category='error')
            
    return render_template("admin/edit_mosque.html", user=current_user, mosque=mosque)

@admin.route('/mosque/announcements/<int:mosque_id>', methods=['GET', 'POST'])
@login_required
def mosque_announcements(mosque_id):
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    mosque = Mosque.query.get_or_404(mosque_id)
    
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
            return redirect(url_for('admin.mosque_announcements', mosque_id=mosque_id))

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
        return redirect(url_for('admin.mosque_announcements', mosque_id=mosque_id))

    announcements = Announcement.query.filter_by(mosque_id=mosque_id).all()
    return render_template('mosque/announcements.html', 
                         announcements=announcements, 
                         user=current_user, 
                         mosque=mosque, 
                         now=datetime.now())

@admin.route('/mosque/announcements/delete/<int:id>', methods=['POST'])
@login_required
def delete_mosque_announcement(id):
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    announcement = Announcement.query.get_or_404(id)
    mosque_id = announcement.mosque_id
    
    try:
        db.session.delete(announcement)
        db.session.commit()
        flash('Announcement deleted successfully!', category='success')
    except Exception as e:
        flash('Error deleting announcement.', category='error')
    
    return redirect(url_for('admin.mosque_announcements', mosque_id=mosque_id))

@admin.route('/reset_password/<int:admin_id>', methods=['GET', 'POST'])
@login_required
def reset_admin_password(admin_id):
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    admin = User.query.get_or_404(admin_id)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('All fields are required.', category='error')
        elif new_password != confirm_password:
            flash('Passwords don\'t match.', category='error')
        elif len(new_password) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            admin.password = generate_password_hash(new_password, method='scrypt')
            db.session.commit()
            flash('Password reset successfully!', category='success')
            return redirect(url_for('admin.dashboard'))
            
    return render_template("admin/reset_password.html", user=current_user, admin=admin)

@admin.route('/delete_admin/<int:admin_id>', methods=['POST'])
@login_required
def delete_admin(admin_id):
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    admin = User.query.get_or_404(admin_id)
    if admin.role == 'superadmin':
        flash('Cannot delete a superadmin account.', category='error')
        return redirect(url_for('admin.dashboard'))
        
    try:
        db.session.delete(admin)
        db.session.commit()
        flash('Administrator account deleted successfully!', category='success')
    except Exception as e:
        flash('Error deleting administrator account.', category='error')
        
    return redirect(url_for('admin.dashboard'))

@admin.route('/reassign_mosque/<int:admin_id>', methods=['GET', 'POST'])
@login_required
def reassign_mosque(admin_id):
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    admin = User.query.get_or_404(admin_id)
    mosques = Mosque.query.all()
    
    if request.method == 'POST':
        mosque_id = request.form.get('mosque_id')
        if mosque_id:
            admin.mosque_id = mosque_id
            db.session.commit()
            flash('Administrator reassigned successfully!', category='success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Please select a mosque.', category='error')
            
    return render_template("admin/reassign_mosque.html", user=current_user, admin=admin, mosques=mosques)

@admin.route('/delete_mosque/<int:mosque_id>', methods=['POST'])
@login_required
def delete_mosque(mosque_id):
    if current_user.role != 'superadmin':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('mosque.dashboard'))
        
    mosque = Mosque.query.get_or_404(mosque_id)
    
    try:
        # Get all admins of this mosque
        admins = User.query.filter_by(mosque_id=mosque_id).all()
        
        # Remove mosque_id from all admins
        for admin in admins:
            admin.mosque_id = None
            
        # Delete all prayer times
        PrayerTime.query.filter_by(mosque_id=mosque_id).delete()
        
        # Delete all announcements
        Announcement.query.filter_by(mosque_id=mosque_id).delete()
        
        # Finally delete the mosque
        db.session.delete(mosque)
        db.session.commit()
        flash('Mosque and all related data deleted successfully!', category='success')
    except Exception as e:
        flash('Error deleting mosque.', category='error')
        
    return redirect(url_for('admin.dashboard')) 