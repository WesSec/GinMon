from time import strftime

import requests

from GinMon import Exit, config


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
