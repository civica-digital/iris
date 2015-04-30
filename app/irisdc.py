#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# irisdc.py

""" Fetches data form a Google Spreadsheet and calculates different variables. """

import argparse
import csv
import json
import sys
import queue
import requests
from oauth2client.client import SignedJwtAssertionCredentials
from flask import Flask, jsonify, request, render_template

import IrisDimmensionalCalculator


__author__ = "Codeando México"
__license__ = "GPL"
__version__ = "1.0"
__credits__ = "Miguel Salazar, Ricardo Alanis"
__maintainer__ = "Miguel Salazar"
__email__ = "miguel@codeandomexico.org"
__status__ = "Prototype"

app = Flask(__name__)
queue = queue.Queue()

@app.route('/')
def form():
    return render_template("form.html")

@app.route('/', methods=['POST'])
def form_post():

    url = request.form['url']
    call_url = 'http://powerful-oasis-7324.herokuapp.com/api/response?url="'+ url+ '"'
    request_url = requests.get(call_url)
    graphdata = request_url.json()['data']
    graphjson = json.dumps(graphdata)
    graphjson = graphjson
    return render_template("graph.html", graphjson= graphjson)

@app.route('/api/response', methods=['GET'])
def get_response():
	urldoc = request.args.get('url')
	stringurl = str(urldoc)
	iris = IrisDimmensionalCalculator.IrisDimmensionalCalculator(stringurl,queue)

	try:
		iris.start()
		iris_grade = queue.get()
	except:
		iris_grade = "Error de procesamiento"
	return jsonify({'data':[iris_grade]})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
	app.run(debug=True, threaded=True)