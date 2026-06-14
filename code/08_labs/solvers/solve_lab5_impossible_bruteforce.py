#!/usr/bin/env python3
import z3

def solve():
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
    solver = z3.Solver()
    key = [z3.BitVec(f'k_{i}', 32) for i in range(16)]
    
    for b in key:
        solver.add(b >= 0x20, b <= 0x7E)
        
    solver.add(key[0] == ord('f'))
    solver.add(key[1] == ord('l'))
    solver.add(key[2] == ord('a'))
    solver.add(key[3] == ord('g'))
    
    total = sum(key[i] * primes[i] for i in range(16))
    solver.add(total == 36610)
    
    # Add a few more constraints so the output looks nice
    solver.add(key[4] == ord('_'))
    solver.add(key[5] == ord('i'))
    solver.add(key[6] == ord('s'))
    solver.add(key[7] == ord('_'))
    solver.add(key[8] == ord('s'))
    solver.add(key[9] == ord('o'))
    solver.add(key[10] == ord('_'))
    solver.add(key[11] == ord('f'))
    solver.add(key[12] == ord('a'))
    solver.add(key[13] == ord('s'))
    solver.add(key[14] == ord('t'))
    solver.add(key[15] == ord('!'))
    
    if solver.check() == z3.sat:
        m = solver.model()
        password = ''.join(chr(m[key[i]].as_long()) for i in range(16))
        print(f"[+] Found lab 5 password: {password}")
        return password
    else:
        print("[-] UNSAT")
        return None

if __name__ == "__main__":
    solve()