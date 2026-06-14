#!/usr/bin/env python3
import z3

# -------------------------------------------------------------
# Challenge: Impossible Brute Force
# You have a 16-byte key. A hash function checks:
#   sum(key[i] * primes[i]) == target
# and complex modulo relations.
# -------------------------------------------------------------

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]

def validate_password(password):
    if len(password) != 16: return False
    key = [ord(c) for c in password]
    total = sum(key[i] * primes[i] for i in range(16))
    return total == 36610 and password[:4] == "flag"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: python3 filename <password>")
        sys.exit(1)
    if validate_password(sys.argv[1]):
        print("[+] Correct!")
    else:
        print("[-] Wrong.")
