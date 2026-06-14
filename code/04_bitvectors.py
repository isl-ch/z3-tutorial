#!/usr/bin/env python3
import z3

def demo_extract_concat():
    print("--- 4.1: Extract and Concat ---")
    solver = z3.Solver()
    
    # Declare a 32-bit register (like EAX)
    eax = z3.BitVec('eax', 32)
    
    # We want to extract AX (lower 16 bits) and AL (lower 8 bits)
    # Syntax: Extract(high_bit, low_bit, bitvector)
    # Note: Bits are 0-indexed, starting from the LSB (Right) to MSB (Left).
    ax = z3.Extract(15, 0, eax)
    al = z3.Extract(7, 0, eax)
    ah = z3.Extract(15, 8, eax)
    
    # Let's say EAX is 0x12345678.
    # What are AX, AL, AH?
    solver.add(eax == 0x12345678)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"EAX: {hex(m[eax].as_long())}")
        print(f"AX:  {hex(m.evaluate(ax).as_long())}") # 0x5678
        print(f"AL:  {hex(m.evaluate(al).as_long())}") # 0x78
        print(f"AH:  {hex(m.evaluate(ah).as_long())}") # 0x56
        
    # Concat joins multiple bitvectors together
    solver.reset()
    byte1 = z3.BitVec('b1', 8)
    byte2 = z3.BitVec('b2', 8)
    
    # Combine two bytes into a 16-bit register
    reg = z3.Concat(byte1, byte2)
    solver.add(reg == 0x4142)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Concat Solved: b1={hex(m[byte1].as_long())}, b2={hex(m[byte2].as_long())}")


def demo_extensions():
    print("\n--- 4.2: ZeroExt and SignExt ---")
    # ZeroExt(n, bv) prepends n zeros (unsigned cast)
    # SignExt(n, bv) prepends n copies of the sign bit (signed cast)
    solver = z3.Solver()
    
    byte_val = z3.BitVecVal(0x80, 8) # Binary: 1000 0000 (MSB is 1)
    
    z_ext = z3.ZeroExt(8, byte_val) # Extends 8-bit to 16-bit
    s_ext = z3.SignExt(8, byte_val)
    
    print(f"ZeroExt of 0x80 to 16-bit: {hex(z3.simplify(z_ext).as_long())}") # 0x0080
    
    # 0x80 has MSB=1, so SignExt will fill the upper bits with 1s (0xFF80)
    print(f"SignExt of 0x80 to 16-bit: {hex(z3.simplify(s_ext).as_long())}") # 0xff80


def demo_shifts_rotations():
    print("\n--- 4.3: Shifts and Rotations ---")
    # Standard >> is Arithmetic shift right (preserves sign bit)
    # LShR is Logical shift right (fills with zeros)
    # RotateLeft and RotateRight rotate bits circularly
    x = z3.BitVecVal(0x80000000, 32)
    
    arith_shift = x >> 1
    logical_shift = z3.LShR(x, 1)
    
    print(f"Arithmetic Shift Right: {hex(z3.simplify(arith_shift).as_long())}") # 0xc0000000
    print(f"Logical Shift Right:    {hex(z3.simplify(logical_shift).as_long())}") # 0x40000000
    
    y = z3.BitVecVal(0x12345678, 32)
    # Rotate 4 bits to the right -> 0x81234567
    rot_r = z3.RotateRight(y, 4)
    # Rotate 4 bits to the left -> 0x23456781
    rot_l = z3.RotateLeft(y, 4)
    
    print(f"Rotate Right (4 bits): {hex(z3.simplify(rot_r).as_long())}")
    print(f"Rotate Left (4 bits):  {hex(z3.simplify(rot_l).as_long())}")


def demo_unsigned_comparisons():
    print("\n--- 4.4: Unsigned Comparisons ---")
    solver = z3.Solver()
    
    # 8-bit variables
    a = z3.BitVecVal(0xFF, 8) # -1 signed, 255 unsigned
    b = z3.BitVecVal(0x01, 8) # 1 signed, 1 unsigned
    
    # Signed comparison: 0xFF (-1) < 0x01 (1) -> True
    print(f"Signed Comparison (0xFF < 0x01): {z3.simplify(a < b)}")
    
    # Unsigned comparison: 0xFF (255) < 0x01 (1) -> False
    # Use z3.ULT (Unsigned Less Than)
    print(f"Unsigned Comparison (0xFF < 0x01): {z3.simplify(z3.ULT(a, b))}")


def challenge_4_solution():
    print("\n--- Challenge 4: Solution ---")
    # Imagine a checksum validation loop emulating this disassembly:
    # movzx eax, byte ptr [esi]
    # ror eax, 3
    # xor eax, 0x55
    # add edx, eax
    #
    # Let's model a 4-byte key check:
    # key is uint32_t (4 bytes).
    # byte0 = key[7:0], byte1 = key[15:8], byte2 = key[23:16], byte3 = key[31:24]
    # For each byte:
    #   val = RotateRight(ZeroExt(24, byte), 3) ^ 0x55
    #   checksum += val
    # We want checksum == 0x12345678 (as 32-bit register)
    # And key must be distinct readable ASCII chars (0x20 to 0x7E)
    solver = z3.Solver()
    key = z3.BitVec('key', 32)
    
    # Extract bytes
    b0 = z3.Extract(7, 0, key)
    b1 = z3.Extract(15, 8, key)
    b2 = z3.Extract(23, 16, key)
    b3 = z3.Extract(31, 24, key)
    
    # Enforce ASCII
    for b in [b0, b1, b2, b3]:
        solver.add(z3.UGE(b, 0x20))
        solver.add(z3.ULE(b, 0x7E))
        
    # Emulate checksum loop
    checksum = z3.BitVecVal(0, 32)
    for b in [b0, b1, b2, b3]:
        # Zero-extend the byte to 32 bits before rotating and XORing
        ext_b = z3.ZeroExt(24, b)
        val = z3.RotateRight(ext_b, 3) ^ 0x55
        checksum += val
        
    solver.add(checksum == 0x40000174) # A plausible checksum value
    
    if solver.check() == z3.sat:
        m = solver.model()
        v_key = m[key].as_long()
        print(f"Solved Key: {hex(v_key)}")
        # Print as string
        chars = [chr((v_key >> (i*8)) & 0xFF) for i in range(4)]
        print(f"Key String: {''.join(chars)}")
    else:
        print("Challenge 4 is UNSAT!")

if __name__ == "__main__":
    demo_extract_concat()
    demo_extensions()
    demo_shifts_rotations()
    demo_unsigned_comparisons()
    challenge_4_solution()
