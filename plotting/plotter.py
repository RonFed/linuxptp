import sys
import matplotlib.pyplot as plt
from scipy.signal import lfilter, savgol_filter

def normalize_timestamps(timestamps):
    return [t - timestamps[0] for t in timestamps]


def parse_input_data(filename):
    master_offsets = []
    freqs = []
    path_delays = []
    timestamps = []
    with open(filename, 'r') as f:
        for line in f:
            # Split the line into timestamp and message
            try:
                timestamp, message = line.strip().split(': ')
                # timestamp is "ptp4l[...]" we're interested in the ... part
                timestamp = float(timestamp[6:-1])
                # Extract the master offset, freq, and path delay from the message
                values = message.split()
                master_offset = int(values[2])
                freq = int(values[5])
                path_delay = int(values[8])
            except ValueError:
                continue

            # Add the extracted values to their respective lists
            master_offsets.append(master_offset)
            freqs.append(freq)
            path_delays.append(path_delay)
            timestamps.append(timestamp)
    return normalize_timestamps(timestamps), freqs, master_offsets, path_delays


filename1 = "output_no_eve_no_auth.txt"#sys.argv[1]
filename2 = "output_with_eve_no_auth.txt"#sys.argv[2]
filename3 = "output_with_eve_with_tlv.txt"
filename4 = "output_with_eve_with_wireguard.txt"

timestamps1, freqs1, master_offsets1, path_delays1 = parse_input_data(filename1)
timestamps2, freqs2, master_offsets2, path_delays2 = parse_input_data(filename2)
timestamps3, freqs3, master_offsets3, path_delays3 = parse_input_data(filename3)
timestamps4, freqs4, master_offsets4, path_delays4 = parse_input_data(filename4)

plt.yscale("log")
plt.title('Master offset over time', fontweight='bold', fontsize=24)
plt.xlabel('Time[s]', fontweight='bold', fontsize=16)
plt.ylabel('Log(Master offset)[ns]', fontweight='bold', fontsize=16)

n = 15  # the larger n is, the smoother curve will be
b = [1.0 / n] * n
a = 1
y_values = [master_offsets1, master_offsets2, master_offsets3, master_offsets4]
x_values = [timestamps1, timestamps2, timestamps3, timestamps4]
for i in range(len(y_values)):
    y_values[i] = [abs(y) for y in y_values[i]]
    y_values[i] = lfilter(b, a, y_values[i])
    #y_values[i] = savgol_filter(y_values[i], 101, 2)

plt.plot(x_values[0], y_values[0], 'b', label='No attack')
plt.plot(x_values[1], y_values[1], 'r', label='Attack without authentication')
plt.plot(x_values[2], y_values[2], 'g', label='Attack with TLV authentication')
plt.plot(x_values[3], y_values[3], 'y', label='Attack with WireGuard authentication')
legend = plt.legend(loc='upper right', fontsize='large')
for text in legend.get_texts():
    text.set_fontweight('bold')
plt.grid()
plt.show()
