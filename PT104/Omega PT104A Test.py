from PT104 import PT104, Channels, DataTypes, Wires
daq = PT104()
daq.connect('GQ840/197')  # ID of Diality's device
time.sleep(60)
daq.set_channel(Channels.CHANNEL_1, DataTypes.PT100, Wires.WIRES_4)


temp = daq.get_value_channel_1
print(f'CH1: {temp})
print('CH1: %1.3f' % temp)

if temp:
    print('CH1: %1.3f'% temp)

daq.disconnect()