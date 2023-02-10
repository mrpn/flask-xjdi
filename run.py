from app import app, discord
from flask_discord_interactions import DiscordInteractions
import sys
import os


# python run.py register to update commands
if "register" in sys.argv:
    # discord.update_commands(guild_id=os.environ.get("GUILD_ID"))
    discord.update_commands(guild_id=600479716616699935)
    print('updated commands')
    sys.exit()

if __name__ == '__main__':
    app.run()