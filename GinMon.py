#!/usr/bin/python3
# --------------------------------------------------
# partial code used from Toulon7559 and from various material from forums, Shoutout to them!
# version 1.0 for download from Ginlong and upload PVOutput
# --------------------------------------------------
import configparser
import hashlib
import sys
import urllib
from xml.etree import ElementTree as ET
import datetime
from time import strftime

import requests

# Import config file
config = configparser.RawConfigParser(allow_no_value=True)
config.read(sys.argv[1])

# Ginlong config
baseURL = 'http://www.ginlongmonitoring.com:10000'  # base url
username = config.get('Ginlong', 'username')
password = config.get('Ginlong', 'password').encode('utf-8')
stationid = config.get('Ginlong', 'systemID')

# Domoticz settings (does not work)
# domoticz settings
# domoticz_host = '127.0.0.1'  # 127.0.0.1 is for local host
# domoticz_port = '8080'
# domoticz_url = 'json.htm'
# domoticz_ActualPower = '<idx>'  # idx of new device

m = hashlib.md5()
m.update(password)

# building url
requestURL = baseURL + '/serverapi/?method=Login&username=' + username + '&password=' + m.hexdigest() + '&key=apitest&client=iPhone'

# login call
root = ET.parse(urllib.request.urlopen(requestURL)).getroot()
token = root.find('token').text

print('Logged In: ' + username)

# info url
infoURL = baseURL + '/serverapi/?method=Data&username=' + username + '&stationid=' + stationid + '&token=' + token + '&key=apitest'

print('Getting Info... ')

# login call
infoRoot = ET.parse(urllib.request.urlopen(infoURL)).getroot()

income = infoRoot.find('income')
TodayIncome = income.find('TodayIncome').text
ActualPower = income.find('ActualPower').text
etoday = income.find('etoday').text
etotal = income.find('etotal').text

multiply = '1000.0'
etotal1000 = float(etotal) * float(multiply)
TotalIncome = income.find('TotalIncome').text
etotalstr = str(etotal1000)

# logging values
print('TodayIncome: ' + TodayIncome)
print('ActualPower: ' + ActualPower)
print('etoday: ' + etoday)
print('etotal: ' + etotal)
print('etotal 1000: ' + etotalstr)

# uploading values to domoticz
# url = (
#         "http://" + domoticz_host + ":" + domoticz_port + "/" + domoticz_url + "?type=command&param=udevice&idx=" + domoticz_ActualPower + "&nvalue=0&svalue=" + ActualPower + ";" + etotalstr)
# urllib.request.urlopen(url)

# Line 75
# --------------------------------------------------
# END OF UPLOAD TO DOMOTICZ
# --------------------------------------------------

# Setting & Translation for values in next section
TEMPINV = 0  # API does not support this stat
VOLTAGE = 0  # API does not support this stat
POWER = ActualPower
LIFEENERGY = etotal1000  # Energy in Wh
multiply = '1000.0'
etoday1000 = float(etoday) * float(multiply)
DAYENERGY = etoday1000  # Energy in Wh

# --------------------------------------------------
# START OF UPLOAD TO PVOUTPUT
# --------------------------------------------------
# Settings for PVOutput
pvout_enabled = config.getboolean('PVoutput', 'enabled')
pvout_apikey = config.get('PVoutput', 'API_key')
pvout_sysid = config.get('PVoutput', 'systemID')
pvout_cumflag = 0  # flag is 1 if you apply lifetime-energy Wh_life / LIFEENERGY

if pvout_enabled:
    # Linking of parameters
    SYSTEMID = pvout_sysid
    APIKEY = pvout_apikey
    t_date = format(strftime('%Y%m%d'))
    t_time = format(strftime('%H:%M'))
    Wh_life = LIFEENERGY
    Wh_today = DAYENERGY
    pv_temp = TEMPINV
    pv_volts = VOLTAGE
    pv_power = POWER
    if pvout_cumflag == 1:
        Wh_upload = Wh_life
    else:
        Wh_upload = Wh_today

    # Load Uploadtime from config
    Starthour = config.getint('PVoutput', 'starthour')
    Stophour = config.getint('PVoutput', 'endhour')

    # Determine Uploadtime

    now = datetime.datetime.now()
    print('Upload-window PVO opens when start-hour =', Starthour)
    print('Upload-window PVO closes after stop-hour=', Stophour)
    uploadtime = (now.hour >= Starthour) and (now.hour <= Stophour)
    if uploadtime:
        print('inside upload-window')
    else:
        print('outside upload-window')

    # Determine Values & Compile for upload to PVOutput

    if pvout_enabled and uploadtime:
        print('uploading')
        pv_power = POWER
        pv_temp = TEMPINV
        pv_volts = VOLTAGE
        payload = {
            "d": t_date,
            "t": t_time,
            "v1": Wh_upload,
            "v2": pv_power,
            "v5": pv_temp,
            "v6": pv_volts,
            "v10": pv_volts,
            "c1": pvout_cumflag
        }
        requests.post("https://pvoutput.org/service/r2/addstatus.jsp",
                      headers={
                          "X-Pvoutput-Apikey": pvout_apikey,
                          "X-Pvoutput-SystemId": pvout_sysid
                      }, data=payload)

    print()
    print('= Info for PVOutput =')
    print('t_date %s' % t_date)
    print('t_time %s' % t_time)
    print('pv_power %s' % pv_power)
    print('Wh_today %s' % Wh_today)
    print('Wh_life %s' % Wh_life)
    print('Wh_upload %s' % Wh_upload)
    print('pv_temp %s' % pv_temp)
    print('pv_volts %s' % pv_volts)
    # --------------------------------------------------
    # END OF UPLOAD TO PVOUTPUT
    # --------------------------------------------------

print("Finished")