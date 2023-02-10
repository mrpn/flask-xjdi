from app import app
from flask_discord_interactions import DiscordInteractions
import sys
import os


discord = DiscordInteractions(app)
# python run.py register to update commands
if "register" in sys.argv:
    discord.set_route("/interactions")
    discord.update_commands(guild_id=os.environ.get("GUILD_ID"))
    print('updated commands')
    sys.exit()

if __name__ == '__main__':
    app.run()