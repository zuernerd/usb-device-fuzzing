import usb.core
import usb.util

# Find the USB device
dev = usb.core.find(idVendor=0x2e8a, idProduct=0x000f)  # Replace with your device's VID/PID


# Check if the device is set to the interface
if dev.is_kernel_driver_active(0):
    try:
        dev.detach_kernel_driver(0)
        print(f"Kernel driver detached from interface")
    except usb.core.USBError as e:
        print(f"Could not detach kernel driver: {str(e)}")
else:
    print(f"No kernel driver active on interface") 

# Configure the device (if needed)
dev.set_configuration()

# Get endpoints (adjust for your device)
cfg = dev.get_active_configuration()
intf = cfg[(0,0)]  # Use the first interface

# Bulk-out endpoint (CBW and data-out)
ep_out = usb.util.find_descriptor(
    intf,
    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
)

# Bulk-in endpoint (data-in and CSW)
ep_in = usb.util.find_descriptor(
    intf,
    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
)

# Construct CBW
#cbw = bytes.fromhex("55 53 42 43 33 6A 00 00 DC 0C 69 DD 80 00 09 28 97 DA 17 35 F7 EF 85 39 00 00 00 00 00 00 00")
cbw = bytes.fromhex("55 53 42 43 70 69 00 00 FC 82 CF DB 80 00 09 28 B5 AB 26 E3 FC 8C BF 5C 00 00 00 00 00 00 00")

# Send CBW
ep_out.write(cbw)

# Read data (8 bytes)
data = dev.read(ep_in.bEndpointAddress, 0x1000, timeout=5000)
data_len = len(data) 
print(f"Data: {data}")
print(f"Data len: {data_len}")

