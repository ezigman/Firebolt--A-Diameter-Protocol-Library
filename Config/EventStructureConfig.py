import os
import sys

eventTypes = ['VOICE', 'SMS', 'GPRS', 'VAS']

eventTypeConfig = {
                    'CER'   : {
                                'CommandCode' : 257,
                                'Runnable' : False,              ## options :- True/False
                                'Mode'     : 'online',           ## options :- online/offline
                                'Host'     : os.environ['HOST'],
                                'Port'     : 34311,
                                'ReceiveTO': 5,
                                'AurorMapping'       : False,    ## options :- True/False
                                'InputFileLocation'  : os.environ['HOME'] + "/firebolt/VoiceEvents.evt",
                                'OutputFileLocation' : os.environ['HOME'] + "/firebolt/EventFiles"
                              },
                    'VOICE' : {
                                'CommandCode' : 272,
                                'Runnable' : True,              ## options :- True/False
                                'Mode'     : 'offline',         ## options :- online/offline
                                'Host'     : os.environ['HOST'],
                                'Port'     : 54321,
                                'ReceiveTO': 5,
                                'AurorMapping'       : False,    ## options :- True/False
                                'InputFileLocation'  : os.environ['HOME'] + '/firebolt/VoiceEvents.evt',
                                'OutputFileLocation' : os.environ['HOME'] + "/firebolt/EventFiles"
                              },
                    'SMS'   : {
                                'CommandCode' : 272,
                                'Runnable' : False,             ## options :- True/False
                                'Mode'     : 'offline',         ## options :- online/offline
                                'Host'     : os.environ['HOST'],
                                'Port'     : 54321,
                                'ReceiveTO': 5,
                                'AurorMapping'       : False,    ## options :- True/False
                                'InputFileLocation'  : os.environ['HOME'] + "/firebolt/SMSEvents.evt",
                                'OutputFileLocation' : os.environ['HOME'] + "/firebolt/EventFiles"
                              },
                    'GPRS'  : {
                                'CommandCode' : 272,
                                'Runnable' : False,             ## options :- True/False
                                'Mode'     : 'offline',         ## options :- online/offline
                                'Host'     : os.environ['HOST'],
                                'Port'     : 54321,
                                'ReceiveTO': 5,
                                'AurorMapping'       : False,    ## options :- True/False
                                'InputFileLocation'  : os.environ['HOME'] + "/firebolt/GPRSEvents.evt",
                                'OutputFileLocation' : os.environ['HOME'] + "/firebolt/EventFiles"
                              },
                    'VAS'   : { 
                                'CommandCode' : 272,
                                'Runnable' : False,             ## options :- True/False
                                'Mode'     : 'offline',         ## options :- online/offline
                                'Host'     : os.environ['HOST'],
                                'Port'     : 54321,
                                'ReceiveTO': 5,
                                'AurorMapping'       : False,    ## options :- True/False
                                'InputFileLocation'  : None,
                                'OutputFileLocation' : os.path.dirname(os.path.abspath(__file__))
                              }
                  }

##------------------------------------------------------------------------------------------------------------------------------------------------

eventStructure = dict()

eventStructure['CER'] = \
{
    'Origin-Host' : '10.193.201.50',
    'Origin-Realm': 'amdocs.com',
    'Auth-Application-Id' : 4,
    'Firmware-Revision'   : 113,
    'Host-IP-Address'     : '10.193.201.50',
    'Origin-State-ID'     : 5333,
    'Product-Name'        : 'EricssonJ20GGSN',
    'Vendor-ID' : 193,
    'Result-Code': 0
}

eventStructure['VOICE'] = \
{
    'Resource-Type'   : 3,
    'Resource-Type-PP1' : '3',
    'Resource-Value'  : '45483',
    'Resource-Value-PP1': '111',
    'Event-Start-Time-PP1':'123543344',
    'Event-Start-Time': 1375952749,
    'Session-ID'      : 'amdocs.optus',
    'Usage-ID'        : 12,
    'Usage-ID-PP1'    : '122',
    'Called-Number-PP1': '34342323',
    'Usage-Event-Type': 'Duration',
    'Called-Number'   : '46578658',
    'Calling-Number'  : '3458390569',
    'Calling-Number-PP1':'34453232',
    'Duration'        : 10,
    'Duration-PP1'    : '11',
    'CC-Request-Type' : 3,
    'CC-Request-Number':1,
    'User-Session-Id' : '123',
    'Message-Id'      : '456',
    'Interface-Id'    : '999',
    'SMSC-Id'         : '777',
    'Class'	      : '111',
    'Billing-Class'   : 1,
    'A-Secondary-Time': '19',
    'A-Cell-Id'       : '9',
    'A-Downlink-Volume': 10,
    'A-Download-Volume-Text':'90',
    'A-Uplink-Volume-Text': '23',
    'A-Uplink-Volume' : 145,
    'A-provider-id-Text': '123',
    'A-Provider-Id'   : '1',
    'Token-Text'      : '34',
    'Interface-Text'  : 'interface',
    'Sponser-Identify': '9',
    'Charged-Amount-Text': '10',
    'Charged-Amount'  : 10,
    'A-Base-amount'   : '50',
    'A-Original-currency-charge-amount': 90,
    'A-Foreign-amount': '45',
    'A-Original-currency-tax-amount': 99,
    'A-Original-currency': '23',
    'OFCA-Recycle-Indicator': 'Y',
    'Physical-File-ID': '45',
    'Physical-File-Sequence':9,
    'TimeZone':'1'
}

eventStructure['SMS'] = \
{
    'Resource-Type'   : 3,
    'Resource-Type-PP1' : '3',
    'Resource-Value'  : '45483',
    'Resource-Value-PP1': '111',
    'Event-Start-Time-PP1':'123543344',
    'Event-Start-Time': 1375952749,
    'Session-ID'      : 'amdocs.optus',
    'Usage-ID'        : 12,
    'Usage-ID-PP1'    : '122',
    'Called-Number-PP1': '34342323',
    'Usage-Event-Type': 'Occurance',
    'Called-Number'   : '46578658',
    'Calling-Number'  : '3458390569',
    'Calling-Number-PP1':'34453232',
    'Duration'        : 10,
    'Duration-PP1'    : '11',
    'CC-Request-Type' : 3,
    'CC-Request-Number':1,
    'User-Session-Id' : '123',
    'Message-Id'      : '456',
    'Interface-Id'    : '999',
    'SMSC-Id'         : '777',
    'Class'           : '111',
    'Billing-Class'   : 1,
    'A-Secondary-Time': '19',
    'A-Cell-Id'       : '9',
    'A-Downlink-Volume': 10,
    'A-Download-Volume-Text':'90',
    'A-Uplink-Volume-Text': '23',
    'A-Uplink-Volume' : 145,
    'A-provider-id-Text': '12',
    'A-Provider-Id'   : '1',
    'Token-Text'      : '12',
    'Interface-Text'  : 'interface',
    'Sponser-Identify': '9',
    'Charged-Amount-Text': '10',
    'Charged-Amount'  : 10,
    'A-Base-amount'   : '50',
    'A-Original-currency-charge-amount': 90,
    'A-Foreign-amount': '45',
    'A-Original-currency-tax-amount': 99,
    'A-Original-currency': '23',
    'OFCA-Recycle-Indicator': 'Y',
    'Physical-File-ID': '45',
    'Physical-File-Sequence':9,
    'TimeZone':'1'
}

eventStructure['GPRS'] = \
{
    'Resource-Type'   : 3,
    'Resource-Type-PP1' : '3',
    'Resource-Value'  : '45483',
    'Resource-Value-PP1': '111',
    'Event-Start-Time-PP1':'123543344',
    'Event-Start-Time': 1375952749,
    'Session-ID'      : 'amdocs.optus',
    'Usage-ID'        : 12,
    'Usage-ID-PP1'    : '122',
    'Called-Number-PP1': '34342323',
    'Usage-Event-Type': 'Volume',
    'Called-Number'   : '46578658',
    'Calling-Number'  : '3458390569',
    'Calling-Number-PP1':'34453232',
    'Duration'        : 10,
    'Duration-PP1'    : '11',
    'CC-Request-Type' : 3,
    'CC-Request-Number':1,
    'User-Session-Id' : '123',
    'Message-Id'      : '456',
    'Interface-Id'    : '999',
    'SMSC-Id'         : '777',
    'Class'           : '111',
    'Billing-Class'   : 1,
    'A-Secondary-Time': '19',
    'A-Cell-Id'       : '9',
    'A-Downlink-Volume': 10,
    'A-Download-Volume-Text':'90',
    'A-Uplink-Volume-Text': '23',
    'A-Uplink-Volume' : 145,
    'A-provider-id-Text': '12',
    'A-Provider-Id'   : '1',
    'Token-Text'      : '12',
    'Interface-Text'  : 'interface',
    'Sponser-Identify': '9',
    'Charged-Amount-Text': '10',
    'Charged-Amount'  : 10,
    'A-Base-amount'   : '50',
    'A-Original-currency-charge-amount': 90,
    'A-Foreign-amount': '45',
    'A-Original-currency-tax-amount': 99,
    'A-Original-currency': '23',
    'OFCA-Recycle-Indicator': 'Y',
    'Physical-File-ID': '45',
    'Physical-File-Sequence':9,
    'TimeZone':'1'
}
