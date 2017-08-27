from project import db
from project.models import purchase_key
db.create_all()
db.session.commit()