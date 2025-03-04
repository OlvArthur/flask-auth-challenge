from database import db
from sqlalchemy.sql import func

class Meal(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  description = db.Column(db.String(80))
  eaten_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
  is_in_diet = db.Column(db.Boolean())
  user_id = db.Column(db.Integer,  db.ForeignKey('user.id'))