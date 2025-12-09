from flask import Blueprint, render_template_string, request
from models import Apartment

apartments_bp = Blueprint('apartments', __name__, url_prefix='/apartments')

@apartments_bp.route('/search')
def search():
    rooms = request.args.get('rooms', type=int)
    
    if rooms:
        apartments = Apartment.query.filter_by(rooms=rooms).all()
    else:
        apartments = Apartment.query.all()
    
    # Простий шаблон для тестування
    html = "<h1>Apartments</h1>"
    for apt in apartments:
        html += f"<p>Apartment {apt.number} - {apt.rooms} rooms</p>"
    
    return render_template_string(html)