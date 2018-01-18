#!/usr/bin/env python

import json, urllib
import commands, subprocess
import redis
import monitor_constants as constants
from common import logger

rclients = {} 

def getRedis(port):
    global rclients
    r = rclients.get(port, None)
    if not isinstance(r, redis.Redis) or r.ping() != 'PONG':
        r = redis.Redis(host=constants.REDIS_MONITOR, port=int(port), db=0, password=constants.REDIS_PASSWD)
        rclients[port] = r        
    return r
    
def measure():
    ''' Prepare the metrics pattern '''
    prev = None
    stats = {}
    for s in (constants.RESULT_PARAMS).split(";") :
        key = s.split(':',1)[0]
        stats[key] = []
    stats['additionalResults'] = []
#    logger.info("Collected statistics: %s", json.dumps(stats))
    p = subprocess.Popen("ps -ef | grep -v grep | grep  -o 'redis-server.*:[0-9]*' | awk -F ':' '{print $2}'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = p.stdout.readlines()
    if not isinstance(lines, list) or len(lines) == 0:
        e = 'There is not any running instance of Redis.'
        logger.critical(e)
        stats['status'].append(constants.NOK_STATE)
        details={'details':str(e)}
        details = urllib.quote(json.dumps(details), '{}')
        stats['additionalResults'].append([details])
    else:
        for line in lines:
            st = {}
            for key in stats:
                st[key] = ''
            st['additionalResults'] = []
            port = line.strip()
            st['port'] = str(port)
            redis_info = ''
            try:
                r = getRedis(port)
                if not isinstance(r, redis.Redis):
                    logger.error("Cannot establish connection to Redis")
                else:
                    redis_info = r.info()
                    prev = r.get('rm_prev')
                    if (isinstance(prev, basestring)) :
                        prev = json.loads(prev)
            except Exception as e :
                logger.critical(e)
                st['status'] = constants.NOK_STATE
                details={'details':str(e)}
                details = urllib.quote(json.dumps(details), '{}')
                st['additionalResults'].append(details)
            else :        
                if(constants.REDIS_DB in redis_info):
                    db_info = redis_info[constants.REDIS_DB]
                    for k in db_info:
                        if(k in stats):
                            st[k] = db_info[k]
                            
                pid = str(redis_info['process_id'])
                cm = commands.getoutput('ps -p'+pid+' -o %cpu,%mem  | grep -v % ') 
                rr = cm.strip().replace('  ',' ').split(' ', 2);
                cpu_pr=float(rr[0])
                mem_pr=float(rr[1])
                ''' Collect measured values '''
                for k, v in st.iteritems():            
                    if k == 'used_memory' :
                        v = mem_pr
                    elif k == 'used_cpu' :
                        v = cpu_pr
                    elif k == 'status' :
                        v = constants.OK_STATE
                    elif(k in redis_info) :
                        v = redis_info[k]
                    st[k] = v
                
                r.set('rm_prev', json.dumps(st)) # keep as previous value
                details={'details':' Redis-'+str(redis_info['redis_version'])+'-'+st['port']+' ('+str(redis_info['process_id']) +') '+' Uptime: '+_toDate(redis_info['uptime_in_seconds'])}
                details = urllib.quote(json.dumps(details), '{}')
                st['additionalResults'].append(details)
            
            ''' Convert to API required form '''
            for k, v in st.iteritems():
                if (k == 'expired_keys' or k == 'evicted_keys' or k == 'keyspace_misses' or k == 'total_connections_received') :
                    if (isinstance(prev, dict) and (k in prev)) :
                        v = max(v - prev[k], 0)
#                        v = v - prev[k]
                    else :
                        v = 0
                stats[k].append(v)
       
    return_value=json.dumps(stats).replace('],', '];').lstrip('{').rstrip('}').replace('"', '').replace(' ', '').replace('}];[{', '}],[{')
    
    logger.info('Returns: '+str(return_value))
    logger.info('Stats: '+str(stats))
    return return_value

# 
#  Format a timestamp into the form 'x-hh:mm:ss'
#   
#   @param timestamp
#              the timestamp in sec
#   @returns formatted string
#  
def _toDate(timestamp):
    time = timestamp
    sec = (time%60)
    mins =((time/60)%60)
    hr = ((time/3600)%24)
    da = (time/86400)
    s = '%02u.%02u.%02u' % (hr, mins, sec)
    if (da > 0):
        s = str(da) + "-" + s; 
    return s;

if __name__ == '__main__':
    measure()