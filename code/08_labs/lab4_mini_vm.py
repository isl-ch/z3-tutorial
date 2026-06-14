#!/usr/bin/env python3
import z3

# -------------------------------------------------------------
# Challenge: Mini VM
# The binary is a small VM executing 3 instructions over a 
# 32-bit register initialized to 0. 
# The VM reads a 3-byte passcode acting as opcodes:
#   op1 = key[0], op2 = key[1], op3 = key[2]
#   for op in [op1, op2, op3]:
#       if op == 'A': reg = (reg + 5) & 0xFFFFFFFF
#       if op == 'B': reg = (reg * 3) & 0xFFFFFFFF
#       if op == 'C': reg = (reg ^ 0x42)
#   if reg == 77: print("Correct!")
# -------------------------------------------------------------

def validate_password(password):
    if len(password) != 3: return False
    reg = 0
    for op in password:
        if op == 'A': reg = (reg + 5) & 0xFFFFFFFF
        elif op == 'B': reg = (reg * 3) & 0xFFFFFFFF
        elif op == 'C': reg = (reg ^ 0x42)
    return reg == 77


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: python3 filename <password>")
        sys.exit(1)
    if validate_password(sys.argv[1]):
        print("[+] Correct!")
    else:
        print("[-] Wrong.")
