import numpy as np
import matplotlib.pyplot as plt
import Processing_energy as PE
import ComEnergy_Cal_4tech as CE4T
import math

def communicationEnergy(dataflow):
    # Create an empty ndarray with the desired shape
    comm_energy = np.zeros((len(dataflow), 4))  # Assuming 4 columns for each comm tech

    # Iterate over each dataflow value
    for i, flow in enumerate(dataflow):
        # Assuming CE4T functions return a scalar energy value
        comm_energy[i, 0] = CE4T.BLE_rx_tx_Energy(flow, 1)  # Append to the 1st column
        comm_energy[i, 1] = CE4T.NBIOT_rx_tx_wait_Energy(flow)  # Append to the 2nd column
        comm_energy[i, 2] = CE4T.LoRa_rx_tx_wait_time_Energy(flow)  # Append to the 3rd column
        comm_energy[i, 3] = CE4T.LC4_tx_Energy(flow)  # Append to the 4th column

    return comm_energy



def designSpaceReduction(energy_constraint, dataflow, FLOPS, other_ops):
    if len(dataflow) != len(FLOPS):
        raise ValueError("The dataflow and the FLOPS array should be of the same size")

    # Calculate processing and communication energy
    energy_m4 = PE.processing_energy(FLOPS, other_ops)  # Placeholder for demonstration
    comm_energy = communicationEnergy(dataflow)
    #print("energy_m4",energy_m4)
    #print("comm_energy",comm_energy)
    #print("Dimension",(comm_energy.shape))
    # Plotting
    plt.figure(1)
    '''newcolors = [[0.83, 0.14, 0.14],
                 [0.00, 0.00, 1.00],
                 [1.00, 0.00, 1.00],
                 [0.00, 1.00, 0.00]]'''

    tech_numb = 4

    # Communication energy consumption
    #for j in range (d)
    color=['Blue','Orange','Green','Red']
    for i in range(tech_numb):
        plt.plot(dataflow, comm_energy[:,i], color=color[i])

    # Processing energy consumption
    for j in range(len(dataflow)):
        plt.plot(dataflow[j], energy_m4[j], marker='v',  label=f"dataflow_{j}", color="k")

    # Overall energy consumption (processing and communication)
    total_consumed_energy=np.zeros((comm_energy.shape))
    for i in range(tech_numb):
        for j in range(len(dataflow)):
            total_consumed_energy[j,i] = comm_energy[j,i] + energy_m4[j]
    #print("Total_consumed_energy",total_consumed_energy)


    for i in range(tech_numb):
        plt.plot(dataflow, total_consumed_energy[:,i], color=color[i], linestyle="--")
    #       plt.plot(dataflow[j], consumed_energy, marker='o', edgecolors=newcolors[j], facecolors=newcolors[j])

    # Energy constraints
    enconst = energy_constraint
    temporal = np.ones(len(dataflow))
    plt.plot(dataflow, temporal * energy_constraint, '-.k')
    for _ in range(5):
        temporal *= enconst
        plt.plot(dataflow, temporal, ':k')
        enconst /= 10

    plt.xlabel("Data volume (Bytes)")
    plt.ylabel("Energy (Joules)")
    plt.xscale('log')
    plt.yscale('log')

    # Legend based on comm_tech
    plt.legend(['BLE', 'NB-IoT', 'LoRa', 'LTE C. 4'])

    plt.savefig('4Tech_DSE.png')
    plt.show()


# Example usage
energy_constraint = 0.5
#dataflow = np.logspace(1, 5, 10, 15)
#dataflow = [8940, 91, 75, 4] #as people counting
#FLOPS = [0, 0, 0, 0]
#other_ops = [26820, 1035760, 1116220, 1207220]
#FLOPS = np.random.randint(100, 1000, len(dataflow))
#other_ops = np.random.rand(len(dataflow))
'''dataflow = [150528, 3211264, 1605632, 802816, 401408, 100352, 25088, 4096, 1000];
FLOPS = [0, 93126656, 2879700992, 7511547904, 12139581440, 14915618816, 15378316800, 15497870848, 15501967848];
other_ops = [50176, 0, 0, 0, 0, 0, 0, 0, 0];'''
dataflow = [256000, 680, 500, 259]
FLOPS = [0, 0, 0, 0]
other_ops = [0, 256000, 1512000, 3816000, 5352400]
designSpaceReduction(energy_constraint, dataflow, FLOPS, other_ops)
