import matplotlib.pyplot as plt
import numpy as np

# Data for LoRaWAN and NB-IoT overheads (percentages)


LoRaWAN_MCU_Overhead = [28.983558282053412, 27.33986413332713, 26.20964907544722, 25.613202507389985, 25.55986572185781, 25.48705281714792]
LoRaWAN_Protocol_Overhead = [52.73178177700385, 54.09029986859267, 55.053671642308544, 55.56786807908129, 55.612801838630965, 55.67392192042264]
NBIOT_MCU_Overhead = [10.634297601850774, 10.79742101533887, 9.706139614092995, 9.259706025445086, 9.143575366857293, 9.055081500861935]
NBIOT_Protocol_Overhead = [37.808927031482526, 43.444162062096275, 60.72250248626288, 77.25917954515532, 78.89184354830972, 81.08127554070643]

# Calculate remaining percentages for LoRaWAN and NB-IoT to make each bar reach 100%
LoRaWAN_Remaining = [
    100 - (mcu + protocol) for mcu, protocol in zip(LoRaWAN_MCU_Overhead, LoRaWAN_Protocol_Overhead)
]
NBIOT_Remaining = [
    100 - (mcu + protocol) for mcu, protocol in zip(NBIOT_MCU_Overhead, NBIOT_Protocol_Overhead)
]

# Define x-axis labels for the cases
cases = ['Case 1', 'Case 2', 'Case 3', 'Case 4', 'Case 5', 'Case 6']
Resolutions=[' QQQQVGA','QQVGA','QVGA','VGA', 'SVGA', 'UXGA']
x = np.arange(len(cases))
bar_width = 0.35

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))

offset = 0.045  # Adjust this value for more or less distance

# LoRaWAN bars
ax.bar(x - bar_width/2, LoRaWAN_MCU_Overhead, width=bar_width, label='LoRaWAN MCU Overhead', color='skyblue')
ax.bar(x - bar_width/2, LoRaWAN_Protocol_Overhead, width=bar_width, bottom=LoRaWAN_MCU_Overhead, label='LoRaWAN Protocol Overhead', color='blue')
ax.bar(x - bar_width/2, LoRaWAN_Remaining, width=bar_width, bottom=np.array(LoRaWAN_MCU_Overhead) + np.array(LoRaWAN_Protocol_Overhead), label='LoRaWAN Effective', color='lightgrey')

# NB-IoT bars
ax.bar(x + bar_width/2, NBIOT_MCU_Overhead, width=bar_width, label='NBIOT MCU Overhead', color='#A3D4A4')
ax.bar(x + bar_width/2, NBIOT_Protocol_Overhead, width=bar_width, bottom=NBIOT_MCU_Overhead, label='NBIOT Protocol Overhead', color='#D083B0')
ax.bar(x + bar_width/2, NBIOT_Remaining, width=bar_width, bottom=np.array(NBIOT_MCU_Overhead) + np.array(NBIOT_Protocol_Overhead), label='NBIOT Effective', color='#9898b8')

for idx in x:
    ax.text(idx - bar_width/2 -offset, 102, 'LoRa', ha='center', va='bottom', fontweight='bold', color='blue')
    ax.text(idx + bar_width/2 + offset, 102, 'NBIoT', ha='center', va='bottom', fontweight='bold', color='Green')


# LoRaWAN bars with values
for idx, (mcu, protocol, remaining) in enumerate(zip(LoRaWAN_MCU_Overhead, LoRaWAN_Protocol_Overhead, LoRaWAN_Remaining)):
    ax.text(idx - bar_width/2, mcu / 2, f'{mcu:.1f}%', ha='center', va='center', color='black', fontsize=8)
    ax.text(idx - bar_width/2, mcu + protocol / 2, f'{protocol:.1f}%', ha='center', va='center', color='white', fontsize=8)
    ax.text(idx - bar_width/2, mcu + protocol + remaining / 2, f'{remaining:.1f}%', ha='center', va='center', color='black', fontsize=8)

# NB-IoT bars with values
for idx, (mcu, protocol, remaining) in enumerate(zip(NBIOT_MCU_Overhead, NBIOT_Protocol_Overhead, NBIOT_Remaining)):
    ax.text(idx + bar_width/2, mcu / 2, f'{mcu:.1f}%', ha='center', va='center', color='black', fontsize=8)
    ax.text(idx + bar_width/2, mcu + protocol / 2, f'{protocol:.1f}%', ha='center', va='center', color='white', fontsize=8)
    ax.text(idx + bar_width/2, mcu + protocol + remaining / 2, f'{remaining:.1f}%', ha='center', va='center', color='black', fontsize=8)


# Labels, title, and legend
ax.set_xlabel('Resolution')
ax.set_ylabel('Percentage (%)')
ax.set_title('MCU and Protocol Overheads for LoRaWAN and NB-IoT')
ax.set_xticks(x)
ax.set_xticklabels(Resolutions)
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

# Display the plot
plt.tight_layout()
plt.savefig("Energy_breakdown_Percentage.png")
plt.show()
