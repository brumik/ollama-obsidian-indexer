from server import app
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    debug = os.getenv("APP_DEVELOPMENT", False)
    app.run(debug=debug)
