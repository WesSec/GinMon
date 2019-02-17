from time import strftime

import pymysql
import requests

from GinMon import config


def PVoutput(Data, inverter):
    if inverter == int(config.get('PVoutput', 'Inverter')):
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
            print("Upload to PVoutput successful")
        else:
            print("Upload failed")


def mariaInsert(ip, Data, db, table, username, password):
    # query2 = insertFromDict(table, Data)
    query = "INSERT INTO " + table + " (DCVPV1, DCVPV2, DCVPV3, " \
                                     "DCVPV4, DCCUR1, DCCUR2, DCCUR3, DCCUR4, ACVOL1, " \
                                     "ACVOL2, ACVOL3, ACCUR1, ACCUR2, ACCUR3, ACWATT, " \
                                     "ACFREQ, DAYGEN, MONGEN, ANNGEN, TOTGEN, INVTMP, " \
                                     "Updatetime) VALUES (" \
                                     "" + Data['DCVPV1'] + ", " \
                                                           "" + Data['DCVPV2'] + ", " \
                                                                                 "" + Data['DCVPV3'] + ", " \
                                                                                                       "" + Data[
                'DCVPV4'] + ", " \
                            "" + Data['DCCUR1'] + ", " \
                                                  "" + Data['DCCUR2'] + ", " \
                                                                        "" + Data['DCCUR3'] + ", " \
                                                                                              "" + Data['DCCUR4'] + ", " \
                                                                                                                    "" + \
            Data['ACVOL1'] + ", " \
                             "" + Data['ACVOL2'] + ", " \
                                                   "" + Data['ACVOL3'] + ", " \
                                                                         "" + Data['ACCUR1'] + ", " \
                                                                                               "" + Data[
                'ACCUR2'] + ", " \
                            "" + Data['ACCUR3'] + ", " \
                                                  "" + Data['ACWATT'] + ", " \
                                                                        "" + Data['ACFREQ'] + ", " \
                                                                                              "" + Data['DAYGEN'] + ", " \
                                                                                                                    "" + \
            Data['MONGEN'] + ", " \
                             "" + Data['ANNGEN'] + ", " \
                                                   "" + Data['TOTGEN'] + ", " \
                                                                         "" + Data['INVTMP'] + ", " \
                                                                                               "" + str(
        Data['Updatetime']) + ");"
    mariadb_connection = pymysql.connect(host=ip, user=username, password=password, database=db)
    cursor = mariadb_connection.cursor()
    try:
        cursor.execute(query)
        mariadb_connection.commit()
        print("Upload to Database succesfull")
    except pymysql.Error as error:
        print("Error: {}".format(error))
