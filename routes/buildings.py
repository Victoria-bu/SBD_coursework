from flask import Blueprint, request, redirect, url_for, flash, render_template_string
from models import db, Building

buildings_bp = Blueprint('buildings', __name__, url_prefix='/buildings')

@buildings_bp.route('/')
def index():
    # Простий відповідь для тестування
    return render_template_string("<h1>Buildings List</h1>")

@buildings_bp.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    building = Building.query.get_or_404(id)
    building.number = request.form['number']
    db.session.commit()
    
    flash('Building updated successfully')
    return redirect(url_for('buildings.index'))