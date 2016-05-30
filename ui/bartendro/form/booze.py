#!/usr/bin/env python
from wtforms import Form, TextField, DecimalField, HiddenField, validators, \
                          TextAreaField, SubmitField, SelectField
from bartendro.model import booze

class BoozeForm(Form):
    id = HiddenField(u"id", default=0)
    name = TextField(u"Name", [validators.Length(min=3, max=255)])
    brand = TextField(u"Brand") # Currently unused
    desc = TextAreaField(u"Description", [validators.Length(min=3, max=1024)])
    abv = DecimalField(u"ABV", [validators.NumberRange(0, 97)], default=0, places=0)
    type = SelectField(u"Type", [validators.NumberRange(0, len(booze.booze_types))], 
                                choices=booze.booze_types,
                                coerce=int)
    flowrate = DecimalField(u"Flowrate (ml/s)", [validators.NumberRange(0, 100)], default=0, places=2)
    price = DecimalField(u"Price per container (e.g. bottle)", [validators.NumberRange(0, 100)], default=0, places=2)
    amount = DecimalField(u"Available amount per container (e.g. bottle size)", [validators.NumberRange(0, 100)], default=1, places=4)
    save = SubmitField(u"save")
    cancel = SubmitField(u"cancel")
    delete = SubmitField(u"delete")

form = BoozeForm()
