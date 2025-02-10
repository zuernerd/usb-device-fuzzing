import sys
import usb.core
import usb.util

def detach_kernel_driver(vid, pid, interface):
    # Convert the vid and pid to integers
    vid = int(vid, 16)
    pid = int(pid, 16)
    interface = int(interface)

    # Find the USB device
    dev = usb.core.find(idVendor=vid, idProduct=pid)

    if not dev:
        print(f"Device with VID:PID {vid:04x}:{pid:04x} not found")
        return

    # Check if the device is set to the interface
    if dev.is_kernel_driver_active(interface):
        try:
            dev.detach_kernel_driver(interface)
            print(f"Kernel driver detached from interface {interface}")
        except usb.core.USBError as e:
            print(f"Could not detach kernel driver: {str(e)}")
            return
    else:
        print(f"No kernel driver active on interface {interface}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 detach.py VID:PID INTERFACE")
        sys.exit(1)

    vid_pid = sys.argv[1]
    interface = sys.argv[2]
    vid, pid = vid_pid.split(':')

    detach_kernel_driver(vid, pid, interface)

