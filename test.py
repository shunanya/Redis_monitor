#!/usr/bin/env python

import subprocess, json, urllib

p = subprocess.Popen("ps -ef | grep -v grep | grep  -o 'redis.*:[0-9]*' | awk -F ':' '{print $2}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
    print line,
retval = p.wait()

#prev="{'status': 'OK', 'total_connections_received': 8, 'evicted_keys': 0, 'connected_clients': 2, 'keyspace_misses': 1, 'keys': '', 'port': '6379', 'used_memory': 0.0, 'instantaneous_ops_per_sec': 0, 'mem_fragmentation_ratio': 2.66, 'used_cpu': 0.0, 'expired_keys': 0}"
prev='{"status": "OK"}'
print prev
print urllib.quote(prev, '{}')
if (isinstance(prev, basestring)) :
    prev = json.loads(prev)
print prev

