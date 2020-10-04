# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 01:43:00 2020

@author: Dell
"""
import pandas as pd
import numpy as np
import flask
import pickle
import os
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from werkzeug.utils import secure_filename
from csv import reader


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# column_names = ['Beneficiary gender code','Beneficiary Age category code','Base DRG code','ICD9 primary procedure code','Inpatient days code','DRG quintile average payment amount','DRG quintile payment amount code']
default_column_names = [
    "Encrypted PUF ID",
    "DRG quintile payment amount code",
    "DRG quintile average payment amount",
    "Inpatient days code",
    "ICD9 primary procedure code",
    "Base DRG code",
    "Beneficiary Age category code",
    "Beneficiary gender code"
]
app = Flask(__name__, template_folder='template')
app.config['UPLOAD_EXTENSIONS'] = ['.csv']
app.config['UPLOAD_PATH'] = 'uploads'


@app.route("/index")
def index():
    return flask.render_template("index.html")

# method to predict if a set of entries is an anomaly or not


def ValuePredictor(to_predict_list, column_names):
    to_predict = np.array(to_predict_list).reshape(1, 7)
    to_predict = pd.DataFrame(data=to_predict, columns=column_names)
    loaded_model = pickle.load(open("rf.pkl", "rb"))
    result = loaded_model.predict(to_predict)
    return result[0]

# route controller to initiate prediction


@app.route("/predict/<string:n>", methods=["GET"])
def result(n):
    response = []
    incorrect_values = []
    # uploaded file path
    file_path = os.path.join(app.config['UPLOAD_PATH'], n)

    with open(file_path, 'r') as read_obj:
        csv_reader = reader(read_obj)
        column_names = next(csv_reader)
        if(default_column_names == column_names):
            response.append({
                'Header': column_names
            })
            for row in csv_reader:
                # print(row)
                isValid = True
                for i in range(1, len(column_names)):
                    if (column_names[i] == 'Beneficiary gender code') and (1 > int(row[i]) or int(row[i]) > 2):
                        isValid = False
                        incorrect_values.append({
                            'values': row,
                            'error': 'Beneficiary gender code not correct'
                        })
                    elif (column_names[i] == 'Beneficiary Age category code') and (1 > int(row[i]) or int(row[i]) > 6):
                        isValid = False
                        incorrect_values.append({
                            'values': row,
                            'error': 'Beneficiary Age category code not correct'
                        })
                    elif (column_names[i] == 'Base DRG code') and (1 > int(row[i]) or int(row[i]) > 311):
                        isValid = False
                        incorrect_values.append({
                            'values': row,
                            'error': 'Base DRG code code not correct'
                        })
                    elif (column_names[i] == 'ICD9 primary procedure code') and (0 > int(row[i]) or int(row[i]) > 99):
                        isValid = False
                        incorrect_values.append({
                            'values': row,
                            'error': 'ICD9 primary procedure code not correct'
                        })
                    elif (column_names[i] == 'Inpatient days code') and (1 > int(row[i]) or int(row[i]) > 4):
                        isValid = False
                        incorrect_values.append({
                            'values': row,
                            'error': 'Inpatient days code not correct'
                        })

                if isValid:
                    print(row)
                    result = ValuePredictor(row[1:], column_names[1:])
                    if(result == 1):
                        response.append({
                            'values': row,
                            'prediction': str(result)
                        })
            return jsonify({'result': response, 'incorrect_entries': incorrect_values})
        else:
            raise InvalidUsage("Columns mismatch, please check the required colums: - Encrypted PUF ID, DRG quintile payment amount code, DRG quintile average payment amount, Inpatient days code, ICD9 primary procedure code, Base DRG code, Beneficiary Age category code, Beneficiary gender code", status_code=403)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    print(filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
        print('file path made')
        print(file_path)
        uploaded_file.save(file_path)
    return jsonify({'file_path': filename})


if __name__ == "__main__":
    app.run(debug=True)
