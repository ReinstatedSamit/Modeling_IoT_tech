
import math
import matplotlib.pyplot as plt

from Trial_code import colors_LoRaWAN

#ta_list = [9, 90 ,180, 900, 1800, 3600, 7200, 10800, 14400, 21600, 43200, 86400]  # [60, 900, 1800, 3600, 7200, 10800, 14400, 21600, 43200, 86400]
ta_list = [3600 * 24]

consumed_energy_BLE=[]
consumed_energy_loRa=[]
consumed_energy_loRa_2=[]
consumed_energy_loRa_3=[]
consumed_energy_NBIOT=[]
consumed_energy_NBIOT_Tmobile=[]
consumed_energy_NBIOT_ATT7KM=[]
consumed_energy_LTECAT4=[]
consumed_energy_WiFiah=[]
consumed_energy_WiFi=[]
total_time_inyear_list_NBIOT_with_solar_panel = []
#Resolution=['QVGA','QVGA']
RResolutions=[' QQQQVGA','QQVGA','QVGA','VGA']
Resolution=[' QQQQVGA',' QQQQVGA','QQVGA','QQVGA','QVGA','QVGA','VGA','VGA']#,'SVGA','SVGA']#,'UXGA','UXGA']
sa_list = [3.6e3,3.6e3,56.25e2,56.25e3,140e2,225e3,900e2,900e3,1406.25e2,1406.25e3,5625e2,5625e3]  # [20e3]#[1000, 10000, 22500, 90000, 140625, 562500]
#sa_list=[140e2,140e3]
PER = 0  # 0.01  # Packet error rate

Label = ['Compressed', 'UnCompressed']
Linestyle = ['-', '--',':','-.']
color = ['black', 'navy', 'red', 'purple', 'teal', 'cyan', 'green','darkorange','magenta','blue','orange','#1f77b4']
Dcell_Eperday= (97200*0.90/(3*365))
AA_Eperday=(16000*0.90/(7*365))
AAA_Eperday=(64800*0.90/(7*365))
CR2032_Eperday=(2430*0.90/(5*365))

component_labels_NBIOT = [
    "ESP Startup", "Capture & Compress", "SPI", "MCU Before Compute",
    "MCU Compute", "UART Compute", "MCU LP Idle", "Comm. Transmit (Trx)",
    "NBIOT Tx", "RRC", "Sleep"
]

component_labels_LoRaWAN = [
    "ESP Startup", "Capture & Compress", "SPI", "MCU Before Compute",
    "MCU Compute", "UART Compute", "MCU LP Idle", "Comm. Transmit (Trx)",
    "LoRaWAN Class A", "Sleep"
]
colors_NBIOT = ['blue', 'green','purple', 'orange', 'red','#9898b8','#D083B0', '#C49A9A', '#A3D4A4','#D8A468']
colors_LoRaWAN = ['blue', 'green','purple', 'orange', 'red','#9898b8','#D083B0', '#A3D4A4','#D8A468']


nbiot_colors = ['#D083B0', '#C49A9A', '#A3D4A4']  # Colors for each segment of NB-IoT
lorawan_colors = ['#D083B0', '#D8A468', '#A3D4A4']  # Colors for each segment of LoRaWAN
MCU_colors=['orange','red','#9898b8']



#Non_com_energy=1.84
Non_com_energy=1.84
Energy_coldstartup=2
Image_cap_comp_energy=0.111

def energy_time_capture_compress(image_size):
    energy= (0.111/14000)*image_size
    time= (0.2/10000)*image_size
    return energy, time

# 1 MHz SPI frequency
def energy_SPI_tranmisssion(image_size):
    energy = (0.0475 / 14000) * image_size
    time = (0.112 / 14000) * image_size
    return energy, time

def energy_esp32_startup():
    energy=0.2765
    time= 1.4
    return energy, time

def MCU_compute(data_size):
    fixed_setup_time=1.4
    fixed_setup_energy=fixed_setup_time*3.3*6e-3
    hexaconvertion_time=data_size*150e-6
    hexaconvertion_energy=hexaconvertion_time*3.3*6e-3
    commandCopyloop_time=data_size*2/96e6
    commandCopyloop_energy=commandCopyloop_time*3.3*6e-3
    total_energy=fixed_setup_energy+hexaconvertion_energy+commandCopyloop_energy
    total_time=fixed_setup_time+hexaconvertion_time+commandCopyloop_time
    return total_energy, total_time


def UART_compute(data_size):
    uart_trasnmission_time=data_size*10*2/115200  # 10 for two additional bit, 2 taking in account for the hexa convertion
    uart_trasnmission_energy=uart_trasnmission_time*3.3*6e-3
    return uart_trasnmission_energy, uart_trasnmission_time


def fulldata_transmission_time(Datasize, MaxDataPacketSize, tpayloadinterval):
    return math.ceil((Datasize / MaxDataPacketSize) * tpayloadinterval)


def NBIOT_calculate_rx_RRC_CDRX_time_ATnT(data_size):
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

    '''RRCSetup_TAU_time= 0.5

    drx_inactivity_time= 0.290

    cDRx_time=0.332*6

    RRC_release_time=0.092'''

    RRCSetup_TAU_time = 0.255
    drx_inactivity_time = 0.365
    icDRx_time_low = 0.257373
    icDRx_time_high = 0.0665501
    icDRx_time = icDRx_time_low + icDRx_time_high
    cDRx_cycle = 6
    cDRx_time = icDRx_time * cDRx_cycle
    RRC_release_time = 0.092

    total_delay = RRCSetup_TAU_time + tx_time +drx_inactivity_time + cDRx_time + RRC_release_time
    print(f"NBIOT each packet Tx Time: {tx_time}")


    print(f"NBIOT each packet Delay Time: {total_delay}")


    return RRCSetup_TAU_time,tx_time ,drx_inactivity_time,cDRx_time,RRC_release_time





def LoRaWAN_calculate_rx_tx_wait_time(data_size,sf_min, bw_max):
    # Lower layer constants
    skip_header = 0
    low_dr_opt = 0
    coding_rate = 1/4#4/5#1 according to measurement
    sf_min = sf_min#9#12#12
    bw_max = bw_max#500  # [kHz]
    symbol_time = (2 ** sf_min) / (bw_max * 1000)
    preamble_size = 8  # symbols
    preamble_time = (preamble_size + 4.25) * symbol_time
    lora_pl_size = 222  # [byte]
    lora_he_size = 13  # [byte]
    turnaround_time = 0.00017#0.00017
    rx_delay = 2.45#3.85#1by default
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

    #wait_time=tx_time*100-(tx_time+rx_time)
    #wait_time= 0.83
    rx_time=2*rx_time+0.007#fitting parameter
    delay = tx_time + rx_time + wait_time
    print(f"LoRA each packet Tx Time: {tx_time}")
    print(f"LoRa each packet Rx Time: {rx_time}")
    print(f"LoRa each packet wait Time: {wait_time}")
    print(f"LoRa each packet Delay Time: {delay}")

    return rx_time, tx_time, wait_time

#Compute the total energy to transmit a full data
def ComputeEnergyToSendData_v3(Datasize, MaxDataPacketSize, PTx, PRx, PIdle, PSleep, PER, tsTx, tsRx, tsIdle, tpayloadinterval):
    """
    Compute the energy consumed to send data.
    Returns:
    float: Energy consumed in sending data in joules.
    """
    # Calculate number of packets
    if (Datasize<MaxDataPacketSize):
        Npackets = 1
    else:
        NPackets = math.ceil(Datasize / MaxDataPacketSize)
    #LastPacket = Datasize % MaxDataPacketSize
    #if LastPacket != 0:
     #   NPackets += 1
    print("LoRa Npackets:", NPackets)
    # Calculate total transmission time for each state

    Ntr = (1 / (1 - PER))  # Number of transmissions
    tsSleep = tpayloadinterval - (tsTx + tsRx + tsIdle)
    tTx = tsTx * Ntr*NPackets
    tRx = tsRx * Ntr*NPackets
    tIdle = tsIdle * Ntr*NPackets

    tSleep = tsSleep * Ntr*NPackets

    #print("Transmit Time:",tTx)
    #print("Recieve Time:",tRx)
    #print("Wait Time:",tIdle)
    #print("Delay:",tTx + tRx + tIdle)
    #print("Sleep time:",tSleep)
    # print("tTx time",tTx)
    # Calculate energy consumption for data transmission
    EeffTrx=PTx * tTx
    Eidle = PIdle * tIdle
    Eactivetrans = (PTx * tTx + PRx * tRx + PIdle * tIdle)
    E_Rx= PRx * tRx
    # print("Eactivwe", Eactivetrans)
    Esleep = (PSleep * tSleep)
    # print("Esleep",Esleep)
    Edata = Eactivetrans + Esleep
    # print("Consumed Energy in sending data", Edata)
    return Edata, EeffTrx,Esleep, Eidle, E_Rx


#Compute the total energy to transmit a full data

def NBIOT_ComputeEnergyToSendData_v4(Datasize, MaxDataPacketSize, P_RRCSetup_TAU, P_Tx, P_DRXinactivity, P_cDRX,P_RRCRelease, PSleep, PER, RRCSetup_TAU_time, tx_time, drx_inactivity_time, cDRx_time, RRC_release_time, tpayloadinterval):
    """
    Compute the energy consumed to send data.
    Returns:
    float: Energy consumed in sending data in joules.
    """
    # Calculate number of packets
    if (Datasize<MaxDataPacketSize):
        Npackets = 1
    else:
       NPackets = math.ceil(Datasize / MaxDataPacketSize)
    #LastPacket = Datasize % MaxDataPacketSize
    #if LastPacket != 0:
     #   NPackets += 1
    print("NBIOT Npackets:", NPackets)
    # Calculate total transmission time for each state

    Ntr = (1 / (1 - PER))  # Number of transmissions
    tSleep = tpayloadinterval - (RRCSetup_TAU_time + tx_time +drx_inactivity_time + cDRx_time + RRC_release_time)

    #print("Transmit Time:",tTx)
    #print("Recieve Time:",tRx)
    #print("Wait Time:",tIdle)
    #print("Delay:",tTx + tRx + tIdle)
    #print("Sleep time:",tSleep)
    # print("tTx time",tTx)
    # Calculate energy consumption for data transmission
    Eactivetrans= (RRCSetup_TAU_time*P_RRCSetup_TAU + tx_time*P_Tx + drx_inactivity_time*P_DRXinactivity + cDRx_time*P_cDRX + RRC_release_time*P_RRCRelease)*Ntr*NPackets
    EeffTrx = tx_time * P_Tx * Ntr * NPackets
    E_RRC=Eactivetrans-EeffTrx
    # print("Eactivwe", Eactivetrans)
    Esleep = (PSleep * tSleep * Ntr * NPackets)
    # print("Esleep",Esleep)
    Edata = Eactivetrans + Esleep
    # print("Consumed Energy in sending data", Edata)
    return Edata, EeffTrx, Esleep,  E_RRC


SPS_NBIOT_Total_Energy = []
SPS_LORAWAN_Total_Energy = []

for k in range(0, len(Resolution), 2):


        # NBIOT AT&T
        for j in range(k, k + 1):
            E_capture_compress, T_capture_compress = energy_time_capture_compress(sa_list[j])
            E_SPI,T_SPI= energy_SPI_tranmisssion(sa_list[j])
            E_ESPStartup, T_ESPStartup= energy_esp32_startup()
            E_MCU_compute, T_MCU_Compute= MCU_compute(sa_list[j])
            E_UART_compute, T_UART_compute= UART_compute(sa_list[j])
            T_MCU_before_compute= T_capture_compress+ T_SPI +T_ESPStartup
            E_MCU_before_compute= T_MCU_before_compute * 3.3* 6e-3


            for i in range(len(ta_list)):
                MaxDataPacketSize = 1500  # 1500  # (BLE)#(NBIOIT)#245(BLE/LoRa)  # Maximum size of a data packet in bytes
                # PTx = 700e-3#375e-3#543e-3  # 24e-3(BLE)  # Power consumption
                # PRx = 213e-3#77e-3#300e-3#90e-3  # 20e-3(BLE)  # Power consumption
                 # PIdle = 21e-3#100e-3#2.4e-3  # 5e-3  (BLE)# Power consumption
                # Pintermediate=15e-6#49e-3# from measured data
                # AT&T 1km Tower
                PSleep = 48.18e-3  # 0.015e-3  # 3e-6(BLE)  # Power consumption
                P_RRCSetup_TAU = 300e-3
                P_Tx = 545e-3
                P_DRXinactivity = 345e-3
                P_cDRX = 100e-3
                P_RRCRelease = 278e-3
                tpayloadinterval=5.12
                Energy_coldstartup=2
                time_coldstartup=11
                # tsRx, tsTx, tsIdle = NBIOT_calculate_rx_tx_wait_time(sa_list[j])
                # tsRx, tsTx, tsIdle, tintermediate = NBIOT_calculate_rx_tx_wait_intermediate_time(sa_list[j])
                # tsRx, tsTx, tsIdle, tintermediate = NBIOT_calculate_rx_tx_wait_intermediate_time(MaxDataPacketSize)

                RRCSetup_TAU_time, tx_time, drx_inactivity_time, cDRx_time, RRC_release_time = NBIOT_calculate_rx_RRC_CDRX_time_ATnT(
                    MaxDataPacketSize)
                NBIOT_Energy_per_FullImagetransmit, NBIOT_Eeff_Trx, NBIOT_Esleep, NBIOT_E_RRC=  NBIOT_ComputeEnergyToSendData_v4(sa_list[j],
                                                                                                   MaxDataPacketSize,
                                                                                                   P_RRCSetup_TAU, P_Tx,
                                                                                                   P_DRXinactivity,
                                                                                                   P_cDRX,
                                                                                                   P_RRCRelease, PSleep,
                                                                                                   PER,
                                                                                                   RRCSetup_TAU_time,
                                                                                                   tx_time,
                                                                                                   drx_inactivity_time,
                                                                                                   cDRx_time,
                                                                                                   RRC_release_time,
                                                                                                   tpayloadinterval)

                NBIOT_Energy_per_FullImagetransmit=NBIOT_Energy_per_FullImagetransmit+Energy_coldstartup

                FullImage_Comm_Transmit_time=fulldata_transmission_time(sa_list[j], MaxDataPacketSize, tpayloadinterval)
                print(f"NBIOT one full {Resolution[k]} size image transmission takes {NBIOT_Energy_per_FullImagetransmit} J energy")
                print(f"NBIOT one full {Resolution[k]} size image transmission takes {NBIOT_Eeff_Trx + NBIOT_Esleep + NBIOT_E_RRC} J energy")
                print(f"NBIOT {sa_list[j]/1000} KB image transmission time: {fulldata_transmission_time(sa_list[j],MaxDataPacketSize,tpayloadinterval)+time_coldstartup} sec")
                E_MCU_LP_Idle = 3.3 * 3e-3 * (FullImage_Comm_Transmit_time - T_UART_compute)

                SPS_NBIOT_Total_Time_image_full_cycle= T_ESPStartup+T_capture_compress+T_SPI+T_MCU_Compute+time_coldstartup+FullImage_Comm_Transmit_time
                SPS_NBIOT_Total_energy_full_image_cycle=E_ESPStartup+E_capture_compress+E_SPI+E_MCU_before_compute+E_MCU_compute+E_UART_compute+E_MCU_LP_Idle+Energy_coldstartup+NBIOT_Eeff_Trx+NBIOT_E_RRC+NBIOT_Esleep
                SPS_NBIOT_Total_Energy.append([E_ESPStartup,E_capture_compress+E_SPI,E_MCU_before_compute,E_MCU_compute,E_UART_compute,E_MCU_LP_Idle,Energy_coldstartup,NBIOT_Eeff_Trx,NBIOT_E_RRC,NBIOT_Esleep])
                print(f"SPS with NBIOT one full {Resolution[k]} size image transmission takes total {SPS_NBIOT_Total_energy_full_image_cycle} J energy per cycle")
                print(f"SPS with NBIOT {sa_list[j] / 1000} KB image transmission time: {SPS_NBIOT_Total_Time_image_full_cycle} sec")



        # LORA  SF=8,BW=500
        #for j in range(k, k + 1):
            for i in range(len(ta_list)):
                MaxDataPacketSize = 240  # Maximum size of a data packet in bytes
                PTx = 429e-3  # 419.604e-3  # 2*0.028#419.604e-3  # Power consumption
                PRx = 28e-3#60e-3  # 44.064e-3  # 2*0.0138#44.064e-3  # Power consumption
                PIdle = 22.4e-3#56e-3  # 3e-6  # Power consumption
                PSleep = 22.4e-3  # 0.04e-6#0.04e-6  # Power consumption
                bw_max = 500
                sf_min = 8
                tpayloadinterval = 10
                tsRx, tsTx, tsIdle = LoRaWAN_calculate_rx_tx_wait_time(MaxDataPacketSize, sf_min, bw_max)
                LoRAWAN_Energy_per_FullImagetransmit,LoRAWAN_Eeff_Trx, LORAWAN_Esleep, LORAWAN_Eidle, LORAWAN_ERX=ComputeEnergyToSendData_v3(sa_list[j], MaxDataPacketSize, PTx, PRx, PIdle,
                                                                    PSleep,
                                                                    PER, tsTx, tsRx,
                                                                    tsIdle, tpayloadinterval)
                LoraWAN_ClassA=LORAWAN_ERX+ LORAWAN_Eidle
                LoRA_FullImage_Comm_Transmit_time = fulldata_transmission_time(sa_list[j], MaxDataPacketSize, tpayloadinterval)
                print(f"LoRa one full {Resolution[k]} size image transmission takes {LoRAWAN_Energy_per_FullImagetransmit} J energy")
                print(f"LoRa one full {Resolution[k]} size image transmission takes {LoRAWAN_Eeff_Trx + LORAWAN_Esleep + LORAWAN_Eidle+ LORAWAN_ERX} J energy")
                print(f"Lora {sa_list[j]/1000} KB image transmission time : {fulldata_transmission_time(sa_list[j], MaxDataPacketSize, tpayloadinterval)} sec")
                E_MCU_LP_Idle = 3.3 * 3e-3 * (LoRA_FullImage_Comm_Transmit_time - T_UART_compute)

                SPS_LORA_Total_Time_image_full_cycle = T_ESPStartup + T_capture_compress + T_SPI + T_MCU_Compute  + LoRA_FullImage_Comm_Transmit_time
                SPS_LORA_Total_energy_full_image_cycle = E_ESPStartup + E_capture_compress + E_SPI + E_MCU_before_compute + E_MCU_compute + E_UART_compute + E_MCU_LP_Idle + LoRAWAN_Eeff_Trx + LoraWAN_ClassA+ LORAWAN_Esleep
                SPS_LORAWAN_Total_Energy.append([E_ESPStartup,E_capture_compress,E_SPI,E_MCU_before_compute,E_MCU_compute,E_UART_compute,E_MCU_LP_Idle,LoRAWAN_Eeff_Trx,LoraWAN_ClassA,LORAWAN_Esleep])
                print(
                    f" SPS with LORAWAN one full {Resolution[k]} size image transmission takes total {SPS_LORA_Total_energy_full_image_cycle} J energy per cycle")
                print(
                    f"SPS with LORAWAN {sa_list[j] / 1000} KB image transmission time: {SPS_LORA_Total_Time_image_full_cycle} sec")



print(f"LorawAN_list {SPS_LORAWAN_Total_Energy}")
print(f"NBIOT_list {SPS_NBIOT_Total_Energy}")
fig, ax = plt.subplots(figsize=(14, 8))
bar_width = 0.3  # Width of each bar
x_positions = range(len(SPS_NBIOT_Total_Energy))  # Positions for each set

        # Plot each case for NB-IoT
for idx, energy_components in enumerate(SPS_NBIOT_Total_Energy):

        bottom = 0
        for i, (component, color) in enumerate(zip(energy_components, colors_NBIOT)):
                ax.bar(x_positions[idx] - bar_width / 2, component, width=bar_width, bottom=bottom, color=color,
                       label=component_labels_NBIOT[i] if idx == 0 else "")
                bottom += component
                # Add 'NBIOT' label at the top of each bar
        ax.text(x_positions[idx] - bar_width / 2, bottom + 0.1, 'NBIOT', ha='center', va='bottom', fontsize=10,
                fontweight='bold')

        # Plot each case for LoRaWAN
for idx, energy_components in enumerate(SPS_LORAWAN_Total_Energy):
        bottom = 0
        for i, (component, color) in enumerate(zip(energy_components, colors_LoRaWAN)):
                ax.bar(x_positions[idx] + bar_width / 2, component, width=bar_width, bottom=bottom, color=color,
                       label=component_labels_LoRaWAN[i] if idx == 0 else "")
                bottom += component
                # Add 'LoRa' label at the top of each bar
        ax.text(x_positions[idx] + bar_width / 2, bottom + 0.1, 'LoRa', ha='center', va='bottom', fontsize=10,
                fontweight='bold')

        # Add labels and title
ax.set_xlabel('Image Resolution')
ax.set_ylabel('Energy (J)')
ax.set_title(
            'Total Energy Distribution for Different Cases (SPS_NBIOT and SPS_LORA Total Energy Full Image Cycle)')
ax.set_xticks(x_positions)
#ax.set_xticklabels([f'Case {i + 1}' for i in x_positions])
ax.set_xticklabels(RResolutions)
        # Display the legend only once
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        # Display the plot
plt.tight_layout()
plt.savefig("Energy_break.png")
plt.show()
