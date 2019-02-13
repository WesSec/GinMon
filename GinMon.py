import argparse
import configparser
import json
import os
import sys
from time import strftime

import requests

# Ginlong output keys
gindict = {"1a": "DCVPV1",
           "1b": "DCVPV2",
           '1c': "DCVPV3",
           '1d': "DCVPV4",
           '1j': "DCCUR1",
           '1k': "DCCUR2",
           '1l': "DCCUR3",
           '1m': "DCCUR4",
           '1af': "ACVOL1",
           '1ag': "ACVOL2",
           '1ah': "ACVOL3",
           '1ai': "ACCUR1",
           '1aj': "ACCUR2",
           '1ak': "ACCUR3",
           '1ao': "ACWATT",
           '1ar': "ACFREQ",
           '1bd': "DAYGEN",
           '1be': "MONGEN",
           '1bf': "ANNGEN",
           '1bc': "TOTGEN",
           '1df': "INVTMP"}


# Functions

def CheckLogin():
    # Retrieve data from config
    print("Loading Config")
    username = config.get('Ginlong', 'username')
    password = config.get('Ginlong', 'password')
    InverterID = config.get('Ginlong', 'inverterID')
    print("Config Loaded, logging in")
    # Build login string
    url = BaseURL + "/cpro/login/validateLogin.json"
    params = {
        "userName": username,
        "password": password,
        "lan": "2",  # lan = 2 == English,
        "domain": "m.ginlong.com",
        "userType": "C"
    }
    r = session.post(url, params=params)
    rson = r.json()
    # Debug
    if rson['result'].get('isAccept') == 1:
        print("Login Succesfull!")
        return InverterID
    else:
        print("Login Failed!!")
        Exit()


def GetData(deviceID):
    url = "http://m.ginlong.com/cpro/device/inverter/goDetailAjax.json"
    params = {
        'deviceId': int(deviceID)
    }
    cookies = {'language': '2'}
    r = session.get(url, params=params, cookies=cookies)
    rson = r.json()
    return ParseData(rson)


def CheckActivity(updatetime):
    if not os.path.isfile('lastlog.txt'):
        wr = open("lastlog.txt", "w+")
        wr.write(str(updatetime))
    else:
        wr = open("lastlog.txt", 'r+')
        lastdata = wr.readline()
        if int(lastdata) == updatetime:
            print("No new data found on server, sun is probably down")
            Exit()
        else:
            wr.seek(0)
            wr.write(str(updatetime))
            wr.truncate()
            wr.close()


def ParseData(rson):
    # Parse all the data from the Json
    print(generation)
    if generation == 3:
        data = rson['result']['deviceWapper']['data']
    elif generation == 4:
        data = rson['result']['paginationAjax']['data']['data']
    else:
        print("wrong generation entered in config (must me 3 or 4)")
        Exit()
    d = json.loads(data)
    results = {}
    for line in d:
        try:
            results.update({gindict[line]: d[line]})
        except:
            pass
    if generation == 3:
        results.update({'Plantname': rson['result']['deviceWapper']['plantName']})  # Plantname
        results.update({'Updatetime': rson['result']['deviceWapper']['updateDate']})  # Last update (epoch)
    elif generation == 4:
        results.update({'Plantname': rson['result']['paginationAjax']['data']['name']})  # Plantname
        results.update({'Updatetime': rson['result']['paginationAjax']['data']['updateDate']})  # Last update (epoch)
    else:
        print("wrong generation entered in config (must me 3 or 4)")
        Exit()
    # Check for last upload time
    CheckActivity(results['Updatetime'])
    return results


def ExportData(Data):
    if config.getboolean('PVoutput', 'enabled'):
        PVoutput(Data)
    else:
        print("Data export disabled")


def PVoutput(Data):
    print("Uploading to PVoutput")
    # Get values from config
    pvout_apikey = config.get('PVoutput', 'API_key')
    pvout_sysid = config.get('PVoutput', 'systemID')
    # Set values for PVoutput
    t_date = format(strftime('%Y%m%d'))
    t_time = format(strftime('%H:%M'))
    # kWh to wh
    if float(Data['DAYGEN']) != 0:
        daywh = float(Data['DAYGEN']) * 1000
    else:
        daywh = 0
    payload = {
        "d": t_date,
        "t": t_time,
        "v1": daywh,
        "v2": Data['ACWATT'],
        "v5": Data['INVTMP'],
        "v6": Data['ACVOL1'],
        "c1": 0
    }
    print("Data sent to PVoutput:")
    print(payload)
    r = requests.post("https://pvoutput.org/service/r2/addstatus.jsp",
                      headers={
                          "X-Pvoutput-Apikey": pvout_apikey,
                          "X-Pvoutput-SystemId": pvout_sysid
                      }, data=payload)
    if r.status_code == 200:
        print("Upload successful")
        Exit()
    else:
        print("Upload failed")
        Exit()


def Exit():
    print("Bye!!")
    sys.exit()


# Base URLs and
BaseURL = "http://m.ginlong.com"

# Project directory
prog_path = os.path.dirname(os.path.abspath(__file__))

# Create session for requests
session = requests.session()

# Import config file
config = configparser.RawConfigParser(allow_no_value=True)
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="Config location")
args = parser.parse_args()

# Check for -c argument, if not load default from project folder
if args.config:
    print("config from argument loaded")
    print(args.config)
    config.read(args.config)
else:
    config.read(prog_path + "/config.ini")

print("Welcome to Ginlong monitoring tool v2 by wessel145")

# Set Generation
generation = int(config.get('Ginlong', 'generation'))

# Actual start commands
InverterID = CheckLogin()
Data = GetData(InverterID)
ExportData(Data)
