# -*- coding: utf-8 -*-

import os
import sys,pika,pjsua,threading,wave,json
from time import sleep
import pymongo

def log_cb(level, str, len):
    print str

class MyAccountCallback(pjsua.AccountCallback):
    sem = None

    def __init__(self, account=None):
        pjsua.AccountCallback.__init__(self, account)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

def cb_func(pid):
    print '%s playback is done' % pid
    current_call.hangup()

# Callback to receive events from Call
class MyCallCallback(pjsua.CallCallback):
    file=''
    def __init__(self, call=None,file=None):
        pjsua.CallCallback.__init__(self, call)
        self.file="/tmp/"+file+".wav"
    # Notification when call state has changed
    def on_state(self):
        global current_call
        global in_call
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

        if self.call.info().state == pjsua.CallState.DISCONNECTED:
            current_call = None
            print 'Current call is', current_call
            in_call = False

        elif self.call.info().state == pjsua.CallState.CONFIRMED:
            try:
				wfile = wave.open(self.file)
				time = (1.0 * wfile.getnframes()) / wfile.getframerate()
				wfile.close()
				call_slot = self.call.info().conf_slot
				self.wav_player_id = pjsua.Lib.instance().create_player(str(self.file), loop=False)
				self.wav_slot = pjsua.Lib.instance().player_get_slot(self.wav_player_id)
				pjsua.Lib.instance().conf_connect(self.wav_slot, call_slot)
				sleep(time)
				pjsua.Lib.instance().player_destroy(self.wav_player_id)
				self.call.hangup()
				os.remove(str(self.file))
				in_call = False
            except pjsua.Error, e:
				ch.basic_ack(delivery_tag=method.delivery_tag)
				print "Exception: " + str(e)

    def on_media_state(self):
        if self.call.info().media_state == pjsua.MediaState.ACTIVE:
            print "Media is now active"
        else:
            print "Media is inactive"

def callback(ch, method,properties,body):
    global in_call
    o = json.loads(body)
    in_call = True
    lck = lib.auto_lock()
    try:
        acc.make_call('sip:' + str(o['phone_number']) + '@sip.zadarma.com', cb=MyCallCallback(None,o['file']))
    except pjsua.Error, e:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print "Exception: " + str(e)
    del lck
    while in_call:
        pass
    ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__=="__main__":
    rabbitmq = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = rabbitmq.channel()
    channel.queue_declare(queue='WAV')
    channel.basic_consume(callback,queue='WAV')
    flag=0
    try:
        lib = pjsua.Lib()
        lib.init(log_cfg=pjsua.LogConfig(level=0, callback=log_cb))
        lib.create_transport(pjsua.TransportType.UDP, pjsua.TransportConfig(5080))
        lib.set_null_snd_dev()
        lib.start()
        lib.handle_events()

        acc_cfg = pjsua.AccountConfig()
        acc_cfg.id = ""
        acc_cfg.reg_uri = "sip:sip."
        acc_cfg.auth_cred = [pjsua.AuthCred("", "", "")]

        acc_cb = MyAccountCallback()
        acc = lib.create_account(acc_cfg, cb=acc_cb)

        acc_cb.wait()

        print "\n"
        print "Registration complete, status=", acc.info().reg_status, \
            "(" + acc.info().reg_reason + ")"
    except pjsua.Error, e:
        print "Exception: " + str(e)
    channel.start_consuming()