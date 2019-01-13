from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required

from analyzeapp.extensions import cache
from analyzeapp.forms import LoginForm, SelectForm
from analyzeapp.models import User

from werkzeug import secure_filename

import os
import csv
from pandas import *

from math import ceil, floor
from statistics import stdev


main = Blueprint('main', __name__)

UPLOAD_PATH = "./uploads/"
EXPORT_PATH = "./exports/"
data_to = {
    "columns_meta" :[
        {
            "text": "timestamp",
            "col_idx": 0
        },
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
}


data_dict = {}

class DataFile:
    def __init__(self, file):
        self.data_cols = []
        self.file = file
        self.data_frame = None

    def read(self):
        self.data_frame = read_csv(self.file, skiprows=1)
        self.data_cols = []
        for col in range(31):
            self.data_cols.append(self.data_frame[str(col)].tolist())

        self.data_frame = self.data_frame.set_index(str(0))



@main.route('/')
@cache.cached(timeout=1000)
def home():
    return render_template('index.html')

@main.route("/select", methods=["GET", "POST"])
def select():
    global data_dict

    form = SelectForm()

    if form.validate_on_submit():
        data_file = request.files.getlist('data_file')

        for f in data_file:
            if f.filename.endswith(".csv"):
                cur_file_name = secure_filename(f.filename)
                if not cur_file_name in data_dict:
                    cur_file_path = os.path.join(UPLOAD_PATH, cur_file_name)
                    f.save(cur_file_path)
                    data_dict[cur_file_name] = DataFile(cur_file_path)

        # flash("Uploaded successfully.", "success")
        return redirect(url_for(".analyze"))

    return render_template("select.html", form=form)


@main.route("/analyze", methods=["GET"])
def analyze():
    global data_dict

    #for file in os.listdir(UPLOAD_PATH):
    #    if file.endswith(".csv"):
    #        if not file in data_dict:
    #            data_dict[file] = DataFile(file)

    if not data_dict:
        return redirect(url_for(".select"))

    #with open(cur_file_path, 'rb') as data_file:
    #    rows = csv.reader(data_file, delimiter=' ', quotechar='|')
    #    for row in rows:
    #        row[0]

    return render_template("analyze.html", files=list(data_dict.keys()), cols_meta=data_to)

@main.route("/getinfo", methods=["GET"])
def get_info():
    global data_dict

    file = request.args.get("file")
    xstart = floor(float(request.args.get("xstart")))
    xend = ceil(float(request.args.get("xend")))
    col_idx = int(request.args.get("col_idx"))

    data_cols = get_data_cols(file)
    data = data_cols[col_idx][xstart: xend+1]

    avg = sum(data) / len(data)
    cnt = 0
    for i in range(xstart + 1, xend):
        if (data_cols[col_idx][i] <= avg and data_cols[col_idx][i - 1] > avg) or (
                data_cols[col_idx][i] >= avg and data_cols[col_idx][i - 1] < avg):
            cnt += 1
    df = floor(cnt / 2) / (data_cols[0][xend-1] - data_cols[0][xstart])

    return jsonify({
        "stdev": round(stdev(data),3),
        "p2p": max(data) - min(data),
        "median": round(sum(data) / len(data), 3),
        "df": cnt/2,
        "xstart": int(xstart),
        "xend": int(xend)
    })

def get_data_cols(file):
    if not data_dict[file].data_cols:
        data_dict[file].read()
    return data_dict[file].data_cols

def get_data_frame(file):
    if not data_dict[file].data_cols:
        data_dict[file].read()
    return data_dict[file].data_frame

@main.route("/getdata", methods=["GET"])
def get_data():
    global data_dict

    file = request.args.get("file")
    col_idx = int(request.args.get("col_idx"))

    if file in data_dict:
        data = get_data_cols(file)[col_idx]

        return jsonify({
            "status": "success",
            "data": data
        })
    else:
        return jsonify({
            "status": "fail"
        })

@main.route("/exportdata", methods=["GET"])
def export_data():

    exportname = request.args.get("exportname")
    file = request.args.get("file")
    xstart = floor(float(request.args.get("xstart")))
    xend = ceil(float(request.args.get("xend")))
    col_idx = int(request.args.get("col_idx"))
    this_only = True if (request.args.get("this_only")) == "true" else False

    data_frame = get_data_frame(file)

    if this_only:
        data = data_frame[str(col_idx)][xstart: xend+1]
        path = os.path.join(EXPORT_PATH, exportname)
        data = data.reset_index()
        data = data.set_index(str(0))
        data.to_csv(path)
    else:
        data = data_frame[xstart: xend+1]
        path = os.path.join(EXPORT_PATH,exportname)
        data.to_csv(path)

    # flash("Successfully saved to " + path, "success")

    return jsonify({
        "status": "success",
        "file": path
    })



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
