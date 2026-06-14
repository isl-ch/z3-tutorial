#!/usr/bin/env python3
import z3

def solve():
    solver = z3.Solver()
    
    # We can model the entire 4-byte key as a single 32-bit BitVec
    key_val = z3.BitVec('key_val', 32)
    
    # Ensure all 4 bytes are printable ASCII (0x20 to 0x7E)
    b0 = z3.Extract(31, 24, key_val)
    b1 = z3.Extract(23, 16, key_val)
    b2 = z3.Extract(15,  8, key_val)
    b3 = z3.Extract( 7,  0, key_val)
    
    for b in [b0, b1, b2, b3]:
        solver.add(b >= 0x20, b <= 0x7E)
        
    # Translate constraints
    v1 = z3.RotateRight(key_val, 5)
    v2 = v1 ^ 0xDEADBEEF
    solver.add(v2 - 0x1337 == 0xd42df267)
    
    if solver.check() == z3.sat:
        m = solver.model()
        solution_int = m[key_val].as_long()
        password = solution_int.to_bytes(4, 'big').decode()
        print(f"[+] Found lab 2 password: {password}")
        return password
    else:
        print("[-] UNSAT")
        return None

if __name__ == "__main__":
    solve()