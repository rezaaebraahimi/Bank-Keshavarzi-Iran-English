from app import db
from persiantools.jdatetime import JalaliDate


class Admin(db.Model):
    __tablename__= 'admin'
    id = db.Column(db.Integer, primary_key=True)
    admin_user = db.Column(db.String(45), nullable=False)
    admin_pass = db.Column(db.String(128), nullable=False)


class Property(db.Model):
    __tablename__ = 'property'
    id = db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.String(45), db.ForeignKey('user.CenterCode'), nullable=False)  
    cardType = db.Column(db.String(45), db.ForeignKey('card.typeOfCards'), nullable=False)
    date_add = db.Column(db.String(45),  default=JalaliDate.today())
    supply = db.Column(db.Integer, default=0, nullable=False)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    CenterName = db.Column(db.String(100), nullable=False)
    CenterCode = db.Column(db.String(45), nullable=False, unique=True)
    personal = db.Column(db.String(45), nullable=False)
    personalCode = db.Column(db.String(45), nullable=False, unique=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    date_added = db.Column(db.String(45),  default=JalaliDate.today())
    status = db.Column(db.Integer, default=0, nullable=False)
    properties = db.relationship('Property', backref='user', lazy=True)  


class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    typeOfCards = db.Column(db.String(45), nullable=False)
    properties = db.relationship('Property', backref='card', lazy=True)  
    receives = db.relationship('Receive', backref='card', lazy=True)  


class Receive(db.Model):
    __tablename__ = 'receive'  
    id = db.Column(db.Integer, primary_key=True)
    admin_supply = db.Column(db.Integer, default=0, nullable=False)
    recieve_date = db.Column(db.String(45),default=JalaliDate.today())
    cardType = db.Column(db.String(45), db.ForeignKey('card.typeOfCards'), nullable=False) 


class Blogpost(db.Model):
    __tablename__ = 'blogpost'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(45))
    date_posted = db.Column(db.Date)
    content = db.Column(db.Text)


class UserRequest(db.Model):
    __tablename__ = 'userrequest'
    id = db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.String(45), db.ForeignKey('user.CenterCode'))
    card_type = db.Column(db.String(45), nullable=False)
    supply_quantity = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.String(45), default=JalaliDate.today())
    status = db.Column(db.Integer, default=0, nullable=False)