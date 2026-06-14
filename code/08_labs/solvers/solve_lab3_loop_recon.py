#!/usr/bin/env python3
import z3

def solve():
    solver = z3.Solver()
    
    key = [z3.BitVec(f'k_{i}', 8) for i in range(6)]
    
    for b in key:
        solver.add(b >= 0x20, b <= 0x7E)
        
    solver.add(key[0] == ord('Z'))
    solver.add(key[5] == ord('3'))
    
    checksum = z3.BitVecVal(0, 8)
    for i in range(6):
        # Emulate the loop in Z3
        checksum = (checksum ^ key[i]) + 0x11
        
    solver.add(checksum == 0xaf)
    
    # Restrict one possible solution for simplicity
    solver.add(key[1] == ord('z'))
    solver.add(key[2] == ord('_'))
    solver.add(key[3] == ord('L'))
    solver.add(key[4] == ord('O'))
    
    if solver.check() == z3.sat:
        m = solver.model()
        password = ''.join(chr(m[key[i]].as_long()) for i in range(6))
        print(f"[+] Found lab 3 password: {password}")
        return password
    else:
        print("[-] UNSAT")
        return None

if __name__ == "__main__":
    solve()