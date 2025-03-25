from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.inventory import Inventory
from ..models.mosque import Mosque
from .. import db
from datetime import datetime

inventory = Blueprint('inventory', __name__)

@inventory.route('/inventory')
@login_required
def inventory_list():
    if current_user.role == 'superadmin':
        mosque_id = request.args.get('mosque_id', type=int)
        if not mosque_id:
            flash('Please select a mosque.', category='error')
            return redirect(url_for('admin.dashboard'))
    else:
        mosque_id = current_user.mosque_id
        
    mosque = Mosque.query.get_or_404(mosque_id)
    items = Inventory.query.filter_by(mosque_id=mosque_id).order_by(Inventory.date_added.desc()).all()
    
    return render_template('inventory/list.html', 
                         items=items, 
                         mosque=mosque,
                         user=current_user)

@inventory.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if current_user.role == 'superadmin':
        mosque_id = request.args.get('mosque_id', type=int)
        if not mosque_id:
            flash('Please select a mosque.', category='error')
            return redirect(url_for('admin.dashboard'))
    else:
        mosque_id = current_user.mosque_id
        
    mosque = Mosque.query.get_or_404(mosque_id)
    
    if request.method == 'POST':
        number = request.form.get('number')
        item_name = request.form.get('item_name')
        item_category = request.form.get('item_category')
        item_description = request.form.get('item_description')
        quantity = request.form.get('quantity', type=int)
        remarks = request.form.get('remarks')
        
        if not number or not item_name or not item_category or quantity is None:
            flash('Required fields cannot be empty.', category='error')
        else:
            try:
                new_item = Inventory(
                    mosque_id=mosque_id,
                    number=number,
                    item_name=item_name,
                    item_category=item_category,
                    item_description=item_description,
                    quantity=quantity,
                    remarks=remarks
                )
                db.session.add(new_item)
                db.session.commit()
                flash('Item added successfully!', category='success')
                return redirect(url_for('inventory.inventory_list', mosque_id=mosque_id))
            except Exception as e:
                flash('Error adding item.', category='error')
                
    return render_template('inventory/add.html', mosque=mosque, user=current_user)

@inventory.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = Inventory.query.get_or_404(id)
    
    if current_user.role == 'superadmin':
        mosque_id = item.mosque_id
    else:
        if item.mosque_id != current_user.mosque_id:
            flash('Unauthorized access.', category='error')
            return redirect(url_for('mosque.dashboard'))
        mosque_id = current_user.mosque_id
        
    mosque = Mosque.query.get_or_404(mosque_id)
    
    if request.method == 'POST':
        item.number = request.form.get('number')
        item.item_name = request.form.get('item_name')
        item.item_category = request.form.get('item_category')
        item.item_description = request.form.get('item_description')
        item.quantity = request.form.get('quantity', type=int)
        item.remarks = request.form.get('remarks')
        
        if not item.number or not item.item_name or not item.item_category or item.quantity is None:
            flash('Required fields cannot be empty.', category='error')
        else:
            try:
                db.session.commit()
                flash('Item updated successfully!', category='success')
                return redirect(url_for('inventory.inventory_list', mosque_id=mosque_id))
            except Exception as e:
                flash('Error updating item.', category='error')
                
    return render_template('inventory/edit.html', item=item, mosque=mosque, user=current_user)

@inventory.route('/inventory/delete/<int:id>', methods=['POST'])
@login_required
def delete_item(id):
    item = Inventory.query.get_or_404(id)
    
    if current_user.role == 'superadmin':
        mosque_id = item.mosque_id
    else:
        if item.mosque_id != current_user.mosque_id:
            flash('Unauthorized access.', category='error')
            return redirect(url_for('mosque.dashboard'))
        mosque_id = current_user.mosque_id
        
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully!', category='success')
    except Exception as e:
        flash('Error deleting item.', category='error')
        
    return redirect(url_for('inventory.inventory_list', mosque_id=mosque_id)) 