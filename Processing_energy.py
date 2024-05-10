def processing_energy(FLOPS, other_ops):
    """
    Computes the energy consumption of ARM Cortex M4 processor.

    Args:
    - FLOPS (list of floats): List of Floating Point Operations Per Second for each operation.
    - other_ops (list of floats): List of other operations' energy consumption.

    Returns:
    - energy_m4 (list of floats): List of energy consumption for each operation.
    """
    freq_m4 = 120  # MHz
    I_m4 = 0.000043  # ampere per MHz
    vdd_m4 = 3.3  # Volt

    # ARM M4
    # FLOPs take 3 cycles for the multiply fused operation (add, subtract)
    power_m4 = I_m4 * vdd_m4 * freq_m4
    energy_m4 = []
    energy_m4.append(((FLOPS[0] * 3) + other_ops[0]) * power_m4 / (freq_m4 * 1000000))
    for i in range(1, len(FLOPS)):
        energy_m4.append(((FLOPS[i] * 3) + other_ops[i]) * power_m4 / (freq_m4 * 1000000) + energy_m4[i - 1])

    return energy_m4
