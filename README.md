### Thermostat like functionality for `orangepi zero`

Is using the project: [DHT22-Python-library-Orange-PI](https://github.com/ionutpi/DHT22-Python-library-Orange-PI)

Similar poject: [smart-thermostat](https://github.com/szlaci83/smart-thermostat)

### Needed libraries:
* pymongo
* https://github.com/wdmomoxx/orangepi_ZERO_gpio_pyH2.git
* OPi.GPIO
* flask
* flask_restful

### usage
```
nohup python3 /path_to_repo/pythermo/api.py > api.log &
nohup python3 /path_to_repo/pythermo/sendData.py > main.log &
```

```
@reboot sleep 30 && nohup python3 /root/pythermo/api.py > /root/api.log &
@reboot sleep 30 && nohup python3 /root/pythermo/sendData.py > /root/snddata.log &
@reboot sleep 30 && python3 /root/pythermo/termo.py >> /root/termo.log 2>&1 &

```

### To do
* authentication middleware for API
* make it dry
* multiple senzors management
* installer
* make a option of not needing internet connexions
* history of heater on and off
* check if opi zero is running from other server
* aware on time based on history
* set path of the script as the home directory
