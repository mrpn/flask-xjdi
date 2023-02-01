from flask import Flask, jsonify
import os
from flask import Flask
from flask_discord_interactions import DiscordInteractions


app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.getenv["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.getenv["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.getenv["DISCORD_CLIENT_SECRET"]


@app.route('/')
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})

@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"


discord.set_route("/interactions")


discord.update_commands(guild_id=os.environ["TESTING_GUILD"])

if __name__ == '__main__':
    app.run(debug=False, port=os.getenv("PORT", default=5000))
