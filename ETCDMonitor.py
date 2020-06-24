# -*- coding: utf-8 -*-
# !/usr/bin/python
import datetime
import time, sched
from spython.main import Client
import spython
import threading
import json
import etcd
import logging

s = sched.scheduler(time.time, time.sleep)
client = etcd.Client('192.168.111.137', port=2379, username='', password='')

# setting log level
logging.basicConfig(
    filename='sin.log',
    level=logging.WARNING,
    format='%(levelname)s:%(asctime)s:%(message)s'
)


# check instance status
def any_instance(instance_name):
    instance = Client.instances(instance_name, quiet=True)
    if type(instance) == spython.instance.Instance:
        return instance
    return None


# start instance
def get_instance(instanceDict):
    try:
        t_ins = Client.instance(image=instanceDict["image"],
                                name=instanceDict["ins_name"],
                                options=instanceDict["options"])
        return t_ins
    except Exception as e:
        logging.error(e)
        return None


def exec(instanceDict):
    try:
        # 检查instance是否在运行
        instance_name = instanceDict.get('instance_name')
        err_time = instanceDict.get('')
        if any_instance(instance_name):
            print('report working' + instance_name)
            # write status working
            client.write('/status/' + instance_name,'working',ttl=10)
        elif err_time < 10:  # errtime 小于 limit
            # start instance
            if get_instance(instanceDict):
                print('working' + instance_name)
                client.write('/status/' + instance_name,'working',ttl=10)
            else:
                logging.warning('fail start instance :',instance_name)
                instanceDict['err_time'] += 1
        else:  # fail start and errtime > 10
            client.write('/dead/' + instance_name)
            logging.warning(instance_name, 'instance dead')
    except Exception as e:
        logging.ERR(e)
        return False
    return True


def initConfig():
    try:
        with open("./servers.json", "r") as load_f:
            load_dict = json.load(load_f)
            sched = load_dict.get("sched")
            services = load_dict.get("servers")
            return sched, services
    except IOError:
        print("file does not exist")

def getdirct():
    dirctDicts = []
    try:
        directory = client.get('/cmds')
        for direct in directory.children:
            instanceName = direct.key.split("/")[2]
            dirctDict = {}
            dirValue = client.read('/cmds/' + instanceName + '/run').value
            dirctDict['instance_name'] = dirValue.split(' ')[0]
            dirctDict['sif'] = dirValue.split(' ')[1]
            dirctDicts.append(dirctDict)
        return dirctDicts
    except Exception as e:
        logging.error(e)


def run(inc, instances=[]):
    for instance in instances:
        a = threading.Thread(target=exec, args=(instance,))
        a.start()

    s.enter(inc, 0, run, (inc,instances,))
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("------------------------------------------------------------------------------")



instances = getdirct()
if __name__ == '__main__':
    print(instances)
    s.enter(0, 0, run, argument=(10,instances))
    s.run()