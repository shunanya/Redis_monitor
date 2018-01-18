# Declaration of monitor constants
HOST='server_host'       # monitored server host (replace by specific data)
REDIS_MONITOR='127.0.0.1' # node server monitor host
REDIS_PASSWD=None
REDIS_DB='db0'

APIKEY='2K3GF.....VG9SE8'	# replace by your APIKEY
SECRETKEY='LLTS....949TE'	# replace by your SECRETKEY

NAME='RedisCache'
MONITOR_NAME=NAME+'_'+HOST    # name of custom monitor
MONITOR_TAG='REDIS_engine'    # tag for custom monitor
MONITOR_TYPE='Python'   # type for custom monitor
MULTIVALUE='true'

MONITOR_ID=0


# format of result params - name1:displayName1:uom1:Integer
# name, displayName, uom and value should be URL encoded.
#UOM is unit of measure(user defined string parameter, e.g. ms, s, kB, MB, GB, GHz, kbit/s, ... ).
#
#dataType:   1 for boolean    2 for integer    3 for string    4 for float
#

P0='port:port::3:true;status:status::3;total_connections_received:connections::2;connected_clients:clients::2;'
P1='used_memory:memory::4;mem_fragmentation_ratio:fragmentation::4;used_cpu:cpu::4;'
P2='instantaneous_ops_per_sec:ops::4;'
P3='keys:keys::2;expired_keys:expired::2;evicted_keys:evicted::2;keyspace_misses:misses::2'
RESULT_PARAMS=str(P0)+str(P1)+str(P2)+str(P3)

OK_STATE='OK'
NOK_STATE='NOK'

# format of additional params - name:displayName:uom:String
ADDITIONAL_PARAMS='details:Details::3'
ARESP_DOWN='[{details:DOWN}]'

DURATION=5                         # information sending duration [min] (REPLACE by any desired value)
