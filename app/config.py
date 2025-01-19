from dotenv import load_dotenv
import os



load_dotenv()

database_url = os.getenv("DB_URI")