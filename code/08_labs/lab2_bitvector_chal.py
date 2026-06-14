#!/usr/bin/env python3
import z3

# -------------------------------------------------------------
# Challenge: Bitvector Magic
# The binary checks a 4-byte key using logical operations:
#   key_val = (key[0] << 24) | (key[1] << 16) | (key[2] << 8) | key[3]
#   v1 = rotate_right(key_val, 5)
#   v2 = (v1 ^ 0xDEADBEEF) - 0x1337
#   if v2 == 0xd42df267: print("Correct!")
# -------------------------------------------------------------

def validate_password(password):
    if len(password) != 4: return False
    key_val = int.from_bytes(password.encode(), 'big')
    # rotate right 5 bits (32-bit width)
    v1 = ((key_val >> 5) | (key_val << 27)) & 0xFFFFFFFF
    v2 = (v1 ^ 0xDEADBEEF)
    v2 = (v2 - 0x1337) & 0xFFFFFFFF
    return v2 == 0xd42df267


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: python3 filename <password>")
        sys.exit(1)
    if validate_password(sys.argv[1]):
        print("[+] Correct!")
    else:
        print("[-] Wrong.")
