import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

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
    sf_min = 7#12#12
    bw_max = 500  # [kHz]
    symbol_time = (2 ** sf_min) / (bw_max * 1000)
    preamble_size = 8  # symbols
    preamble_time = (preamble_size + 4.25) * symbol_time
    lora_pl_size = 222  # [byte]
    lora_he_size = 13  # [byte]
    turnaround_time = 0.00017
    rx_delay = 1
    empty_packet_time = 0.004864
    full_frame_symbols = 8 + max(math.ceil(
        ((8 * (lora_he_size + lora_pl_size)) - (4 * sf_min) + 28 + 16 - (20 * skip_header)) / (
                    4 * (sf_min - (2 * low_dr_opt)))) * (coding_rate + 4), 0)

    # Model data transmission
    app_data_size = data_size

    # Calculate number of symbols per application packet
    mac_frame_num = app_data_size // lora_pl_size
    mac_last_size = app_data_size % lora_pl_size

    last_frame_symbols = 0
    if mac_last_size > 0:
        last_frame_symbols = 8 + max(math.ceil(
            ((8 * (lora_he_size + mac_last_size)) - (4 * sf_min) + 28 + 16 - (20 * skip_header)) / (
                        4 * (sf_min - (2 * low_dr_opt)))) * (coding_rate + 4), 0)

    # Calculate timing
    tx_time = 0
    if mac_last_size > 0:
        tx_time = (mac_frame_num * full_frame_symbols * symbol_time) + (
                    last_frame_symbols * symbol_time) + preamble_time
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
    udp_header_size = 8
    ip_max_size = 1500  # MTU is larger than in case of 6Lo
    ip_header_size = 40

    ip_over = ip_header_size + udp_header_size
    ip_pl_size = ip_max_size - ip_over

    # Lower layer constants
    phy_tti_time = 0.001
    phy_tb_size = 51024  # bit

    # Values from 2009_larmo -> Table 1, p. 58
    pdcp_pl_size = 1460  # byte
    pdcp_ip_he_comp = 8  # byte
    pdcp_he_size = 28  # bit
    rlc_he_size = 44  # bit
    mac_he_size = 8  # bit

    # Assumed-not given
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


def LT1_calculate_tx_time(data_size):
    udp_header_size = 8
    ip_max_size = 1500
    ip_header_size = 40
    ip_over = ip_header_size + udp_header_size
    ip_pl_size = ip_max_size - ip_over

    pdcp_pl_size = 1460
    pdcp_ip_he_comp = 8
    pdcp_he_size = 28

    rlc_he_size = 44
    mac_he_size = 8

    phy_tti_time = 0.001
    phy_tb_size = 5160

    ip_pack_num = data_size // ip_pl_size
    ip_last_size = data_size % ip_pl_size

    ip_amount = ip_pack_num * (ip_max_size - ip_header_size) + udp_header_size + ip_last_size

    data_at_pdcp = 0

    if ip_last_size > 0:
        data_at_pdcp = ((ip_amount + ((ip_pack_num + 1) * pdcp_ip_he_comp)) * 8) + (ip_pack_num + 1) * pdcp_he_size
    else:
        data_at_pdcp = ((ip_amount + (ip_pack_num * pdcp_ip_he_comp)) * 8) + (ip_pack_num) * pdcp_he_size

    net_tb_size = phy_tb_size - mac_he_size - rlc_he_size

    tti_num = math.ceil(data_at_pdcp / net_tb_size)

    tx_time = tti_num * phy_tti_time

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
    # print ("Delay:",delay)

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



def ComputeEnergyToSendData_v3(sa, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle, ta):
    """
    Compute the energy consumed to send data.
    Returns:
    float: Energy consumed in sending data in joules.
    """
    # Calculate number of packets
    NPackets = math.ceil(sa / MaxDataPacketSize)
    LastPacket = sa % MaxDataPacketSize
    if LastPacket != 0:
        NPackets += 1
    print("Npackets:", NPackets)
    # Calculate total transmission time for each state

    Ntr = (1 / (1 - PER))  # Number of transmissions
    tTx = tsTx * Ntr*NPackets
    tRx = tsRx * Ntr*NPackets
    tIdle = tsIdle * Ntr*NPackets
    tsSleep = ta - (tTx + tRx + tIdle)
    tSleep = tsSleep * Ntr

    print("Transmit Time:",tTx)
    print("Recieve Time:",tRx)
    print("Wait Time:",tIdle)
    print("Delay:",tTx + tRx + tIdle)
    print("Sleep time:",tSleep)
    # print("tTx time",tTx)
    # Calculate energy consumption for data transmission
    Eactivetrans = (PTx * tTx + PRx * tRx + PIdle * tIdle)
    # print("Eactivwe", Eactivetrans)
    Esleep = (PSleep * tSleep)
    # print("Esleep",Esleep)
    Edata = Eactivetrans + Esleep
    # print("Consumed Energy in sending data", Edata)
    return Edata
# Parameter Value

def ta_to_dutycycle(ta,tsTx, tsRx, tsIdle):
    tactive = tsTx+tsRx+tsIdle
    tsleep = ta - tactive
    Tduty= tactive/(tsleep+ tactive)*100


    return Tduty

def lux_to_irradiance(lux, light_source='sunlight'):
    """
    Convert illuminance in lux to irradiance in W/m² based on the light source.

    Parameters:
    lux (float): Illuminance in lux
    light_source (str): Type of light source ('sunlight' or 'incandescent')

    Returns:
    float: Irradiance in W/m²
    """
    # Conversion factors for different light sources
    conversion_factors = {
        'sunlight': 0.0079,  # W/m² per lux for sunlight
        'incandescent': 0.00146  # W/m² per lux for incandescent light
    }

    # Check if the light source is valid
    if light_source not in conversion_factors:
        raise ValueError("Invalid light source. Use 'sunlight' or 'incandescent'.")

    # Get the conversion factor for the given light source
    factor = conversion_factors[light_source]

    # Calculate irradiance
    irradiance = lux * factor

    return irradiance

def calculate_solar_harvested_energy_perday(irradiance, panel_area, sunlight_hours, efficiency):
    # Convert irradiance to kW/m^2
    irradiance_kW_per_m2 = irradiance / 1000

    # Calculate energy harvested in kWh
    harvested_energy_kWh = efficiency * irradiance_kW_per_m2 * panel_area * sunlight_hours
    harvested_energy_J = (harvested_energy_kWh*1000*3600)
    return harvested_energy_J







# Parameter Value

#ta = 10000
# sa_list = [0.001,0.01,0.1,1,10,100, 1000, 10000, 100000, 1000000] # Total time in seconds
ta_list = [90 ,180, 900, 1800, 3600, 7200, 10800, 14400, 21600, 43200,
           86400]  # [60, 900, 1800, 3600, 7200, 10800, 14400, 21600, 43200, 86400]
ta_list_one = [3600 * 24]
consumed_energy_BLE=[]
consumed_energy_loRa=[]
consumed_energy_NBIOT=[]
consumed_energy_LTECAT4=[]
consumed_energy_WiFiah=[]
total_time_inyear_list_NBIOT_with_solar_panel = []
#Resolution=['VGA','VGA']
Resolution=[' QQQQVGA',' QQQQVGA','QQVGA','QQVGA','QVGA','QVGA','VGA','VGA','SVGA','SVGA','UXGA','UXGA']
sa_list = [3.6e3,3.6e3,56.25e2,56.25e3,225e2,225e3,900e2,900e3,1406.25e2,1406.25e3,5625e2,5625e3]  # [20e3]#[1000, 10000, 22500, 90000, 140625, 562500]
#sa_list=[900e2,900e3]
PER = 0  # 0.01  # Packet error rate

Label = ['Compressed', 'UnCompressed']
Linestyle = ['-', '--',':','-.']
color = ['black', 'navy', 'red', 'purple', 'teal', 'cyan', 'green','darkorange','magenta','blue','orange','#1f77b4']
Dcell_Eperday= (97200*0.90/(3*365))
AA_Eperday=(16000*0.90/(7*365))
AAA_Eperday=(64800*0.90/(7*365))
CR2032_Eperday=(2430*0.90/(5*365))


lux_value = 40e3#29600#40e3
irradiance_sunlight = lux_to_irradiance(lux_value, 'sunlight')
irradiance_incandescent = lux_to_irradiance(lux_value/2, 'incandescent')

panel_area = 0.00159 #53mmx30mm Panel area in m^2
sunlight_hours = 3  # Sunlight hours
efficiency = 0.2  # Solar panel efficiency (assume 15% for example)

Outdoor_solar=calculate_solar_harvested_energy_perday(irradiance_sunlight, panel_area, sunlight_hours, efficiency)
Indoor_solar= calculate_solar_harvested_energy_perday(irradiance_incandescent, panel_area, sunlight_hours, efficiency)
print(f"Irradiance for {lux_value} lux under sunlight: {irradiance_sunlight} W/m²")
print(f"Irradiance for {lux_value/2} lux under incandescent light: {irradiance_incandescent} W/m²")

print(f"Solar energy per day for {lux_value} lux under sunlight: {Outdoor_solar} J")
print(f"Solar energy per day for {lux_value} lux under incandescent light: {Indoor_solar} J")
#print(f"Irradiance for {lux_value} lux under incandescent light: {irradiance_incandescent} W/m²")




for k in range(0,len(Resolution),2):
    # BLE
    for j in range(k,k+1):
        print('sa', sa_list[j])
        for i in range(len(ta_list)):
            # print('sa', sa_list[i])
            MaxDataPacketSize = 1245  # (BLE)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
            PTx = 24e-3  # (BLE)  # Power consumption
            PRx = 20e-3  # (BLE)  # Power consumption
            PIdle = 5e-3  # (BLE)# Power consumption
            PSleep = 3e-6  # (BLE)  # Power consumption
            tsRx, tsTx = BLE_calculate_rx_tx_time(sa_list[j], 1)
            tsIdle = 0  # Idle time in seconds counted in Rx and Tx
            consumed_energy_BLE.append(
                86400 / ta_list[i] * ComputeEnergyToSendData_v3(sa_list[j], MaxDataPacketSize, PTx, PRx, PIdle, PSleep,
                                                                PER, tsTx, tsRx,
                                                                tsIdle, ta_list[i]))

        BLE_plot=plt.plot((86400 / np.array(ta_list))[::-1], consumed_energy_BLE[::-1], label=f"BLE_{Label[j-k]}",
                 marker='o', linestyle=f'{Linestyle[j-k]}', color=color[1])
        consumed_energy_BLE.clear()

    # NBIOT
    for j in range(k,k+1):
        for i in range(len(ta_list)):
            MaxDataPacketSize = 1500  # (BLE)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
            PTx = 543e-3  # 24e-3(BLE)  # Power consumption
            PRx = 90e-3  # 20e-3(BLE)  # Power consumption
            PIdle = 2.4e-3  # 5e-3  (BLE)# Power consumption
            PSleep = 0.015e-3  # 3e-6(BLE)  # Power consumption
            tsRx, tsTx, tsIdle = NBIOT_calculate_rx_tx_wait_time(sa_list[j])
            consumed_energy_NBIOT.append(
                86400 / ta_list[i] * ComputeEnergyToSendData_v3(sa_list[j], MaxDataPacketSize, PTx, PRx, PIdle, PSleep,
                                                                PER, tsTx, tsRx,
                                                                tsIdle, ta_list[i]))

        NBIOT_plot=plt.plot((86400 / np.array(ta_list))[::-1], consumed_energy_NBIOT[::-1], label=f"NBIOT_{Label[j-k]}",
                 marker='v', linestyle=f'{Linestyle[j-k]}', color=color[2])
        consumed_energy_NBIOT.clear()

    # print("total_time_inday_list_NBIOT", total_time_inyear_list_NBIoT)

    # LORA
    for j in range(k,k+1):
        for i in range(len(ta_list)):
            MaxDataPacketSize = 250  # Maximum size of a data packet in bytes
            PTx = 419.604e-3  # 2*0.028#419.604e-3  # Power consumption
            PRx = 44.064e-3  # 2*0.0138#44.064e-3  # Power consumption
            PIdle = 3e-6  # Power consumption
            PSleep = 0.04e-6  # Power consumption
            tsRx, tsTx, tsIdle = LoRa_calculate_rx_tx_wait_time_lora(sa_list[j])
            consumed_energy_loRa.append(
                86400 / ta_list[i] * ComputeEnergyToSendData_v3(sa_list[j], MaxDataPacketSize, PTx, PRx, PIdle, PSleep,
                                                                PER, tsTx, tsRx,
                                                                tsIdle, ta_list[i]))

        Lora_plot=plt.plot((86400 / np.array(ta_list))[::-1], consumed_energy_loRa[::-1], label=f"LORA_{Label[j-k]}",
                 marker='*', linestyle=f'{Linestyle[j-k]}', color=color[3])
        consumed_energy_loRa.clear()

    # LTECAT 4
    for j in range(k,k+1):
        for i in range(len(ta_list)):
            # print('sa', sa_list[i])
            MaxDataPacketSize = 1500  # (BLE)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
            PTx = 2.318  # Power consumption
            PRx = 0.1178  # as iactive# Power consumption
            PIdle = 0.01026  # asidle Power consumption
            PSleep = 0.00494  # 3e-6(BLE)  # Power consumption
            tsRx, tsTx, tsIdle = LT1_calculate_tx_time(sa_list[j])
            consumed_energy_LTECAT4.append(
                86400 / ta_list[i] * ComputeEnergyToSendData_v3(sa_list[j], MaxDataPacketSize, PTx, PRx, PIdle, PSleep,
                                                                PER, tsTx, tsRx,
                                                                tsIdle, ta_list[i]))

        LTECAT4_plot=plt.plot((86400 / np.array(ta_list))[::-1], consumed_energy_LTECAT4[::-1], label=f"L.C.4_{Label[j-k]}",
                 marker='d', linestyle=f'{Linestyle[j-k]}', color=color[4])
        consumed_energy_LTECAT4.clear()

    # WiFi_ah
    for j in range(k,k+1):
        for i in range(len(ta_list)):
            # print('sa', sa_list[i])
            MaxDataPacketSize = 1245  # (BLE)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
            PTx = 255e-3  # 0.0072    # Power consumption
            PRx = 135e-3  # 0.0044   # Power consumption
            PIdle = 0  # Power consumption
            PSleep = 1.5e-3  # # Power consumption
            tsRx, tsTx = wifiah_calculate_Trx(sa_list[j])
            tsIdle = 0  # Idle time in seconds counted in Rx and Tx
            consumed_energy_WiFiah.append(
                86400 / ta_list[i] * ComputeEnergyToSendData_v3(sa_list[j], MaxDataPacketSize, PTx, PRx, PIdle, PSleep,
                                                                PER, tsTx, tsRx,
                                                                tsIdle, ta_list[i]))
        WiFiah_plot=plt.plot((86400 / np.array(ta_list))[::-1], consumed_energy_WiFiah[::-1], label=f"WiFiah_{Label[j-k]}",
                 marker='x', linestyle=f'{Linestyle[j-k]}', color=color[6])
        consumed_energy_WiFiah.clear()

    '''plt.plot(np.array(sa_list) / 1000, total_time_inyear_list_BLE, label="BLE", marker='o', linestyle='-')
    plt.plot(np.array(sa_list) / 1000, total_time_inyear_list_loRA, label="LORA", marker='o', linestyle='-')
    plt.plot(np.array(sa_list) / 1000, total_time_inyear_list_NBIoT, label="NBIOT", marker='o', linestyle='-')
    plt.plot(np.array(sa_list) / 1000, total_time_inyear_list_LTECAT4, label="LTECAT4", marker='o', linestyle='-')
    #plt.plot(np.array(sa_list) / 1000, total_time_inyear_list_BLE_with_solar_panel, label="BLE_solarpanel", marker='o',
            # linestyle='-')'''
    #hline1=plt.hlines(Dcell_Eperday,xmin=0,xmax=1000, label ="Dcell Energy_per_day",linestyles=f'{Linestyle[1]}', color=color[0])
    #hline2=plt.hlines(AA_Eperday, xmin=0, xmax=1000, label="AA Energy_per_day", linestyles=f'{Linestyle[2]}',
    #           color=color[7])
    #hline3=plt.hlines(AAA_Eperday, xmin=0, xmax=1000, label="AAA Energy_per_day", linestyles=f'{Linestyle[3]}',
    #           color=color[8])
    #hline4=plt.hlines(CR2032_Eperday, xmin=0, xmax=1000, label="CR2032 Energy_per_day", linestyles=f'{Linestyle[1]}',
    #           color=color[9])
    hline5=plt.hlines(Outdoor_solar, xmin=0, xmax=1000, label="Outdoor_Solar harvested energy 53mmx35mm panel", linestyles=f'{Linestyle[1]}',
               color=color[10])
    hline6=plt.hlines(Indoor_solar, xmin=0, xmax=1000, label="Indoor_solar harvested energy with 53mmx35mm panel", linestyles=f'{Linestyle[1]}',
               color=color[11])

    plt.xscale('log')
    plt.yscale('log')
   # plt.xlim(left=0)
    plt.xlabel(
        f"Number of {Resolution[k]} Images Transmitted per Day")  # ('Application time interval/Periodicity of image transfer each day (Hour)')
    plt.ylabel('Energy Consumed per day (J)')
    plt.title(f" {Resolution[k]} Compressed Image Transfer Energy of Different IoT Technlogies",
              fontsize=7, color='black', loc='left')
    print(Resolution[k])
    #plt.legend(handles=[hline1,hline2,hline3,hline4],loc='lower center', bbox_to_anchor=(0.5,0.01),fontsize=6)

    All_legend=plt.legend(loc='upper right', bbox_to_anchor=(1, 1), fontsize=5)
    '''for text in All_legend.get_texts():
        if text.get_text() == 'Dcell Energy_per_day':
            text.set_visible(False)'''

    handles=All_legend.legend_handles
    other_legend= plt.legend(handles=[handles[0],handles[1],handles[2],handles[3], handles[4]],loc='upper left', bbox_to_anchor=(0.01, 1), fontsize=6)
    #battery_legend=plt.legend(handles=[hline1,hline2,hline3,hline4,hline5, hline6],loc='lower center', bbox_to_anchor=(0.5,0.01),fontsize=6)
    battery_legend = plt.legend(handles=[hline5, hline6], loc='lower center',
                                bbox_to_anchor=(0.5, 0.01), fontsize=6)
    plt.gca().add_artist(other_legend) #to add the first legend back to the plot after creating the second legend. This approach prevents the second legend from overwriting the first one.
    ''' print("Legend Handles:",(handles[3]))
    for handle in handles:
        print(f" Handle: {handle}")'''
    #plt.legend(handles=[BLE_plot,WiFiah_plot], loc='lower center', bbox_to_anchor=(0.5, 0.01), fontsize=6)

    plt.grid(True, linewidth=0.25, alpha=0.5)
    # plt.savefig('5Tech_QQVGA_NumberofImageperDaylogscale.png')
    plt.show()



