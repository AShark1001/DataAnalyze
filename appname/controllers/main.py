from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_user, logout_user, login_required

from appname.extensions import cache
from appname.forms import LoginForm, SelectForm
from appname.models import User

from werkzeug import secure_filename

import os
import csv
from pandas import *


main = Blueprint('main', __name__)

UPLOAD_PATH = "./uploads/"
cur_file_path = ""
cur_file_name = "current file name"
col_dict = [
    {
        "text": "xlaccel1",
        "col_idx": 1
    },{
        "text": "xori1",
        "col_idx": 2
    },{
        "text": "xlaccel2",
        "col_idx": 3
    },{
        "text": "xori2",
        "col_idx": 4
    },{
        "text": "xlaccel3",
        "col_idx": 5
    },{
        "text": "xori3",
        "col_idx": 6
    },{
        "text": "xlaccel4",
        "col_idx": 7
    },{
        "text": "xori4",
        "col_idx": 8
    },{
        "text": "xlaccel5",
        "col_idx": 9
    },{
        "text": "xori5",
        "col_idx": 10
    },{
        "text": "ylaccel1",
        "col_idx": 11
    },{
        "text": "yori1",
        "col_idx": 12
    },{
        "text": "ylaccel2",
        "col_idx": 13
    },{
        "text": "yori2",
        "col_idx": 14
    },{
        "text": "ylaccel3",
        "col_idx": 15
    },{
        "text": "yori3",
        "col_idx": 16
    },{
        "text": "ylaccel4",
        "col_idx": 17
    },{
        "text": "yori4",
        "col_idx": 18
    },{
        "text": "ylaccel5",
        "col_idx": 19
    },{
        "text": "yori5",
        "col_idx": 20
    },{
        "text": "zlaccel1",
        "col_idx": 21
    },{
        "text": "zori1",
        "col_idx": 22
    },{
        "text": "zlaccel2",
        "col_idx": 23
    },{
        "text": "zori2",
        "col_idx": 24
    },{
        "text": "zlaccel3",
        "col_idx": 25
    },{
        "text": "zori3",
        "col_idx": 26
    },{
        "text": "zlaccel4",
        "col_idx": 27
    },{
        "text": "zori4",
        "col_idx": 28
    },{
        "text": "zlaccel5",
        "col_idx": 29
    },{
        "text": "zori5",
        "col_idx": 30
    }
]

@main.route('/')
@cache.cached(timeout=1000)
def home():
    return render_template('index.html')

@main.route("/select", methods=["GET", "POST"])
def select():
    global cur_file_name
    global cur_file_path

    form = SelectForm()

    if form.validate_on_submit():
        data_file = request.files['data_file']
        cur_file_name = secure_filename(data_file.filename)
        cur_file_path = os.path.join(UPLOAD_PATH, cur_file_name)
        data_file.save(cur_file_path)

        flash("Uploaded successfully.", "success")
        return redirect(url_for(".analyze"))

    return render_template("select.html", form=form)


@main.route("/analyze", methods=["GET"])
def analyze():
    if (cur_file_name == "current file name"):
        return redirect(url_for(".select"))
    #with open(cur_file_path, 'rb') as data_file:
    #    rows = csv.reader(data_file, delimiter=' ', quotechar='|')
    #    for row in rows:
    #        row[0]
    df = read_csv(cur_file_path)

    return render_template("analyze.html", cur_file_name=cur_file_name, columns=col_dict)


# ---------------------------------------------------------------
@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user)

        flash("Logged in successfully.", "success")
        return redirect(request.args.get("next") or url_for(".home"))

    return render_template("login.html", form=form)


@main.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")

    return redirect(url_for(".home"))


@main.route("/restricted")
@login_required
def restricted():
    return "You can only see this if you are logged in!", 200
