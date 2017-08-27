import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'../..'))

from project import db
from project.models import purchase_key
db.reflect()
db.drop_all()
db.session.commit()
db.create_all()
db.session.commit()