#!/usr/bin/env python3
"""A simple script to generate a keycard ID for the SCP Foundation.

This script is based on the keycard ID generation algorithm used by the SCP
Foundation. It is intended to be used as a tool for SCP roleplay, and is not
intended to be used for any other purpose.

Typical usage example:
    $ python scpidgen.py
"""
import binascii
import colorama

import pyperclip

# COLOR CODES
colorama.init()
RED = colorama.Fore.RED
RESET = colorama.Fore.RESET
BLUE = colorama.Fore.BLUE

print(RED + "SCP Foundation ID Generator")
print("Access strictly prohibited to unauthorized personnel!")
print(RESET)

data = ["", "", "", "", ""]

# DEPARTMENT CODE (5 chars) - Padded with asterisks
while True:
    dept = input("Enter the department code (Max 5 chars):\n")
    if len(dept) > 5:
        print(RED + "Error: Department code too long!" + RESET)
        continue
    dept = "*"*(5-len(dept)) + dept.upper()
    data[0] = dept
    break

# POSITION CODE (2 chars) - No padding
while True:
    pos = input("Enter the position code (2 chars):\n")
    if len(pos) != 2:
        print(RED + "Error: Position code invalid length!" + RESET)
        continue
    pos = pos.upper()
    data[1] = pos
    break

# POSITION ID (4 chars) - Padded with zeros
while True:
    posid = input("Enter the position ID (Max 4 chars):\n")
    if len(posid) > 4:
        print(RED + "Error: Position ID too long!" + RESET)
        continue
    if not posid.isnumeric():
        print(RED + "Error: Position ID must be numeric!" + RESET)
        continue
    posid = posid.zfill(4)
    data[2] = posid
    break

# FORMATION TYPE (2 chars) - No padding
while True:
    frmt = input("Enter the formation type (2 chars):\n")
    if len(frmt) != 2:
        print(RED + "Error: Formation type invalid length!" + RESET)
        continue
    frmt = frmt.upper()
    data[3] = frmt
    break

# FORMATION ID (3 chars) - Padded with zeros
while True:
    frmtid = input("Enter the formation ID (Max 3 chars):\n")
    if len(frmtid) > 3:
        print(RED + "Error: Formation ID too long!" + RESET)
        continue
    if not frmtid.isnumeric():
        print(RED + "Error: Formation ID must be numeric!" + RESET)
        continue
    frmtid = frmtid.zfill(3)
    data[4] = frmtid
    break

# GENERATE ID
print(BLUE + "Generating ID...")
k_id = ""
for datafield in data:
    k_id += datafield
    k_id += f"{binascii.crc32(bytes(k_id,'utf-8')):x}".zfill(8)

print("ID generation complete!" + RESET)
print(f"ID: {k_id}")
pyperclip.copy(k_id)
print("Keycacard ID ready for use!")
