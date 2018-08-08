# -*- coding: utf-8 -*-
""" A Wrapper around the usbpt104 library from Pico for the Pico PT-104A RTD DATA Acquisition Module

It also works for the Omega PT-104A.

Based on Code from:
https://www.picotech.com/support/topic27941.html
https://www.picotech.com/support/topic31981.html?sid=48264e01d90ccb6a8a72240a5d024ea6

Drivers for Linux can be found at:
https://www.picotech.com/downloads/linux

The API documentation:
https://www.picotech.com/download/manuals/usb-pt104-rtd-data-logger-programmers-guide.pdf

Example::

    from PT104 import PT104, Channels, DataTypes, Wires
    unit = PT104()
    unit.connect('AY429/026')
    unit.set_channel(Channels.CHANNEL_1, DataTypes.PT100, Wires.WIRES_4)
    value = unit.get_value_channel_1
    if value:
        print('CH1: %1.3f'%value)
    unit.disconnect()


"""
__author__ = "Martin Schröder"
__copyright__ = "Copyright 2018, Technische Universität Berlin"
__credits__ = []
__license__ = "GPLv3"
__version__ = "1.0.0"
__maintainer__ = "Martin Schröder"
__email__ = "m.schroeder@tu-berlin.de"
__status__ = "Beta"
__docformat__ = 'reStructuredText'

from ctypes import *
from ctypes.util import find_library
from enum import IntEnum
from time import time


class CtypesEnum(IntEnum):
    @classmethod
    def from_param(cls, obj):
        return int(obj)


class Channels(CtypesEnum):
    CHANNEL_1 = 1
    CHANNEL_2 = 2
    CHANNEL_3 = 3
    CHANNEL_4 = 4
    CHANNEL_5 = 5
    CHANNEL_6 = 6
    CHANNEL_7 = 7
    CHANNEL_8 = 8
    MAX_CHANNELS = CHANNEL_8


class Wires(CtypesEnum):
    WIRES_2 = 2
    WIRES_3 = 3
    WIRES_4 = 4
    MIN_WIRES = WIRES_2
    MAX_WIRES = WIRES_4


class DataTypes(CtypesEnum):
    OFF = 0
    PT100 = 1
    PT1000 = 2
    RESISTANCE_TO_375R = 3
    RESISTANCE_TO_10K = 4
    DIFFERENTIAL_TO_115MV = 5
    DIFFERENTIAL_TO_2500MV = 6
    SINGLE_ENDED_TO_115MV = 7
    SINGLE_ENDED_TO_2500MV = 8


class CommunicationType(CtypesEnum):
    CT_USB = 0x00000001
    CT_ETHERNET = 0x00000002
    CT_ALL = 0xFFFFFFFF


class PicoInfo(CtypesEnum):
    PICO_DRIVER_VERSION = 0
    PICO_USB_VERSION = 1
    PICO_HARDWARE_VERSION = 2
    PICO_VARIANT_INFO = 3
    PICO_BATCH_AND_SERIAL = 4
    PICO_CAL_DATE = 5
    PICO_KERNEL_DRIVER_VERSION = 6


# load the shared library
lib_path = find_library('usbpt104')
if lib_path is None:
    raise OSError('shared library usbpt104 not found')
else:
    libusbpt104 = cdll.LoadLibrary(lib_path)

    # define function argument types
    # Close the port (do this each time you finish using the device!)
    libusbpt104.UsbPt104CloseUnit.argtypes = [c_short]
    # This function returns a list of all the attached PT-104 devices of the specified port type
    libusbpt104.UsbPt104Enumerate.argtypes = [POINTER(c_char), POINTER(c_ulong), CommunicationType]

    # This function obtains information on a specified device.
    libusbpt104.UsbPt104GetUnitInfo.argtypes = [c_short, POINTER(c_char), c_short, POINTER(c_short), PicoInfo]

    # Get the most recent data reading from a channel.
    libusbpt104.UsbPt104GetValue.argtypes = [c_short, Channels, POINTER(c_long), c_short]

    # Open the device through its USB interface.
    libusbpt104.UsbPt104OpenUnit.argtypes = [POINTER(c_short), POINTER(c_char)]

    # Specify the sensor type and filtering for a channel.
    libusbpt104.UsbPt104SetChannel.argtypes = [c_short, Channels, DataTypes, c_short]

    # This function is used to inform the driver of the local mains (line) frequency. This helps the driver to filter
    # out electrical noise.
    libusbpt104.UsbPt104SetMains.argtypes = [c_short, c_ushort]


class PT104(object):
    def __init__(self):
        self.channels = {Channels.CHANNEL_1: {'data_type': DataTypes.OFF,
                                              'nb_wires': Wires.WIRES_4,
                                              'low_pass_filter': False,
                                              'value': c_long(0),
                                              'last_query': time()},
                         Channels.CHANNEL_2: {'data_type': DataTypes.OFF,
                                              'nb_wires': Wires.WIRES_4,
                                              'low_pass_filter': False,
                                              'value': c_long(0),
                                              'last_query': time()},
                         Channels.CHANNEL_3: {'data_type': DataTypes.OFF,
                                              'nb_wires': Wires.WIRES_4,
                                              'low_pass_filter': False,
                                              'value': c_long(0),
                                              'last_query': time()},
                         Channels.CHANNEL_4: {'data_type': DataTypes.OFF,
                                              'nb_wires': Wires.WIRES_4,
                                              'low_pass_filter': False,
                                              'value': c_long(0),
                                              'last_query': time()}}
        self._handle = None

    @staticmethod
    def discover_devices(communication_type=CommunicationType.CT_USB):
        """This function returns a list of all the attached PT-104 devices of the specified port type

        :param communication_type: type of the devices to discover (COMMUNICATION_TYPE)
        :return: string
        """
        enum_len = c_ulong(256)
        enum_string = create_string_buffer(256)

        libusbpt104.UsbPt104Enumerate(enum_string, enum_len, communication_type)
        return enum_string.value

    @property
    def get_unit_info(self, print_result=True):
        """This function obtains information on a specified device.

        :param print_result: also print the unit info to the console
        :return: the unit info as dict
        """
        if not self.is_connected:
            return None
        info_len = c_short(256)
        info_string = create_string_buffer(256)
        req_len = c_short()
        libusbpt104.UsbPt104GetUnitInfo(self._handle, info_string, info_len, byref(req_len),
                                        PicoInfo.PICO_DRIVER_VERSION)
        driver_version = info_string.value.decode()
        libusbpt104.UsbPt104GetUnitInfo(self._handle, info_string, info_len, byref(req_len), PicoInfo.PICO_USB_VERSION)
        usb_version = info_string.value.decode()
        libusbpt104.UsbPt104GetUnitInfo(self._handle, info_string, info_len, byref(req_len),
                                        PicoInfo.PICO_HARDWARE_VERSION)
        hardware_version = info_string.value.decode()
        libusbpt104.UsbPt104GetUnitInfo(self._handle, info_string, info_len, byref(req_len),
                                        PicoInfo.PICO_VARIANT_INFO)
        variant_info = info_string.value.decode()
        libusbpt104.UsbPt104GetUnitInfo(self._handle, info_string, info_len, byref(req_len),
                                        PicoInfo.PICO_BATCH_AND_SERIAL)
        batch_and_serial = info_string.value.decode()
        libusbpt104.UsbPt104GetUnitInfo(self._handle, info_string, info_len, byref(req_len), PicoInfo.PICO_CAL_DATE)
        cal_date = info_string.value.decode()
        libusbpt104.UsbPt104GetUnitInfo(self._handle, info_string, info_len, byref(req_len),
                                        PicoInfo.PICO_KERNEL_DRIVER_VERSION)
        kernel_driver_version = info_string.value.decode()
        if print_result:
            print('driver_version: %s' % driver_version)
            print('usb_version: %s' % usb_version)
            print('hardware_version:  %s' % hardware_version)
            print('variant_info: %s' % variant_info)
            print('batch_and_serial: %s' % batch_and_serial)
            print('cal_date: %s' % cal_date)
            print('kernel_driver_version: %s' % kernel_driver_version)

        return dict(driver_version=driver_version,
                    usb_version=usb_version,
                    hardware_version=hardware_version,
                    variant_info=variant_info,
                    batch_and_serial=batch_and_serial,
                    cal_date=cal_date,
                    kernel_driver_version=kernel_driver_version)

    @property
    def is_connected(self):
        """returns the connection status

        :return: connection status
        """
        return self._handle is not None

    def connect(self, serial=b'', interface=CommunicationType.CT_USB):
        """Connect to a PT-104A data acquisition module via USB or Ethernet

        .. note:: Ethernet connection is not implemented

        :param serial: serial number of the device
        :return: connection status
        """
        if interface == CommunicationType.CT_ALL:
            raise ValueError('interface must be either CommunicationType.CT_USB or CommunicationType.CT_ETHERNET')

        if interface == CommunicationType.CT_ETHERNET:
            raise NotImplementedError('interface CommunicationType.CT_ETHERNET is not implemented jet')

        if self.is_connected:
            self.disconnect()

        self._handle = c_short()

        if type(serial) is str:
            serial = serial.encode()
        status_unit = libusbpt104.UsbPt104OpenUnit(byref(self._handle), serial)
        if status_unit == 0:
            print('Picolog PT104 opened successfully')
            _ = self.get_unit_info
            self.set_channels()
            return True
        else:
            print('>>>> Picolog ERROR opening device <<<<')
            self._handle = None
            return status_unit

    @property
    def active_channel_count(self):
        """return the number of active channels

        :return: number of active channels
        """
        n = 0
        for channel, conf in self.channels.items():
            if conf['data_type'] == DataTypes.OFF:
                continue
            n += 1
        return n

    def disconnect(self):
        """disconnect from the unit

        :return:
        """
        if not self.is_connected:
            return False
        libusbpt104.UsbPt104CloseUnit(self._handle)
        self._handle = None
        return True

    def set_channel(self, channel, data_type, nb_wires, low_pass_filter=False):
        """writes the channel configuration to self.channels and the device.

        :param channel: channel number (Channels)
        :param data_type: data type of the connected probe (DataType)
        :param nb_wires: number of wires (Wires)
        :param low_pass_filter: use the low pass filter [True, False]
        :return: status
        """
        self.channels[channel]['data_type'] = data_type
        self.channels[channel]['nb_wires'] = nb_wires
        self.channels[channel]['low_pass_filter'] = low_pass_filter
        if not self.is_connected:
            # change config only
            return False

        cs = libusbpt104.UsbPt104SetChannel(self._handle,
                                            channel,
                                            data_type,
                                            nb_wires)
        return cs

    def set_channels(self):
        """sets the channel configuration from self.channels
        """
        for channel, conf in self.channels.items():
            self.set_channel(channel, conf['data_type'], conf['nb_wires'])

    def get_value(self, channel, raw_value=False):
        """queries the measurement value from the unit

        :param channel: channel number (Channels)
        :param raw_value: skip conversion
        :return: measured value
        """
        if not self.is_connected:
            return None
        self._wait_for_conversion(channel)
        status_channel = libusbpt104.UsbPt104GetValue(self._handle,
                                                      channel,
                                                      byref(self.channels[channel]['value']),
                                                      self.channels[channel]['low_pass_filter'])
        self.channels[channel]['last_query'] = time()
        if status_channel == 0:
            if raw_value:
                return float(self.channels[channel]['value'].value)
            return self.scale_value(float(self.channels[channel]['value'].value), channel)
        else:
            return None

    @property
    def get_value_channel_1(self):
        """queries the measurement value from channel 1
        :return: scaled measured value
        """
        return self.get_value(Channels.CHANNEL_1)

    @property
    def get_value_channel_2(self):
        """queries the measurement value from channel 2
        :return: scaled measured value
        """
        return self.get_value(Channels.CHANNEL_2)

    @property
    def get_value_channel_3(self):
        """queries the measurement value from channel 3
        :return: scaled measured value
        """
        return self.get_value(Channels.CHANNEL_3)

    @property
    def get_value_channel_4(self):
        """queries the measurement value from channel 4
        :return: scaled measured value
        """
        return self.get_value(Channels.CHANNEL_4)

    def set_mains(self, sixty_hertz=False):
        """This function is used to inform the driver of the local mains (line) frequency.

        This helps the driver to filter out electrical noise.

        :param sixty_hertz: mains frequency is sixty
        :return: success
        """
        if sixty_hertz:
            sixty_hertz = c_ushort(1)
        else:
            sixty_hertz = c_ushort(0)
        libusbpt104.UsbPt104SetMains(self._handle, sixty_hertz)
        return True

    def _wait_for_conversion(self, channel):
        """wait until the adc cionversion is finished

        :param channel: channel number (Channels)
        :return:
        """
        conversion_time = self.active_channel_count * 0.75
        last_query = self.channels[channel]['last_query']
        while last_query + conversion_time > time():
            pass
        return True

    def scale_value(self, value, channel):
        """scales the value from the device.

        :param value: value to convert as float
        :param channel: channel number (Channels)
        :return: Temperature in °C, Resistance in mOhm, Voltage in mV
        """
        if self.channels[channel]['data_type'] in [DataTypes.PT100, DataTypes.PT1000]:
            return value / 10.0 ** 3  # °C
        if self.channels[channel]['data_type'] == DataTypes.RESISTANCE_TO_375R:
            return value / 10.0 ** 3  # mOhm
        if self.channels[channel]['data_type'] == DataTypes.RESISTANCE_TO_10K:
            return value  # mOhm
        if self.channels[channel]['data_type'] in [DataTypes.DIFFERENTIAL_TO_115MV, DataTypes.SINGLE_ENDED_TO_115MV]:
            return value / 10.0 ** 9  # mV
        if self.channels[channel]['data_type'] in [DataTypes.DIFFERENTIAL_TO_2500MV,
                                                   DataTypes.SINGLE_ENDED_TO_2500MV]:
            return value / 10.0 ** 8  # mV
