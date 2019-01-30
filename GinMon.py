import argparse
import configparser
import os
import sys
from time import strftime

import requests


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


def ParseData(json):
    # Parse all the data from the Json
    Data = {'SN': json['result']['deviceWapper']['sn'],
            'Plantname': json['result']['deviceWapper']['plantName'],  # Plantname
            'Updatetime': json['result']['deviceWapper']['updateDate'],  # Last update (epoch)
            'DCVPV1': json['result']['deviceWapper']['realTimeDataImp'][0]['value'],  # DC Voltage PV1 (V)
            'DCVPV2': json['result']['deviceWapper']['realTimeDataImp'][1]['value'],  # DC Voltage PV2 (V)
            'DCVPV3': json['result']['deviceWapper']['realTimeDataImp'][2]['value'],  # DC Voltage PV3 (V)
            'DCVPV4': json['result']['deviceWapper']['realTimeDataImp'][3]['value'],  # DC Voltage PV4 (V)
            'DCCUR1': json['result']['deviceWapper']['realTimeDataImp'][4]['value'],  # DC Current 1 (A)
            'DCCUR2': json['result']['deviceWapper']['realTimeDataImp'][5]['value'],  # DC Current 2 (A)
            'DCCUR3': json['result']['deviceWapper']['realTimeDataImp'][6]['value'],  # DC Current 3 (A)
            'DCCUR4': json['result']['deviceWapper']['realTimeDataImp'][7]['value'],  # DC Current 4 (A)
            'ACVOL1': json['result']['deviceWapper']['realTimeDataImp'][8]['value'],  # AC Voltage R/U/A (A)
            'ACVOL2': json['result']['deviceWapper']['realTimeDataImp'][9]['value'],  # AC Voltage S/V/B (A)
            'ACVOL3': json['result']['deviceWapper']['realTimeDataImp'][10]['value'],  # AC Voltage T/W/C (A)
            'ACCUR1': json['result']['deviceWapper']['realTimeDataImp'][11]['value'],  # AC Current R/U/A (A)
            'ACCUR2': json['result']['deviceWapper']['realTimeDataImp'][12]['value'],  # AC Current S/V/B (A)
            'ACCUR3': json['result']['deviceWapper']['realTimeDataImp'][13]['value'],  # AC Current T/W/C (A)
            'ACWATT': json['result']['deviceWapper']['realTimeDataImp'][14]['value'],  # AC Output Total Power (W)
            'ACFREQ': json['result']['deviceWapper']['realTimeDataImp'][15]['value'],  # AC Output Frequency (Hz)
            'DAYGEN': json['result']['deviceWapper']['realTimeDataImp'][16]['value'],  # Daily Generation (kWh)
            'MONGEN': json['result']['deviceWapper']['realTimeDataImp'][17]['value'],  # Monthly Generation (kWh)
            'ANNGEN': json['result']['deviceWapper']['realTimeDataImp'][18]['value'],  # Annual Generation (kWh)
            'TOTGEN': json['result']['deviceWapper']['realTimeDataImp'][19]['value'],  # Total Generation (kWh)
            'INVTMP': json['result']['deviceWapper']['realTimeDataImp'][20]['value']  # Inverter Temperature (C)
            }
    CheckActivity(Data['Updatetime'])
    return Data


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
    payload = {
        "d": t_date,
        "t": t_time,
        "v1": Data['ANNGEN'],
        "v2": Data['ACWATT'],
        "v5": Data['INVTMP'],
        "c1": 1
    }
    r = requests.post("https://pvoutput.org/service/r2/addstatus.jsp",
                      headers={
                          "X-Pvoutput-Apikey": pvout_apikey,
                          "X-Pvoutput-SystemId": pvout_sysid
                      }, data=payload)
    if r.status_code == 200:
        print("Upload successful")
    else:
        print("Upload failed")


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

# Actual start commands
InverterID = CheckLogin()
Data = GetData(InverterID)
ExportData(Data)
