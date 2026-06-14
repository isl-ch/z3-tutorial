#!/usr/bin/env python3
import z3

def demo_int_real():
    print("--- 2.1 & 2.2: Int and Real ---")
    solver = z3.Solver()
    
    # Ints are mathematical integers (arbitrary precision, no overflow)
    x = z3.Int('x')
    # Reals are mathematical real numbers (fractions/decimals, no rounding errors)
    r = z3.Real('r')
    
    solver.add(x * 2 == 5) # Impossible for Int
    print(f"Int check (x * 2 == 5): {solver.check()}") # Should be unsat
    
    solver.reset()
    solver.add(r * 2 == 5)
    print(f"Real check (r * 2 == 5): {solver.check()}") # Should be sat
    if solver.check() == z3.sat:
        print(f"  Solved Real: r = {solver.model()[r]}")


def demo_bool():
    print("\n--- 2.3: Bool ---")
    solver = z3.Solver()
    
    # Bools represent truth values (True / False)
    is_valid = z3.Bool('is_valid')
    is_admin = z3.Bool('is_admin')
    
    # We can combine them with logical operators
    solver.add(z3.Or(is_valid, is_admin))
    solver.add(z3.Not(is_admin))
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved Bool: is_valid={m[is_valid]}, is_admin={m[is_admin]}")


def demo_bitvec():
    print("\n--- 2.4: BitVec (The RE Bread & Butter) ---")
    # BitVec represents fixed-width machine integers (like 8-bit char, 32-bit uint, 64-bit size_t)
    # They exhibit realistic overflow and underflow behavior.
    solver = z3.Solver()
    
    # 8-bit unsigned char variables
    x = z3.BitVec('x', 8)
    y = z3.BitVec('y', 8)
    
    # Overflow check: x + 10 == 5
    # Mathematically impossible for Int, but possible for 8-bit integers due to overflow!
    # (251 + 10 = 261. 261 % 256 = 5)
    solver.add(x + 10 == 5)
    
    # Masking check: (y & 0x0F) == 0x0B
    solver.add(y & 0xF0 == 0xA0)
    solver.add(y & 0x0F == 0x0B)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved BitVec (8-bit):")
        print(f"  x = {m[x]} (Hex: {hex(m[x].as_long())})")
        print(f"  y = {m[y]} (Hex: {hex(m[y].as_long())})")


def demo_arrays():
    print("\n--- 2.5: Arrays (Memory Modeling) ---")
    # Z3 Arrays model computer memory (index-to-value mappings)
    # Array(name, domain_sort, range_sort)
    # e.g., mapping 32-bit addresses to 8-bit values (bytes)
    solver = z3.Solver()
    
    mem = z3.Array('mem', z3.BitVecSort(32), z3.BitVecSort(8))
    addr = z3.BitVec('addr', 32)
    
    # Write a byte 0x41 ('A') to address 0x1000
    # Store returns a new modified array state
    new_mem = z3.Store(mem, z3.BitVecVal(0x1000, 32), z3.BitVecVal(0x41, 8))
    
    # Constraint: reading from 'addr' in 'new_mem' gives 0x41
    # Select reads from an array
    solver.add(z3.Select(new_mem, addr) == 0x41)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved Array Index: addr = {hex(m[addr].as_long())}")


def demo_strings():
    print("\n--- 2.6: Strings ---")
    solver = z3.Solver()
    
    s1 = z3.String('s1')
    s2 = z3.String('s2')
    
    # Constraints: concatenation of s1 and s2 is "FLAG{Z3_is_fun}"
    solver.add(z3.Concat(s1, s2) == "FLAG{Z3_is_fun}")
    solver.add(z3.Length(s1) == 5)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved Strings: s1 = {m[s1]}, s2 = {m[s2]}")


def demo_floating_point():
    print("\n--- 2.7: Floating Point ---")
    solver = z3.Solver()
    
    # Declaring a double precision (64-bit) floating point variable
    f = z3.FP('f', z3.Float64())
    
    # Constraint: f + 1.0 == 3.5
    # Note: We must use z3.FPVal to represent floating point constants
    solver.add(f + z3.FPVal(1.0, z3.Float64()) == z3.FPVal(3.5, z3.Float64()))
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved Floating Point: f = {m[f]}")



def demo_datatypes():
    print("\n--- 2.8: Custom Datatypes ---")
    solver = z3.Solver()
    
    # Define a custom record/struct in Z3
    # E.g. a Point struct with 'x' and 'y' fields
    Point = z3.Datatype('Point')
    Point.declare('mk_point', ('x', z3.IntSort()), ('y', z3.IntSort()))
    Point = Point.create()
    
    p = z3.Const('p', Point)
    
    # Access fields using the accessor functions
    solver.add(Point.x(p) > 10)
    solver.add(Point.y(p) == Point.x(p) * 2)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved Custom Datatype Point: {m[p]}")


def demo_functions():
    print("\n--- 2.9: Symbolic Functions ---")
    solver = z3.Solver()
    
    # Define a function sort: takes two Ints, returns one Int
    f = z3.Function('f', z3.IntSort(), z3.IntSort(), z3.IntSort())
    
    x = z3.Int('x')
    
    # Define constraints on the function f
    solver.add(f(1, 2) == 10)
    solver.add(f(2, 3) == 20)
    solver.add(f(x, 2) == 10)
    
    # Ensure x is not 1 (which would be trivial)
    solver.add(x != 1)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved x: x = {m[x]}")
        print(f"Solver's interpretation of function f: {m[f]}")


def challenge_2_solution():
    print("\n--- Challenge 2: Solution ---")
    # Find a 16-bit BitVec 'key' such that:
    # 1. key + 0x1337 == 0x4242 (with 16-bit unsigned overflow)
    # 2. key ^ 0x55AA == 0x7AA1 (bitwise XOR)
    solver = z3.Solver()
    key = z3.BitVec('key', 16)
    
    solver.add(key + 0x1337 == 0x4242)
    solver.add(key ^ 0x55AA == 0x7AA1)
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved Challenge 2: key = {hex(m[key].as_long())}")
    else:
        print("Challenge 2 is UNSAT!")



if __name__ == "__main__":
    demo_int_real()
    demo_bool()
    demo_bitvec()
    demo_arrays()
    demo_strings()
    demo_floating_point()
    demo_datatypes()
    demo_functions()
    challenge_2_solution()
