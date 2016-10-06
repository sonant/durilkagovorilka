# -*- coding: utf-8 -*-

from flask import Flask,  request, render_template, redirect
import os, requests, hashlib, sys, datetime

app = Flask(__name__)

_cwd = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET','POST'])
def index():    
      return "0"

@app.route('/run', methods=['GET','POST'])
def run():
		f=open("/durilka/acsour.log","a+")
		f.write(request.values['name'])
		f.close()
		return "0"

app.config['ASSETS_DEBUG'] = True
app.debug = False

#app.run(host='0.0.0.0', port=4141, debug=True)
