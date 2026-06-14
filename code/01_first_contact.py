#!/usr/bin/env python3
import z3

def example_simple_equation():
    print("--- Example 1: Simple Equation ---")
    # 1. Create a solver instance
    solver = z3.Solver()

    # 2. Define variables (Integers in this case)
    x = z3.Int('x')
    y = z3.Int('y')

    # 3. Add constraints
    solver.add(x + y == 10)
    solver.add(x > 2)
    solver.add(y < 5)

    # 4. Check satisfiability
    result = solver.check()
    print(f"Solver result: {result}")

    if result == z3.sat:
        # 5. Extract the model
        model = solver.model()
        print(f"Model: {model}")
        
        # 6. Read specific values
        val_x = model[x]
        val_y = model[y]
        print(f"Solved: x = {val_x}, y = {val_y}")
        
        # Evaluate expressions using the model
        expr = x * 2 + y
        val_expr = model.evaluate(expr)
        print(f"Evaluated expression (2*x + y): {val_expr}")
    else:
        print("No solution found (UNSAT)")


def example_multiple_solutions():
    print("\n--- Example 2: Finding Multiple Solutions ---")
    solver = z3.Solver()
    a = z3.Int('a')
    
    # We want a value between 1 and 5 (inclusive)
    solver.add(a >= 1)
    solver.add(a <= 5)
    
    print("Finding all valid solutions:")
    while solver.check() == z3.sat:
        model = solver.model()
        val_a = model[a]
        print(f"  Found solution: a = {val_a}")
        
        # Add a constraint to prevent the solver from finding the same solution again
        solver.add(a != val_a)
    print("No more solutions.")


def example_unsat():
    print("\n--- Example 3: Unsat Scenario ---")
    solver = z3.Solver()
    x = z3.Int('x')
    
    solver.add(x > 10)
    solver.add(x < 5)
    
    result = solver.check()
    print(f"Solver result for x > 10 AND x < 5: {result}")


def challenge_1_solution():
    print("\n--- Challenge 1: Solution ---")
    # Solve for 3 numbers (a, b, c) such that:
    # 1. a + b + c == 100
    # 2. a > 0, b > 0, c > 0
    # 3. a * 2 - b == 50
    # 4. c % 7 == 0
    # 5. a, b, c are distinct
    solver = z3.Solver()
    a, b, c = z3.Int('a'), z3.Int('b'), z3.Int('c')
    
    solver.add(a + b + c == 100)
    solver.add(a > 0, b > 0, c > 0)
    solver.add(a * 2 - b == 50)
    solver.add(c % 7 == 0)
    solver.add(z3.Distinct(a, b, c))
    
    if solver.check() == z3.sat:
        m = solver.model()
        print(f"Solved Challenge 1: a={m[a]}, b={m[b]}, c={m[c]}")
    else:
        print("Challenge 1 is UNSAT!")

if __name__ == "__main__":
    example_simple_equation()
    example_multiple_solutions()
    example_unsat()
    challenge_1_solution()
