# USB Device Fuzzing

This repository contains a collection of tools for testing USB devices. The code was first released at T2 Infosec 2012: [T2 Infosec 2012](http://www.t2.fi/2012/).

## Contents

### Tools

- **simple_ctrl_fuzzer.py**: A simple fuzzer for USB control transfers.

### USBFuzz Modules

- **USBFuzz**: Core Python modules for building USB fuzzers.
  - **USBFuzz.Exceptions**: Common exception definitions for the USBFuzz modules.
  - **USBFuzz.Device**: Module to interface with USB devices.
  - **USBFuzz.MSC**: Scapy layers and USB device interface class for the USB Bulk-Only Mass Storage Class.
  - **USBFuzz.SCSI**: Scapy layers for SCSI primary and bulk commands, used by USBFuzz.MSC.
  - **USBFuzz.CCID**: Scapy layers and USB device interface class for the USB Integrated Circuit Cards Interface Device Class.
  - **USBFuzz.MTP**: Scapy layers and USB device interface class for the USB Media Transfer Protocol (based on Picture Transfer Protocol).
  - **USBFuzz.QCDM**: Scapy layers and USB device interface class for the Qualcomm baseband DIAG protocol.

### Examples

- **examples**: Contains examples of simple fuzzers built using the USBFuzz modules.

## Getting Started

To start using these tools and modules, clone the repository and explore the provided scripts and modules.

### Running Examples

To run the example fuzzers, navigate to the `examples` directory and run the desired script with the appropriate USB device identifier (VID:PID). For example:

```bash
python ccid_fuzzer.py VID:PID
```
