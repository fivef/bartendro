# -*- coding: utf-8 -*-
from bartendro import app, db, login_manager
from bartendro.form.login import LoginForm
from flask import request, render_template, redirect, url_for, jsonify
from flask.ext.login import login_required, login_user, logout_user
from bartendro.model.user import User
from bartendro.view.drink.drink import is_ip_allowed_to_pour_drinks


@login_manager.user_loader
def load_user(userid):
    return db.session.query(User).filter(User.id == userid).first()

"""
@login_manager.unauthorized_handler
def handle_needs_login():
    next = request.args.get("next")
    if next:
        return redirect(url_for('login', next=next))
    else:
        return redirect(url_for('login'))
"""
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
                login_user(user_object.first())
                """ TODO: next_is_valid should check if the user has valid permission to access the `next` url
                if not the application will be vulnerable to open redirects. """
                next_args = request.args.get("next")
                if next_args:
                    print("Redirect to {}".format(next_args))
                    return redirect(next_args)
                else:
                    print("Redirect to index")
                    return redirect(url_for("index"))
                    
                    
        next_args = request.args.get("next")
        print("Show login failed")
        return render_template("/login",
                               options=app.options,
                               form=form,
                               fail=1,
                               allowed_to_pour=is_ip_allowed_to_pour_drinks(request.remote_addr),
                               next=next_args)

    next_args = request.args.get("next")
    print("Show login")
    return render_template("/login",
                           options=app.options,
                           form=form,
                           fail=0,
                           allowed_to_pour=is_ip_allowed_to_pour_drinks(request.remote_addr),
                           next=next_args)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/rfid', methods=['GET'])
def rfid():
    """Login user via rfid tag"""
    print("RFID read")
    tag_id = app.rfid_reader.get_tag()
    user_object = db.session.query(User).filter(User.rfid == tag_id)

    if user_object.first():
        # check if users rfid is empty, if empty ignore
        if user_object.first().rfid == "":
            return jsonify(tag_id=tag_id)
        login_user(user_object.first())
        print("User {} logged in".format(user_object.first().name))
        next_args = request.args.get("next")
        if next_args:
            return jsonify(url=next_args)
        else:
            return jsonify(url=url_for("index"))

    return jsonify(url="")
