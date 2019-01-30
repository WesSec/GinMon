# GinMon
Script for parsing data from m.ginlong.com and use it elsewhere (currently only PVoutput is supported)
Note: The script is far from finished but it does 'work'. 

## Installation
```git clone https://github.com/wessel145/GinMon.git```  

Rename the file config-default.ini to config.ini and add your parameters in the config file
Create a cron job for the script to run  

```*/15 * * * * /usr/bin/python3 <PATH TO GinMon.py> >/dev/null 2>&1```

Options:

```-c``` is used to manually set the location of the config file (default: projectdir/config.ini)

### Features
- Only logs data when data is newer than x minutes, Ginlong inverters tend to upload new data ever 10 minutes when active, 
when no energy is generated for longer than 20 minutes no new data will be uploaded

### ToDo
- [ ] Add domoticz support
- [ ] Add database support
- [x] Log more data
- [ ] Save timestamp and only log new data