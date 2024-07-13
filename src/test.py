import utils.pullnsave as pullnsave
import utils.config_handler as config_handler



config = config_handler.load_config('benz_finder.yaml')

vehicles = []

for location in config['locations']:
    for vehicle in config['vehicles']:
        for model in vehicle['models']:
            for year in vehicle['years']:
                search_results = pullnsave.search_vehicles(
                    make=vehicle['make'],
                    model=model,
                    year=year,
                    store=location
                )
                for result in search_results:
                    vehicles.append(result)

print(vehicles)
