import requests
import json
import dw_util
import constants
import config
import websocket
import logging
import urllib
import subprocess
from omxplayer import OMXPlayer
import sqlite3

connection = sqlite3.connect('dwplayer.db')
cursor = connection.cursor()

def register():
    #check for device registration
    cursor.execute('SELECT registrationID,deviceID FROM player')
    row = cursor.fetchone()
    print row
    if row == None :
        #get device unique id
        uid = dw_util.getserial()
        #make a
        data = {'deviceID':str(uid)}
        url='{}{}'.format(config.api_endpoint,constants.ENDPOINT_REGISTER)
        logging.debug('{}-{}'.format(__file__,'register',url))
        response = requests.post(url, json.dumps(data))
        if response.status_code==200:
                payload = response.json()
                logging.debug('{}-{}'.format(__file__,'register',payload))
                cursor.execute('INSERT INTO player(registrationID,deviceID) VALUES(?,?)',(payload.get('registrationID'),payload.get('deviceID')))
                connection.commit()
                return payload.get('registrationID')
        else:
                raise Exception('something went wrong during device registration')
    else:
        return row[0]
        

def on_message(ws, message):
    print(type(message), message)
    payload = json.loads(message)
    cursor.execute('INSERT INTO log(event,rawResponse) VALUES(?,?)',(payload.get('type'),message))
    connection.commit()
    if payload.get('type') == 'PLAYERCREATED' or payload.get('type') == 'PLAYERUPDATED':
        get_campaign_details('DEFAULT',payload.get('campID'))
    if payload.get('type') == 'SCHEDULECREATED' or payload.get('type') == 'SCHEDULEUPDATED':
        get_schedule_details(payload.get('clientID'),payload.get('scheduleID'))

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### connection closed ###")

def connect(registrationID):
    websocket.enableTrace(True)
    socket_url = config.socket_endpoint+constants.ENDPOINT_SOCKET+"?room="+registrationID
    ws = websocket.WebSocketApp(socket_url,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.run_forever()


def get_campaign_details(clientID,campaignID):
    headers = {'clientID':clientID}
    print(config.api_endpoint+constants.ENDPOINT_CAMPAIGN + campaignID + r'?outputFilters={"layout":1}',clientID)
    response = requests.get(config.api_endpoint+constants.ENDPOINT_CAMPAIGN + campaignID + r'?outputFilters={"layout":1}', headers=headers)
    payload = response.json()
    logging.debug(payload)
    layout = payload.get('layout')
    channels = layout.get('channels')
    for channel in channels:
        for asset in channel.get('assets'):
            asset_extension = asset.get('url').split('.')[-1]
            logging.debug('Initiating download of asset : {}'.format(asset.get('_id')))
            file_url = '{}/{}'.format('assets',asset.get('_id')+'.'+asset_extension)
            urllib.urlretrieve(asset.get('url'),file_url,download_report)
            logging.debug('Download completed of asset : {}'.format(asset.get('_id')))
            #player = OMXPlayer(file_url)
            #subprocess.call(['omxplayer','{}/{}_{}_{}'.format('assets','asset',asset.get('_id'),asset_name)])

def get_schedule_details(clientID,scheduleID):
    headers = {'clientID':clientID}
    response = requests.get(config.api_endpoint+constants.ENDPOINT_SCHEDULE + scheduleID + r'?outputFilters={"campaignId":1,"schedules":1}', headers=headers)
    payload = response.json()
    logging.debug(payload)
    get_campaign_details(clientID,payload.get('campaignId'))


def download_report(block_number,block_size,size):
    current = block_number * block_size
    logging.debug('{0:.2f}%'.format(100.0*current/size))

if __name__== "__main__":
    logging.basicConfig(level=logging.DEBUG)
    registrationID = register()
    logging.debug(registrationID)
    connect(registrationID)
