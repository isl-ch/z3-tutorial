# Part 3 — Expressions and Constraints

In this chapter, you will learn how to build complex formulas in Z3. We will cover how to simplify formulas, replace variables in expressions, handle boolean logic, and model branching logic (like `if-else` blocks).

---

## 3.1 simplify()

When writing models for complex binaries (or when a symbolic execution engine extracts path constraints), you often end up with massive, ugly equations. Z3 provides the `simplify()` API to run algebraic and logical reductions on expressions.

* **Syntax**:
  ```python
  z3.simplify(expression)
  ```

* **Example**:
  ```python
  x = z3.Int('x')
  expr = x + 1 + x + 2 + x * 2
  print(z3.simplify(expr)) # Prints: 3 + 4*x
  ```

* **BitVector Simplification**:
  ```python
  a = z3.BitVec('a', 8)
  expr_bv = a ^ a ^ a
  print(z3.simplify(expr_bv)) # Prints: a
  ```

---

## 3.2 substitute()

Sometimes you need to replace a variable in an expression with another variable or a constant value. The `substitute()` API allows you to perform drop-in replacements.

* **Syntax**:
  ```python
  z3.substitute(expression, (old_var_1, new_val_1), (old_var_2, new_val_2), ...)
  ```

* **Example**:
  ```python
  x = z3.Int('x')
  y = z3.Int('y')
  expr = x + y * 2
  
  # Replace x with 10, and y with (x + 1)
  new_expr = z3.substitute(expr, (x, z3.IntVal(10)), (y, x + 1))
  print(new_expr) # Prints: 10 + (x + 1)*2
  ```

---

## 3.3 Logical Operations: And, Or, Not

These are the building blocks for combining rules.
* **`z3.And(c1, c2, ...)`**: All constraints must be True.
* **`z3.Or(c1, c2, ...)`**: At least one constraint must be True.
* **`z3.Not(c)`**: The constraint must be False.

### Syntax
```python
solver.add(z3.And(x > 5, x < 10))
solver.add(z3.Or(y == 0, y == 1))
```

---

## 3.4 Branching Logic: If (ITE)

In decompiled code, you see branching statements everywhere:
```c
int result;
if (condition) {
    result = 10;
} else {
    result = 20;
}
```

You **cannot** use standard Python `if` statements to model this inside Z3:
```python
# WARNING: THIS IS A CRITICAL BEGINNER MISTAKE!
if condition:
    result = 10
else:
    result = 20
```
This fails because `condition` is a symbolic Z3 variable, not a Python boolean. Python tries to evaluate it to `True` or `False` immediately, which throws an error or leads to incorrect solving.

Instead, you must use `z3.If()` (often called **ITE: If-Then-Else**):
* **Syntax**:
  ```python
  z3.If(condition, value_if_true, value_if_false)
  ```

* **RE Example**:
  ```python
  cond = z3.Bool('cond')
  res = z3.Int('res')
  solver.add(res == z3.If(cond, 10, 20))
  ```

---

## 3.5 Logical Implication: Implies

* **Concept**: `z3.Implies(A, B)` means *"If A is True, then B MUST be True."*
* **Truth Table**:
  * If $A$ is True and $B$ is True: Satisfiable.
  * If $A$ is True and $B$ is False: Unsatisfiable.
  * If $A$ is False: Satisfiable regardless of whether $B$ is True or False (this is called "vacuous truth").

### Syntax
```python
solver.add(z3.Implies(is_admin, has_root_privs))
```

---

## 3.6 Distinct

* **Concept**: `z3.Distinct(x, y, z, ...)` is a shorthand for ensuring that every variable in the list has a unique value. Writing `z3.Distinct(x, y, z)` is equivalent to writing `x != y, y != z, x != z`.
* **Syntax**:
  ```python
  solver.add(z3.Distinct(x, y, z))
  ```

---

## 3.7 Why Beginners Fail

### The Python `if` Trap
We cannot stress this enough: **Never use a Python `if` statement to branch on a Z3 symbolic variable.**
```python
# WRONG
x = z3.Int('x')
if x > 5:
    solver.add(y == 1)
else:
    solver.add(y == 2)
```
*Why it fails*: When Python executes this code, it evaluates the expression `x > 5`. Because `x` is symbolic, this evaluation does not yield a Boolean `True` or `False`—it yields a symbolic expression object. Python then coerces this object to `True` (standard Python behavior for non-empty objects), meaning the `else` branch is *never* compiled.

*Correct way*:
```python
# CORRECT
x = z3.Int('x')
solver.add(y == z3.If(x > 5, 1, 2))
```

---

## Challenge 3 — The Overflowing Branch

Consider this validation routine in a crackme:

```c
int val = (key ^ 0x33) * 2;
if (key < 100) {
    val += 10;
} else {
    val -= 20;
}
// Goal: val == 150
```

1. Model this logic in Z3 using a **32-bit BitVector** for `key`.
2. Use `z3.If` to handle the conditional check. Remember to use unsigned comparison (`z3.ULT`) because `key` is unsigned!
3. Solve for `key`. 

Check the solution script in [code/03_expressions.py](file:///home/i5l3m/Desktop/CTF/tutorials/z3-tutorial/code/03_expressions.py). You will notice that Z3 finds two solutions. One of them is a standard mathematical solution ($102$), and the other is a large integer ($2147483750$, or `0x80000066`) that triggers an integer overflow during multiplication to satisfy the `else` branch! 

This is the power of SMT solvers: they find edge-cases that are practically invisible to human eyes.
