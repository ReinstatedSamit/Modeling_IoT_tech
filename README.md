# Power Consumption Values Used for Modeling Different IoT Technology


| Technology          | Coverage | PTx(W)      | PRx(W)    | PIdle(W)  | PSleep(W)   | Reference                    |
|---------------------|----------|-------------|-----------|-----------|-------------|------------------------------|
| BLE                 | 20-100m  | 24.11e-3    | 19.26e-3  | 4.67e-3   | 3.24e-6     | [BLE](#ble)                  |
| LORA                | <20 Km   | 419.6e-3    | 44.06e-3  | NA        | 4.32e-6     | [LORA](#lora)                |
| NBIOT               | <100 Km  | 543e-3      | 90e-3     | 2.4e-3    | 0.015e-3    | [NBIOT](#nbiot)              |
| WiFi HaLow (802.11ah)| <1.5 Km | 0.0072      | 0.0044    | NA        | 1.5e-3      | [WiFi HaLow](#wifi-halow) |
| LTE_CAT4            | <100 Km  | 2.318       | 0.1178    | 0.01026   | 0.00494     | [TOBT_L210](#tobt_l210)      |

## References

- <a name="ble"></a>BLE: É. Morin, M. Maman, R. Guizzetti and A. Duda, "Comparison of the Device Lifetime in Wireless Networks for the Internet of Things," in IEEE Access, vol. 5, pp. 7097-7114, 2017, doi: 10.1109/ACCESS.2017.2688279.
- <a name="lora"></a>LORA: É. Morin, M. Maman, R. Guizzetti and A. Duda, "Comparison of the Device Lifetime in Wireless Networks for the Internet of Things," in IEEE Access, vol. 5, pp. 7097-7114, 2017, doi: 10.1109/ACCESS.2017.2688279.
- <a name="nbiot"></a>NBIOT: R. Ratasuk, B. Vejlgaard, N. Mangalvedhe and A. Ghosh, "NB-IoT system for M2M communication," 2016 IEEE Wireless Communications and Networking Conference Workshops (WCNCW), Doha, Qatar, 2016, pp. 428-432, doi: 10.1109/WCNCW.2016.7552737.
- <a name="wifi-halow"></a>WiFi HaLow : Del Carpio, L.F., Di Marco, P., Skillermark, P. et al. Comparison of 802.11ah, BLE and 802.15.4 for a Home Automation Use Case. Int J Wireless Inf Networks 24, 243–253 (2017). https://doi.org/10.1007/s10776-017-0355-2
  O. Raeesi, J. Pirskanen, A. Hazmi, T. Levanen and M. Valkama, "Performance evaluation of IEEE 802.11ah and its restricted access window mechanism," 2014 IEEE International Conference on Communications Workshops (ICC), Sydney, NSW, Australia, 2014, pp. 460-466, doi: 10.1109/ICCW.2014.6881241.
- <a name="tobt_l210"></a>TOBT_L210: Datasheet link: https://content.u-blox.com/sites/default/files/TOBY-L2_DataSheet_UBX-13004573.pdf

More related info can be found here: https://datatracker.ietf.org/doc/html/rfc8376
