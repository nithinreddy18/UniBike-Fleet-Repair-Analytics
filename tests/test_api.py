import pytest
from fastapi.testclient import TestClient
from src.api.server import app, get_db
from src.database.models import Bike, WorkOrder, Inventory


@pytest.fixture
def client(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def test_login_success(client):
    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "password"},
    )
    assert response.status_code == 200
    assert "token" in response.json()
    assert response.json()["token"] == "unibike-admin-token-valid"


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/login",
        json={"username": "admin", "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_submit_ticket_and_auto_create_bike(client, db_session):
    payload = {
        "bike_id": 999,
        "issue_type": "Flat Tire",
        "description": "Rear tire punctured near library",
    }
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["bike_id"] == 999
    assert data["status"] == "Out of Order"

    # Verify bike was created
    bike = db_session.query(Bike).filter(Bike.id == 999).first()
    assert bike is not None
    assert bike.status == "Out of Order"

    # Verify work order was created
    wo = db_session.query(WorkOrder).filter(WorkOrder.bike_id == 999).first()
    assert wo is not None
    assert wo.issue_type == "Flat Tire"
    assert wo.status == "Open"


def test_submit_ticket_duplicate_prevented(client):
    payload = {
        "bike_id": 101,
        "issue_type": "Broken Chain",
        "description": "Chain snapped",
    }
    res1 = client.post("/api/tickets", json=payload)
    assert res1.status_code == 200

    # Submitting duplicate active ticket should fail with 400
    res2 = client.post("/api/tickets", json=payload)
    assert res2.status_code == 400
    assert "already an active ticket" in res2.json()["detail"]


def test_get_tickets(client, db_session):
    bike = Bike(id=50, brand="Gazelle")
    db_session.add(bike)
    db_session.commit()

    wo = WorkOrder(bike_id=50, issue_type="Brakes Loose", description="Soft lever")
    db_session.add(wo)
    db_session.commit()

    response = client.get("/api/tickets")
    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) >= 1
    assert any(
        t["bike_id"] == 50 and t["issue_type"] == "Brakes Loose" for t in tickets
    )


def test_update_ticket_status_and_sync_bike(client, db_session):
    bike = Bike(id=77, status="Out of Order")
    db_session.add(bike)
    db_session.commit()

    wo = WorkOrder(bike_id=77, issue_type="Flat Tire", status="Open")
    db_session.add(wo)
    db_session.commit()

    # Update to In Progress -> Bike should transition to In Repair
    res1 = client.patch(f"/api/tickets/{wo.id}", json={"status": "In Progress"})
    assert res1.status_code == 200
    db_session.refresh(bike)
    assert bike.status == "In Repair"

    # Update to Resolved -> Bike should transition to Available
    res2 = client.patch(f"/api/tickets/{wo.id}", json={"status": "Resolved"})
    assert res2.status_code == 200
    db_session.refresh(wo)
    db_session.refresh(bike)
    assert wo.status == "Resolved"
    assert wo.resolved_at is not None
    assert bike.status == "Available"


def test_kpi_endpoint(client, db_session):
    bike = Bike(id=88)
    db_session.add(bike)
    db_session.commit()

    inv = Inventory(part_name="Test Tube", quantity=10, threshold=5)
    db_session.add(inv)
    db_session.commit()

    response = client.get("/api/kpi")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "status_distribution" in data
    assert "inventory" in data
    assert any(item["part_name"] == "Test Tube" for item in data["inventory"])


def test_spa_serving_fallback(client):
    import os
    from src.api.server import FRONTEND_DIST

    # When requesting the frontend root in an environment where dist is built,
    # index.html should be served
    if not os.path.isdir(FRONTEND_DIST) or not os.path.isfile(
        os.path.join(FRONTEND_DIST, "index.html")
    ):
        pytest.skip(
            "frontend/dist is not built in this test environment, skipping SPA test"
        )

    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
