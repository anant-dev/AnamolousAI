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

# column_names = ['Beneficiary gender code','Beneficiary Age category code','Base DRG code','ICD9 primary procedure code','Inpatient days code','DRG quintile average payment amount','DRG quintile payment amount code']

app=Flask(__name__, template_folder = 'template')
app.config['UPLOAD_EXTENSIONS'] = ['.csv']
app.config['UPLOAD_PATH'] = 'uploads'



@app.route("/index")
def index():
 return flask.render_template("index.html")

def ValuePredictor(to_predict_list, column_names):
    to_predict = np.array(to_predict_list).reshape(1,7)
    to_predict = pd.DataFrame(data = to_predict, columns = column_names)
    loaded_model = pickle.load(open("rf.pkl","rb"))
    result = loaded_model.predict(to_predict)
    return result[0]

@app.route("/predict/<string:n>",methods = ["GET"])
def result(n):
  response = []
  # file_path = request.json['file_path']
  file_path = os.path.join(app.config['UPLOAD_PATH'], n)
  with open(file_path, 'r') as read_obj:
    csv_reader = reader(read_obj)
    column_names = next(csv_reader)
    print(column_names)
    response.append({
      'Header': column_names
    })
    count = 0
    for row in csv_reader:
      print(row[1:])
      if(count < 500):
        count= count + 1
        result = ValuePredictor(row[1:], column_names[1:])
        if(result == 1):
          print(result)
          response.append({
            'values': row,
            'prediction': str(result)
          })
  return jsonify({'result': response})

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