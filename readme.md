# GinMon
Script for parsing data from m.ginlong.com and use it elsewhere (currently only PVoutput is supported)
Note: The script is far from finished but it does 'work'. 

## Installation
```git clone https://github.com/wessel145/GinMon.git```   
```cd GinMon && pip3 install -r requirements.txt  ```

- Rename the file config-default.ini to config.ini and add your parameters in the config file

- To retrieve deviceID in the ginlong section  
  - Log in at m.ginlong.com
  - Visit http://m.ginlong.com/cpro/epc/plantview/view/doPlantList.json and look for "plantId"
  - Visit http://m.ginlong.com/cpro/epc/plantDevice/inverterListAjax.json?plantId=YOURPLANTID
  - Look for "deviceID"

- First run the script manually to check if it is working correctly
```python3 GinMon.py```

- Create a cron job for the script to run  

```*/15 * * * * /usr/bin/python3 <PATH TO GinMon.py> >/dev/null 2>&1```

Options:

```-c``` is used to manually set the location of the config file (default: projectdir/config.ini)

### Features
- Checks if new data is available on the ginglong server, script aborts when data is same as previous upload. (lastlog.txt is created for storing this data, modifying it may break the script)
- Supports multiple inverters (only if 4th gen, max 3 inverters)
### ToDo
- [ ] Add domoticz support
- [x] Add database support
- [x] Log more data
- [x] Save timestamp and only log new data
- [ ] Setup script to retrieve deviceID for inverter


#### MariaDB table create statement
```
CREATE TABLE `Solaroutput` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `DCVPV1` float DEFAULT NULL,
  `DCVPV2` float DEFAULT NULL,
  `DCVPV3` float DEFAULT NULL,
  `DCVPV4` float DEFAULT NULL,
  `DCCUR1` float DEFAULT NULL,
  `DCCUR2` float DEFAULT NULL,
  `DCCUR3` float DEFAULT NULL,
  `DCCUR4` float DEFAULT NULL,
  `ACVOL1` float DEFAULT NULL,
  `ACVOL2` float DEFAULT NULL,
  `ACVOL3` float DEFAULT NULL,
  `ACCUR1` float DEFAULT NULL,
  `ACCUR2` float DEFAULT NULL,
  `ACCUR3` float DEFAULT NULL,
  `ACWATT` float DEFAULT NULL,
  `ACFREQ` float DEFAULT NULL,
  `DAYGEN` float DEFAULT NULL,
  `MONGEN` float DEFAULT NULL,
  `ANNGEN` float DEFAULT NULL,
  `TOTGEN` float DEFAULT NULL,
  `INVTMP` float DEFAULT NULL,
  `Updatetime` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`log_id`)
) COMMENT='outputs from m.ginglong';
```


