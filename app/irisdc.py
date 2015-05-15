#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# irisdc.py

""" Fetches data form a Google Spreadsheet and calculates different variables. """

import argparse
import csv
import json
import sys
import queue
import os
import requests
import mistune

from oauth2client.client import SignedJwtAssertionCredentials
from flask import Flask, jsonify, request, render_template, send_from_directory
from hamlish_jinja import HamlishExtension
from flask.ext.assets import Environment, Bundle


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

app.jinja_env.filters['env'] = os.getenv

app.jinja_env.add_extension(HamlishExtension)

assets = Environment(app)
assets.url = app.static_url_path

css_bundle = Bundle('css/home.css.scss', filters="scss", output='css/all.css')
assets.register('css_all', css_bundle)

#js_bundl = Bundle('js/home.js.coffe', filters='coffescript', output='all.js')
#assets.register('js_all', js_bundle)

@app.route('/visualiza-tus-resultados')
def form():
    return render_template("form.html.haml")

@app.route('/', methods=['POST'])
def form_post():

    url = request.form['url']
    call_url = 'http://powerful-oasis-7324.herokuapp.com/api/response?url="'+ url+ '"'
    request_url = requests.get(call_url)
    graphdata = request_url.json()['data']
    graphjson = json.dumps(graphdata)
    graphjson = graphjson
    return render_template("graph.html.haml", graphjson= graphjson)

@app.route('/')
def get_que_es_iris():
    file = open("app/static/content/index.md")
    content = mistune.markdown(file.read())
    return render_template("md.html.haml", title="Inicio", content=content)

@app.route('/contesta-iris')
def get_como_contestar_iris():
    file = open("app/static/content/como-contestar-iris.md")
    content = mistune.markdown(file.read())
    return render_template("md.html.haml", title="Contesta IRIS", content=content)

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

if __name__ == '__main__':
	app.run(debug=True, threaded=True)
