from bs4 import BeautifulSoup
import datetime as dt
import logging


def filter_listings(listings):
    filtered_listings = [listing for listing in listings if listing['location'] != 'Salt Lake City']
    sorted_listings = sorted(filtered_listings, key=lambda x: x['date_recieved'], reverse=True)[:5]

    return sorted_listings


def parse_listings(html):
    # Initiate bs4 parser
    soup = BeautifulSoup(html, 'html.parser')

    try:
        # Find the tbody element that contains all listings
        tbody = soup.find('tbody')

        listings = []
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
        
        return listings
    except Exception as e:
        logging.error(f'HTML_PARSER-PARSE_LISTINGS: Parsing Error: {e}')
        return False


def parse_makes(html):
    # Initiate bs4 parser
    soup = BeautifulSoup(html, 'html.parser')

    try:
        # Find all span elements with the class 'notranslate'
        spans = soup.find_all('span', {'class': 'notranslate'})

        # Extract span text
        makes = []
        for span in spans:
            makes.append(span.text)
        
        return makes
    except Exception as e:
        logging.error(f'HTML_PARSER-PARSE_MAKES: Parsing Error: {e}')
        return False
