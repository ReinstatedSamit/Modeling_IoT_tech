'''    Args:
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

import math
import numpy as np
import matplotlib.pyplot as plt

def BLE_calculate_rx_tx_time(data_size, use_6lo_hc):
    # Upper layer constants
    udp_header_size = 8
    ip_max_size = 1280
    ip_header_size = 40
    lo_hc_header_size = 7

    # Lower layer constants
    phy_overhead_size = 8
    phy_pl_size = 257
    phy_rate = 2000e3
    phy_byte_time = 8 / phy_rate
    mac_header_size = 2
    mac_tail_size = 4
    mac_ifs_time = 0.000150
    mac_ack_time = 0.00004
    lo_first_header_size = 8
    lo_subseq_header_size = 6

    # Calculate IPv6 payload
    if use_6lo_hc > 0:
        ip_over = lo_hc_header_size + udp_header_size
        ip_pl_size = ip_max_size - ip_over
    else:
        ip_over = ip_header_size + udp_header_size
        ip_pl_size = ip_max_size - ip_over

    # Model data transmission
    ip_trans_num = data_size // ip_pl_size
    ip_last_size = data_size % ip_pl_size

    # Calculate number of 6LoWPAN fragments
    lo_trans_num = ip_max_size // (phy_pl_size - (mac_header_size + mac_tail_size + lo_subseq_header_size))
    lo_last_size = ip_max_size % (phy_pl_size - (mac_header_size + mac_tail_size + lo_subseq_header_size)) - 1

    lo_full_frame_cnt = lo_trans_num * ip_trans_num
    last_pack = ip_over + ip_last_size

    if ip_last_size > 0:
        lo_full_frame_cnt += last_pack // (phy_pl_size - (mac_header_size + mac_tail_size + lo_subseq_header_size))

    lo_last_frame_cnt = ip_trans_num
    lo_final_size = last_pack % (phy_pl_size - (mac_header_size + mac_tail_size + lo_subseq_header_size))

    # Calculate timing
    rx_time = 0
    if lo_final_size > 0:
        rx_time = (lo_full_frame_cnt + lo_last_frame_cnt + 1) * (mac_ack_time + (2 * mac_ifs_time))
    else:
        rx_time = (lo_full_frame_cnt + lo_last_frame_cnt) * (mac_ack_time + (2 * mac_ifs_time))

    tx_time = 0
    tx_6lo_last_size = lo_last_size + mac_header_size + mac_tail_size + lo_subseq_header_size + phy_overhead_size
    tx_6lo_final_size = lo_final_size + mac_header_size + mac_tail_size + lo_subseq_header_size + phy_overhead_size

    if lo_final_size > 0:
        tx_time = (265) * phy_byte_time * lo_full_frame_cnt + (tx_6lo_last_size) * phy_byte_time * lo_last_frame_cnt + (
                    tx_6lo_final_size) * phy_byte_time
    else:
        tx_time = (265) * phy_byte_time * lo_full_frame_cnt + (tx_6lo_last_size) * phy_byte_time * lo_last_frame_cnt

    return rx_time, tx_time


def NBIOT_calculate_rx_tx_wait_time(data_size):
    # Upper layer constants
    udp_header_size = 8
    ip_max_size = 1500
    ip_header_size = 40

    ip_over = ip_header_size + udp_header_size
    ip_pl_size = ip_max_size - ip_over

    # Lower layer constants
    phy_tti_time = 0.001
    phy_tb_size = 680

    pdcp_pl_size = 1460
    pdcp_ip_he_comp = 8
    pdcp_he_size = 28

    rlc_he_size = 44
    mac_he_size = 8

    phy_k0_time = 0.008
    phy_n_slots = 4
    phy_min_ack_delay = 0.003
    phy_n_wait = 0
    phy_ul_dl_wait_time = phy_n_wait * phy_tti_time

    # Model data transmission
    ip_pack_num = data_size // ip_pl_size
    ip_last_size = data_size % ip_pl_size

    ip_amount = ip_pack_num * (ip_max_size - ip_header_size) + udp_header_size + ip_last_size

    data_at_pdcp = 0
    if ip_last_size > 0:
        data_at_pdcp = ((ip_amount + ((ip_pack_num + 1) * pdcp_ip_he_comp)) * 8) + (ip_pack_num + 1) * pdcp_he_size
    else:
        data_at_pdcp = ((ip_amount + (ip_pack_num * pdcp_ip_he_comp)) * 8) + (ip_pack_num) * pdcp_he_size

    net_tb_size = phy_tb_size - mac_he_size - rlc_he_size

    tb_num = (data_at_pdcp + net_tb_size - 1) // net_tb_size
    rb_num = phy_n_slots * tb_num

    # Calculate timing
    tx_time = rb_num * phy_tti_time

    wait_time = tb_num * (phy_k0_time + phy_min_ack_delay + phy_ul_dl_wait_time)

    rx_r_time = tb_num * phy_tti_time
    rx_gap_time = (tx_time + rx_r_time + wait_time) // 0.256 * 0.04
    rx_time = rx_r_time + rx_gap_time

    total_delay = tx_time + rx_time + wait_time

    return rx_time, tx_time, wait_time

def LoRa_calculate_rx_tx_wait_time_lora(data_size):
    # Lower layer constants
    skip_header = 0
    low_dr_opt = 0
    coding_rate = 1
    sf_min = 12
    bw_max = 500  # [kHz]
    symbol_time = (2 ** sf_min) / (bw_max * 1000)
    preamble_size = 8  # symbols
    preamble_time = (preamble_size + 4.25) * symbol_time
    lora_pl_size = 222  # [byte]
    lora_he_size = 13  # [byte]
    turnaround_time = 0.00017
    rx_delay = 1
    empty_packet_time = 0.004864
    full_frame_symbols = 8 + max(math.ceil(((8 * (lora_he_size + lora_pl_size)) - (4 * sf_min) + 28 + 16 - (20 * skip_header)) / (4 * (sf_min - (2 * low_dr_opt)))) * (coding_rate + 4), 0)

    # Model data transmission
    app_data_size = data_size

    # Calculate number of symbols per application packet
    mac_frame_num = app_data_size // lora_pl_size
    mac_last_size = app_data_size % lora_pl_size

    last_frame_symbols = 0
    if mac_last_size > 0:
        last_frame_symbols = 8 + max(math.ceil(((8 * (lora_he_size + mac_last_size)) - (4 * sf_min) + 28 + 16 - (20 * skip_header)) / (4 * (sf_min - (2 * low_dr_opt)))) * (coding_rate + 4), 0)

    # Calculate timing
    tx_time = 0
    if mac_last_size > 0:
        tx_time = (mac_frame_num * full_frame_symbols * symbol_time) + (last_frame_symbols * symbol_time) + preamble_time
    else:
        tx_time = mac_frame_num * full_frame_symbols * symbol_time

    rx_time = 0
    if mac_last_size > 0:
        rx_time = (mac_frame_num + 1) * (empty_packet_time + (5 * symbol_time))
    else:
        rx_time = mac_frame_num * (empty_packet_time + (5 * symbol_time))

    wait_time = 0
    if mac_last_size > 0:
        wait_time = (mac_frame_num + 1) * (turnaround_time + rx_delay)
    else:
        wait_time = mac_frame_num * (turnaround_time + rx_delay)

    delay = tx_time + rx_time + wait_time

    return rx_time, tx_time, wait_time


def LC4_calculate_tx_delay(data_size):
    # Upper layer constants
    # udp_max_size = 65535;   % theoretical maximum including the udp header; not used here because one UDP per IP is more realistic for implemenations
    udp_header_size = 8
    ip_max_size = 1500  # MTU is larger than in case of 6Lo
    ip_header_size = 40  #Default IP Header

    ip_over = ip_header_size + udp_header_size
    ip_pl_size = ip_max_size - ip_over

    # Lower layer constants
    phy_tti_time = 0.001
    phy_tb_size = 51024  # bit

    # Values from 2009_larmo -> Table 1, p. 58
    pdcp_pl_size = 1460  # byte (1500-40)
    pdcp_ip_he_comp = 8  # byte
    pdcp_he_size = 28  # bit
    rlc_he_size = 44  # bit
    mac_he_size = 8  # bit

    #Assumed from NBIOT-not given
    phy_k0_time = 0.008
    phy_min_ack_delay = 0.003
    phy_n_wait = 0
    phy_ul_dl_wait_time = phy_n_wait * phy_tti_time

    # Model data transmission
    app_data_size = data_size

    # Calculate number of TTI per application packet
    ip_pack_num = app_data_size // ip_pl_size
    ip_last_size = app_data_size % ip_pl_size

    # Data amount without IP headers replaced by PDCP compressed version
    ip_amount = ip_pack_num * (ip_max_size - ip_header_size) + udp_header_size + ip_last_size

    # Data amount on PDCP layer
    # one packet on pdcp = one ip packet = one udp packet 
    if ip_last_size > 0:
        data_at_pdcp = ((ip_amount + ((ip_pack_num + 1) * pdcp_ip_he_comp)) * 8) + (ip_pack_num + 1) * pdcp_he_size
    else:
        data_at_pdcp = ((ip_amount + (ip_pack_num * pdcp_ip_he_comp)) * 8) + (ip_pack_num) * pdcp_he_size

    # Data amount per TB in bit (RLC, MAC overhead)
    net_tb_size = phy_tb_size - mac_he_size - rlc_he_size

    # Number of TTI > one TB per TTI
    tti_num = math.ceil(data_at_pdcp / net_tb_size)

    # Calculate timing
    tx_time = tti_num * phy_tti_time
    '''
    #assumed as NBIOT_not given
    wait_time = tti_num * (phy_k0_time + phy_min_ack_delay + phy_ul_dl_wait_time)

    rx_r_time = tti_num * phy_tti_time
    rx_gap_time = (tx_time + rx_r_time + wait_time) // 0.256 * 0.04
    rx_time = rx_r_time + rx_gap_time
    '''
    # Total delay for transmission
    delay = tx_time

    return 0, tx_time, 0

def wifiah_calculate_Trx(data_size):
    # Upper layer constants
    udp_header_size = 8
    ip_max_size = 1334
    ip_header_size = 40

    ip_over = ip_header_size + udp_header_size
    ip_pl_size = ip_max_size - ip_over

    # Phy layer constants
    phy_syml_time = 0.00004
    phy_sym_time = phy_syml_time
    phy_bit_per_sym = 78
    n_es = 1
    n_service = 8
    n_tail = 6

    t_stf = 0.00016
    t_ltf1 = 0.00008
    t_sig = 0.00024
    t_ltfn = 0.00004
    n_ltf = 1

    phy_preamble_time = t_stf + t_ltf1 + t_sig + (n_ltf - 1) * t_ltfn

    psdu_max_size = math.floor((511 * phy_bit_per_sym - n_service - (n_tail * n_es)) / 8)

    # Mac layer constants
    msdu_pl_size = 1634
    msdu_over = 14
    msdu_pad_full = 0

    mpdu_max_size = psdu_max_size
    a_mpdu_over = 28

    mpdu_n_msdus = math.floor((mpdu_max_size - a_mpdu_over) / (msdu_over + msdu_pl_size))
    mpdu_size = a_mpdu_over + (mpdu_n_msdus * (msdu_over + msdu_pl_size))

    a_mpdu_n_mpdus = math.floor(psdu_max_size / mpdu_size)
    a_mpdu_size = a_mpdu_n_mpdus * mpdu_size

    mac_rts_sym_n = math.ceil(((8 * 20) + n_service + (n_tail * n_es)) / phy_bit_per_sym)
    mac_full_sym_n = math.ceil(((8 * a_mpdu_size) + n_service + (n_tail * n_es)) / phy_bit_per_sym)

    mac_rts_time = phy_preamble_time + (mac_rts_sym_n * phy_sym_time)
    mac_cts_time = phy_preamble_time
    mac_ack_time = phy_preamble_time
    mac_full_time = phy_preamble_time + (mac_full_sym_n * phy_sym_time)

    mac_slottime = 0.000052
    mac_sifs_time = 0.00016
    mac_difs_time = mac_sifs_time + 2 * mac_slottime

    # Model data transmission
    app_data_size = data_size

    # Calculate number of UDP/IP packets
    ip_trans_num = app_data_size // ip_pl_size
    ip_last_size = app_data_size % ip_pl_size

    # Calculate number of mpdus
    a_msdu_num = 0
    msdu_sf_last_num = 0

    if ip_last_size > 0:
        ip_num = ip_trans_num + 1
        a_msdu_num = ip_num // mpdu_n_msdus
        msdu_sf_last_num = ip_num % mpdu_n_msdus
    else:
        a_msdu_num = ip_trans_num // mpdu_n_msdus
        msdu_sf_last_num = ip_trans_num % mpdu_n_msdus

    last_a_msdu_size = 0

    if ip_last_size > 0:
        if msdu_sf_last_num > 0:
            last_a_msdu_size = a_mpdu_over + ((msdu_sf_last_num - 1) * (msdu_over + msdu_pl_size)) + (
                        msdu_over + ip_over + ip_last_size)
        else:
            a_msdu_num -= 1
            last_a_msdu_size = a_mpdu_over + ((2) * (msdu_over + msdu_pl_size)) + (msdu_over + ip_over + ip_last_size)
    else:
        if msdu_sf_last_num > 0:
            last_a_msdu_size = a_mpdu_over + ((msdu_sf_last_num) * (msdu_over + msdu_pl_size))

    psdu_num = 0
    psdu_msdu_last_num = 0

    if last_a_msdu_size > 0:
        psdu_num = a_msdu_num
        psdu_msdu_last_num = 1
    else:
        psdu_num = a_msdu_num

    last_psdu_size = 0

    if psdu_msdu_last_num > 0:
        if last_a_msdu_size > 0:
            last_psdu_size = ((psdu_msdu_last_num - 1) * mpdu_size) + last_a_msdu_size
        else:
            last_psdu_size = (psdu_msdu_last_num * mpdu_size)
    else:
        if last_a_msdu_size > 0:
            last_psdu_size = last_a_msdu_size

    mac_last_sym_n = 0
    mac_last_time = 0

    if last_psdu_size > 0:
        mac_last_sym_n = math.ceil(((8 * last_psdu_size) + n_service + (n_tail * n_es)) / phy_bit_per_sym)
        mac_last_time = phy_preamble_time + (mac_last_sym_n * phy_sym_time)

    rx_time = 0

    if mac_last_time > 0:
        rx_time = (psdu_num + 1) * (mac_difs_time + (3 * mac_sifs_time) + mac_cts_time + mac_ack_time)
    else:
        rx_time = psdu_num * (mac_difs_time + (3 * mac_sifs_time) + mac_cts_time + mac_ack_time)

    tx_time = 0

    if mac_last_time > 0:
        if psdu_num >= 1:
            tx_time = (psdu_num * mac_rts_time) + ((psdu_num) * mac_full_time) + mac_last_time
        else:
            tx_time = mac_rts_time + mac_last_time
    else:
        tx_time = psdu_num * (mac_rts_time + mac_full_time)

    delay = rx_time + tx_time
    #print ("Delay:",delay)

    return rx_time, tx_time



def ComputeEnergyToSendData_v2(sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle, ta):
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
    tTx = tsTx * Ntr
    tRx = tsRx * Ntr
    tIdle = tsIdle * Ntr
    tSleep = tsSleep * Ntr
    #print("tTx time",tTx)
    # Calculate energy consumption for data transmission
    Eactivetrans = (PTx * tTx + PRx * tRx + PIdle * tIdle)
    #print("Eactivwe", Eactivetrans)
    Esleep = (PSleep * tSleep)
    #print("Esleep",Esleep)
    Edata = Eactivetrans + Esleep
    #print("Consumed Energy in sending data", Edata)
    return Edata



def calculate_solar_harvested_energy_perday(irradiance, panel_area, sunlight_hours, efficiency):
    # Convert irradiance to kW/m^2
    irradiance_kW_per_m2 = irradiance / 1000

    # Calculate energy harvested in kWh
    harvested_energy_kWh = efficiency * irradiance_kW_per_m2 * panel_area * sunlight_hours
    harvested_energy_J = (harvested_energy_kWh*1000*3600)
    return harvested_energy_J


def Lifetime_cal(ta, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle, Ebattery):
    """
    Compute the lifetime of the system.

    Returns:
    float: Lifetime of the system in seconds.
    """
    consumed_energy = ComputeEnergyToSendData_v2(sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle, ta)
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


def Lifetime_cal_with_solarpanel(ta, sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx,
                                 tsIdle, Ebattery, irradiance, panel_area, sunlight_hours, efficiency):
    """
    Compute the lifetime of the system.

    Returns:
    float: Lifetime of the system in seconds.
    """
    consumed_energy = ComputeEnergyToSendData_v2(sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle, ta)
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
            #print("Len_Temp_lifetime", len(temp_lifetime_list))

        #print("lifetime:",Lifetime/86400)
        #print("Energy",E)
        Lifetime = Lifetime + ta

        if (Lifetime > 86400*365*50):
            print("Lifetime exceeds 50 year")
            return Lifetime


    return Lifetime
                                     
   
#Pararmeter Initialization

ta_list = [60, 900, 1800, 3600, 7200, 10800, 14400, 21600, 43200, 86400] # in seconds
total_time_inyear_list_loRA = []
total_time_inyear_list_BLE = []
total_time_inyear_list_NBIoT = []
total_time_inyear_list_LTECAT4 = []
total_time_inyear_list_BLE_with_solar_panel = []
sa_list = [1000, 10000, 22500, 90000, 140625, 562500] # Compressed image sizes in bytes
PER = 0  # 0.01  # Packet error rate
Ebattery = 13000  # Initial energy level of the battery in joules
irradiance = 400  # Irradiance in W/m^2 (STC)
panel_area = 0.0033  # Panel area in m^2
sunlight_hours = 3  # Sunlight hours
efficiency = 0.2  # Solar panel efficiency (assume 15% for example)


# BLE
for j in range (len(sa_list)):
    for i in range(len(ta_list)):
        # print('sa', sa_list[i])
        MaxDataPacketSize = 1245  # (BLE)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
        PTx = 24e-3  # (BLE)  # Power consumption
        PRx = 20e-3  # (BLE)  # Power consumption
        PIdle = 5e-3  # (BLE)# Power consumption
        PSleep = 3e-6  # (BLE)  # Power consumption
        tsRx, tsTx = BLE_calculate_rx_tx_time(sa_list[j], 1)

        tsIdle = 0  # Idle time in seconds counted in Rx and Tx
        total_time = Lifetime_cal(ta_list[i], sa_list[j], MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx,
                                  tsIdle, Ebattery)
        total_time_inyear_BLE = total_time / (3600 * 24)
        total_time_inyear_list_BLE.append(total_time_inyear_BLE)
    # total_time_with_Solar_panel = Lifetime_cal_with_solarpanel(ta, tsyn, sa_list[i], MaxDataPacketSize, PTx, PRx, PIdle,
    # PSleep, PER, tsTx, tsRx, tsIdle,synchronization_on_data_frame_possible,
    # Esyn, Ebattery, irradiance, panel_area, sunlight_hours, efficiency)
    # total_time_inyear_list_BLE_with_solar_panel.append(total_time_with_Solar_panel / (3600 * 24))
    plt.plot(np.array(ta_list) / 3600, total_time_inyear_list_BLE, label=f"BLE_sa_{j}", marker='o', linestyle='-')
    total_time_inyear_list_BLE.clear()
print("total_time_inday_list_BLE", total_time_inyear_list_BLE)



#NBIOT
for j in range (len(sa_list)):
    for i in range(len(ta_list)):
        MaxDataPacketSize = 1500  # (BLE)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
        PTx = 543e-3  # 24e-3(BLE)  # Power consumption
        PRx = 90e-3  # 20e-3(BLE)  # Power consumption
        PIdle = 2.4e-3  # 5e-3  (BLE)# Power consumption
        PSleep = 0.015e-3  # 3e-6(BLE)  # Power consumption
        tsRx, tsTx, tsIdle = NBIOT_calculate_rx_tx_wait_time(sa_list[j])
        total_time = Lifetime_cal(ta_list[i], sa_list[j], MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx,
                                  tsIdle, Ebattery)
        total_time_inyear_NBIOT = total_time / (3600 * 24)
        total_time_inyear_list_NBIoT.append(total_time_inyear_NBIOT)
# total_time_with_Solar_panel = Lifetime_cal_with_solarpanel(ta, tsyn, sa_list[i], MaxDataPacketSize, PTx, PRx, PIdle,
# PSleep, PER, tsTx, tsRx, tsIdle,synchronization_on_data_frame_possible,
# Esyn, Ebattery, irradiance, panel_area, sunlight_hours, efficiency)
# total_time_inyear_list_BLE_with_solar_panel.append(total_time_with_Solar_panel / (3600 * 24))
    plt.plot(np.array(ta_list) / 3600, total_time_inyear_list_NBIoT, label=f"NBIOT_sa_{j}", marker='v', linestyle='-')
    total_time_inyear_list_NBIoT.clear()

print("total_time_inday_list_NBIOT", total_time_inyear_list_NBIoT)

#LORA
for j in range(len(sa_list)):
    for i in range(len(ta_list)):
        MaxDataPacketSize = 250  # Maximum size of a data packet in bytes
        PTx = 419.604e-3  # Power consumption
        PRx = 44.064e-3  # Power consumption
        PIdle = 3e-6  # Power consumption
        PSleep = 0.04e-6  # Power consumption
        tsRx, tsTx, tsIdle = LoRa_calculate_rx_tx_wait_time_lora(sa_list[j])
        total_time = Lifetime_cal(ta_list[i], sa_list[j], MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx,
                                  tsIdle, Ebattery)
        total_time_inyear_lora = total_time / (3600 * 24)
        total_time_inyear_list_loRA.append(total_time_inyear_lora)
# total_time_with_Solar_panel = Lifetime_cal_with_solarpanel(ta, tsyn, sa_list[i], MaxDataPacketSize, PTx, PRx, PIdle,
# PSleep, PER, tsTx, tsRx, tsIdle,synchronization_on_data_frame_possible,
# Esyn, Ebattery, irradiance, panel_area, sunlight_hours, efficiency)
# total_time_inyear_list_BLE_with_solar_panel.append(total_time_with_Solar_panel / (3600 * 24))
    plt.plot(np.array(ta_list) / 3600, total_time_inyear_list_loRA, label=f"LORA_sa_{j}", marker='*', linestyle='-')
    total_time_inyear_list_loRA.clear()

print("total_time_inday_list_LORA", total_time_inyear_list_loRA)
#print("total_time_in_DAY_list_BLE", total_time_inyear_list_BLE_with_solar_panel)



#LTECAT 4
for j in range (len(sa_list)):
    for i in range(len(ta_list)):
        # print('sa', sa_list[i])
        MaxDataPacketSize = 1500  # (BLE)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
        PTx = 2.318  # Power consumption
        PRx = 0.1178  # as iactive# Power consumption
        PIdle = 0.01026  # asidle Power consumption
        PSleep = 0.000057  # 3e-6(BLE)  # Power consumption
        tsRx, tsTx, tsIdle = NBIOT_calculate_rx_tx_wait_time(sa_list[j])
        total_time = Lifetime_cal(ta_list[i], sa_list[j], MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx,
                                  tsIdle, Ebattery)
        total_time_inyear_LTECAT4 = total_time / (3600 * 24)
        total_time_inyear_list_LTECAT4.append(total_time_inyear_LTECAT4)
# total_time_with_Solar_panel = Lifetime_cal_with_olarpanel(ta, tsyn, sa_list[i], MaxDataPacketSize, PTx, PRx, PIdle,
# PSleep, PER, tsTx, tsRx, tsIdle,synchronization_on_data_frame_possible,
# Esyn, Ebattery, irradiance, panel_area, sunlight_hours, efficiency)
# total_time_inyear_list_BLE_with_solar_panel.append(total_time_with_Solar_panel / (3600 * 24))
    plt.plot(np.array(ta_list) / 3600, total_time_inyear_list_LTECAT4, label=f"L.C.4_sa_{j}", marker='d', linestyle='-')
    total_time_inyear_list_LTECAT4.clear()

print("total_time_inday_list_LTECAT4", total_time_inyear_list_LTECAT4)


#WiFi_ah
for j in range (len(sa_list)):
    for i in range(len(ta_list)):
        # print('sa', sa_list[i])
        MaxDataPacketSize = 1245  # (BLE)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
        PTx = 0.0072    # Power consumption
        PRx = 0.0044   # Power consumption
        PIdle = 0  # Power consumption
        PSleep = 1.5e-3  #   # Power consumption
        tsRx, tsTx = wifiah_calculate_Trx(sa_list[j])
        tsIdle = 0  # Idle time in seconds counted in Rx and Tx
        total_time = Lifetime_cal(ta_list[i], sa_list[j], MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx,
                                  tsIdle, Ebattery)
        total_time_inyear_WiFiah = total_time / (3600 * 24*365)
        total_time_inyear_list_WiFiah.append(total_time_inyear_WiFiah)
    # total_time_with_Solar_panel = Lifetime_cal_with_solarpanel(ta, tsyn, sa_list[i], MaxDataPacketSize, PTx, PRx, PIdle,
    # PSleep, PER, tsTx, tsRx, tsIdle,synchronization_on_data_frame_possible,
    # Esyn, Ebattery, irradiance, panel_area, sunlight_hours, efficiency)
    # total_time_inyear_list_BLE_with_solar_panel.append(total_time_with_Solar_panel / (3600 * 24))
    #plt.plot(np.array(ta_list) / 3600, total_time_inyear_list_WiFiah, label=f"WiFiah_{j}", marker='x', linestyle='-')
    plt.plot((24/(np.array(ta_list) / 3600))[::-1], total_time_inyear_list_WiFiah[::-1], label=f"WiFiah_{Label[j]}", marker='x', linestyle=f'{Linestyle[j]}',  color=color[6])
    total_time_inyear_list_WiFiah.clear()
#print("total_time_inday_list_BLE", total_time_inyear_list_BLE)

plt.xlabel('Different application time in Hour')
plt.ylabel('Lifetime in DAYS')
plt.legend(loc='upper right',bbox_to_anchor=(1.135, 1),fontsize=5)
plt.grid(True, linewidth=0.25, alpha=0.5)
plt.savefig('4Tech_.png')
plt.show()
