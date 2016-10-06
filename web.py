# -*- coding: utf-8 -*-

from flask import Flask, session, escape, request,render_template, session, redirect
import os, requests, hashlib, sys, pika, json,datetime
from pymongo import MongoClient
from vk import *




app = Flask(__name__)

_cwd = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET','POST'])
def index():
	if is_iframe():
		users= db.users
		user = users.find({'user_id':request.values['viewer_id']})
		if user.count()==0:
			user = {
				'user_id': request.values['viewer_id'],
				'valet':0
			}
			try:
				users.insert_one(user)
			except:
				print "Error!"
		if request.method=='POST':
			if ('message' and 'phone_number') in request.form:
				data = {
					'txt':request.form['message'],
					'phone_number':request.form['phone_number']
				}
				message = json.dumps(data)
				rabbitmq = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
				channel = rabbitmq.channel()
				channel.queue_declare(queue='TXT')
				channel.basic_publish(exchange='', routing_key='TXT', body=message)
				rabbitmq.close()
				
				msg = db.msg
				msg.insert_one({
					'phone_number':request.form['phone_number'],
					'txt':request.form['message'],
					'datetime':datetime.datetime.now().strftime("%d.%m.%Y %I:%M %p"),
					'user_id':user[0]['user_id']
				})				
				
		return render_template("main.html", data = user[0])
	return "0"
	
@app.route('/vk_back', methods=['GET','POST'])
def vk_back():
	if 'sig' in request.values:
		if sig_check():
			if request.values['notification_type']=='order_status_change_test':
				if request.values['status']=='chargeable':
					ret = {
						'response':{
							'order_id':int(request.values['order_id']),
							'app_order_id': int(123412)
						}}
					return json.dump(ret)
		else:
			return json.dump(vk_error_10)
	else:
		return "0"
				
	
@app.route('/d4958543cac7.html', methods=['GET'])
def r():
    return render_template("r.html")
	
app.config['ASSETS_DEBUG'] = True
app.debug = True

mongo = MongoClient(connect=False)
db = mongo.test_db

#app.run(host='0.0.0.0', port=4141, debug=True)
