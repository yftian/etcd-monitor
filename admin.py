import etcd


client = etcd.Client(host='192.168.111.137',port=2379,
                     username='',password='')
# write instance cmd for start
# client.write('/cmds/redis/run', 'redis /opt/example/database/redis/redis.sif')
# client.write('/cmds/httpd/run', 'httpd /opt/examples/http-server/apache2-web-server/httpd.sif')

# read cmds for instance start
directory = client.get('/cmds')
for direct in directory.children:
    dirctDicts=[]
    instanceName = direct.key.split("/")[2]
    try:
        dirctDict = {}
        dirValue = client.read('/cmds/'+ instanceName + '/run').value
        dirctDict['instance_name'] = dirValue.split(' ')[0]
        dirctDict['sif'] = dirValue.split(' ')[1]
        # dirctDicts.append(dirctDict)
        print('dirctDict:' + dirctDict['instance_name'])
    except Exception as e:
        print(e)
    print(dirValue)

