from ptracker import create_app
from dotenv import dotenv_values

config = dotenv_values(".env")

port = int(config.get("PORT") or 5000)

app = create_app()

if __name__ == "__main__":
    app.run(port=port, debug=True)
