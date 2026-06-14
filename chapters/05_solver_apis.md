# Part 5 — Solver APIs Deep Dive

So far, we have used Z3's solver by adding rules and calling `check()`. In real-world projects, you will deal with massive constraint lists, debugging unsolvable inputs (UNSAT), and looking for the "best" answer. In this chapter, you will learn the APIs that power professional Z3 implementations.

---

## 5.1 push() and pop() (State Scoping)

In reverse engineering, we often explore a program's Control Flow Graph (CFG). As we move down a branch, we accumulate constraints. If we hit a dead end, we want to backtrack without throwing away all the constraints we gathered before the branch.

`push()` and `pop()` let you manage constraints like a stack:
* **`push()`**: Saves the solver's current state (creates a checkpoint).
* **`pop()`**: Restores the solver's state to the last checkpoint (removes all constraints added since the last `push()`).

### Visual Model of Scoping

```
  Base State: [x > 5]
       |
       +---> push()
       |       |
       |       +---> temporary constraint added: [x == 10]
       |       |     (solver checks SAT -> Yes, x=10)
       |       |
       |<--- pop() (temporary constraints discarded)
       |
  Returned to Base State: [x > 5]
```

### RE Use Case
Symbolic execution tools like `angr` use `push()` and `pop()` as they traverse down a binary's execution paths:
1. Walk down the main code path.
2. Hit a branch point (`if`).
3. Call `push()`.
4. Add the `True` branch constraints and check if they are satisfiable.
5. If yes, explore further.
6. Call `pop()` to return to the branch point.
7. Call `push()`.
8. Add the `False` branch constraints and explore.

---

## 5.2 assertions() and statistics()

When debugging a script, you need to understand what the solver knows.
* **`solver.assertions()`**: Returns a list of all constraints currently registered on the solver.
* **`solver.statistics()`**: Returns metadata about the last `check()` execution, such as:
  * Running time (`time`)
  * Memory consumption (`memory` / `max memory`)
  * Internal decisions and conflicts (`decisions` / `conflicts`)

```python
solver.add(x > 10)
solver.add(x < 20)

# Print all rules
for constraint in solver.assertions():
    print(constraint)

solver.check()
stats = solver.statistics()
print(f"Time taken: {stats.get_key_value('time')} seconds")
```

---

## 5.3 unsat_core() (Debugging Conflicts)

When you write a complex Z3 model and it returns `unsat`, it means your rules contradict each other. In a model with hundreds of variables, finding the conflict is like searching for a needle in a haystack.

`unsat_core()` tells you exactly which assertions are conflicting. To use it, you must track constraints using **assertions/labels** (Boolean variables):

```python
solver = z3.Solver()
x = z3.Int('x')

# Define labels
rule1 = z3.Bool('rule_greater_than_10')
rule2 = z3.Bool('rule_less_than_5')

# Add constraints implied by these labels
solver.add(z3.Implies(rule1, x > 10))
solver.add(z3.Implies(rule2, x < 5))

# Check satisfiability, passing the tracking labels as assumptions
result = solver.check(rule1, rule2)

if result == z3.unsat:
    # Retrieve the subset of rules causing the conflict
    print(solver.unsat_core()) 
    # Prints: [rule_greater_than_10, rule_less_than_5]
```

---

## 5.4 Optimize() (The Best Solution)

In standard Z3, the solver stops searching as soon as it finds *any* working solution. But sometimes you want to find the *best* solution:
* The key with the highest value.
* The input with the minimum number of characters.
* The value that minimizes code size.

To do this, replace `z3.Solver()` with `z3.Optimize()`:
* **`opt.minimize(expr)`**: Directs the solver to find a solution that minimizes `expr`.
* **`opt.maximize(expr)`**: Directs the solver to find a solution that maximizes `expr`.

### RE Use Case
Minimizing input size to find the shortest payload that triggers a buffer overflow or vulnerability.

---

## 5.5 Why Beginners Fail

1. **Calling pop() without a matching push()**:
   This results in a `Z3Exception: Solver has no backtrack points`. Always structure your push/pop calls in pairs.
2. **Slow solving due to no push/pop hygiene**:
   Adding constraints indefinitely slows down the solver. If you are solving multiple separate equations in a loop, either call `solver.reset()` between loops or use `push()` and `pop()` appropriately.

---

## Challenge 5 — Key Minimizer

A custom validation algorithm requires a 16-bit key satisfying the constraint:
* `key ^ 0x1337 == 0x7FBA`

However, the binary also runs a security check: it rejects any input containing more than 8 set bits (weight/popcount).

1. Write a Z3 model using `z3.Optimize()`.
2. Model a 16-bit BitVector representing `key`.
3. Compute the popcount (number of 1s in the key) by extracting each of the 16 bits, zero-extending them to 16 bits, and summing them up.
4. Minimize the popcount using `opt.minimize()`.
5. Solve for `key`.

Find the complete implementation in [code/05_solver_apis.py](file:///home/i5l3m/Desktop/CTF/tutorials/z3-tutorial/code/05_solver_apis.py).
