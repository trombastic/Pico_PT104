# Code for recording temperature measurements from Omega PT104A data logger

from PT104 import PT104, Channels, DataTypes, Wires
from datetime import datetime
import time
import csv

daq = PT104()
print('waiting for connection...')
daq.connect('GQ840/197')  # ID of specific PT104A device (use discover devices method to return device name)
print('device connected')
daq.set_channel(Channels.CHANNEL_1, DataTypes.PT100, Wires.WIRES_4)
# daq.set_channel(Channels.CHANNEL_2, DataTypes.PT100, Wires.WIRES_4)

sampling_rate_s = 1  # For pressure measurements
test_duration_s = 120

now = datetime.now()
current_date_time = now.strftime('%d%b%Y_%H%M')
test = 'PT104A_Temperature Measurements_40 deg C'
file_name = f'results/PT104A Results_{current_date_time}_{test}.csv'
notes = 'Testing with PT100 Ohm RTD and PT104A Daq (Equip-00146)'

try:

    with open(file_name, 'w') as results_file:
        writer = csv.writer(results_file, delimiter=',')
        writer.writerows([[f'Date and Time: {datetime.now()}'],
                          [f'Sampling Rate: {sampling_rate_s} (s)'],
                          [f'Notes: {notes}'],
                          [f'\n']
                          ])
        writer.writerow(['Temperature Data:'])
        writer.writerow(['Sample Number', 'Time Elapsed (s)', 'Time Elapsed (h)',
                         'Channel 1 Temperature (deg C)', 'Channel 2 Temperature (deg C)']
                        )

        i = 0
        time_elapsed_s = 0
        start_time = time.perf_counter()

        while time_elapsed_s <= test_duration_s:
            time.sleep(sampling_rate_s)
            end_time = time.perf_counter()
            time_elapsed_s = end_time - start_time
            time_elapsed_min = time_elapsed_s / 60

            # Obtain temperature reading, record in csv file, and print.
            temperature_ch1 = daq.get_value_channel_1
            # temperature_ch2 = daq.get_value_channel_2

            data = f'{i}, ' \
                   f'{time_elapsed_s:.2f}, ' \
                   f'{time_elapsed_min:.2f}, ' \
                   f'{temperature_ch1:.3f}, ' \
                   # f'{temperature_ch2}' \

            writer.writerow(data.split(','))

            print(f'Sample number: {i},   '
                  f'Time elapsed (s): {time_elapsed_s:.2f},   '
                  f'Time elapsed (min): {time_elapsed_min:.2f},   '
                  f'CH1 Temp (deg C): {temperature_ch1:.3f},   '
                  # f'CH2 Temp (deg C): {temperature_ch2}'
                  )
            i += 1

except KeyboardInterrupt:
    daq.disconnect()
    print('Script ended by user')

finally:
    daq.disconnect()
    print('Test complete')
