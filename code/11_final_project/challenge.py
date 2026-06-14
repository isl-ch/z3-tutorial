#!/usr/bin/env python3
import sys

# -------------------------------------------------------------
# Z3 Tutorial: Final Project Challenge
# A realistic crackme combining multiple techniques.
# -------------------------------------------------------------

def rotate_left(val, r_bits, max_bits):
    return ((val << r_bits) | (val >> (max_bits - r_bits))) & ((1 << max_bits) - 1)

def validate(password):
    if len(password) != 12:
        return False
        
    key = [ord(c) for c in password]
    
    # 1. First 4 bytes form a 32-bit integer. Must satisfy an equation.
    v1 = (key[0] << 24) | (key[1] << 16) | (key[2] << 8) | key[3]
    if (v1 ^ 0x12345678) != 0x5458371B:
        return False
        
    # 2. Middle 4 bytes: Rolling XOR and checksum
    # key[4] ^ key[5] = 0x11
    # key[5] ^ key[6] = 0x16
    # key[6] ^ key[7] = 0x05
    # sum(key[4:8]) = 0x11C
    if key[4] ^ key[5] != 0x11: return False
    if key[5] ^ key[6] != 0x16: return False
    if key[6] ^ key[7] != 0x05: return False
    if sum(key[4:8]) != 0x11C: return False
    
    # 3. Last 4 bytes: Mini-VM
    reg = 0x10
    for op in key[8:12]:
        if op % 2 == 0:
            reg = (reg * 2) & 0xFF
        else:
            reg = (reg ^ op)
            
    if reg != 123:
        return False
        
    # Additional tie-breaker to ensure exactly one intended string
    if key[8] != ord('c') or key[9] != ord('o') or key[10] != ord('d') or key[11] != ord('e'):
        return False

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 challenge.py <password>")
        sys.exit(1)
        
    if validate(sys.argv[1]):
        print("[+] Access Granted! You are a Z3 Master.")
    else:
        print("[-] Access Denied.")
