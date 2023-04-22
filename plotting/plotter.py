import sys
import matplotlib.pyplot as plt


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


filename1 = sys.argv[1]
#filename2 = sys.argv[2]

timestamps1, freqs1, master_offsets1, path_delays1 = parse_input_data(filename1)
#timestamps2, freqs2, master_offsets2, path_delays2 = parse_input_data(filename2)
plt.plot(timestamps1, master_offsets1, 'b')
#plt.yscale('symlog')
plt.show()
