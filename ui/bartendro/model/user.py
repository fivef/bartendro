# -*- coding: utf-8 -*-
from bartendro import db
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, Column, Integer, String, MetaData, UnicodeText, ForeignKey, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base
from bartendro.model.drink_name import DrinkName
from operator import attrgetter
from flask.ext.permissions.models import UserMixin
from werkzeug import generate_password_hash, check_password_hash


class User(UserMixin):
    """
    Contains the users and their stats.
    """
    # __tablename__  is defined in supercalls UserMixin
    # id is defined in supercalls UserMixin
    name = Column(String, default='')
    password = Column(String, default='')
    weight = Column(Numeric, default=80)
    age = Column(Integer, default=30)
    height = Column(Numeric, default=180)
    sex = Column(String, default='male')
    bac = Column(String, default=0.0)
    balance = Column(Numeric, default=0.0)

    query = db.session.query_property()

    # Identify the class to differentiate between sub-types of the UserMixin.
    __mapper_args__ = {
        'polymorphic_identity':
        'user'  # This can be any unique value except 'usermixin'.
    }

    def __init__(self, name, password, roles=None):
        UserMixin.__init__(self, roles)
        self.name = name
        self.set_password(password)

        db.session.add(self)
        
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # start flask user functions
    def is_authenticated(self):
        return self.name != ""

    def is_active(self):
        return True

    def is_anonymous(self):
        return self.name == ""

    def get_id(self):
        return self.id

    def __repr__(self):
        return "<User(name='%s', password='%s')>" % (self.name, self.password)
