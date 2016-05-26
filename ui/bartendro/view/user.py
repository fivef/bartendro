# -*- coding: utf-8 -*-
from bartendro import app, db, login_manager
from bartendro.form.login import LoginForm
from flask import Flask, request, render_template, flash, redirect, url_for, jsonify
from flask.ext.login import login_required, login_user, logout_user
from bartendro.model.user import User
from flask.ext.permissions.models import UserMixin
from bartendro.view.root import index


@login_manager.user_loader
def load_user(userid):
    return db.session.query(User).filter(User.id == userid).first()


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = request.form.get("user" or '')
        password = request.form.get("password" or '')

        # check if user with these credentials exists

        user_object = db.session.query(User).filter(User.name == user)

        if user_object.first():

            if user_object.first().check_password(password):
                # import ipdb; ipdb.set_trace()
                login_user(user_object.first())

                return redirect(request.args.get("next") or "/")
        return render_template("/login",
                               options=app.options,
                               form=form,
                               fail=1)
    return render_template("/login",
                           options=app.options,
                           form=form,
                           fail=0)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

"""Login user via rfid tag"""
@app.route('/rfid', methods= ['GET'])                       
def rfid():
    print("RFID read")
    tag_id = app.rfid_reader.get_tag()
    user_object = db.session.query(User).filter(User.rfid == tag_id)
    
    if user_object.first():
        #check if users rfid is empty, if empty ignore
        if user_object.first().rfid == "":
            return jsonify(tag_id=tag_id)
        login_user(user_object.first())
        print("User {} logged in".format(user_object.first().name))
        
        # TODO: redirect and calling index doesnt work to update the index page
        return jsonify(tag_id=tag_id)
         #redirect(request.args.get("/shots"))
    return jsonify(tag_id=tag_id)

