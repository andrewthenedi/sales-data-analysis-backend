from .extensions import db


class City(db.Model):
    __tablename__ = "cities"
    id = db.Column(db.Integer, primary_key=True)
    district_name = db.Column(db.String(128), nullable=False)
    city_name = db.Column(db.String(128), nullable=False)
    orders = db.relationship("Order", backref="city", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "district_name": self.district_name,
            "city_name": self.city_name,
        }


class Order(db.Model):
    __tablename__ = "orders"
    unique_order_number = db.Column(db.String(128), primary_key=True)
    order_time = db.Column(db.Time, nullable=False)  # Assuming HH:MM:SS format
    order_date = db.Column(db.Date, nullable=False)  # Separating date
    district_city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)
    rptg_amt = db.Column(db.Float, nullable=False)
    currency_cd = db.Column(db.String(10), nullable=False)
    order_qty = db.Column(db.Integer, nullable=False)
    locked = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        city = self.city.to_dict() if self.city else None
        return {
            "unique_order_number": self.unique_order_number,
            "order_time": self.order_time.isoformat() if self.order_time else None,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "district_city_id": self.district_city_id,
            "rptg_amt": self.rptg_amt,
            "currency_cd": self.currency_cd,
            "order_qty": self.order_qty,
            "locked": self.locked,
            "city": city,
        }
