import numpy as np
import matplotlib.pyplot as plt
def ComputeEnergyToSendData(sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle, tsSleep):
    """
    Compute the energy consumed to send data.

    Args:
    sa (int): Size of application data in bytes.
    MaxDataPacketSize (int): Maximum size of a data packet in bytes.
    PTx (float): Power consumption during transmission in watts.
    PRx (float): Power consumption during reception in watts.
    PIdle (float): Power consumption during idle state in watts.
    PSleep (float): Power consumption during sleep mode in watts.
    PER (float): Packet error rate.
    tsTx (float): Transmission time in seconds.
    tsRx (float): Reception time in seconds.
    tsIdle (float): Idle time in seconds.
    tsSleep (float): Sleep time in seconds.

    Returns:
    float: Energy consumed in sending data in joules.
    """
    # Calculate number of packets
    NPackets = int(sa / MaxDataPacketSize)
    LastPacket = sa % MaxDataPacketSize
    if LastPacket != 0:
        NPackets += 1
    print("Npackets:",NPackets)
    # Calculate total transmission time for each state
    Ntr = (1 / (1 - PER))  # Number of transmissions
    tTx = sum([tsTx for _ in range(NPackets)]) * Ntr
    tRx = sum([tsRx for _ in range(NPackets)]) * Ntr
    tIdle = sum([tsIdle for _ in range(NPackets)]) * Ntr
    tSleep = sum([tsSleep for _ in range(NPackets)]) * Ntr

    # Calculate energy consumption for data transmission
    Eactivetrans= (PTx * tTx + PRx * tRx + PIdle * tIdle)
    Esleep= (PSleep * tSleep)
    Edata = Eactivetrans + Esleep
    print("Consumed Energy in sending data", Edata)
    return Edata


def ComputeEnergyInSleepMode(ta, ton, PSleepR):
    """
    Compute the energy consumed in sleep mode.

    Args:
    ta (float): Total time in seconds.
    ton (float): On-time duration in seconds.
    PSleepR (float): Power consumption during sleep mode for reception in watts.

    Returns:
    float: Energy consumed in sleep mode in joules.
    """
    # Compute the energy consumed in sleep mode
    EnergySleep= PSleepR * (ta-ton)
    print("Energy_sleep", EnergySleep)
    return EnergySleep  # Energy in joules


def ConsumedEnergy(ta, tsyn, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle, tsSleep, ton, PsleepR, synchronization_on_data_frame_possible, Esyn):
    """
    Compute the total energy consumed.

    Args:
    ta (float): Total time in seconds.
    tsyn (float): Time for synchronization in seconds.
    sa (int): Size of data in bytes.
    MaxDataPacketSize (int): Maximum size of a data packet in bytes.
    PTx (float): Power consumption during transmission in watts.
    PRx (float): Power consumption during reception in watts.
    PIdle (float): Power consumption during idle state in watts.
    PSleep (float): Power consumption during sleep mode in watts.
    PER (float): Packet error rate.
    tsTx (float): Transmission time in seconds.
    tsRx (float): Reception time in seconds.
    tsIdle (float): Idle time in seconds.
    tsSleep (float): Sleep time in seconds.
    ton (float): On-time duration in seconds.
    PsleepR (float): Power consumption during sleep mode for reception in watts.
    synchronization_on_data_frame_possible (bool): Whether synchronization on data frame is possible.
    Esyn (float): Energy consumed for synchronization in joules.

    Returns:
    float: Total energy consumed in joules.
    """
    Edata = ComputeEnergyToSendData(sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER,  tsTx, tsRx, tsIdle, tsSleep)

    if ta < tsyn:
        Nsyn = 1
    else:
        Nsyn = ta / tsyn

    if synchronization_on_data_frame_possible:
        NdataSyn = 1
    else:
        NdataSyn = 0

    Esleep = ComputeEnergyInSleepMode(ta, ton, PsleepR)

    Etot = Edata + (Nsyn - NdataSyn) * Esyn + Esleep
    print("Total energy consumed ", Etot)
    return Etot


def Lifetime_cal(ta, tsyn, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER,  tsTx, tsRx, tsIdle, tsSleep, ton, PsleepR, synchronization_on_data_frame_possible, Esyn, Ebattery):
    """
    Compute the lifetime of the system.

    Args:
    ta (float): Total time in seconds.
    tsyn (float): Time for synchronization in seconds.
    sa (int): Size of data in bytes.
    MaxDataPacketSize (int): Maximum size of a data packet in bytes.
    PTx (float): Power consumption during transmission in watts.
    PRx (float): Power consumption during reception in watts.
    PIdle (float): Power consumption during idle state in watts.
    PSleep (float): Power consumption during sleep mode in watts.
    PER (float): Packet error rate.
    tsTx (float): Transmission time in seconds.
    tsRx (float): Reception time in seconds.
    tsIdle (float): Idle time in seconds.
    tsSleep (float): Sleep time in seconds.
    ton (float): On-time duration in seconds.
    PsleepR (float): Power consumption during sleep mode for reception in watts.
    synchronization_on_data_frame_possible (bool): Whether synchronization on data frame is possible.
    Esyn (float): Energy consumed for synchronization in joules.
    Ebattery (float): Initial energy level of the battery in joules.

    Returns:
    float: Lifetime of the system in seconds.
    """
    consumed_energy = ConsumedEnergy(ta, tsyn, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER,  tsTx, tsRx, tsIdle, tsSleep, ton, PsleepR, synchronization_on_data_frame_possible, Esyn)
    gamma_leak = 0.05 * ta/31536000  # 5% leakage factor (years)
    E = Ebattery  # Initial energy level
    Lifetime = 0
    Eleak = Ebattery * gamma_leak  # Energy lost due to leakage (joules)
    print("Eleak: ",Eleak)

    while E > 0.1 * Ebattery:  # While energy is above 10% of initial energy
        E = E - consumed_energy - Eleak
        Lifetime = Lifetime + ta
    return Lifetime

sa_list = [0.008,0.08,0.8,8,80,800, 8000, 80000, 800000, 8000000] # Total time in seconds
ta_list = [100, 1000, 10000, 100000, 1000000, 10000000]
ta_list_one = [3600*24]
total_time_inyear_list_loRA=[]
total_time_inyear_list_BLE=[]
total_time_inyear_list_NBIoT=[]

# Example usage for BLE
for i in range(len(ta_list)):
    print('ta',ta_list[i])
    tsyn = 5 * 365 * 24 * 60 * 60  # Time for synchronization in seconds
    sa = 0.8  # Size of data in bytes
    PER = 0.1  # Packet error rate
    MaxDataPacketSize = 245#(Lora)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
    PTx = 24e-3#(BLE)  # Power consumption
    PRx = 20e-3#(BLE)  # Power consumption
    PIdle =5e-3 # (BLE)# Power consumption
    PSleep =3e-6#(BLE)  # Power consumption
    tsTx = 1080e-6#(BLE)#(2193e-3)*245/100#1080e-6(BLE)  # Transmission time in seconds
    tsRx = 400e-6#(BLE)#400e-6#400e-6  (BLE)# Reception time in seconds
    tsIdle = 1080e-6  # Idle time in seconds
    ton = tsTx + tsRx + tsIdle
    tsSleep = ta_list[i] - ton  # Sleep time in seconds
    print(tsSleep)
    PER = 0.01  # Packet error rate
    PSleepR = 0#0.001408e-3#4.3e-6#3e-6  # Power consumption during sleep mode for reception in watts
    synchronization_on_data_frame_possible = 0  # Boolean indicating if synchronization on data frame is possible
    Esyn = 0  # Energy consumed for synchronization in joules
    Ebattery = 13000  # Initial energy level of the battery in joules
    total_time = Lifetime_cal(ta_list[i], tsyn, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle,
                              tsSleep, ton, PSleepR, synchronization_on_data_frame_possible, Esyn, Ebattery)
    total_time_inyear_BLE= total_time / (3600 * 24 * 365)
    #print(
        #f"Total time in {'year' if total_time_inyear >= 1 else 'day'}s: {total_time_inyear if total_time_inyear >= 1 else total_time / (3600 * 24)}")
    total_time_inyear_list_BLE.append(total_time_inyear_BLE)



# Example usage for LORA
for i in range(len(ta_list)):
    print('ta',ta_list[i])
    tsyn = 5 * 365 * 24 * 60 * 60  # Time for synchronization in seconds
    sa = 0.8  # Size of data in bytes
    PER = 0.1  # Packet error rate
    MaxDataPacketSize = 250#(Lora)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
    PTx = 420e-3#24e-3(BLE)  # Power consumption
    PRx = 44e-3#20e-3(BLE)  # Power consumption
    PIdle = 7e-3#5e-3  (BLE)# Power consumption
    PSleep = 0.001408e-3  # 3e-6(BLE)  # Power consumption
    tsTx = 7755093e-6#(Lora)#(2193e-3)*245/100#1080e-6(BLE)  # Transmission time in seconds
    tsRx = 7755093e-6#(Lora)#400e-6#400e-6  (BLE)# Reception time in seconds
    tsIdle = 1#1080e-6  # Idle time in seconds
    ton = tsTx + tsRx + tsIdle
    tsSleep = ta_list[i] - ton  # Sleep time in seconds
    print(tsSleep)
    PER = 0.01  # Packet error rate
    PSleepR = 0#0.001408e-3#4.3e-6#3e-6  # Power consumption during sleep mode for reception in watts
    synchronization_on_data_frame_possible = 0  # Boolean indicating if synchronization on data frame is possible
    Esyn = 0  # Energy consumed for synchronization in joules
    Ebattery = 13000  # Initial energy level of the battery in joules
    total_time = Lifetime_cal(ta_list[i], tsyn, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle,
                              tsSleep, ton, PSleepR, synchronization_on_data_frame_possible, Esyn, Ebattery)
    total_time_inyear_lora= total_time / (3600 * 24 * 365)
   # print(
     #   f"Total time in {'year' if total_time_inyear >= 1 else 'day'}s: {total_time_inyear if total_time_inyear >= 1 else total_time / (3600 * 24)}")
    total_time_inyear_list_loRA.append(total_time_inyear_lora)

# Example usage for NBIOT
for i in range(len(ta_list)):
    print('ta',ta_list[i])
    tsyn = 5 * 365 * 24 * 60 * 60  # Time for synchronization in seconds
    sa = 0.8  # Size of data in bytes
    PER = 0.1  # Packet error rate
    MaxDataPacketSize = 1500#(Lora)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
    PTx = 543e-3#24e-3(BLE)  # Power consumption
    PRx = 90e-3#20e-3(BLE)  # Power consumption
    PIdle = 2.4e-3#5e-3  (BLE)# Power consumption
    PSleep = 0.015e-3  # 3e-6(BLE)  # Power consumption
    tsTx = 1.67#0.92857e-3#(Lora)#(2193e-3)*245/100#1080e-6(BLE)  # Transmission time in seconds
    tsRx = 0.92857e-3#(Lora)#400e-6#400e-6  (BLE)# Reception time in seconds
    tsIdle = 10#1080e-6  # Idle time in seconds
    ton = tsTx + tsRx + tsIdle
    tsSleep = ta_list[i] - ton  # Sleep time in seconds
    print(tsSleep)
    PER = 0.01  # Packet error rate
    PSleepR = 0#0.001408e-3#4.3e-6#3e-6  # Power consumption during sleep mode for reception in watts
    synchronization_on_data_frame_possible = 0  # Boolean indicating if synchronization on data frame is possible
    Esyn = 0  # Energy consumed for synchronization in joules
    Ebattery = 13000  # Initial energy level of the battery in joules
    total_time = Lifetime_cal(ta_list[i], tsyn, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle,
                              tsSleep, ton, PSleepR, synchronization_on_data_frame_possible, Esyn, Ebattery)
    total_time_inyear_NBIOT= total_time / (3600 * 24 * 365)
   # print(
     #   f"Total time in {'year' if total_time_inyear >= 1 else 'day'}s: {total_time_inyear if total_time_inyear >= 1 else total_time / (3600 * 24)}")
    total_time_inyear_list_NBIoT.append(total_time_inyear_NBIOT)


plt.semilogx(ta_list, total_time_inyear_list_BLE, label="BLE")
plt.semilogx(ta_list, total_time_inyear_list_loRA, label="LoRa")
plt.semilogx(ta_list, total_time_inyear_list_NBIoT, label="NBIOT")
plt.xlabel('ta_list in sec sa=0.8 b/s')
plt.ylabel('total_time_year_list')
plt.legend()
plt.grid(True)
plt.show()



'''for i in range(len(sa_list)):
    print('sa',sa_list[i])
    tsyn = 5 * 365 * 24 * 60 * 60  # Time for synchronization in seconds
    ta = 24*3600  # Size of data in bytes
    PER = 0.1  # Packet error rate
    MaxDataPacketSize = 245#(Lora)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
    PTx = 24e-3#(BLE)  # Power consumption
    PRx = 20e-3#(BLE)  # Power consumption
    PIdle =5e-3 # (BLE)# Power consumption
    PSleep =3e-6#(BLE)  # Power consumption
    tsTx = 1080e-6#(BLE)#(2193e-3)*245/100#1080e-6(BLE)  # Transmission time in seconds
    tsRx = 400e-6#(BLE)#400e-6#400e-6  (BLE)# Reception time in seconds
    tsIdle = 1080e-6  # Idle time in seconds
    ton = tsTx + tsRx + tsIdle
    tsSleep = ta - ton  # Sleep time in seconds
    print(tsSleep)
    PER = 0.01  # Packet error rate
    PSleepR = 0#0.001408e-3#4.3e-6#3e-6  # Power consumption during sleep mode for reception in watts
    synchronization_on_data_frame_possible = 0  # Boolean indicating if synchronization on data frame is possible
    Esyn = 0  # Energy consumed for synchronization in joules
    Ebattery = 13000  # Initial energy level of the battery in joules
    total_time = Lifetime_cal(ta, tsyn, sa_list[i], MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle,
                              tsSleep, ton, PSleepR, synchronization_on_data_frame_possible, Esyn, Ebattery)
    total_time_inyear_BLE= total_time / (3600 * 24 * 365)
    #print(
        #f"Total time in {'year' if total_time_inyear >= 1 else 'day'}s: {total_time_inyear if total_time_inyear >= 1 else total_time / (3600 * 24)}")
    total_time_inyear_list_BLE.append(total_time_inyear_BLE)



# Example usage:
for i in range(len(sa_list)):
    print('sa',sa_list[i])
    tsyn = 5 * 365 * 24 * 60 * 60  # Time for synchronization in seconds
    ta = 24*3600  # Size of data in bytes
    PER = 0.1  # Packet error rate
    MaxDataPacketSize = 250#(Lora)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
    PTx = 420e-3#24e-3(BLE)  # Power consumption
    PRx = 44e-3#20e-3(BLE)  # Power consumption
    PIdle = 7e-3#5e-3  (BLE)# Power consumption
    PSleep = 0.001408e-3  # 3e-6(BLE)  # Power consumption
    tsTx = 7755093e-6#(Lora)#(2193e-3)*245/100#1080e-6(BLE)  # Transmission time in seconds
    tsRx = 7755093e-6#(Lora)#400e-6#400e-6  (BLE)# Reception time in seconds
    tsIdle = 1#1080e-6  # Idle time in seconds
    ton = tsTx + tsRx + tsIdle
    tsSleep = ta - ton  # Sleep time in seconds
    print(tsSleep)
    PER = 0.01  # Packet error rate
    PSleepR = 0#0.001408e-3#4.3e-6#3e-6  # Power consumption during sleep mode for reception in watts
    synchronization_on_data_frame_possible = 0  # Boolean indicating if synchronization on data frame is possible
    Esyn = 0  # Energy consumed for synchronization in joules
    Ebattery = 13000  # Initial energy level of the battery in joules
    total_time = Lifetime_cal(ta, tsyn, sa_list[i], MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle,
                              tsSleep, ton, PSleepR, synchronization_on_data_frame_possible, Esyn, Ebattery)
    total_time_inyear_lora= total_time / (3600 * 24 * 365)
   # print(
     #   f"Total time in {'year' if total_time_inyear >= 1 else 'day'}s: {total_time_inyear if total_time_inyear >= 1 else total_time / (3600 * 24)}")
    total_time_inyear_list_loRA.append(total_time_inyear_lora)

# Example usage:
for i in range(len(sa_list)):
    print('sa',sa_list[i])
    tsyn = 5 * 365 * 24 * 60 * 60  # Time for synchronization in seconds
    ta = 24*3600  # Size of data in bytes
    PER = 0.1  # Packet error rate
    MaxDataPacketSize = 1500#(Lora)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
    PTx = 543e-3#24e-3(BLE)  # Power consumption
    PRx = 90e-3#20e-3(BLE)  # Power consumption
    PIdle = 2.4e-3#5e-3  (BLE)# Power consumption
    PSleep = 0.015e-3  # 3e-6(BLE)  # Power consumption
    tsTx = 1.67#0.92857e-3#(Lora)#(2193e-3)*245/100#1080e-6(BLE)  # Transmission time in seconds
    tsRx = 0.92857e-3#(Lora)#400e-6#400e-6  (BLE)# Reception time in seconds
    tsIdle = 10#1080e-6  # Idle time in seconds
    ton = tsTx + tsRx + tsIdle
    tsSleep = ta - ton  # Sleep time in seconds
    print(tsSleep)
    PER = 0.01  # Packet error rate
    PSleepR = 0#0.001408e-3#4.3e-6#3e-6  # Power consumption during sleep mode for reception in watts
    synchronization_on_data_frame_possible = 0  # Boolean indicating if synchronization on data frame is possible
    Esyn = 0  # Energy consumed for synchronization in joules
    Ebattery = 13000  # Initial energy level of the battery in joules
    total_time = Lifetime_cal(ta, tsyn, sa_list[i], MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle,
                              tsSleep, ton, PSleepR, synchronization_on_data_frame_possible, Esyn, Ebattery)
    total_time_inyear_NBIOT= total_time / (3600 * 24 * 365)
   # print(
     #   f"Total time in {'year' if total_time_inyear >= 1 else 'day'}s: {total_time_inyear if total_time_inyear >= 1 else total_time / (3600 * 24)}")
    total_time_inyear_list_NBIoT.append(total_time_inyear_NBIOT)'''



"""LORA
Macpl=250+13
NbSymbPreamble=12.25
Tsymb= 32768
numerator=2100
denominator=48
NySymbol=212
packet_time time=7755093e-3ms
idle time=1s
rxtime=7755093e-3ms
419.604mW in Tx 
	44.064mW in Rx 
	7.104mW for cpu On 
	0.001408mW in sleep mode
	
	
#print("ta_list =", ta_list)
#print("total_time_year_list =", total_time_inyear_list)
	
"""
