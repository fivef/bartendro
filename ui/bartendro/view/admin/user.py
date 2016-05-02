# -*- coding: utf-8 -*-
from bartendro import app, db, login_manager
from bartendro.form.login import LoginForm
from flask import Flask, request, render_template, flash, redirect, url_for
from flask.ext.login import login_required, login_user, logout_user
from bartendro.model.user import User
from flask.ext.permissions.models import UserMixin

@login_manager.user_loader
def load_user(userid):
    return db.session.query(User).filter(User.id == userid).first()

@app.route("/admin/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = request.form.get("user" or '')
        password = request.form.get("password" or '')
        
        #check if user with these credentials exists
        
        user_object = db.session.query(User).filter(User.name == user)
        
        if user_object.first():
                        
            if db.session.query(User).filter(User.name == user).first().password == password:
                # import ipdb; ipdb.set_trace()
                login_user(user_object.first())

                return redirect(request.args.get("next") or url_for("dispenser"))
        return render_template("/admin/login", options=app.options, form=form, fail=1)
    return render_template("/admin/login", options=app.options, form=form, fail=0)

@app.route("/admin/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
