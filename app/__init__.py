from flask import Flask
import os
from flask_discord_interactions import DiscordInteractions
from config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
app.config.from_object(Config)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ.get("DISCORD_CLIENT_ID")
app.config["DISCORD_PUBLIC_KEY"] = os.environ.get("DISCORD_PUBLIC_KEY")
app.config["DISCORD_CLIENT_SECRET"] = os.environ.get("DISCORD_CLIENT_SECRET")

from app import routes, models