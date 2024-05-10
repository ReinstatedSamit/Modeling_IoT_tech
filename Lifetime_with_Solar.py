'''Args:
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
    irradiance (float): Solar irradiance in W/m^2.
    panel_area (float): Area of the solar panel in m^2.
    sunlight_hours (float): Number of sunlight hours per day.
    efficiency (float): Efficiency of the solar panel.'''

import numpy as np
import matplotlib.pyplot as plt


def ComputeEnergyToSendData(sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle, ta):
    """
    Compute the energy consumed to send data.
    Returns:
    float: Energy consumed in sending data in joules.
    """
    # Calculate number of packets
    NPackets = int(sa / MaxDataPacketSize)
    LastPacket = sa % MaxDataPacketSize
    if LastPacket != 0:
        NPackets += 1
    #print("Npackets:", NPackets)
    # Calculate total transmission time for each state
    tsSleep= ta-( tsTx+ tsRx+ tsIdle)
    Ntr = (1 / (1 - PER))  # Number of transmissions
    tTx = sum([tsTx for _ in range(NPackets)]) * Ntr
    tRx = sum([tsRx for _ in range(NPackets)]) * Ntr
    tIdle = sum([tsIdle for _ in range(NPackets)]) * Ntr
    tSleep = sum([tsSleep for _ in range(NPackets)]) * Ntr
    #print("tTx time",tTx)
    # Calculate energy consumption for data transmission
    Eactivetrans = (PTx * tTx + PRx * tRx + PIdle * tIdle)
    Esleep = (PSleep * tSleep)
    Edata = Eactivetrans + Esleep
    #print("Consumed Energy in sending data", Edata)
    return Edata


def ComputeEnergyInSleepMode(ta, ton, PSleepR):
    """
    Compute the energy consumed in sleep mode.
    Returns:
    float: Energy consumed in sleep mode in joules.
    """
    # Compute the energy consumed in sleep mode
    EnergySleep = PSleepR * (ta - ton)
    #print("Energy_sleep", EnergySleep)
    return EnergySleep  # Energy in joules


def ConsumedEnergy(ta, tsyn, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle, synchronization_on_data_frame_possible, Esyn):
    """
    Compute the total energy consumed.
    Returns:
    float: Total energy consumed in joules.
    """
    Edata = ComputeEnergyToSendData(sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle,ta)

    if ta < tsyn:
        Nsyn = 1
    else:
        Nsyn = ta / tsyn

    if synchronization_on_data_frame_possible:
        NdataSyn = 1
    else:
        NdataSyn = 0

    #Esleep = ComputeEnergyInSleepMode(ta, ton, PsleepR)

    Etot = Edata + (Nsyn - NdataSyn) * Esyn   # + Esleep
   # print("Total energy consumed ", Etot)
    return Etot


def calculate_solar_harvested_energy_perday(irradiance, panel_area, sunlight_hours, efficiency):
    # Convert irradiance to kW/m^2
    irradiance_kW_per_m2 = irradiance / 1000

    # Calculate energy harvested in kWh
    harvested_energy_kWh = efficiency * irradiance_kW_per_m2 * panel_area * sunlight_hours
    harvested_energy_J = (harvested_energy_kWh*1000*3600)
    return harvested_energy_J


def calculate_solar_harvested_energy_daily(harvested_energy_perday_J, Lifetime_seconds):
    if Lifetime_seconds < 24 * 3600:
        return 0
    else:
        return harvested_energy_perday_J * int(Lifetime_seconds / (24 * 3600))


def Lifetime_cal(ta, tsyn, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle, synchronization_on_data_frame_possible, Esyn, Ebattery):
    """
    Compute the lifetime of the system.
    Returns:
    float: Lifetime of the system in seconds.
    """
    consumed_energy = ConsumedEnergy(ta, tsyn, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle,
                                    synchronization_on_data_frame_possible, Esyn)
    print("consumed_energy", consumed_energy)
    gamma_leak = 0.05 * ta / 31536000  # 5% leakage factor (years)
    E = Ebattery  # Initial energy level
    Lifetime = 0
    Eleak = Ebattery * gamma_leak  # Energy lost due to leakage (joules)
    #print("Eleak: ", Eleak)

    while E > 0.1 * Ebattery:  # While energy is above 10% of initial energy
        E = E - consumed_energy - Eleak
        Lifetime = Lifetime + ta
    return Lifetime


def Lifetime_cal_with_solarpanel(ta, tsyn, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx,
                                 tsIdle, synchronization_on_data_frame_possible, Esyn,
                                 Ebattery, irradiance, panel_area, sunlight_hours, efficiency):
    """
    Compute the lifetime of the system.
    Returns:
    float: Lifetime of the system in seconds.
    """
    consumed_energy = ConsumedEnergy(ta, tsyn, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx,
                                     tsRx, tsIdle, synchronization_on_data_frame_possible,
                                     Esyn)
    print("consumed_energy",consumed_energy)
    gamma_leak = 0.05 * ta / 31536000  # 5% leakage factor (years)
    E = Ebattery  # Initial energy level
    Lifetime = 0
    Eleak = Ebattery * gamma_leak  # Energy lost due to leakage (joules)

    # Calculate harvested energy
    harvested_energy_perday = calculate_solar_harvested_energy_perday(irradiance, panel_area, sunlight_hours,
                                                                      efficiency)
    print("Harvested_ebergy_per_day",harvested_energy_perday)
    #print("harvested_energy_per_day in Joule",harvested_energy_perday)
    #harvested_energy=calculate_solar_harvested_energy_daily(harvested_energy_perday, Lifetime_n_1)
    E_remaining= E
    temp_lifetime_list=[]
    while E > 0.1 * Ebattery:  # While energy is above 10% of initial energy
        E = E - consumed_energy - Eleak

        temp_lifetime_list.append(Lifetime)
        # Check if a day has passed
        if (temp_lifetime_list[-1]-temp_lifetime_list[0]) >= 86400:
            #E = E + (E - Ebattery)
            E=E+harvested_energy_perday
            counter+=1
            temp=temp_lifetime_list[-1]
            temp_lifetime_list.clear()
            temp_lifetime_list.append(temp)
            #print("Len_Temp_lifetime", len(temp_lifetime

        Lifetime = Lifetime + ta

        if (Lifetime > 86400*365*50):
            print("Lifetime exceeds 50 year")
            return Lifetime


    return Lifetime


# sa_list = [0.001,0.01,0.1,1,10,100, 1000, 10000, 100000, 1000000] # Total time in seconds
ta_list = [100, 1000, 10000, 100000, 1000000, 10000000]
ta_list_one = [3600 * 24]
total_time_inyear_list_loRA = []
total_time_inyear_list_BLE = []
total_time_inyear_list_NBIoT = []
total_time_inyear_list_BLE_with_solar_panel = []
sa_list = [562500]#225000, 900000, 1406250, 5625000]

sa_list_BLE = [5625000]
# BLE
for i in range(len(sa_list)):
    #print('sa', sa_list[i])
    tsyn = 32  # Time for synchronization in seconds
    ta = 1000 # 8#15*60  # Size of data in bytes
    MaxDataPacketSize = 245  # (BLE)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
    PTx = 24e-3  # (BLE)  # Power consumption
    PRx = 20e-3  # (BLE)  # Power consumption
    PIdle = 5e-3  # (BLE)# Power consumption
    PSleep = 3e-6  # (BLE)  # Power consumption
    tsTx = 1080e-6  # (BLE)#(2193e-3)*245/100#1080e-6(BLE)  # Transmission time in seconds
    tsRx = 400e-6  # (BLE)#400e-6#400e-6  (BLE)# Reception time in seconds
    tsIdle = 1080e-6  # Idle time in seconds
    #ton = tsTx + tsRx + tsIdle
    #tsSleep = ta - ton  # Sleep time in seconds
    #print("tsSleep", tsSleep)
    PER = 0.01  # Packet error rate
    PSleepR = 0  # 0.001408e-3#4.3e-6#3e-6  # Power consumption during sleep mode for reception in watts
    synchronization_on_data_frame_possible = 0  # Boolean indicating if synchronization on data frame is possible
    Esyn = 0  # Energy consumed for synchronization in joules
    Ebattery = 13000  # Initial energy level of the battery in joules
    irradiance = 400  # Irradiance in W/m^2 (STC)
    panel_area = 0.0033  # Panel area in m^2
    sunlight_hours = 3  # Sunlight hours
    efficiency = 0.2  # Solar panel efficiency (assume 15% for example)
    total_time = Lifetime_cal(ta, tsyn, sa_list[i], MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx,
                              tsIdle, synchronization_on_data_frame_possible, Esyn, Ebattery)
    total_time_inyear_BLE = total_time / (3600 * 24)
    total_time_inyear_list_BLE.append(total_time_inyear_BLE)
    total_time_with_Solar_panel = Lifetime_cal_with_solarpanel(ta, tsyn, sa_list[i], MaxDataPacketSize, PTx, PRx, PIdle,
                                                               PSleep, PER, tsTx, tsRx, tsIdle,synchronization_on_data_frame_possible,
                                                               Esyn, Ebattery, irradiance, panel_area, sunlight_hours, efficiency)
    total_time_inyear_list_BLE_with_solar_panel.append(total_time_with_Solar_panel / (3600 * 24))


print("total_time_inday_list_BLE", total_time_inyear_list_BLE)
print("total_time_in_DAY_list_BLE", total_time_inyear_list_BLE_with_solar_panel)
'''plt.plot(np.array(sa_list) / 1000, total_time_inyear_list_BLE, label="BLE", marker='o', linestyle='-')
plt.plot(np.array(sa_list) / 1000, total_time_inyear_list_BLE_with_solar_panel, label="BLE_solarpanel", marker='o',
         linestyle='-')
plt.xlabel('Different size of images in KB each DAY')
plt.ylabel('Lifetime in DAYS')
plt.legend()
plt.grid(True, linewidth=0.25, alpha=0.5)
plt.show()
'''

