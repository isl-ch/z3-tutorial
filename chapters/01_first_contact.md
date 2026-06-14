# Part 1 — First Contact with Z3

In this chapter, you will install Z3, write your very first solver script, query the solver for answers, and learn how to extract those answers into Python variables.

---

## 1.1 Installation

First, let's get Z3 running on your machine. Z3 is written in C++, but it has a very clean and powerful Python wrapper.

### The virtual environment (Recommended)
It is always good practice to install python packages in a virtual environment:

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install the Z3 Python wrapper
pip install z3-solver
```

> [!IMPORTANT]
> Always install `z3-solver` and **not** `z3`. The `z3` package on PyPI is a completely unrelated tool. Installing the wrong one is a classic beginner mistake.

### Checking the installation
Run the following commands in your terminal to verify that Z3 is installed and check its version:

```bash
python3 -c "import z3; print(z3.get_version_string())"
```
*Expected Output: `4.13.0` (or similar)*

---

## 1.2 Solver Basics

The Z3 API relies on a few key building blocks:
* `z3.Solver()`: Creates a new solver instance (think of it as a clean whiteboard).
* `add(constraint)`: Writes a mathematical rule on the whiteboard.
* `check()`: Asks the solver, *"Is it possible to satisfy all the rules on the whiteboard?"* It returns either `sat` (yes), `unsat` (no), or `unknown` (rarely, when the math is too hard).
* `model()`: Retrieves the solution if the solver returned `sat`.

### Mental Model: The Solver as a Judge

```
                  +--------------------------------+
                  |           z3.Solver()          |
                  +--------------------------------+
                                  |
                                  | .add(x + y == 10)
                                  v
                  +--------------------------------+
                  |         The Whiteboard         |
                  |         (Constraints)          |
                  +--------------------------------+
                                  |
                                  | .check()
                                  v
                      /-------------------------\
                     /   Is it possible?         \
                     \                           /
                      \-------------------------/
                        /                     \
                  Yes  /                       \ No
                      v                         v
              +---------------+         +---------------+
              |    z3.sat     |         |   z3.unsat    |
              +-------+-------+         +---------------+
                      |
                      | .model()
                      v
              +---------------+
              |   The Model   |
              | {x: 10, y: 0} |
              +---------------+
```

Let's look at the basic syntax. Create a file called `first_contact.py` (or view the existing [code/01_first_contact.py](file:///home/i5l3m/Desktop/CTF/tutorials/z3-tutorial/code/01_first_contact.py)):

```python
import z3

# 1. Create a solver
solver = z3.Solver()

# 2. Declare symbolic variables
x = z3.Int('x')
y = z3.Int('y')

# 3. Add rules (constraints)
solver.add(x + y == 10)
# Note: You can add multiple rules at once, or one by one
solver.add(x > 2)
solver.add(y < 5)

# 4. Check if a solution exists
result = solver.check()
print(f"Result: {result}") # Prints: Result: sat
```

---

## 1.3 Reading Models

If `solver.check()` returns `z3.sat`, we can query the solver for the values it assigned to our variables to satisfy the constraints. We do this by calling `solver.model()`.

```python
if result == z3.sat:
    m = solver.model()
    print(m) # Prints: [y = 0, x = 10]
```

### Accessing variables in the model
To extract a value into a Python variable, we index the model object using the Z3 variable:

```python
val_x = m[x]
val_y = m[y]
print(f"Solved: x = {val_x}, y = {val_y}") # Solved: x = 10, y = 0
```

> [!WARNING]
> The value returned by `m[x]` is **not** a standard Python `int`. It is a Z3 AST (Abstract Syntax Tree) node object. If you want to convert it to a standard Python integer for further processing (like sending it over a socket), you should cast it or use `.as_long()`:
> ```python
> py_x = m[x].as_long() # Converts to standard Python int
> ```

### Evaluating Arbitrary Expressions
You can also ask the model to evaluate a complex mathematical expression based on the solved variables using `model.evaluate()`:

```python
# What would (x * 2 + y) be under the solved model?
expr = x * 2 + y
val_expr = m.evaluate(expr)
print(f"Evaluated expression: {val_expr}") # Evaluated expression: 20
```

### Iteration over a model
If you don't know the names of the variables in the model beforehand (common in generic scripts), you can iterate over it:

```python
for d in m.decls():
    print(f"{d.name()} = {m[d]}")
```

---

## 1.4 Advanced: Finding Multiple Solutions

What if there are multiple sets of variables that satisfy the rules, and you want to see all of them? 

Every time Z3 solves a system, it picks a solution. If you run it again, it might give you the exact same solution. To force it to find a *different* one, you must:
1. Find a solution.
2. Extract the value of the variables.
3. Add a new constraint stating: **"The variables cannot equal these specific values."**
4. Run `check()` again.

Here is how to do that in Python:

```python
solver = z3.Solver()
a = z3.Int('a')

# Constrain 'a' to be between 1 and 5 inclusive
solver.add(a >= 1)
solver.add(a <= 5)

while solver.check() == z3.sat:
    m = solver.model()
    val_a = m[a]
    print(f"Found solution: a = {val_a}")
    
    # Block this specific solution from appearing again
    solver.add(a != val_a)
```

**Output:**
```
Found solution: a = 1
Found solution: a = 2
Found solution: a = 3
Found solution: a = 4
Found solution: a = 5
```

---

## 1.5 Why Beginners Fail

1. **Confusing Python variables with Z3 symbolic variables**:
   ```python
   x = z3.Int('y') # WARNING: The Python variable is 'x', but Z3 knows it as 'y'!
   ```
   If you print the model, Z3 will say `y = 10`. If you try to query `m[x]`, it works because `x` is the Python reference, but it's highly confusing. **Rule: Always name your Python variable the same as the Z3 string name.**

2. **Using standard Python comparison/operators on models directly**:
   ```python
   m = solver.model()
   if m[x] > 5: # CRASH or unexpected behavior!
       ...
   ```
   You cannot directly compare `m[x]` to a Python int inside Python conditionals without converting it using `.as_long()` or evaluating it.

3. **Modifying constraints after check()**:
   Z3 solvers are stateful. If you add constraints in a loop without management, they persist on the solver whiteboard.

---

## 1.6 Reverse Engineering Example

Imagine a decompiler output for a password checker looking like this:

```c
int check_password(int char1, int char2) {
    if (char1 * 12 + char2 * 34 == 4210) {
        if (char1 - char2 == 15) {
            return 1; // Access Granted
        }
    }
    return 0; // Access Denied
}
```

Instead of solving this system of linear equations by hand, you write this Z3 model:

```python
import z3

solver = z3.Solver()
char1 = z3.Int('char1')
char2 = z3.Int('char2')

solver.add(char1 * 12 + char2 * 34 == 4210)
solver.add(char1 - char2 == 15)

if solver.check() == z3.sat:
    m = solver.model()
    print(f"Password characters: char1={m[char1]}, char2={m[char2]}")
else:
    print("No valid password exists!")
```

---

## Mini Exercises

1. **Verify Unsat**: Set up a solver with constraints `x > 5` and `x < 2`. Verify that `solver.check()` returns `z3.unsat`. What happens if you call `solver.model()` when the result is `unsat`? (Spoiler: It raises a `Z3Exception`).
2. **Double Solution**: Find two distinct integers `x` and `y` such that `x * y == 36` and `x + y == 13`.

---

## Challenge 1 — Number Hunt

Find three positive integers `a`, `b`, and `c` that satisfy the following constraints:
1. They sum to exactly $100$ ($a + b + c = 100$).
2. $a > 0$, $b > 0$, $c > 0$.
3. Double of $a$ minus $b$ is $50$ ($2a - b = 50$).
4. $c$ is a multiple of $7$ ($c \pmod 7 = 0$).
5. All three numbers are distinct ($a \neq b \neq c$).

Write a Python script to find these numbers. You can find the solution implementation in [code/01_first_contact.py](file:///home/i5l3m/Desktop/CTF/tutorials/z3-tutorial/code/01_first_contact.py).
