
import matplotlib.pyplot as plt

# Data from the table
references = ["Pham, 2016", "Jebril et al., 2018", "Giordana et al., 2020", "Khan et al., 2021", "Juliando et al., 2021", "Chaparro B. et al., 2022", "Desai et al., 2022", "Nardello et al., 2023", "Us (bengroup)", "Us(Bengroup)"]
communication_technology = ["LoRa", "LoRa", "LoRa", "NBIOT+ BLE", "LoRa", "LoRa", "LoRa", "Low Earth Orbit Radio", "LoRa", "NBIOT"]
image_sizes_kb = [1, 0, 0, 32, 614, 0.819, 19, 2, 10, 10]  # Sizes in KB, where "-" is converted to 0
transmission_times_s = [36, 867, 0, 72, 51480, 2.51, 0, 0.92, 398, 16.8 ]  # Times in seconds, where "-" is converted to 0
self_powered = [False, False, False, False, False, False, True, True, True, True]  # Indicates if self-powered

# Calculate transmission intervals from transmission times (seconds to minutes)
#transmission_intervals = [86400 / tt if tt != 0 else 0 for tt in transmission_times_s]

# Define colors for each reference
'''color_map = {
    "Pham, 2016": 'blue',
    "Jebril et al., 2018": 'green',
    "Giordana et al., 2020": 'red',
    "Khan et al., 2021": 'purple',
    "Juliando et al., 2021": 'orange',
    "Chaparro B. et al., 2022": 'brown',
    "Desai et al., 2022": 'pink',
    "Nardello et al., 2023": 'cyan',
    "Us (bengroup)": 'magenta'
}'''


# Define colors and markers for each communication technology
technology_marker = {
    "LoRa": ('o', 'blue'),
    "NBIOT+ BLE": ('s', 'green'),
    "Low Earth Orbit Radio": ('^', 'red'),
    "NBIOT": ('D', 'purple')
}

# Create a scatter plot
plt.figure(figsize=(10, 6))


for i in range(len(references)):
    tech = communication_technology[i]
    marker, color = technology_marker.get(tech, ('o', 'black'))

    if transmission_times_s[i] == 0 and self_powered[i]:
        plt.scatter(image_sizes_kb[i], transmission_times_s[i], color=color, label=f'{tech}({references[i]})',                   #color=color_map[references[i]], label=references[i]
                    marker='x', s=280, linewidths=5)
    elif transmission_times_s[i] == 0:
        plt.scatter(image_sizes_kb[i], transmission_times_s[i], color=color, label=f'{tech}({references[i]})', marker='x', s=100)
    elif self_powered[i] and transmission_times_s[i] != 0:
        plt.scatter(image_sizes_kb[i], transmission_times_s[i], color=color, label=tech, marker='o', s=280, edgecolors='black', linewidths=1.5)
    else:
        plt.scatter(image_sizes_kb[i], transmission_times_s[i], color=color, label=tech, marker='o', s=100)


# Set plot labels and title
plt.xlabel('Image Size after Optimization (KB)')
plt.ylabel('Transmission Time (seconds)')
plt.title('Image Size vs Transmission Time for Communication Technologies')
plt.legend(loc='upper left', title='IoT Technology', bbox_to_anchor=(0.01, 1.01))

# Annotate each point with the reference
for i, ref in enumerate(references):
    plt.annotate(ref, (image_sizes_kb[i], transmission_times_s[i]))

# Add a footer with additional information
plt.figtext(0.1, 0.01, 'Note: Larger markers indicate self-powered.\n X marker indicates transmission occurs on inference.', horizontalalignment='left', fontsize=9, color='gray')

plt.xscale('log')
plt.yscale('log')
plt.grid(True)
plt.show()
