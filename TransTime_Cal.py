import math
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

    return rx_time, tx_time, wait_time, total_delay

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

    return rx_time, tx_time, wait_time, delay


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

    # Total delay for transmission
    delay = tx_time

    return delay


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

    return 0,tx_time,0




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


Example usage:
data_size = 1000000
use_6lo_hc = 1
rx_time, tx_time = BLE_calculate_rx_tx_time(data_size, use_6lo_hc)
print("BLE_RX Time:", rx_time)
print("BLE_TX Time:", tx_time)


data_size = 1000000
rx_time, tx_time, wait_time, total_delay = NBIOT_calculate_rx_tx_wait_time(data_size)
print("NBIOT_RX Time:", rx_time)
print("NBIOT_TX Time:", tx_time)
print("NBIOT_Wait Time:", wait_time)
print("NBIOT_Total Delay:", total_delay)

data_size = 1000000
rx_time, tx_time, wait_time, total_delay = LoRa_calculate_rx_tx_wait_time_lora(data_size)
print("LORA_RX Time:", rx_time)
print("LORA_TX Time:", tx_time)
print("LORA_Wait Time:", wait_time)
print("LORA_Total Delay:", total_delay)


data_size = 100000
transmission_delay = LC4_calculate_tx_delay(data_size)
print("L4_Transmission Delay:", transmission_delay)
