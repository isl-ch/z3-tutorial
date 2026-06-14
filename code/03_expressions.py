#!/usr/bin/env python3
import z3

def demo_simplify():
    print("--- 3.1: simplify() ---")
    x = z3.Int('x')
    
    # We can write complex algebraic expressions and ask Z3 to simplify them
    expr = x + 1 + x + 2 + x * 2
    simplified = z3.simplify(expr)
    print(f"Original:   x + 1 + x + 2 + 2*x")
    print(f"Simplified: {simplified}") # Should show: 3 + 4*x
    
    # It also works on bitvectors
    a = z3.BitVec('a', 8)
    expr_bv = a ^ a ^ a
    print(f"BV Original:   a ^ a ^ a")
    print(f"BV Simplified: {z3.simplify(expr_bv)}") # Should show: a


def demo_substitute():
    print("\n--- 3.2: substitute() ---")
    x = z3.Int('x')
    y = z3.Int('y')
    
    expr = x + y * 2
    print(f"Original: {expr}")
    
    # Substitute x with 10 and y with (x + 1)
    new_expr = z3.substitute(expr, (x, z3.IntVal(10)), (y, x + 1))
    print(f"After substitution: {new_expr}")
    print(f"Simplified: {z3.simplify(new_expr)}")


def demo_logical_ops():
    print("\n--- 3.3: And, Or, Not ---")
    solver = z3.Solver()
    a = z3.Bool('a')
    b = z3.Bool('b')
    
    # And requires all constraints to be True
    # Or requires at least one constraint to be True
    # Not negates a constraint
    solver.add(z3.And(a, z3.Or(b, z3.Not(a))))
    
    if solver.check() == z3.sat:
        print(f"Solved: a={solver.model()[a]}, b={solver.model()[b]}")


def demo_if_then_else():
    print("\n--- 3.4: If (ITE - If Then Else) ---")
    # In binary execution, we often have branching:
    # val = (condition) ? value_if_true : value_if_false
    # We model this in Z3 using If(cond, true_val, false_val)
    solver = z3.Solver()
    
    cond = z3.Bool('cond')
    res = z3.Int('res')
    
    # C-like logic: if (cond) res = 10; else res = 20;
    solver.add(res == z3.If(cond, 10, 20))
    solver.add(res == 10)
    
    if solver.check() == z3.sat:
        print(f"Solved condition to get res=10: cond={solver.model()[cond]}")


def demo_implies():
    print("\n--- 3.5: Implies ---")
    # Implies(A, B) translates to "If A is True, then B MUST be True"
    # Note: If A is False, B can be True or False (vacuum truth).
    solver = z3.Solver()
    is_admin = z3.Bool('is_admin')
    has_root_privs = z3.Bool('has_root_privs')
    
    # If a user is admin, they must have root privileges
    solver.add(z3.Implies(is_admin, has_root_privs))
    
    # Force user to be admin, but deny root privileges
    solver.add(is_admin == True)
    solver.add(has_root_privs == False)
    
    print(f"Check conflict (admin = True, root = False): {solver.check()}") # Should be unsat


def demo_distinct():
    print("\n--- 3.6: Distinct ---")
    solver = z3.Solver()
    
    # Distinct enforces that all passed variables have different values
    vars_list = [z3.Int(f'x_{i}') for i in range(5)]
    
    # Enforce variables are in range [1, 5]
    for v in vars_list:
        solver.add(v >= 1, v <= 5)
        
    # Enforce they are all different
    solver.add(z3.Distinct(*vars_list))
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved Distinct values: {[m[v] for v in vars_list]}")


def challenge_3_solution():
    print("\n--- Challenge 3: Solution ---")
    # Modeling branching logic in a crackme validation:
    # int val = (key ^ 0x33) * 2;
    # if (key < 100) {
    #     val += 10;
    # } else {
    #     val -= 20;
    # }
    # We want val == 150
    solver = z3.Solver()
    key = z3.BitVec('key', 32)
    
    val = (key ^ 0x33) * 2
    val_after_branch = z3.If(z3.ULT(key, 100), val + 10, val - 20)
    
    solver.add(val_after_branch == 150)
    
    # Find all solutions
    while solver.check() == z3.sat:
        m = solver.model()
        v_key = m[key].as_long()
        print(f"  Valid key: {v_key} (Hex: {hex(v_key)})")
        solver.add(key != v_key)


if __name__ == "__main__":
    demo_simplify()
    demo_substitute()
    demo_logical_ops()
    demo_if_then_else()
    demo_implies()
    demo_distinct()
    challenge_3_solution()
