#!/usr/bin/env python3
import z3

# -------------------------------------------------------------
# Challenge: Loop Reconstruction
# The binary takes a 6-byte password and applies a loop:
#   checksum = 0
#   for i in range(6):
#       checksum = (checksum ^ key[i]) + 0x11
#   if checksum == 0xaf: print("Correct!")
# We also know key[0] is 'Z' and key[5] is '3'
# -------------------------------------------------------------

def validate_password(password):
    if len(password) != 6: return False
    checksum = 0
    key = [ord(c) for c in password]
    for i in range(6):
        checksum = ((checksum ^ key[i]) + 0x11) & 0xFF
    return checksum == 0xaf and password[0] == 'Z' and password[5] == '3'


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: python3 filename <password>")
        sys.exit(1)
    if validate_password(sys.argv[1]):
        print("[+] Correct!")
    else:
        print("[-] Wrong.")
