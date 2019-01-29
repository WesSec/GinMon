# GinMon
Script for parsing data from ginlongmonitoring.com and use it elsewhere
Note: The script is far from finished but it does 'work'. 

## Installation
```git clone https://github.com/wessel145/GinMon.git```  

Rename the file config-default.ini to config.ini and add your parameters in the config file
Create a cron job for the script to run  

```*/30 * * * * /usr/bin/python3 <PATH TO GinMon.py> >/dev/null 2>&1```

### ToDo
- [ ] Add domoticz support
- [ ] Add database support
- [ ] Log more data