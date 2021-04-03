from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

app = Flask(__name__)
db = SQLAlchemy()
ma = Marshmallow(app)

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


if __name__ == '__main__':
    
    from models import *
    import os
    
    # Delete database file if it exists currently
    if os.path.exists('attendance.db'):
        os.remove('attendance.db')

    # Create the database
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'

    db.app = app
    db.init_app(app)
    db.create_all()

    user = User(username='admin')
    user.hash_password('12345')
    db.session.add(user)

    db.session.commit()