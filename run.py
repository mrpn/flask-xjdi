from app import app
import os


app.run(debug=False, port=os.environ.get("PORT", default=5000))