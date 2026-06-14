#!/usr/bin/env python3
import z3

def solve():
    solver = z3.Solver()
    key = [z3.BitVec(f'op_{i}', 8) for i in range(3)]
    
    # Opcodes can only be 'A', 'B', or 'C'
    for b in key:
        solver.add(z3.Or(b == ord('A'), b == ord('B'), b == ord('C')))
        
    reg = z3.BitVecVal(0, 32)
    
    for i in range(3):
        # We model the switch-case execution
        reg = z3.If(key[i] == ord('A'), reg + 5,
              z3.If(key[i] == ord('B'), reg * 3,
              z3.If(key[i] == ord('C'), reg ^ 0x42,
              reg)))
              
    solver.add(reg == 77)
    
    if solver.check() == z3.sat:
        m = solver.model()
        password = ''.join(chr(m[key[i]].as_long()) for i in range(3))
        print(f"[+] Found lab 4 password: {password}")
        return password
    else:
        print("[-] UNSAT")
        return None

if __name__ == "__main__":
    solve()