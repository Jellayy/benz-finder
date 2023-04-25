from interactions import Extension, slash_command, SlashContext, OptionType, slash_option
import requests


class Commands(Extension):


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
    async def search(self, ctx: SlashContext, make: str, model: str=""):
        # Defer response to give time for request
        await ctx.defer()

        if model == "":
            model = "0"

        # Make request
        r = requests.post(
            url='https://pullnsave.com/wp-admin/admin-ajax.php',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'host': 'pullnsave.com',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0'
            },
            data=f"makes={make}&models={model}&years=0&store=0&beginDate=&endDate=&action=getVehicles"
        )

        if r.status_code == 200:
            # Scrape some data
            images = ""
            split = r.text.split("<img width='100' src='")
            split.pop(0)
            iterator = 0
            for section in split:
                if iterator <= 24:
                    images = images + (section.split("'>")[0] + "\n")
                    iterator += 1
            
            if images != "":
                await ctx.send(images)
            else:
                await ctx.send(f"No listings found for Make: {make} Model: {model}")
        else:
            await ctx.send(f"Unhandled request exception: {r.status_code}")
            


def setup(bot):
    Commands(bot)
