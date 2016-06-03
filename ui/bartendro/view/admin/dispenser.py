# -*- coding: utf-8 -*-
from sqlalchemy import func, asc
import memcache
from bartendro import app, db
from flask import Flask, request, redirect, render_template
from flask.ext.login import login_required
from flask.ext.permissions.decorators import user_is, user_has
from wtforms import Form, SelectField, IntegerField, validators
from bartendro.model.drink import Drink
from bartendro.model.booze import Booze
from bartendro.model.dispenser import Dispenser
from bartendro.form.dispenser import DispenserForm
from bartendro.mixer import ML_PER_SECOND
from operator import itemgetter
from bartendro import fsm
from bartendro.mixer import LL_OK

count = 0


@app.route('/admin')
@login_required
@user_is('admin')
def dispenser():
    driver = app.driver
    global count
    count = driver.count()

    saved = int(request.args.get('saved', "0"))
    updated = int(request.args.get('updated', "0"))

    class F(DispenserForm):
        pass

    dispensers = db.session.query(Dispenser).order_by(Dispenser.id).all()
    boozes = db.session.query(Booze).order_by(Booze.id).all()
    booze_list = [(b.id, b.name) for b in boozes]
    sorted_booze_list = sorted(booze_list, key=itemgetter(1))

    if app.options.use_liquid_level_sensors:
        states = [dispenser.out for dispenser in dispensers]
    else:
        states = [LL_OK for dispenser in dispensers]

    kwargs = {}
    fields = []
    for i in xrange(1, 17):
        dis = "dispenser%d" % i
        actual = "actual%d" % i
        setattr(F, dis, SelectField("%d" % i, choices=sorted_booze_list)) 
        setattr(F, actual, IntegerField(actual, [validators.NumberRange(min=1, max=100)]))
        kwargs[dis] = "1" # string of selected booze
        fields.append((dis, actual))

    form = F(**kwargs)
    for i, dispenser in enumerate(dispensers):

        #get the booze id as string!!!
        for booze in booze_list:
            if booze[0] == dispenser.booze_id:
                booze_id_string = "%d" % dispenser.booze_id

        form["dispenser%d" % (i + 1)].data = booze_id_string
        form["actual%d" % (i + 1)].data = dispenser.actual

    bstate = app.globals.get_state()
    error = False
    if bstate == fsm.STATE_START:
        state = "Bartendro is starting up."
    elif bstate == fsm.STATE_READY:
        state = "Bartendro is ready!"
    elif bstate == fsm.STATE_LOW:
        state = "Bartendro is ready, but one or more boozes is low!"
    elif bstate == fsm.STATE_OUT:
        state = "Bartendro is ready, but one or more boozes is out!"
    elif bstate == fsm.STATE_HARD_OUT:
        state = "Bartendro cannot make any drinks from the available booze!"
    elif bstate == fsm.STATE_ERROR:
        state = "Bartendro is out of commission. Please reset Bartendro!"
        error = True
    else:
        state = "Bartendro is in bad state: %d" % bstate

    avail_drinks = app.mixer.get_available_drink_list()
    return render_template("admin/dispenser", 
                           title="Dispensers",
                           calibrate_ml=ML_PER_SECOND, 
                           form=form, count=count, 
                           fields=fields, 
                           saved=saved,
                           state=state,
                           error=error,
                           updated=updated,
                           num_drinks=len(avail_drinks),
                           options=app.options,
                           dispenser_version=driver.dispenser_version,
                           states=states)

@app.route('/admin/save', methods=['POST'])
@login_required
def save():
    cancel = request.form.get("cancel")
    if cancel: return redirect('/admin/dispenser')

    form = DispenserForm(request.form)
    if request.method == 'POST' and form.validate():
        dispensers = db.session.query(Dispenser).order_by(Dispenser.id).all()

        print "dispensers: %s" % dispensers

        print "count: %s " % count

        booze = db.session.query(Booze).first()
        print booze

        #create dispenser database entry if not available
        if len(dispensers) < count:
            for counter in range(len(dispensers) + 1,count +1):

                db.session.add(Dispenser(booze=booze, actual=booze.id))
                print "Added dispenser with id %s " % counter
                db.session.commit()

        for dispenser in dispensers:
            try:
                dispenser.booze_id = request.form['dispenser%d' % dispenser.id]
                #dispenser.actual = request.form['actual%d' % dispenser.id]
            except KeyError:
                continue
        db.session.commit()

    app.mixer.mc.delete("available_drink_list")
    app.mixer.check_levels()
    return redirect('/admin?saved=1')
