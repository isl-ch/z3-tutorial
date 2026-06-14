#!/usr/bin/env python3
import z3

def demo_decompiled_c():
    print("--- 6.1: Modeling Decompiled C ---")
    # Decompiled logic:
    # int solve_me(int a, int b) {
    #     int x = a + 5;
    #     int y = b ^ x;
    #     if (y * 3 == 0x1337) return 1;
    #     return 0;
    # }
    solver = z3.Solver()
    a = z3.BitVec('a', 32)
    b = z3.BitVec('b', 32)
    
    # Model SSA (Static Single Assignment) variables
    x = a + 5
    y = b ^ x
    
    # Target path constraint
    solver.add(y * 3 == 0x1337)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved: a = {m[a]} ({hex(m[a].as_long())}), b = {m[b]} ({hex(m[b].as_long())})")


def demo_assembly():
    print("\n--- 6.2: Modeling Assembly Registers ---")
    # Assembly:
    # mov eax, edi      ; edi is input1
    # add eax, esi      ; esi is input2
    # xor eax, 0x1234
    # sub eax, esi
    # ; target: eax == 0x7777
    solver = z3.Solver()
    
    edi = z3.BitVec('edi', 32)
    esi = z3.BitVec('esi', 32)
    
    # Model register state transformations over instructions
    eax_0 = edi
    eax_1 = eax_0 + esi
    eax_2 = eax_1 ^ 0x1234
    eax_3 = eax_2 - esi
    
    solver.add(eax_3 == 0x7777)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved inputs: edi={hex(m[edi].as_long())}, esi={hex(m[esi].as_long())}")


def demo_loops():
    print("\n--- 6.3: Modeling Loops (Unrolling) ---")
    # Since Z3 cannot model dynamic loops easily, we must "unroll" them:
    # char key[4] = ...;
    # for (int i = 0; i < 4; i++) {
    #     key[i] = (key[i] ^ 0x42) + i;
    # }
    # Target: key == [0x05, 0x06, 0x07, 0x08]
    solver = z3.Solver()
    key_bytes = [z3.BitVec(f'key_{i}', 8) for i in range(4)]
    
    target = [0x05, 0x06, 0x07, 0x08]
    
    # Unroll the loop manually
    for i in range(4):
        transformed = (key_bytes[i] ^ 0x42) + i
        solver.add(transformed == target[i])
        
    if solver.check() == z3.sat:
        m = solver.model()
        solved_key = [m[key_bytes[i]].as_long() for i in range(4)]
        print(f"Solved Key Bytes: {solved_key}")
        print(f"Key String: {''.join(chr(x) for x in solved_key)}")


def demo_memory():
    print("\n--- 6.4: Modeling Memory and Pointers ---")
    # C code:
    # int main() {
    #     int arr[3] = {10, 20, 30};
    #     int* p = arr;
    #     p[idx] = val;
    #     if (arr[2] == 99) { success(); }
    # }
    solver = z3.Solver()
    
    # Initial array state
    arr_0 = z3.Array('arr', z3.BitVecSort(32), z3.BitVecSort(32))
    
    # Set up initial array: arr[0]=10, arr[1]=20, arr[2]=30
    arr_1 = z3.Store(arr_0, z3.BitVecVal(0, 32), z3.BitVecVal(10, 32))
    arr_2 = z3.Store(arr_1, z3.BitVecVal(1, 32), z3.BitVecVal(20, 32))
    arr_3 = z3.Store(arr_2, z3.BitVecVal(2, 32), z3.BitVecVal(30, 32))
    
    # Symbolic write index and value
    idx = z3.BitVec('idx', 32)
    val = z3.BitVec('val', 32)
    
    # arr[idx] = val
    arr_4 = z3.Store(arr_3, idx, val)
    
    # Target: arr[2] == 99
    solver.add(z3.Select(arr_4, z3.BitVecVal(2, 32)) == 99)
    # Ensure index is within bounds [0, 2]
    solver.add(z3.UGE(idx, 0), z3.ULE(idx, 2))
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved Memory Write: write to index={m[idx]} with value={m[val]}")


def challenge_6_solution():
    print("\n--- Challenge 6: Solution ---")
    # Challenge logic (register state & stack):
    # struct data { uint32_t val1; uint32_t val2; };
    # void validate(struct data* d) {
    #     uint32_t temp = d->val1 ^ 0xdeadbeef;
    #     temp = temp + d->val2;
    #     d->val1 = temp;
    # }
    # We want: val1 ends up as 0x13371337, and val2 was 0x00123456.
    # What was the original val1?
    solver = z3.Solver()
    val1_orig = z3.BitVec('val1_orig', 32)
    val2 = z3.BitVecVal(0x00123456, 32)
    
    temp = val1_orig ^ 0xdeadbeef
    val1_final = temp + val2
    
    solver.add(val1_final == 0x13371337)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved Original val1: {hex(m[val1_orig].as_long())}")
    else:
        print("Challenge 6 is UNSAT!")

if __name__ == "__main__":
    demo_decompiled_c()
    demo_assembly()
    demo_loops()
    demo_memory()
    challenge_6_solution()
