import time
import schedule
import pandas as pd
from sqlalchemy.orm import Session
from src.database.session import SessionLocal
from src.core.logger import logger

def check_inventory():
    logger.info("Running daily inventory check...")
    db: Session = SessionLocal()
    
    try:
        # Read inventory directly into a pandas DataFrame using SQLAlchemy session bind
        query = "SELECT part_name, quantity, threshold FROM inventory"
        df = pd.read_sql(query, db.bind)
        
        # Filter for low inventory
        low_inventory_df = df[df['quantity'] < df['threshold']]
        
        if not low_inventory_df.empty:
            logger.warning(f"CRITICAL: {len(low_inventory_df)} items are below threshold!")
            for _, row in low_inventory_df.iterrows():
                logger.warning(f" - {row['part_name']}: Only {row['quantity']} left (Threshold: {row['threshold']})")
            # In a real app, send an email or Slack alert here.
        else:
            logger.info("All inventory levels are sufficient.")
            
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error checking inventory: {e}")
    finally:
        db.close()

def main():
    logger.info("Starting inventory alert automation script...")
    
    # Run once immediately
    check_inventory()
    
    # Schedule to run every day (using seconds for demo purposes)
    schedule.every(24).hours.do(check_inventory)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Inventory alert script stopped.")

if __name__ == "__main__":
    main()
