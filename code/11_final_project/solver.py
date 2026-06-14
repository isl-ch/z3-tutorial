#!/usr/bin/env python3
import z3

def solve():
    solver = z3.Solver()
    
    # 12-byte key
    key = [z3.BitVec(f'k_{i}', 8) for i in range(12)]
    
    # Enforce printable ASCII
    for b in key:
        solver.add(b >= 0x20, b <= 0x7E)
        
    # 1. First 4 bytes
    v1 = z3.Concat(key[0], key[1], key[2], key[3])
    solver.add((v1 ^ 0x12345678) == 0x5458371B)
    
    # 2. Middle 4 bytes
    solver.add(key[4] ^ key[5] == 0x11)
    solver.add(key[5] ^ key[6] == 0x16)
    solver.add(key[6] ^ key[7] == 0x05)
    
    sum_mid = z3.ZeroExt(8, key[4]) + z3.ZeroExt(8, key[5]) + z3.ZeroExt(8, key[6]) + z3.ZeroExt(8, key[7])
    solver.add(sum_mid == 0x11C)
    
    # 3. Last 4 bytes (Mini-VM)
    reg = z3.BitVecVal(0x10, 8)
    for i in range(8, 12):
        # op % 2 == 0 means the lowest bit is 0
        is_even = (key[i] & 1) == 0
        reg = z3.If(is_even, reg * 2, reg ^ key[i])
        
    solver.add(reg == 123)
    
    # Tie breakers
    solver.add(key[8] == ord('c'))
    solver.add(key[9] == ord('o'))
    solver.add(key[10] == ord('d'))
    solver.add(key[11] == ord('e'))
    
    if solver.check() == z3.sat:
        m = solver.model()
        password = ''.join(chr(m[key[i]].as_long()) for i in range(12))
        print(f"[+] Found Final Project Password: {password}")
        return password
    else:
        print("[-] UNSAT")
        return None

if __name__ == "__main__":
    solve()
