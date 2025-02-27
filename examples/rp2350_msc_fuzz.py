import sys
import os
import struct
import sqlite3
import time
import hashlib
from scapy.packet import Raw
from USBFuzz.MSC import *

# Setup database
conn = sqlite3.connect("fuzz_results.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    opcode INTEGER,
                    random_value INTEGER,
                    command_data BLOB,
                    response_data BLOB,
                    hash_data BLOB,
                    response_size INTEGER,
                    status TEXT)''')
conn.commit()

# Initialize device
arg = sys.argv[1].split(':')
dev = BOMSDevice(arg[0], arg[1], timeout=1200)
dev.boms_reset()

# Read Capacity
cmd = MSCCBW()/SCSICmd()/ReadCapacity10()
dev.send(cmd)
reply = dev.read_reply()
dev.check_status(reply)

if Raw in reply and len(reply[Raw]) == 8:
    data = bytes(reply[Raw])
    max_lba = struct.unpack(">I", data[:4])[0]
    block_size = struct.unpack(">I", data[4:])[0]
else:
    reply.show()
    sys.exit()

print(f"Device is {round(float(max_lba*block_size)/1048576)}MB, max LBA: {max_lba:x}, blocksize: {block_size:x}")

opcode = 0x00 
while dev is not None:
    try:
        opcode += 1        
        for test in range(10000):
            r = struct.unpack("I", os.urandom(4))[0]
            print(f"\nSending command {dev.cur_tag() + 1} with random value {r:x}")
            cmd = MSCCBW(ReqTag=dev.next_tag(), ExpectedDataSize=r)/SCSICmd(OperationCode=opcode)/Raw(os.urandom(r%20))
            cmd_data = bytes(cmd)
            
            try:
                dev.send(cmd)
                reply = dev.read_reply()
                status = "Success"
            except USBException as e:
                print(f"Exception: {e} while processing command {dev.cur_tag()}")
                dev.reset()
                reply = b""
                status = f"Error: {e}"

            reply_data = bytes(reply[Raw]) if Raw in reply and len(reply) > 0 else b""
            response_size = len(reply_data)

            # If data too big store only the hash
            hash_data = b""
            if len(reply_data) > 1024 and reply_data.count(0) == len(reply_data):  
                reply_data = b""
                hash_data = hashlib.sha256(reply_data).digest() 
            
            # Store in database
            cursor.execute("INSERT INTO results (timestamp, opcode, random_value, command_data, response_data, hash_data, response_size, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (time.strftime('%Y-%m-%d %H:%M:%S'), opcode, r, cmd_data, reply_data, hash_data, response_size, status))
            conn.commit()

            if test % 1000 == 0 and not dev.is_alive():
                print("Device not responding, resetting!")
                dev.reset()
    
    except USBException as e:
        print(f"Exception: {e} in command loop, resetting!")
        dev.reset()

conn.close()

