from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Bike(db.Model):
    __tablename__ = 'bikes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    badge = db.Column(db.String(50))
    info = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='unsold')
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Bike, self).__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "price": self.price,
            "category": self.category,
            "badge": self.badge,
            "info": self.info,
            "description": self.description,
            "status": self.status,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Valuation(db.Model):
    __tablename__ = 'valuations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    bike_model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(10))
    kilometers = db.Column(db.String(50))
    city = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Valuation, self).__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "bike_model": self.bike_model,
            "year": self.year,
            "kilometers": self.kilometers,
            "city": self.city,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AdminUser(db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
