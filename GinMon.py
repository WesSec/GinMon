import argparse
import configparser
import json
import os
import sys

import requests

import Exports

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
    dataset = ParseMultiData(rson, amount_inverters)
    return dataset


def ParseMultiData(rson, inverters):
    for i in range(inverters):
        global d, data
        results = {'Inverter': i + 1}
        # Get data based on inverter generation
        if generation == 3:
            data = rson['result']['deviceWapper']['data']
            d = json.loads(data)
            results.update({'Plantname': rson['result']['deviceWapper']['plantName']})  # Plantname
            results.update({'Updatetime': rson['result']['deviceWapper']['updateDate']})  # Last update (epoch)
        elif generation == 4:
            data = rson['result']['paginationAjax']['data'][i]['data']
            d = json.loads(data)
            results.update({'Plantname': rson['result']['plantInfo']['name']})  # Plantname
            results.update(
                {'Updatetime': rson['result']['paginationAjax']['data'][0]['updateDate']})  # Last update (epoch)
        else:
            print("wrong generation entered in config (must be 3 or 4)")
            Exit()
        # Try to fill in all values declared in gindict
        for line in d:
            try:
                results.update({gindict[line]: d[line]})
            except:
                pass
        # Check for last upload time
        i += 1
        CheckActivity(results['Updatetime'])
        # Print results (for debugging)
        # print(results)
        return results


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


def ExportData(Data, i):
    if config.getboolean('PVoutput', 'enabled'):
        Exports.PVoutput(Data, i)
    else:
        print("Data export to PVoutput disabled")
    if config.getboolean('MariaDB', 'enabled'):
        ip = config.get('MariaDB', 'serverip')
        db = config.get('MariaDB', 'database')
        table = config.get('MariaDB', 'table')
        username = config.get('MariaDB', 'username')
        password = config.get('MariaDB', 'password')
        Exports.mariaInsert(ip, Data, db, table, username, password)
    else:
        print("Data export to MariaDB disabled")

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

if __name__ == "__main__":
    print("Welcome to Ginlong monitoring tool v2 by wessel145")

    # Set Generation
    generation = int(config.get('Ginlong', 'generation'))
    amount_inverters = int(config.get('Ginlong', 'Amount_inverters'))

    # Actual start commands
    InverterID = CheckLogin()
    Data = GetData(InverterID)
    ExportData(Data, 1)
    Exit()
