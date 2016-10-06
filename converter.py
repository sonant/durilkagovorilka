# -*- coding: utf-8 -*-
import sys,pika, hashlib, io, json,requests,os
reload(sys)
sys.setdefaultencoding("utf-8")

class apirequst:
    eid='2'#engine id
    lid='21' #language id
    vid='1'#voice id
    api=''
    acc=''
    secret =''
    apiurl=''
    ext='mp3'

    def __init__(self):
        self.apiurl=''

    def run(self,ch, method, properties,body):
        o = json.loads(body)
        cs=hashlib.md5(self.eid+self.lid+self.vid+o['txt']+self.ext+self.acc+self.api+self.secret).hexdigest()
        res = requests.post(self.apiurl,data={'EID':self.eid,'LID':self.lid,'VID':self.vid,'API':self.api,'ACC':self.acc,'EXT':self.ext,'TXT':o['txt'],'CS':cs})
        sample = io.open("/tmp/"+cs+".mp3",'wb')	
        sample.write(res.content)
        os.system("mpg123 -w /tmp/"+cs+".wav /tmp/"+cs+".mp3 > converter.log")
        os.remove("/tmp/"+cs+".mp3")
        data={
            'phone_number':o['phone_number'],
            'file':cs
        }
        message = json.dumps(data)
        channel.basic_publish(exchange='', routing_key='WAV', body=message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__=="__main__":
    rabbitmq = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = rabbitmq.channel()
    channel.queue_declare(queue='TXT')
    channel.queue_declare(queue='WAV')
    r=apirequst()
    channel.basic_consume(r.run,queue='TXT')
    channel.start_consuming()