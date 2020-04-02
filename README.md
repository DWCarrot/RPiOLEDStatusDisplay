# RPiOLEDStatusDisplay
display RaspberryPi status (average cpu load, memory usage, temperature &amp; inner-ip) on OLED, using [adafruit-circuitpython-ssd1306](https://learn.adafruit.com/monochrome-oled-breakouts/python-wiring)

## install

- environment: Raspberry Pi 3B+, Raspbian Buster with desktop 2020-02-13

- install `PIL`:

```
sudo apt-get install python3-pil
```

- install `adafruit-circuitpython-ssd1306`

```
sudo pip3 install adafruit-circuitpython-ssd1306
```

notice that `sudo` used for auto start & stop (service)

- test `oledshowstatus.py`

- register service:

```
sudo cp oledstatus /etc/init.d
```

and reboot, then use `sudo service oledstatus start` & `sudo service oledstatus stop` to test

- enable auto start & stop

```
sudo update-rc.d oledstatus defaults
```

