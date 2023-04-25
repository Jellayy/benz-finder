from interactions import Embed, EmbedField, EmbedFooter


def vehicle_listing(listing_data):
    embed = Embed(
        title=f"{listing_data['model_year']} {listing_data['model']}",
        fields=[
            EmbedField(
                name="Color",
                value=listing_data['color'],
                inline=True
            ),
            EmbedField(
                name="VIN",
                value=listing_data['VIN'],
                inline=True
            ),
            EmbedField(
                name="Stock #",
                value=listing_data['stock_number'],
                inline=True
            ),
            EmbedField(
                name="Location",
                value=listing_data['location'],
                inline=True
            ),
            EmbedField(
                name="Row",
                value=listing_data['row'],
                inline=True
            ),
            EmbedField(
                name="Date Revieved",
                value=listing_data['date_recieved'].strftime("%A %B %d, %Y"),
                inline=True
            )
        ],
        footer=EmbedFooter(
            text="Benz-Finder | Powered by Pull-N-Save",
            icon_url="https://cdn.discordapp.com/embed/avatars/0.png"
        )
    )
    embed.set_image(listing_data['image'])

    return embed
