import time
import matplotlib.pyplot as plt
from scipy.signal import lfilter

# from watchdog.observers.polling import PollingObserver as Observer

# Global variables
graph_names = ["Baseline", "Slave-NoAuth", "Slave-WG", "Slave-TLV"]
filenames = ["plotting\\baseline.txt", "plotting\\slave_no_auth.txt", "plotting\\slave_wg.txt", "plotting\\slave_tlv.txt"]
timestamps = [[] for _ in range(len(filenames))]
master_offsets = [[] for _ in range(len(filenames))]

# Function to update the graph
def update_graph():
    global timestamps, master_offsets
    
    plt.clf()
    plt.yscale("log")
    plt.title('Master offset over time', fontweight='bold', fontsize=24)
    plt.xlabel('Time[s]', fontweight='bold', fontsize=16)
    plt.ylabel('Log(Master offset)[ns]', fontweight='bold', fontsize=16)

    n = 15  # the larger n is, the smoother curve will be
    b = [1.0 / n] * n
    a = 1
    for i in range(len(master_offsets)):
        x_values = timestamps[i]
        y_values = [abs(y) for y in master_offsets[i]]
        y_values = lfilter(b, a, y_values)
        plt.plot(x_values, y_values, label=f"{graph_names[i]}")

    legend = plt.legend(loc='upper right', fontsize='large')
    for text in legend.get_texts():
        text.set_fontweight('bold')
    plt.grid()
    plt.pause(0.1)

# Function to parse input data from file
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

# Initial graph update
for i in range(len(filenames)):
    timestamps[i], _, master_offsets[i], _ = parse_input_data(filenames[i])

update_graph()

# Start the file change observer
# observer = Observer()
# for filename in filenames:
#     observer.schedule(None, path=filename)

# observer.start()

try:
    while True:
        time.sleep(0.1)  # Add a small delay to reduce CPU usage
        for i, filename in enumerate(filenames):
            with open(filename, 'r') as f:
                contents = f.read()

            if len(contents) > 0:
                timestamps[i], _, master_offsets[i], _ = parse_input_data(filenames[i])
                update_graph()
except KeyboardInterrupt:
    pass

# Stop the observer
# observer.stop()
# observer.join()

plt.show()