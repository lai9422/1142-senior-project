from src import create_app
from config import Config

app = create_app()

if __name__ == "__main__":
    app.run(port=int(Config.PORT), debug=True)