import pytest
from src.database.models import Bike, WorkOrder, Inventory

# To make UI functions use test DB, we patch SessionLocal
@pytest.fixture(autouse=True)
def patch_session(monkeypatch, db_session):
    monkeypatch.setattr("src.database.session.SessionLocal", lambda: db_session)
    monkeypatch.setattr("src.ui.tabs.ticketing.SessionLocal", lambda: db_session)
    monkeypatch.setattr("src.ui.tabs.kpi.SessionLocal", lambda: db_session)
    monkeypatch.setattr("src.scripts.inventory_alert.SessionLocal", lambda: db_session)

def test_create_bike(db_session):
    bike = Bike(brand="TestBrand", model="TestModel")
    db_session.add(bike)
    db_session.commit()
    
    saved_bike = db_session.query(Bike).first()
    assert saved_bike is not None
    assert saved_bike.brand == "TestBrand"
    assert saved_bike.status == "Available"

def test_create_work_order(db_session):
    bike = Bike(brand="TestBrand")
    db_session.add(bike)
    db_session.commit()
    
    wo = WorkOrder(bike_id=bike.id, issue_type="Flat Tire", description="Test desc")
    db_session.add(wo)
    db_session.commit()
    
    saved_wo = db_session.query(WorkOrder).first()
    assert saved_wo is not None
    assert saved_wo.issue_type == "Flat Tire"
    assert saved_wo.status == "Open"
    
def test_inventory_alert_logic(db_session, caplog):
    from src.scripts.inventory_alert import check_inventory
    import logging
    
    inv1 = Inventory(part_name="Part 1", quantity=5, threshold=3)
    inv2 = Inventory(part_name="Part 2", quantity=2, threshold=4) # Below threshold
    db_session.add_all([inv1, inv2])
    db_session.commit()
    
    with caplog.at_level(logging.WARNING):
        check_inventory()
    
    assert "CRITICAL: 1 items are below threshold!" in caplog.text
    assert "Part 2" in caplog.text
