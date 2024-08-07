import yaml
import sys
import re
import logging

from typing import List, Dict, Union
from notifications import get_notifier

import utils.pullnsave as pullnsave


def __read_config(file_path: str) -> Dict:
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        logging.error("CONFIG_HANDLER: Error parsing config yaml file: %s", e)
        sys.exit(1)
    except FileNotFoundError:
        logging.error("CONFIG_HANDLER: Config yaml file not found: %s", file_path)
        sys.exit(1)


def __validate_year(year: Union[int, str]) -> bool:
    if isinstance(year, int):
        return 1900 <= year <= 2100
    elif isinstance(year, str):
        match = re.match(r'(\d{4})-(\d{4})', year)
        if match:
            start, end = map(int, match.groups())
            return 1900 <= start < end <= 2100
    return False


def __replace_spaces_in_models(config: Dict) -> Dict:
    for vehicle in config['vehicles']:
        if 'models' in vehicle:
            vehicle['models'] = [model.replace(' ', '+') for model in vehicle['models']]
    return config


def __validate_config(config: Dict) -> None:
    if not isinstance(config, dict):
        raise ValueError("Config must be a dictionary")
    
    if 'locations' not in config or not isinstance(config['locations'], list):
        raise ValueError("Config must contain a 'locations' list")
    
    for location in config['locations']:
        if not isinstance(location, str):
            raise ValueError("Each location must be a string")
    
    if 'vehicles' not in config or not isinstance(config['vehicles'], list):
        raise ValueError("Config must contain a 'vehicles' list")
    
    for vehicle in config['vehicles']:
        if not isinstance(vehicle, dict):
            raise ValueError("Each vehicle must be a dictionary")
        
        if 'make' not in vehicle or not isinstance(vehicle['make'], str):
            raise ValueError("Each vehicle must have a 'make' string")
        
        if 'years' not in vehicle or not isinstance(vehicle['years'], list):
            raise ValueError("Each vehicle must have a 'years' list")
        
        for year in vehicle['years']:
            if not __validate_year(year):
                raise ValueError(f"Invalid year format: {year}")
    
    if 'notifications' in config:
        __validate_notifications(config['notifications'])


def __map_locations_to_store_ids(config: Dict) -> Dict:
    # Call pullnsave for store IDs
    store_data = pullnsave.get_stores()
    store_map = {store['StoreName']: store['StoreNumber'] for store in store_data}

    new_locations = []
    for location in config['locations']:
        if location in store_map:
            new_locations.append(int(store_map[location]))
        else:
            raise ValueError(f"Location '{location}' not found")
    config['locations'] = new_locations
    return config


def __validate_notifications(notifications: List[Dict]) -> None:
    if not isinstance(notifications, list):
        raise ValueError("Notifications must be a list")
    
    for notification in notifications:
        if not isinstance(notification, dict):
            raise ValueError("Each notification must be a dictionary")
        
        if 'type' not in notification:
            raise ValueError("Each notification must have a 'type'")
        
        try:
            notifier = get_notifier(notification)
            notifier.validate_config(notification)
        except ValueError as e:
            raise ValueError(f"Invalid notification config: {str(e)}")


def load_config(file_path: str) -> Dict:
    config = __read_config(file_path)
    try:
        __validate_config(config)
        logging.info("CONFIG_HANDLER: Config yaml validation successful!")
        return __map_locations_to_store_ids(__replace_spaces_in_models(config))
    except ValueError as e:
        logging.error("CONFIG_HANDLER: Config yaml validation error: %s", e)
        exit(1)
