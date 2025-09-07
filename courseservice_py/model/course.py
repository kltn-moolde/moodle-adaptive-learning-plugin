from database import db

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    moodle_id = db.Column(db.Integer, unique=True, nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)