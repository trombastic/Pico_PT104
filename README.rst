A Python Wrapper for the usbpt104 library from Pico
===================================================

Class based interface to the Pico (Omega) PT-104 RTD DAQ Module


Dependencies
------------

 - libusbpt104 (see installation)


What is Working
---------------

 - discover units connected via USB (Ethernet untested)
 - Configure the Channels
 - Reading of measured values


What is not Working/Missing
---------------------------

 - Documentation
 - Configure the ethernet interface
 - Connection via ethernet
 - usage on Windows


Installation
------------

Linux installation:
1. Install libusb104 following https://www.picotech.com/downloads/linux

Ubuntu 18.04::

    sudo bash -c 'echo "deb https://labs.picotech.com/debian/ picoscope main" >/etc/apt/sources.list.d/picoscope.list'
    wget -O - https://labs.picotech.com/debian/dists/picoscope/Release.gpg.key | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install libusbpt104

2. Install this package::

    sudo pip3 install https://github.com/trombastic/Pico_PT104/archive/master.zip


Usage
-----

::

    from PT104 import PT104, Channels, DataTypes, Wires
    unit = PT104()
    unit.connect('AY429/026')
    unit.set_channel(Channels.CHANNEL_1, DataTypes.PT100, Wires.WIRES_4)
    value = unit.get_value_channel_1
    if value:
        print('CH1: %1.3f'%value)
    unit.disconnect()

Contribute
----------

 - Issue Tracker: https://github.com/trombastic/Pico_PT104/issues
 - Source Code: https://github.com/trombastic/Pico_PT104


License
-------

The project is licensed under the _GNU General Public License v3 (GPLv3)_.
