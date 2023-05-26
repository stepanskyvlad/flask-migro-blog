from flask import Flask
from routes import pages
from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()


def create_app():
    app = Flask(__name__)
    app.register_blueprint(pages)

    client = MongoClient(os.getenv("MONGO_URI"))
    app.db = client.microblog

    return app
