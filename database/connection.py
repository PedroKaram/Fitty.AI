from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml
from pathlib import Path

config = yaml.safe_load(open(Path(__file__).parent.parent / "config.yaml"))

db_config = config["postgres"]
DB_URL = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    return SessionLocal()
