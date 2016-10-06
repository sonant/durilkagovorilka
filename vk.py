# -*- coding: utf-8 -*-

import os
from hashlib import md5
from flask import request

api_secret=''
api_id=''

vk_error_10 ={
						'error':{
							'error_code':10,
							'error_msg':'Несовпадение вычисленной и переданной подписи',
							'critical':True
						}
					}

def auth_key(viewer_id):
	return md5(api_id+'_'+viewer_id+'_'+api_secret).hexdigest()
	
def is_iframe():
	if 'auth_key' in request.values:
		if auth_key(request.values['viewer_id'])==request.values['auth_key']:
			return True
		else:
			return False
	else:
		return False

def sig_check():	
		s=''
		for key in sorted(request.values):
			if key!='sig':
				s =s+ key+'='+str(request.values['key'])
		if md5(s+api_secret).hexdigest()==request.values['sig']:
			return True
		else:
			return True
		
def order():	
	pass