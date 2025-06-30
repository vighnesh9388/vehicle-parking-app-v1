from . import db

class Spot(db.Model):
    __tablename__ = 'parkingspot'
    
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parkinglot.id'), nullable=False)
    spot_number = db.Column(db.String(20), nullable=False)
    status= db.Column(db.Boolean, default=False)
    was_occupied = db.Column(db.Boolean, default=False)
    
    reservations = db.relationship('Reserve', backref='spot', lazy=True)
    