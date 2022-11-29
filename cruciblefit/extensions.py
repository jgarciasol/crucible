from flask_sqlalchemy import SQLAlchemy
'''
Reason for extensions.py is so that we don't have to import anything from __init__.py
We want to only import things inside __init__.py. This way we don't have to do
import __init__ from anywhere else.
'''
db = SQLAlchemy()