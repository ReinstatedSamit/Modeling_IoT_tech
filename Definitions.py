def image_size_in_bytes(width, height, color_depth):
    # Calculate the size of the image in bytes
    # Formula: size = width * height * (color_depth / 8)
    size_bytes = width * height * (color_depth / 8)
    return size_bytes


def total_byte_size(width, height, color_depth, frame_rate):
    # Calculate the size of each frame in bytes
    frame_size_bytes = image_size_in_bytes(width, height, color_depth)

    # Calculate the total byte size based on frame rate
    total_size_bytes = frame_size_bytes * frame_rate
    return total_size_bytes

def calculate_image_transmission_rate(transmit_power_dBm, upload_speed_bps, image_size_bytes):
    # Convert transmit power to milliwatts if needed
    transmit_power_mW = 10 ** (transmit_power_dBm / 10)

    # Estimate transmission efficiency (e.g., based on signal-to-noise ratio)
    transmission_efficiency = 0.8  # Example value

    # Calculate available bandwidth based on upload speed
    available_bandwidth_bps = upload_speed_bps

    # Calculate maximum data rate based on available bandwidth and transmission efficiency
    max_data_rate_bps = available_bandwidth_bps * transmission_efficiency

    # Calculate number of images that can be transmitted per second
    images_per_second = max_data_rate_bps / image_size_bytes

    # Calculate total power consumption for transmission
    total_power_consumption_mW = transmit_power_mW * images_per_second

    return images_per_second, total_power_consumption_mW


def calculate_transmission_time(image_size_bytes, upload_speed_bps):
    # Convert upload speed to bytes per second
    upload_speed_bps /= 8

    # Calculate transmission time
    transmission_time_seconds = image_size_bytes / upload_speed_bps
    return transmission_time_seconds

def dbm_to_mw(dbm):
    return 10 ** (dbm / 10)

# Example usage:
dbm_power = 23  # dBm
mw_power = dbm_to_mw(dbm_power)
print(f"{dbm_power} dBm is equivalent to {mw_power} mW")


def calculate_total_energy_consumed(image_size_bytes, upload_speed_bps, transmit_power_mW):
    # Convert upload speed to bytes per second
    upload_speed_bps /= 8

    # Calculate transmission time
    transmission_time_seconds = image_size_bytes / upload_speed_bps

    # Calculate total energy consumed (in millijoules)
    total_energy_consumed_mJ = transmit_power_mW * transmission_time_seconds

    return transmission_time_seconds, total_energy_consumed_mJ


def calculate_solar_harvested_energy(irradiance, panel_area, sunlight_hours, efficiency):
    # Convert irradiance to kW/m^2
    irradiance_kW_per_m2 = irradiance / 1000

    # Calculate energy harvested in kWh
    harvested_energy_kWh = efficiency * irradiance_kW_per_m2 * panel_area * sunlight_hours
    return harvested_energy_kWh


# Given parameters
irradiance = 1000  # Irradiance in W/m^2 (STC)
panel_area = 1  # Panel area in m^2
sunlight_hours = 5  # Sunlight hours
efficiency = 0.15  # Solar panel efficiency (assume 15% for example)

# Calculate harvested energy
harvested_energy_kWh = calculate_solar_harvested_energy(irradiance, panel_area, sunlight_hours, efficiency)
print(f"Solar harvested energy: {harvested_energy_kWh:.2f} kWh")



# Example usage:
width = 1920  # Width of the image in pixels
height = 1080  # Height of the image in pixels
color_depth = 8  # Color depth of the image in bits per pixel (e.g., 24-bit RGB)
frame_rate =30

# Take user input for image parameters
'''width = int(input("Enter the width of the image in pixels: "))
height = int(input("Enter the height of the image in pixels: "))
color_depth = int(input("Enter the color depth of the image in bits per pixel: "))
frame_rate = float(input("Enter the frame rate in frames per second: "))'''

SONY_size_bytes = image_size_in_bytes(1906, 2608, color_depth)
SONY_size_kilobytes = SONY_size_bytes/1024
print(f"SONY Image size: {SONY_size_kilobytes} Kilo bytes")

NANEYE_size_bytes = image_size_in_bytes(249, 250, color_depth)
NANEYE_size_kilobytes = NANEYE_size_bytes/1024
print(f"NANEYE Image size: {NANEYE_size_kilobytes} Kilo bytes")


MDPI_size_bytes = image_size_in_bytes(1600, 1200, color_depth)
MDPI_size_kilobytes = MDPI_size_bytes/1024
print(f"MDPI Image size: {MDPI_size_kilobytes} Kilo bytes")

# Calculate the total byte size
#total_size_bytes = total_byte_size(width, height, color_depth, frame_rate)
#print(f"Total byte size for {frame_rate} FPS: {total_size_bytes} bytes")





# Example usage
transmit_power_dBm = 20  # Example transmit power in dBm
upload_speed_bps = 1000000  # Example upload speed in bits per second (e.g., 1 Mbps)
image_size_bytes = 500000  # Example image size in bytes (e.g., 0.5 MB)

images_per_second, total_power_consumption_mW = calculate_image_transmission_rate(transmit_power_dBm, upload_speed_bps,
                                                                                  image_size_bytes)
print(f"Number of images transmitted per second: {images_per_second}")
print(f"Total power consumption for transmission: {total_power_consumption_mW} mW")



# Example usage
image_size_bytes = 500000  # Example image size in bytes
upload_speed_bps = 1000000  # Example upload speed in bits per second (e.g., 1 Mbps)

transmission_time_seconds = calculate_transmission_time(image_size_bytes, upload_speed_bps)
print(f"Transmission time: {transmission_time_seconds} seconds")

# Example usage:
width = 1920  # Width of the image in pixels
height = 1080  # Height of the image in pixels
color_depth = 24  # Color depth of the image in bits per pixel (e.g., 24-bit RGB)
frame_rate =30

# Example usage
image_size_bytes = 500000  # Example image size in bytes
upload_speed_bps = 1000000  # Example upload speed in bits per second (e.g., 1 Mbps)
transmit_power_mW = 100  # Example transmit power in milliwatts

transmission_time_seconds, total_energy_consumed_mJ = calculate_total_energy_consumed(image_size_bytes,
                                                                                      upload_speed_bps,
                                                                                      transmit_power_mW)
print(f"Transmission time: {transmission_time_seconds} seconds")
print(f"Total energy consumed: {total_energy_consumed_mJ} mJ")


from PIL import Image

def image_size_in_bytes_to_jpg(width, height, color_depth):
    """
    Convert the size of an image in bytes to a JPEG file with default settings.

    Parameters:
        width (int): Width of the image in pixels.
        height (int): Height of the image in pixels.
        color_depth (int): Color depth of the image in bits per pixel.

    Returns:
        int: Size of the equivalent JPEG file in bytes.
    """
    # Calculate the size of the image in bytes
    size_bytes = width * height * (color_depth / 8)

    # Create a blank image using PIL
    image = Image.new('RGB', (width, height))

    # Save the image to a temporary file in JPEG format
    temp_filename = 'temp.jpg'
    image.save(temp_filename, format='JPEG')

    # Get the size of the saved JPEG file
    jpg_size_bytes = len(open(temp_filename, 'rb').read())

    # Delete the temporary file
    import os
    os.remove(temp_filename)

    return jpg_size_bytes/1024

# Example usage:
width = 1600
height = 1200
color_depth = 24
jpg_size_bytes = image_size_in_bytes_to_jpg(width, height, color_depth)
print(f"Size of equivalent JPEG file: {jpg_size_bytes} kilo_bytes")
