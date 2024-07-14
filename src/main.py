import schedule
import time

from models.base import Session
from models.vehicle import Vehicle


def manage_vehicle_state(searched_vehicles):
    session = Session()

    for vehicle_data in searched_vehicles:
        vehicle = session.query(Vehicle).filter_by(
            stock_number=vehicle_data['stock_number'],
            model=vehicle_data['model'],
            location=vehicle_data['location']
        )


def main():
    print("Hello World")


def run_scheduler():
    schedule.every().day.at("02:00").do(main)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    run_scheduler()
