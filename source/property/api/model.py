from sqlalchemy_utils import UUIDType
from .. import db


class PropertyModel(db.Model):
    id = db.Column(UUIDType(), primary_key=True)
    name = db.Column(db.Unicode(40))
    pathname = db.Column(db.UnicodeText)
    posted_at = db.Column(db.DateTime)
