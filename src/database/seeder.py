import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.models import Bike, WorkOrder, Inventory
from src.database.session import engine, SessionLocal
from src.core.logger import logger

def seed_db():
    logger.info("Starting database seeder...")
    db: Session = SessionLocal()
    
    # Check if we already have bikes
    if db.query(Bike).first():
        logger.info("Database already seeded.")
        db.close()
        return

    # 1. Seed Bikes
    bikes_data = [
        {"brand": "Gazelle", "model": "Orange C7", "status": "Available"},
        {"brand": "VanMoof", "model": "S3", "status": "Out of Order"},
        {"brand": "Batavus", "model": "Dinsdag", "status": "Available"},
        {"brand": "Cortina", "model": "U4", "status": "Available"},
        {"brand": "Swapfiets", "model": "Deluxe", "status": "In Repair"},
    ]
    
    bikes = []
    for data in bikes_data:
        bike = Bike(**data)
        db.add(bike)
        bikes.append(bike)
    
    db.commit()
    logger.info(f"Seeded {len(bikes)} bikes.")

    # 2. Seed Work Orders
    issues = ["Flat Tire", "Broken Chain", "Brakes Loose", "Gears Skipping", "Saddle Stolen"]
    for bike in bikes:
        # Give some bikes work orders
        if bike.status == "Available":
            # Maybe some old resolved tickets
            if random.random() > 0.5:
                wo = WorkOrder(
                    bike_id=bike.id,
                    issue_type=random.choice(issues),
                    description="Old resolved issue",
                    status="Resolved",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(5, 30)),
                    resolved_at=datetime.utcnow() - timedelta(days=random.randint(1, 4))
                )
                db.add(wo)
        else:
            # Active tickets
            wo = WorkOrder(
                bike_id=bike.id,
                issue_type=random.choice(issues),
                description="Needs fixing ASAP",
                status="Open" if bike.status == "Out of Order" else "In Progress",
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 3))
            )
            db.add(wo)
    
    db.commit()
    logger.info("Seeded work orders.")

    # 3. Seed Inventory (One below threshold for alert script demo)
    inventory_items = [
        {"part_name": "Inner Tube 28\"", "quantity": 15, "threshold": 5},
        {"part_name": "Brake Pad Set", "quantity": 8, "threshold": 4},
        {"part_name": "Chain KMC Z1", "quantity": 2, "threshold": 3},  # Below threshold
        {"part_name": "Derailleur Cable", "quantity": 10, "threshold": 5},
    ]

    for item in inventory_items:
        inv = Inventory(**item)
        db.add(inv)
        
    db.commit()
    logger.info("Seeded inventory.")
    db.close()
    logger.info("Database seeding complete.")

if __name__ == "__main__":
    seed_db()
