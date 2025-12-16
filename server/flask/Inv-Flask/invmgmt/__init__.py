from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from . import config
from . import controller


class Base(DeclarativeBase):
    pass

# initialization
controller.db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
print("***** flask app running!!!!!");
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = config.db_url
# app.config['SQLALCHEMY_ECHO'] = True
# initialize the app with the extension
controller.db.init_app(app)

# info
app.logger.setLevel(1)
