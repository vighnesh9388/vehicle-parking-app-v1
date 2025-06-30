from . import db

class Lot(db.Model):
    __tablename__ = 'parkinglot'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    spots = db.relationship('Spot', backref='lot', lazy=True)
 