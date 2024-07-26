from .base import BaseNotifier
from discord_webhook import DiscordWebhook, DiscordEmbed


class DiscordNotifier(BaseNotifier):
    def __init__(self, config):
        self.webhook_url = config['webhook_url']
        self.message = config['message']
    
    def __create_vehicle_embed(self, vehicle: dict) -> DiscordEmbed:
        embed = DiscordEmbed(title=f"{vehicle['model_year']} {vehicle['model']}", color="00FF00")
        embed.add_embed_field(name="Color", value=vehicle['color'])
        embed.add_embed_field(name="VIN", value=vehicle['VIN'])
        embed.add_embed_field(name="Location", value=vehicle['location'])
        embed.add_embed_field(name="Row", value=vehicle['row'])
        embed.add_embed_field(name="Stock #", value=vehicle['stock_number'])
        embed.add_embed_field(name="Date Recieved", value=vehicle['date_recieved'].strftime("%A %B %d, %Y"))
        embed.set_image(url=vehicle['image'])
        embed.set_footer(text="Benz-Finder")
        return embed
        
    def send_vehicle_notification(self, vehicles: list) -> None:
        # Send base message
        webhook = DiscordWebhook(url=self.webhook_url, content=self.message, rate_limit_retry=True)
        response = webhook.execute()

        # Send vehicles as embeds
        for vehicle in vehicles:
            webhook = DiscordWebhook(url=self.webhook_url, rate_limit_retry=True)
            webhook.add_embed(self.__create_vehicle_embed(vehicle))
            response = webhook.execute()

    @classmethod
    def validate_config(cls, config):
        if 'webhook_url' not in config:
            raise ValueError("Discord notifications must have a 'webhook_url'")
        if 'message' not in config:
            raise ValueError("Discord notifications must have a 'message")