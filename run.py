from app import app
import os

if __name__ == "__main__":
    app.run(debug=False, port=os.environ.get("PORT", default=5000))