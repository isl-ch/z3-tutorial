#!/usr/bin/env python3
import z3

# -------------------------------------------------------------
# 1. Simulated Decompiled Binary logic
# -------------------------------------------------------------
def validate_password(password):
    if len(password) != 8:
        return False
    
    key = [ord(c) for c in password]
    
    c1 = (key[0] ^ key[7] == 0x19)
    c2 = (key[1] + key[6] == 0x64)
    c3 = (key[2] - key[5] == 0x18)
    c4 = (key[3] ^ 0x55 == 0x18)
    c5 = (key[4] + 0x12 == 0x46)
    c6 = (key[5] ^ key[6] == 0x76)
    c7 = (key[7] - key[6] == 0x12)
    c8 = (key[7] + key[0] == 0x9D)
    
    return all([c1, c2, c3, c4, c5, c6, c7, c8])

# -------------------------------------------------------------
# 2. Z3 Solver
# -------------------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: python3 filename <password>")
        sys.exit(1)
    if validate_password(sys.argv[1]):
        print("[+] Correct!")
    else:
        print("[-] Wrong.")
