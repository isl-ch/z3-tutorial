#!/usr/bin/env python3
import z3

def demo_xor_pattern():
    print("--- 7.1: XOR Obfuscation Pattern ---")
    # A common obfuscation is a rolling XOR:
    # key[i] = flag[i] ^ flag[i-1] ^ constant
    solver = z3.Solver()
    
    # We have an encrypted ciphertext
    ciphertext = [0x38, 0x0b, 0x08, 0x5e]
    n = len(ciphertext)
    
    # We want to solve for the original plaintext key bytes
    plaintext = [z3.BitVec(f'pt_{i}', 8) for i in range(n)]
    
    # Enforce printable ASCII
    for char in plaintext:
        solver.add(z3.And(char >= 0x20, char <= 0x7E))
        
    # The encryption logic
    solver.add(plaintext[0] ^ 0x42 == ciphertext[0])
    for i in range(1, n):
        solver.add(plaintext[i] ^ plaintext[i-1] ^ 0x42 == ciphertext[i])
        
    if solver.check() == z3.sat:
        m = solver.model()
        solved = [m[plaintext[i]].as_long() for i in range(n)]
        print(f"Decrypted: {''.join(chr(x) for x in solved)}")


def demo_crc_pattern():
    print("\n--- 7.2: CRC / Checksum Pattern ---")
    # Let's model a custom 8-bit CRC-like checksum validation.
    # unsigned char crc8(unsigned char* data, int len) {
    #     unsigned char crc = 0xFF;
    #     for (int i = 0; i < len; i++) {
    #         crc ^= data[i];
    #         for (int j = 0; j < 8; j++) {
    #             if (crc & 0x80) crc = (crc << 1) ^ 0x07;
    #             else crc <<= 1;
    #         }
    #     }
    #     return crc;
    # }
    solver = z3.Solver()
    
    # Input is 2 bytes
    data = [z3.BitVec(f'd_{i}', 8) for i in range(2)]
    
    # We want crc8(data, 2) == 0xBC
    crc = z3.BitVecVal(0xFF, 8)
    
    for i in range(2):
        crc = crc ^ data[i]
        for j in range(8):
            # Model the conditional branch 'crc & 0x80'
            msb = z3.Extract(7, 7, crc)
            crc = z3.If(msb == 1, (crc << 1) ^ 0x07, crc << 1)
            
    solver.add(crc == 0xBC)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved CRC inputs: d_0={hex(m[data[0]].as_long())}, d_1={hex(m[data[1]].as_long())}")


def demo_byte_relations():
    print("\n--- 7.3: Byte Relations Pattern ---")
    # Common in crackmes: systems of linear congruences on flag bytes.
    # flag[0] + flag[1] == 160
    # flag[1] - flag[2] == 10
    # flag[2] * flag[0] == 5000
    solver = z3.Solver()
    
    f = [z3.BitVec(f'f_{i}', 8) for i in range(3)]
    
    solver.add(f[0] + f[1] == 160)
    solver.add(f[1] - f[2] == 10)
    # Be careful of multiplication overflow in 8-bit. We can zero-extend to 16-bit to do math.
    solver.add(z3.ZeroExt(8, f[2]) * z3.ZeroExt(8, f[0]) == 5000)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved Bytes: {[m[x].as_long() for x in f]}")


def demo_vm_handler():
    print("\n--- 7.4: VM Handler Pattern ---")
    # emulating a step in a virtual machine interpreter:
    # opcode = code[pc];
    # if (opcode == 0x01) regA += regB;
    # else if (opcode == 0x02) regA ^= regB;
    # else if (opcode == 0x03) regA *= 2;
    solver = z3.Solver()
    
    opcode = z3.BitVec('opcode', 8)
    regA_in = z3.BitVecVal(10, 32)
    regB = z3.BitVecVal(5, 32)
    
    # Result of handler execution
    regA_out = z3.If(opcode == 0x01, regA_in + regB,
               z3.If(opcode == 0x02, regA_in ^ regB,
               z3.If(opcode == 0x03, regA_in * 2,
               regA_in))) # default: no change
               
    # We want regA_out to be 20
    solver.add(regA_out == 20)
    
    # Solve for opcode
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved VM Opcode to double regA: {hex(m[opcode].as_long())}")


def challenge_7_solution():
    print("\n--- Challenge 7: Solution ---")
    # Reconstruct 4-byte key passing rolling XOR and byte relation checks:
    # key[0] ^ key[1] == 0x05
    # key[1] + key[2] == 150
    # key[2] ^ key[3] == 0x08
    # key[3] * key[0] == 4818 (using 16-bit math to prevent overflow)
    solver = z3.Solver()
    key = [z3.BitVec(f'k_{i}', 8) for i in range(4)]
    
    # Enforce ASCII printable
    for b in key:
        solver.add(z3.And(b >= 0x20, b <= 0x7E))
        
    solver.add(key[0] ^ key[1] == 0x05)
    solver.add(key[1] + key[2] == 150)
    solver.add(key[2] ^ key[3] == 0x08)
    
    # 16-bit multiplication
    solver.add(z3.ZeroExt(8, key[3]) * z3.ZeroExt(8, key[0]) == 4818)
    
    if solver.check() == z3.sat:
        m = solver.model()
        solved_key = [m[key[i]].as_long() for i in range(4)]
        print(f"Solved Challenge 7 Key: {''.join(chr(x) for x in solved_key)}")
    else:
        print("Challenge 7 is UNSAT!")

if __name__ == "__main__":
    demo_xor_pattern()
    demo_crc_pattern()
    demo_byte_relations()
    demo_vm_handler()
    challenge_7_solution()
