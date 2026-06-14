import z3

def solve():
    solver = z3.Solver()
    key = [z3.BitVec(f'k_{i}', 8) for i in range(8)]
    for b in key:
        solver.add(b >= 0x20, b <= 0x7E)
        
    solver.add(key[0] ^ key[7] == 0x19)
    solver.add(key[1] + key[6] == 0x64)
    solver.add(key[2] - key[5] == 0x18)
    solver.add(key[3] ^ 0x55 == 0x18)
    solver.add(key[4] + 0x12 == 0x46)
    solver.add(key[5] ^ key[6] == 0x76)
    solver.add(key[6] - key[7] == 0xEE)
    solver.add(key[7] + key[0] == 0x9D)
    
    # ensure it's the only solution:
    while solver.check() == z3.sat:
        m = solver.model()
        password = ''.join(chr(m[key[i]].as_long()) for i in range(8))
        print(f"[+] Found password: {password}")
        solver.add(z3.Or([key[i] != m[key[i]] for i in range(8)]))

solve()
