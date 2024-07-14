import requests
import logging
import re
import json

import datetime as dt

from bs4 import BeautifulSoup


def parse_vehicles(html):
    # Initiate bs4 parser
    soup = BeautifulSoup(html, 'html.parser')

    try:
        # Find the tbody element that contains all listings
        tbody = soup.find('tbody')

        listings = []
        try:
            for tr in tbody.find_all('tr'):
                listings.append({
                    "image": tr.find('img')['src'],
                    "model_year": tr.find_all('td')[1].get_text().strip(),
                    "model": tr.find('span', class_='notranslate').get_text().strip(),
                    "date_recieved": dt.datetime.strptime(tr.find_all('td')[3].get_text().strip(), "%m-%d-%y"),
                    "row": tr.find_all('td')[4].get_text().strip(),
                    "location": tr.find_all('td')[5].get_text().strip(),
                    "color": tr.find_all('td')[6].get_text().strip(),
                    "stock_number": tr.find_all('td')[7].get_text().strip(),
                    "VIN": tr.find_all('td')[8].get_text().strip()
                })
        except:
            pass
        
        return listings
    except Exception as e:
        logging.error(f'HTML_PARSER-PARSE_LISTINGS: Parsing Error: {e}')
        return []


def search_vehicles(make, model=None, year=None, store=None, begin_date=None, end_date=None):
    # Build request body
    data = f'makes={make}'
    if model:
        data += f'&models={model}'
    if year:
        if isinstance(year, int):
            data += f'&years={year}'
            data += f'&endYears={year}'
        elif isinstance(year, str):
            start, end = map(int, year.split('-'))
            data += f'&years={start}'
            data += f'&endYears={end}'
    if store:
        data += f'&store={store}'
    if begin_date:
        data += f'&beginDate={begin_date}'
    if end_date:
        data += f'&endDate={end_date}'
    data += '&action=getVehicles'

    # Send request
    logging.info(f'PULLNSAVE: Sending Request: {data}')
    print(f'PULLNSAVE: Sending Request: {data}')
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
        vehicles = parse_vehicles(r.text)
        return vehicles
    else:
        logging.error(f'PULLNSAVE: Unhandled Response Status: {r.status_code}')
        return []


def get_stores():
    # Build request body
    data = 'action=getStores'

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
        return json.loads(r.text)
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

    if r.status_code == 200:
        # Parse values from returned HTML
        pattern = r"value='([^']*)"
        makes = re.findall(pattern, r.text)
        return makes
    else:
        logging.error(f'PULLNSAVE: Unhandled Response Status: {r.status_code}')
        return False
