#!/usr/bin/env python3

import sys
import time
import usb.core
import binascii

def is_alive(device):
    try:
        res = device.ctrl_transfer(0x80, 0, 0, 0, 2)
    except usb.core.USBError as e:
        if e.errno == -4:  # LIBUSB_ERROR_NO_DEVICE
            print("\nDevice not found!")
            sys.exit()
        if e.errno == -3:  # LIBUSB_ERROR_ACCESS
            print("\nAccess denied to device!")
            sys.exit()
        print("\nGET_STATUS returned error %i" % e.errno)
        return False

    if len(res) != 2:
        print("\nGET_STATUS returned %u bytes: %s" % (len(res), binascii.hexlify(res).decode()))
        return False

    return True

    try:
        device.write(1, bytearray.fromhex('55534243E019EA850002000080000A28000000000000000100000000000000'))
    except usb.core.USBError as e:
        if e.errno == -4:
            raise Exception('Function check failed: device not present!')
        elif e.errno == -6:
            raise Exception('Function check failed: function is busy!')
        else:
            print("Function check failed: usb error %i" % e.errno)
            return False

    try:
        res = device.read(0x82, 0x400)
    except usb.core.USBError as e:
        print("Function check failed: usb error %i" % e.errno)
        return False

    if len(res) != 0x20d:
        print("Function check returned %x bytes: %s" % (len(res), binascii.hexlify(res).decode()))
        return False

    return True

def TestCtrlTransfer(device, rt, r, v, i):
    for size in (0, 10, 100, 4000):
        sys.stdout.write('TRY %0.2x %0.2x %0.4x %0.4x len(%0.4u)\r' % (rt, r, v, i, size))
        sys.stdout.flush()
        
        try:
            res = device.ctrl_transfer(rt & 0x80, r, v, i, bytearray.fromhex('ff' * size), timeout=250)
            print('OUT %0.2x %0.2x %0.4x %0.4x res(%u) len(%u)' % (rt, r, v, i, res, size))
        except usb.core.USBError as e:
            if e.errno not in (-9, -1):  # Ignore LIBUSB_ERROR_PIPE and LIBUSB_ERROR_IO
                print('OUT %0.2x %0.2x %0.4x %0.4x err(%i) len(%u)' % (rt, r, v, i, e.errno, size))

        try:
            res = device.ctrl_transfer(rt | 0x80, r, v, i, size, timeout=250)
            print('IN  %0.2x %0.2x %0.4x %0.4x data(%u) len(%u):\t%s' % (rt, r, v, i, len(res), size, binascii.hexlify(res).decode()))
        except usb.core.USBError as e:
            if e.errno not in (-9, -1):
                print('IN  %0.2x %0.2x %0.4x %0.4x err(%i) len(%u)' % (rt, r, v, i, e.errno, size))

        if i % 10 == 0:
            if not is_alive(device):
                device.reset()
                time.sleep(1)

arg = sys.argv[1].split(':')
device = usb.core.find(idVendor=int(arg[0], 16), idProduct=int(arg[1], 16))

initq = initv = initvv = 0
if len(sys.argv) > 2:
    initq = int(sys.argv[2], 16)
if len(sys.argv) > 3:
    initv = int(sys.argv[3], 16)
if len(sys.argv) > 4:
    initvv = int(sys.argv[4], 16)

for q in range(initq, 0x100):
    for v in range(initv, 0x10):
        for vv in range(initvv, 0x10):
            for i in range(0, 0x10):
                if q == 3 and vv == 2 and i == 0:
                    continue
                for ii in range(0, 0x10):
                    for t in range(0, 0x04):
                        for r in range(0, 0x04):
                            TestCtrlTransfer(device, (t << 5) | r, q, (v << 8) | vv, (i << 8) | ii)

