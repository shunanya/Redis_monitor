import json
import time
import sys
import re
import fileinput
import monitor_constants as constants
from api import custom
from common import logger

class Monitor:
    __monitorId = constants.MONITOR_ID
    __api = custom.Custom(constants.APIKEY, constants.SECRETKEY)
    
    def __init__(self, monitorId = None):
        if monitorId != None:
            self.__monitorId = monitorId

    def prepareMonitor(self):
        logger.info('Prepare Monitor with parameters:\nname:\t%s\ntag:\t%s\ntype:\t%s\nduration:\t%s min\nmonitorID:\t%s'
                    , constants.MONITOR_NAME, constants.MONITOR_TAG, constants.MONITOR_TYPE, constants.DURATION, self.__monitorId)
        if self.__monitorId > 0:
            logger.info('Check correctness of monitor ID (%s)', self.__monitorId)
            try:
                info = self.__api.requestMonitorInfo(self.__monitorId)
            except Exception as e:
                logger.warning(e)
                info = None
            logger.info('Monitor info: %s', str(info))
            if info == None or not isinstance(info, dict) or not (info['name'] == constants.MONITOR_NAME and info['tag'] == constants.MONITOR_TAG):
                logger.warning('Incorrect monitor ID')
                self.__monitorId = 0
        if self.__monitorId <= 0:
            logger.info('Trying to get monitor info by name...')
            try:
                info = self.__api.requestMonitors(monitorName=constants.MONITOR_NAME, monitorTag=constants.MONITOR_TAG, monitorType=constants.MONITOR_TYPE)
            except Exception as e:
                logger.warning(e)
                info = None
            logger.info('monitorInfo: %s', str(info))
            if info and len(info) > 0 and isinstance(info, list) and isinstance(info[0], dict) and info[0]['id'] > 0:
                self.__monitorId = info[0]['id']
            else:
                logger.info('Monitor is not exist. Create a new one.')
                try:
                    info = self.__api.addMonitor(monitorName=constants.MONITOR_NAME, monitorTag=constants.MONITOR_TAG, monitorType=constants.MONITOR_TYPE, 
                            isMultiValue = constants.MULTIVALUE, resultParams = constants.RESULT_PARAMS, additionalResultParams = constants.ADDITIONAL_PARAMS)
                except Exception as e:
                    logger.warning(e) 
                    info = None
                logger.info('addMonitor: %s',str(info))           
                if not info :
                    return False         
                self.__monitorId = info['data']
        logger.info('monitor ID: %s', self.__monitorId) 
        if info and self.__monitorId > 0 :
            self.replaceInFile('./monitor_constants.py', 'MONITOR_ID=\d{1,}', 'MONITOR_ID='+str(self.__monitorId))
        return (self.__monitorId > 0)  
    
    def replaceInFile(self, replacedFile, searchRegExp, replaceBy):
        if replacedFile and searchRegExp and replaceBy :
            logger.info("Replace '"+str(constants.MONITOR_ID)+"' by '"+str(replaceBy)+"' in file '"+str(replacedFile)+"'")
            for line in fileinput.input(replacedFile, inplace=True):
                if re.match(searchRegExp, line) :
                    line = re.sub(searchRegExp,replaceBy, line)
#                    logger.info('Replaced')
                sys.stdout.write(line)
        
    def send(self, data):
        res, resa = self.compacting(data)
        now = int(time.time()*1000)
#        logger.info('Monitor results: %s', str(res))
        addResults = self.__api.addMonitorResults(self.__monitorId, now, res )
        if isinstance(addResults, dict):
            logger.info('Result.Response: %s', str(addResults))                      
        if 'error' in addResults :
            if addResults.get('errorCode', 0) == 4 : #Invalid or expired auth token
                logger.warn('Result.Response: %s; refresh token and try again..', str(addResults))
                self.__api.updateAuthToken()
                addResults = self.__api.addMonitorResults(self.__monitorId, now, res )
            else :
                logger.error('Undefined error: %s', str(addResults))
        logger.info('Result.Response: %s', json.dumps(addResults))            
        if isinstance(resa, basestring) and len(resa) > 2 and 'status' in addResults and addResults['status'] == 'ok' :
#           logger.info('addAdditionalResults: %s', json.dumps(resa))
            addResults = self.__api.addMonitorAdditionalResults(self.__monitorId, now, resa)
            logger.info('AdResult.Response: %s', json.dumps(addResults))
            
    def compacting(self, data):
        res = ""
        resa = []
        adParam = (constants.ADDITIONAL_PARAMS).split(":",2)[0]
        if not data == None and len(data) > 0 :
            l = data.rsplit("|", 2)
            res = l[0].strip()
            if len(l) > 1 and isinstance(l[1], basestring) :
                ll = l[1].split("+");
                if (len(ll) > 0) :
                    for val in ll:
                        resa.append({adParam : val.strip()})
            if not isinstance(res, basestring) :
                res = json.dumps(res).replace(" ","")
            resa = json.dumps(resa)
        else:
            logger.warn('Compaction: data is empty.')
        return res, resa
    
