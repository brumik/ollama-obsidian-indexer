from .server import app
from dotenv import load_dotenv
from waitress import serve
import os

def main():
    load_dotenv()
    debug = os.getenv("APP_DEVELOPMENT", "0")
    port = int(os.getenv("APP_PORT", 5000))
    if debug != "0":
        serve(app, host='0.0.0.0', port=port)
    else:
        app.run(host="0.0.0.0", debug=True, port=port)

if __name__ == "__main__":
    main()
