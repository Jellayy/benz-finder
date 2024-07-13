import schedule
import time


def main():
    print("Hello World")


def run_scheduler():
    schedule.every().day.at("02:00").do(main)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    run_scheduler()
