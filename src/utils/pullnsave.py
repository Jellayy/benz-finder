import requests
import logging


def search_vehicles(make, model=None, year=None, store=None, begin_date=None, end_date=None):
    # Build request body
    data = f'makes={make}'
    if model:
        data += f'&models={model}'
    if year:
        data += f'&years={year}'
    if store:
        data += f'&store={store}'
    if begin_date:
        data += f'&beginDate={begin_date}'
    if end_date:
        data += f'&endDate={end_date}'
    data += '&action=getVehicles'

    # Send request
    logging.info(f'PULLNSAVE: Sending Request: {data}')
    r = requests.post(
        url='https://pullnsave.com/wp-admin/admin-ajax.php',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'host': 'pullnsave.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0'
        },
        data=data
    )

    # Return response
    if r.status_code == 200:
        return r.text
    else:
        logging.error(f'PULLNSAVE: Unhandled Response Status: {r.status_code}')
        return False


def get_makes():
    # Build request body
    data = 'action=getMakes'

    # Send request
    logging.info(f'PULLNSAVE: Sending Request: {data}')
    r = requests.post(
        url='https://pullnsave.com/wp-admin/admin-ajax.php',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'host': 'pullnsave.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0'
        },
        data=data
    )

    # Return response
    if r.status_code == 200:
        return r.text
    else:
        logging.error(f'PULLNSAVE: Unhandled Response Status: {r.status_code}')
        return False
