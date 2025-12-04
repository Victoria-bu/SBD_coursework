from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Street, Building, Apartment

address_bp = Blueprint('addresses', __name__)


@address_bp.route('/address/add', methods=['GET', 'POST'])
@login_required
def add_address():
    if current_user.role != 'admin':
        flash("Access denied.")
        return redirect(url_for('tenants.tenants_list'))

    if request.method == 'POST':
        try:
            street_name = request.form['street_name']
            building_number = request.form['building_number']
            apartment_number = request.form['apartment_number']
            area = request.form['area']
            rooms = request.form.get('rooms')
            ownership_type = request.form['ownership_type']

            street = Street.query.filter_by(name=street_name).first()
            if not street:
                street = Street(name=street_name)
                db.session.add(street)
                db.session.commit()

            building = Building.query.filter_by(
                street_id=street.id, number=building_number
            ).first()
            if not building:
                building = Building(street_id=street.id, number=building_number)
                db.session.add(building)
                db.session.commit()

            apartment = Apartment(
                building_id=building.id,
                number=apartment_number,
                area=area,
                rooms=rooms,
                ownership_type=ownership_type
            )
            db.session.add(apartment)
            db.session.commit()

            flash("Address added successfully!")
            return redirect(url_for('tenants.add_tenant'))

        except Exception as e:
            flash(f"Error: {e}")

    return render_template("add_address.html")


@address_bp.route('/address/delete/<int:apartment_id>', methods=['POST'])
@login_required
def delete_address(apartment_id):
    if current_user.role != 'admin':
        flash("Access denied.")
        return redirect(url_for('tenants.tenants_list'))

    try:
        # Get apartment by ID
        apartment = Apartment.query.get_or_404(apartment_id)

        # Optional: delete building/street if they no longer have related objects
        building = apartment.building
        street = building.street

        # Delete apartment
        db.session.delete(apartment)
        db.session.commit()
        flash("Apartment/address deleted successfully!")

        # Check if building has remaining apartments
        if not building.apartments:
            db.session.delete(building)
            db.session.commit()
        
        # Check if street has remaining buildings
        if not street.buildings:
            db.session.delete(street)
            db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f"Error while deleting: {e}")

    return redirect(url_for('addresses.add_address'))


@address_bp.route('/address/edit/<int:apartment_id>', methods=['GET', 'POST'])
@login_required
def edit_address(apartment_id):
    if current_user.role != 'admin':
        flash("Access denied.")
        return redirect(url_for('tenants.tenants_list'))

    apartment = Apartment.query.get_or_404(apartment_id)
    building = apartment.building
    street = building.street

    if request.method == 'POST':
        try:
            # Update street
            street.name = request.form['street_name']
            
            # Update building
            building.number = request.form['building_number']
            
            # Update apartment
            apartment.number = request.form['apartment_number']
            apartment.area = request.form['area']
            apartment.rooms = request.form.get('rooms')
            apartment.ownership_type = request.form['ownership_type']

            db.session.commit()
            flash("Address updated!")
            return redirect(url_for('tenants.add_tenant'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}")

    return render_template("add_address.html", apartment=apartment, building=building, street=street)
