import schedule
import time
import logging
import argparse
import os

import utils.config_handler as config_handler
import utils.pullnsave as pullnsave

from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from models.base import get_session, init_db
from models.vehicle import Vehicle
from notifications import get_notifier


CONFIG, NOTIFIERS = None, None


def manage_vehicle_state(searched_vehicles: list, muted_run: bool = False) -> None:
    session = get_session()

    # Process search results
    new_vehicles = []
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

            # Add vehicle to notification queue
            new_vehicles.append(vehicle_data)
    
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
    
    # Notify of newly found vehicles
    if len(new_vehicles) > 0 and not muted_run:
        logging.info("MANAGE_VEHICLE_STATE: Sending notifications for new vehicles")
        for notifier in NOTIFIERS:
            notifier.send_vehicle_notification(new_vehicles)


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


def main(muted_run: bool = False) -> None:
    logging.info("MAIN: Running scheduled job...")
    search_results = run_search()
    manage_vehicle_state(search_results, muted_run)
    logging.info("MAIN: Scheduled job complete!")


def run_scheduler(frequency: timedelta):
    # Run once silently to build initial database entries
    main(muted_run=True)

    # Schedule real runs
    logging.info("MAIN: Scheduled to run every %s seconds", frequency.total_seconds())
    schedule.every(frequency.total_seconds()).seconds.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', '-c', help="Location of the configration yaml file. Default: ./benz_finder.yaml", type=str, default='./benz_finder.yaml')
    parser.add_argument('--logfile', '-l', help="Location of the logfile. Default: ./benz_finder.log", type=str, default='./benz_finder.log')
    parser.add_argument('--database', '-d', help="Location of the sqlite database. Default: ./benz_finder.db", type=str, default='./benz_finder.db')
    parser.add_argument('--frequency', '-f', help="How often benz_finder should search for new vehicles. Default: 1d", type=str, default="1d")
    args = parser.parse_args()

    # Init Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            RotatingFileHandler(args.logfile, maxBytes=5000000, backupCount=1),
            logging.StreamHandler()
        ]
    )
    logging.info("MAIN: Logging started!")

    # Parse run frequency from args and env
    run_freq_str = os.environ.get("JOB_FREQUENCY") or args.frequency
    if run_freq_str.endswith('h'):
        run_freq_delta = timedelta(hours=int(run_freq_str[:-1]))
    elif run_freq_str.endswith('d'):
        run_freq_delta = timedelta(days=int(run_freq_str[:-1]))
    else:
        raise ValueError("Invalid run frequency format. Use 'h' for hours or 'd' for days (e.g., '12h', '1d')")

    # Load config
    logging.info("MAIN: Initializing config yaml...")
    CONFIG = config_handler.load_config(args.config_file)
    NOTIFIERS = [get_notifier(notif_cfg) for notif_cfg in CONFIG['notifications']]

    init_db(args.database)

    run_scheduler(run_freq_delta)
