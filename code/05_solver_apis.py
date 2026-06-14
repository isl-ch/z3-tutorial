#!/usr/bin/env python3
import z3

def demo_push_pop():
    print("--- 5.1: push() and pop() ---")
    solver = z3.Solver()
    x = z3.Int('x')
    
    solver.add(x > 5)
    
    # Save the current state of the solver (creates a backtrack point)
    solver.push()
    
    # Add a temporary constraint
    solver.add(x == 10)
    print(f"Check inside push context (x > 5 AND x == 10): {solver.check()}") # sat
    if solver.check() == z3.sat:
        print(f"  Model: {solver.model()}")
        
    # Restore the solver state (removes the 'x == 10' constraint)
    solver.pop()
    
    solver.push()
    solver.add(x == 2)
    print(f"Check inside second push context (x > 5 AND x == 2): {solver.check()}") # unsat
    solver.pop()
    
    # The solver is back to having only 'x > 5'
    print(f"Check after pops (x > 5): {solver.check()}") # sat


def demo_assertions_stats():
    print("\n--- 5.2: assertions() and statistics() ---")
    solver = z3.Solver()
    x = z3.Int('x')
    solver.add(x > 10)
    solver.add(x < 20)
    
    # View all currently registered constraints
    print("Current assertions:")
    for a in solver.assertions():
        print(f"  - {a}")
        
    solver.check()
    # Print solving statistics (useful for tuning performance)
    print("Solver statistics:")
    stats = solver.statistics()
    for name in stats.keys():
        print(f"  {name}: {stats.get_key_value(name)}")


def demo_unsat_core():
    print("\n--- 5.3: unsat_core() ---")
    # Debugging why a system is unsatisfiable. We name constraints using 'assumptions'
    solver = z3.Solver()
    x = z3.Int('x')
    
    # We assign boolean variables (labels) to track assertions
    p1 = z3.Bool('rule_greater_than_10')
    p2 = z3.Bool('rule_less_than_5')
    p3 = z3.Bool('rule_is_even')
    
    # Assert constraints under assumptions
    solver.add(z3.Implies(p1, x > 10))
    solver.add(z3.Implies(p2, x < 5))
    solver.add(z3.Implies(p3, x % 2 == 0))
    
    # Check satisfiability under these assumptions
    # We pass the tracking booleans to check()
    result = solver.check(p1, p2, p3)
    print(f"Check with assumptions: {result}") # unsat
    
    if result == z3.unsat:
        # Retrieve the subset of assumptions that caused the conflict
        core = solver.unsat_core()
        print(f"Unsat Core (Conflicting rules): {core}")


def demo_optimize():
    print("\n--- 5.4: Optimize() ---")
    # Sometimes we want the "best" solution (e.g. shortest string, highest value, lowest cost)
    # Z3 provides z3.Optimize() which has minimize() and maximize()
    opt = z3.Optimize()
    
    x = z3.Int('x')
    y = z3.Int('y')
    
    opt.add(x + y == 100)
    opt.add(x >= 0, y >= 0)
    
    # We want to maximize the product x * y
    h = opt.maximize(x * y)
    
    if opt.check() == z3.sat:
        m = opt.model()
        print(f"Maximized Product: x={m[x]}, y={m[y]}, product={m.evaluate(x * y)}")


def challenge_5_solution():
    print("\n--- Challenge 5: Solution ---")
    # Finding the optimal solution to a crackme where the license key must satisfy:
    # 1. key ^ 0x1337 == 0x7FBA (16-bit BitVec)
    # 2. But we want to find the key with the minimum number of set bits (popcount).
    # We can model popcount of a 16-bit BitVec by summing its bits:
    # bit_i = Extract(i, i, key)
    # cost = Sum(bit_0, bit_1, ..., bit_15)
    opt = z3.Optimize()
    key = z3.BitVec('key', 16)
    
    opt.add(key ^ 0x1337 == 0x7FBA)
    
    # Define popcount
    popcount = z3.ZeroExt(16, z3.Extract(0, 0, key))
    for i in range(1, 16):
        popcount += z3.ZeroExt(16, z3.Extract(i, i, key))
        
    opt.minimize(popcount)
    
    if opt.check() == z3.sat:
        m = opt.model()
        v_key = m[key].as_long()
        print(f"Optimal Key: {hex(v_key)}")
        print(f"Popcount: {m.evaluate(popcount)}")
    else:
        print("Challenge 5 is UNSAT!")

if __name__ == "__main__":
    demo_push_pop()
    demo_assertions_stats()
    demo_unsat_core()
    demo_optimize()
    challenge_5_solution()
