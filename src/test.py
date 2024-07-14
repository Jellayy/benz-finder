import utils.pullnsave as pullnsave
import utils.config_handler as config_handler

from notifications import get_notifier

config = config_handler.load_config('benz_finder.yaml')
notifiers = [get_notifier(notif_cfg) for notif_cfg in config['notifications']]

vehicles = []
for location in config['locations']:
    for vehicle in config['vehicles']:
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

for vehicle in vehicles:
    for notifier in notifiers:
        notifier.send_vehicle_notification(vehicle)
