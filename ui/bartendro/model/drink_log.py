# -*- coding: utf-8 -*-
from bartendro import db
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, Column, Integer, String, MetaData, Unicode, UnicodeText, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

class DrinkLog(db.Model):
    """
    Keeps a record of everything we've dispensed
    """

    __tablename__ = 'drink_log'
    id = Column(Integer, primary_key=True)
    drink_id = Column(Integer, ForeignKey('drink.id'), nullable=False)
    time = Column(Integer, nullable=False, default=0)
    size = Column(Integer, nullable=False, default=-1)
    user_id = Column(Integer, ForeignKey('fp_user.id'))
 
    query = db.session.query_property()

    def __init__(self, drink_id, time, size, user_id):
        self.drink_id = drink_id
        self.time = time
        self.size = size
        self.user_id = user_id
        db.session.add(self)

    def __repr__(self):
        return "<DrinkLog(%d,'%s','%s')>" % (self.id, self.drink_id, self.user_id)

