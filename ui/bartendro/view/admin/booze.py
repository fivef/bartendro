# -*- coding: utf-8 -*-
from bartendro import app, db
from sqlalchemy import func, asc
from flask import request, redirect, render_template
from bartendro.model.booze import Booze
from bartendro.model.drink_booze import DrinkBooze
from bartendro.form.booze import BoozeForm
from flask.ext.permissions.decorators import user_is


@app.route('/admin/booze')
@user_is('admin')
def admin_booze():
    form = BoozeForm(request.form)
    boozes = Booze.query.order_by(asc(func.lower(Booze.name)))

    deleted = int(request.args.get('deleted', "0"))
    delete_message = request.args.get('delete_message', "")
    return render_template("admin/booze",
                           options=app.options,
                           boozes=boozes,
                           form=form,
                           title="Booze",
                           deleted=deleted,
                           delete_message=delete_message)


@app.route('/admin/booze/edit/<id>')
@user_is('admin')
def admin_booze_edit(id):
    saved = int(request.args.get('saved', "0"))
    booze = Booze.query.filter_by(id=int(id)).first()
    form = BoozeForm(obj=booze)
    boozes = Booze.query.order_by(asc(func.lower(Booze.name)))
    return render_template("admin/booze",
                           options=app.options,
                           booze=booze,
                           boozes=boozes,
                           form=form,
                           title="Booze",
                           saved=saved)


@app.route('/admin/booze/save', methods=['POST'])
@user_is('admin')
def admin_booze_save():

    cancel = request.form.get("cancel")
    if cancel:
        return redirect('/admin/booze')

    delete = request.form.get("delete")

    form = BoozeForm(request.form)
    if request.method == 'POST' and form.validate():
        id = int(request.form.get("id") or '0')
        if id:
            booze = Booze.query.filter_by(id=int(id)).first()

            if delete:
                # check if booze is still used for a drink

                drink_boozes = DrinkBooze.query.filter_by(booze_id=booze.id)

                if drink_boozes.first():
                    # there are still drinks with this booze
                    delete_message = u"Unable to delete the booze {booze}. The drink {drink} still contains {booze}. Delete the drink {drink} first!".format(drink=drink_boozes.first().drink.name.name, booze=booze.name, booze_id=booze.id)
                else:
                    delete_message = u"The booze {booze} has been deleted successfully.".format(booze=booze.name)
                    db.session.delete(booze)
            else:
                booze.update(form.data)
        else:
            booze = Booze(data=form.data)
            db.session.add(booze)

        db.session.commit()
        mc = app.mc
        mc.delete("top_drinks")
        mc.delete("other_drinks")
        mc.delete("available_drink_list")

        if delete:
            return redirect('/admin/booze?deleted=1&delete_message='+delete_message)
        else:
            return redirect('/admin/booze/edit/%d?saved=1' % booze.id)

    # do nothing, just refresh the page
    boozes = Booze.query.order_by(asc(func.lower(Booze.name)))
    return render_template("admin/booze",
                           options=app.options,
                           boozes=boozes,
                           form=form,
                           title="Booze")
