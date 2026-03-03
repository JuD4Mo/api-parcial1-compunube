from db.db import db

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    priceU = db.Column(db.Numeric(10, 2), nullable=False)

    def __init__(self, name, quantity, priceU):
        self.name = name
        self.quantity = quantity
        self.priceU = priceU