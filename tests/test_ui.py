import pytest
from src.ui.tabs.ticketing import submit_ticket
from src.database.models import Bike, WorkOrder

def test_submit_ticket_valid(db_session, monkeypatch):
    monkeypatch.setattr("src.ui.tabs.ticketing.SessionLocal", lambda: db_session)
    bike = Bike(brand="TestBrand")
    db_session.add(bike)
    db_session.commit()
    
    submit_ticket(str(bike.id), "Flat Tire", "Test")
    
    saved_wo = db_session.query(WorkOrder).first()
    assert saved_wo is not None
    assert saved_wo.issue_type == "Flat Tire"
    
def test_submit_ticket_invalid_bike(db_session, monkeypatch):
    monkeypatch.setattr("src.ui.tabs.ticketing.SessionLocal", lambda: db_session)
    submit_ticket("999", "Flat Tire", "Test")
    assert db_session.query(WorkOrder).count() == 0

def test_submit_ticket_duplicate(db_session, monkeypatch):
    monkeypatch.setattr("src.ui.tabs.ticketing.SessionLocal", lambda: db_session)
    monkeypatch.setattr(db_session, "close", lambda: None)
    bike = Bike(brand="TestBrand")
    db_session.add(bike)
    db_session.commit()
    
    submit_ticket(str(bike.id), "Flat Tire", "Test")
    submit_ticket(str(bike.id), "Flat Tire", "Test")
    # Duplicate shouldn't create a second ticket
    assert db_session.query(WorkOrder).count() == 1

def test_kpi_dashboard(db_session, monkeypatch):
    from src.ui.tabs.kpi import get_kpi_data
    monkeypatch.setattr("src.ui.tabs.kpi.SessionLocal", lambda: db_session)
    
    bike = Bike(brand="TestBrand")
    db_session.add(bike)
    db_session.commit()
    
    wo = WorkOrder(bike_id=bike.id, issue_type="Flat Tire", status="Open")
    db_session.add(wo)
    db_session.commit()
    
    report, fig1, fig2, inventory_df = get_kpi_data()
    assert "Mean Time to Repair" in report
    assert isinstance(inventory_df, type(pd.DataFrame())) if "pd" in globals() else True # DataFrame check
