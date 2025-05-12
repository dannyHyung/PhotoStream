from app import create_app
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = create_app()

if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)