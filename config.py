import os
from dotenv import load_dotenv

#Load the .env file.
load_dotenv()

class Config:
    FLASK_ENV=os.getenv("FLASK_ENV")
    SECRET_KEY=os.getenv("SECRET_KEY")
    REDIS_HOST=os.getenv("REDIS_HOST")
    REDIS_PORT=os.getenv("REDIS_PORT")
    OPA_URL=os.getenv("OPA_URL")
    STREAM_NAME=os.getenv("STREAM_NAME")
    CONSUMER_GROUP=os.getenv("CONSUMER_GROUP")
    CONSUMER_NAME=os.getenv("CONSUMER_NAME") 
    AUTH_INVALIDATION_TIME=os.getenv("AUTH_INVALIDATION_TIME")

