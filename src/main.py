import schedule
import time
import logging

import utils.config_handler as config_handler
import utils.pullnsave as pullnsave

from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from models.base import Session, init_db
from models.vehicle import Vehicle
from notifications import get_notifier


CONFIG, NOTIFIERS = None, None


def manage_vehicle_state(searched_vehicles: list, muted_run: bool = False) -> None:
    session = Session()

    # Process search results
    for vehicle_data in searched_vehicles:
        vehicle = session.query(Vehicle).filter_by(
            stock_number=vehicle_data['stock_number'],
            year=vehicle_data['model_year'],
            model=vehicle_data['model'],
            location=vehicle_data['location']
        ).first()

        if vehicle:
            logging.info("MANAGE_VEHICLE_STATE: Existing vehicle updated: %s %s - %s", vehicle_data['model_year'], vehicle_data['model'], vehicle_data['stock_number'])
            # Update vehicle in db
            vehicle.last_seen = datetime.now()
        else:
            logging.info("MANAGE_VEHICLE_STATE: New vehicle found: %s %s - %s", vehicle_data['model_year'], vehicle_data['model'], vehicle_data['stock_number'])
            # Add vehicle to DB for tracking
            new_vehicle = Vehicle(
                stock_number=vehicle_data['stock_number'],
                model=vehicle_data['model'],
                color=vehicle_data['color'],
                year=vehicle_data['model_year'],
                location=vehicle_data['location'],
                row=vehicle_data['row'],
                date_recieved=vehicle_data['date_recieved']
            )
            session.add(new_vehicle)
            # Notify of new vehicle
            for notifier in NOTIFIERS:
                notifier.send_vehicle_notification(vehicle_data)
    
    # Remove vehicles not seen in latest search
    cutoff_time = datetime.now() - timedelta(days=1)
    removed_vehicles = session.query(Vehicle).filter(Vehicle.last_seen < cutoff_time).all()
    for vehicle in removed_vehicles:
        logging.info("MANAGE_VEHICLE_STATE: Vehicle removed: %s %s - %s", vehicle.year, vehicle.model, vehicle.stock_number)
        session.delete(vehicle)
    
    try:
        session.commit()
    except IntegrityError:
        logging.error("MANAGE_VEHICLE_STATE: Attempted to write duplicate entry to db, rolling back...")
        session.rollback()
    finally:
        session.close()


def run_search() -> list:
    vehicles = []
    for location in CONFIG['locations']:
        for vehicle in CONFIG['vehicles']:
            make = vehicle['make']
            models = vehicle.get('models', [None])
            for year in vehicle['years']:
                for model in models:
                    search_params = {
                        'make': make,
                        'year': year,
                        'store': location
                    }
                    if model:
                        search_params['model'] = model
                    
                    search_results = pullnsave.search_vehicles(**search_params)
                    vehicles.extend(search_results)
    
    return vehicles


def main():
    logging.info("MAIN: Running scheduled job...")
    search_results = run_search()
    manage_vehicle_state(search_results)
    logging.info("MAIN: Scheduled job complete!")


def run_scheduler():
    main()
    schedule.every().day.at("02:00").do(main)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    # Init Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            # RotatingFileHandler(f"benz-finder.log", maxBytes=5000000, backupCount=1),
            logging.StreamHandler()
        ]
    )
    logging.info("MAIN: Logging started!")

    logging.info("MAIN: Initializing config yaml...")
    CONFIG = config_handler.load_config('benz_finder.yaml')
    NOTIFIERS = [get_notifier(notif_cfg) for notif_cfg in CONFIG['notifications']]

    init_db()

    run_scheduler()
