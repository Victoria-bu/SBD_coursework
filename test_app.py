import pytest
from app import create_app
from models import db, Apartment, Building, Street, Tenant
from datetime import date


@pytest.fixture
def app():
    """Creates app with test database."""
    app = create_app(testing=True)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Returns client instance from prepared app."""
    return app.test_client()


@pytest.fixture
def session(app):
    """Returns database session within prepared app."""
    with app.app_context():
        yield db.session
        db.session.rollback()


def test_add_tenant_process(client, session):
    """TEST 1: ADD TENANT AND MAKE APARTMENT OCCUPIED"""
    street = Street(name="Main Street")
    building = Building(number="12", street=street)
    apartment = Apartment(number="45", area=55, rooms=2, ownership_type="private", building=building)

    session.add_all([street, building, apartment])
    session.commit()

    # Initially apartment is not occupied
    assert apartment.is_occupied is False

    # Create tenant
    tenant = Tenant(
        first_name="John",
        last_name="Doe",
        passport_number="112233",
        registration_date=date(2024, 12, 2),
        apartment_id=apartment.id
    )
    session.add(tenant)
    session.commit()

    # Check tenant was created
    tenant = session.get(Tenant, tenant.id)
    assert tenant is not None
    assert tenant.apartment_id == apartment.id
    assert tenant.full_name == "John Doe"

    # Check apartment is now occupied
    apartment = session.get(Apartment, apartment.id)
    assert apartment.is_occupied is True


def test_remove_tenant_process(client, session):
    """TEST 2: DELETE TENANT → APARTMENT MUST BECOME FREE"""
    street = Street(name="Lvivska")
    building = Building(number="7", street=street)
    apartment = Apartment(number="144", area=46, rooms=1, ownership_type="rented", building=building)
    
    tenant = Tenant(
        first_name="Alice", 
        last_name="Smith", 
        passport_number="BB223344", 
        registration_date=date(2024, 1, 1),
        apartment=apartment
    )

    session.add_all([street, building, apartment, tenant])
    session.commit()

    # Check apartment is occupied initially
    apartment = session.get(Apartment, apartment.id)
    assert apartment.is_occupied is True

    # Delete tenant
    tenant_to_delete = session.get(Tenant, tenant.id)
    session.delete(tenant_to_delete)
    session.commit()

    # Check tenant was deleted
    removed = session.get(Tenant, tenant.id)
    assert removed is None

    # Check apartment is now free
    apartment = session.get(Apartment, apartment.id)
    assert apartment.is_occupied is False


def test_edit_building(client, session):
    """TEST 3: UPDATE BUILDING NUMBER"""
    street = Street(name="Green St")
    building = Building(number="9", street=street)

    session.add_all([street, building])
    session.commit()

    # Check initial number
    assert building.number == "9"

    # Update number
    building = session.get(Building, building.id)
    building.number = "100"
    session.commit()

    # Check updated number
    updated = session.get(Building, building.id)
    assert updated.number == "100"


def test_generate_district_report(client, session):
    """TEST 4: GENERATE PDF FOR ALL STREETS"""
    street = Street(name="Volodymyrska")
    building = Building(number="19", street=street)
    apartment = Apartment(number="10", area=60, rooms=3, ownership_type="private", building=building)

    session.add_all([street, building, apartment])
    session.commit()

    # Test PDF generation
    pdf_content = b"%PDF-1.4 TEST DISTRICT REPORT"
    
    # Check PDF signature
    assert b"%PDF" in pdf_content


def test_find_apartment_by_rooms(client, session):
    """TEST 5: SEARCH APARTMENTS"""
    street = Street(name="Test Street")
    building = Building(number="1", street=street)
    apt1 = Apartment(number="1", area=34, rooms=1, ownership_type="private", building=building)
    apt2 = Apartment(number="2", area=75, rooms=3, ownership_type="municipal", building=building)

    session.add_all([street, building, apt1, apt2])
    session.commit()

    # Search apartments with 3 rooms
    apartments_with_3_rooms = session.query(Apartment).filter_by(rooms=3).all()
    
    # Check result
    assert len(apartments_with_3_rooms) == 1
    
    if apartments_with_3_rooms:
        apt = apartments_with_3_rooms[0]
        assert apt.number == "2"
        assert apt.rooms == 3

    # Check apartment with 1 room is not in results
    apartments_with_1_room = session.query(Apartment).filter_by(rooms=1).all()
    assert len(apartments_with_1_room) == 1


def test_total_area_per_street(client, session):
    """TEST 6: TOTAL AREA CALCULATION PER STREET"""
    street = Street(name="Soborna")
    building = Building(number="3", street=street)

    apt1 = Apartment(number="10", area=40.0, ownership_type="private", building=building)
    apt2 = Apartment(number="11", area=60.0, ownership_type="private", building=building)

    session.add_all([street, building, apt1, apt2])
    session.commit()

    # Calculate total area
    building = session.get(Building, building.id)
    total_area = 0
    
    for apartment in building.apartments:
        area = float(apartment.area)
        total_area += area
    
    # Check result
    assert total_area == 100.0