# -*- coding: utf-8 -*-
from bartendro import db
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, Column, Integer, String, MetaData, UnicodeText, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

class DrinkLogBooze(db.Model):
    """
    Join between the DrinkLog table and the Booze table for 1:n relationship
    """

    __tablename__ = 'drink_log_booze'
    id = Column(Integer, primary_key=True)
    drink_log_id = Column(Integer, ForeignKey('drink_log.id'), nullable=False)
    booze_id = Column(Integer, ForeignKey('booze.id'), nullable=False)
    amount = Column(Integer, default=0)
 
    query = db.session.query_property()

    def __init__(self, drink_log, booze, amount):
        self.drink_log = drink_log
        self.drink_log_id = drink_log.id
        self.booze = booze
        self.booze_id = booze.id
        self.amount = amount
#        db.session.add(self)

    def json(self):
        return { 
                 'id' : self.id, 
                 'amount' : self.amount
               }

    def __repr__(self):
        return "<DrinkLogBooze(%d,<DrinkLog>(%d),<Booze>(%d),%d,%d)>" % (self.id or -1, 
                                                 self.drink_log.id,
                                                 self.booze.id or -1,
                                                 self.amount)

