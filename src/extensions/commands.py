from interactions import Extension, slash_command, SlashContext, OptionType, slash_option, Client
from interactions.ext.paginators import Paginator
import logging
import datetime as dt
import utils.html_parser as html_parser
import utils.embeds as embeds
import utils.pullnsave as pullnsave


class Commands(Extension):
    # Extension init
    def __init__(self, client: Client):
        self.client = client


    # User-invoked command to manually search for make
    @slash_command(name="search", description="Manually search for cars")
    @slash_option(
        name="make",
        description="Make of vehicle to search",
        required=True,
        opt_type=OptionType.STRING
    )
    @slash_option(
        name="model",
        description="Model of vehicle to search",
        required=False,
        opt_type=OptionType.STRING
    )
    @slash_option(
        name="year",
        description="Model year of vehicle to search",
        required=False,
        opt_type=OptionType.INTEGER
    )
    async def search(self, ctx: SlashContext, make: str, model: str=None, year: int=None):
        logging.info(f'COMMANDS-SEARCH: Command Invoked! args: {make} {model} {year}')
        
        # Defer response to give time for request
        await ctx.defer()

        # Query pullnsave site
        data = pullnsave.search_vehicles(make, model, year)
        if not data:
            logging.error('COMMANDS-SEARCH: pullnsave returned no data, exiting...')
            await ctx.send('pullnsave returned no data')
            return
        
        # Parse site data
        all_listings = html_parser.parse_listings(data)
        if not all_listings:
            logging.info('COMMANDS-SEARCH: no results, exiting...')
            await ctx.send('No results found')
            return
        
        # Filter listings
        filtered_listings = html_parser.filter_listings(all_listings)

        # Build embeds
        listing_embeds = []
        for listing in filtered_listings:
            listing_embeds.append(embeds.vehicle_listing(listing))
        
        # Send paginated resposne
        paginator = Paginator.create_from_embeds(self.client, *listing_embeds)
        await paginator.send(ctx)
        logging.info('COMMANDS-SEARCH: paginated results sent!')
    

    # User-invoked command to get new stock
    @slash_command(name="new_stock", description="Get all latest arrivals")
    async def new_stock(self, ctx: SlashContext):
        logging.info('COMMANDS-NEW_STOCK: Command Invoked!')

        # Defer response to give time for requests
        await ctx.defer()

        # Query pullnsave for all makes
        make_data = pullnsave.get_makes()
        if not make_data:
            logging.error('COMMANDS-NEW_STOCK: pullnsave returned no data, exiting...')
            await ctx.send("Couldn't grab make data")
            return
        
        # Parse make data
        all_makes = html_parser.parse_makes(make_data)
        if not all_makes:
            logging.error('COMMANDS-NEW_STOCK: make parse error, exiting...')
            await ctx.send("Couldn't parse make data")
            return
        
        # Grab all recent listings
        all_listings = []
        for make in all_makes:
            data = pullnsave.search_vehicles(make, begin_date=(dt.datetime.now() - dt.timedelta(days=3)).strftime('%Y-%m-%d'))
            if not data:
                logging.error('COMMANDS-NEW_STOCK: pullnsave returned no data, skipping...')
                continue
            listings = html_parser.parse_listings(data)
            if not listings:
                logging.error('COMMANDS-NEW_STOCK: pullnsave returned no data, skipping...')
                continue
            for listing in listings:
                all_listings.append(listing)
        
        # Filter and sort listings
        filtered_listings = html_parser.filter_listings(all_listings)

        # Build embeds
        listing_embeds = []
        for listing in filtered_listings:
            listing_embeds.append(embeds.vehicle_listing(listing))
        
        # Send paginated resposne
        paginator = Paginator.create_from_embeds(self.client, *listing_embeds)
        await paginator.send(ctx)
        logging.info('COMMANDS-SEARCH: paginated results sent!')


def setup(bot):
    Commands(bot)
