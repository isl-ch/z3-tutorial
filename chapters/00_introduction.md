# Part 0 — Introduction

Welcome to **Z3 for Reverse Engineering**! If you have ever stared at a decompiled binary containing nested `if` statements, bitwise arithmetic, and complex validations, and thought, *"There has to be a smarter way to solve this than guessing or writing a massive brute-forcer,"* then this course is for you.

---

## 0.1 What is Z3?

**Z3** is a state-of-the-art **SMT (Satisfiability Modulo Theories) solver** developed by Microsoft Research. In plain English: it is an automated math engine. You feed it a list of mathematical statements (constraints) and variables, and it tells you:
1. Whether it is possible to make all those statements true at the same time (**SAT**, or Satisfiable).
2. If it is possible, it gives you a concrete example of variable values that work (**Model**).
3. If it is impossible, it tells you so (**UNSAT**, or Unsatisfiable).

### SAT vs. SMT

To understand Z3, you must understand the difference between SAT and SMT:

```
+-------------------------------------------------------------+
|                         SMT Solvers                         |
|  (Understand integers, reals, bitvectors, arrays, strings)  |
|                                                             |
|   +-----------------------------------------------------+   |
|   |                     SAT Solvers                     |   |
|   |  (Only understand Boolean values: True/False, 0/1)  |   |
|   +-----------------------------------------------------+   |
+-------------------------------------------------------------+
```

* **SAT (Boolean Satisfiability)**: These solvers deal purely with binary state. If your equation is $(A \lor B) \land (\neg A \lor C)$, a SAT solver can find a combination of True/False values for $A$, $B$, and $C$.
* **SMT (Satisfiability Modulo Theories)**: These solvers build *on top* of SAT solvers by adding "theories." A theory lets the solver understand specific types of math:
  * **Theory of BitVectors**: Understands that a variable is a 32-bit integer, and handles CPU-native operations like shift left (`<<`), bitwise XOR (`^`), and integer overflow.
  * **Theory of Arrays**: Understands memory reads/writes (e.g., pointers and buffers).
  * **Theory of Integers/Reals**: Understands algebraic math ($x + y > 10$).

As a reverse engineer, you are almost always dealing with **SMT** because computer programs operate on registers (bitvectors), memory (arrays), and floating-point units.

### Why Reverse Engineers Use Solvers

Consider a typical license key validation function in a binary:

```c
bool check_serial(char* key) {
    if (key[0] ^ key[1] != 0x42) return false;
    if (key[2] + key[3] != 0x88) return false;
    if ((key[0] * key[2]) % 256 != 0x12) return false;
    return true;
}
```

Normally, to reverse this, you would:
1. Solve it by hand (takes time, prone to arithmetic mistakes).
2. Write a Python script to brute-force combinations.

### Why Brute Force Fails

Brute force scales exponentially. Let's look at the math. If our key is 16 bytes:
* Each byte has 256 possible values.
* Total search space = $256^{16} = 2^{128} \approx 3.4 \times 10^{38}$ combinations.
* If your computer can check $10^9$ (1 billion) keys per second, it will take **$10^{22}$ years** to find a working key. This is longer than the age of the universe.

**Z3 does not brute force.** Instead of guessing values one by one, it treats your program as a system of mathematical equations. Using advanced logical deduction algorithms (like DPLL(T)), Z3 prunes massive branches of the search space. It can often solve a keygen space of $2^{128}$ in **milliseconds**.

---

## 0.2 When to Use Z3

You should reach for Z3 when you encounter:

1. **Crackmes & Keygenning**: Reconstructing key validation algorithms to generate valid inputs.
2. **Obfuscated Conditions**: Opaque predicates (junk conditions that always evaluate to true/false to confuse you) or mixed boolean-arithmetic (MBA) obfuscation.
3. **Symbolic Execution**: Automatically finding paths through a binary (Z3 is the execution engine behind tools like `angr` and `Triton`).
4. **Malware Analysis**: Reversing custom encryption algorithms or configuration decoders.
5. **VM Challenges**: Resolving inputs that satisfy custom instruction sets or interpreters.
6. **Path Solving**: Determining what input is required to reach a specific "success" block deep inside nested control-flow branches.

---

## 0.3 Reverse Engineering Workflow

Using Z3 in a real reverse engineering project follows a structured loop:

```
  +--------------------------------------------+
  |                   Binary                   |
  +---------------------+----------------------+
                        |
                        | Decompile / Disassemble
                        v
  +---------------------+----------------------+
  |           Decompiler / Assembly            |
  +---------------------+----------------------+
                        |
                        | Extract constraints (Identify inputs & math)
                        v
  +---------------------+----------------------+
  |          Z3 Python Constraints             |
  +---------------------+----------------------+
                        |
                        | Solve (check() & model())
                        v
  +---------------------+----------------------+
  |           Solved Variable Values           |
  +---------------------+----------------------+
                        |
                        | Validate (Run binary with solved input)
                        v
  +---------------------+----------------------+
  |               Success / Flag!              |
  +--------------------------------------------+
```

1. **Analyze the Binary**: Open it in Ghidra, IDA Pro, or Binary Ninja. Locate the validation logic.
2. **Extract Constraints**: Identify the input variables (e.g. `char input[16]`) and the operations applied to them.
3. **Write the Z3 Model**: Declare matching variables in Python using Z3, translate assembly/decompiler operations into Z3 operations, and set up your constraints.
4. **Solve**: Run Z3 to solve the constraints.
5. **Validate**: Feed the output back into the original binary to confirm it works.

---

## 0.4 How to Think: Solver vs. Debugger

A debugger is **imperative**: you run the program step-by-step, feeding it inputs and observing the output.
* *Debugger thought*: "If I pass `AAAA` as input, what does the register `EAX` hold at line 42?"

Z3 is **declarative**: you describe the relationship between inputs and outputs, and ask the solver to fill in the inputs.
* *Z3 thought*: "I want register `EAX` to hold `0x1337` at line 42. What input must I provide at the start to make this true?"

---

## Challenge 0 — The Mindset Shift

Before coding, think about how you would solve this system of inequalities manually.
Assume $x$ and $y$ are positive integers:
1. $x + y < 10$
2. $x > 5$
3. $y > 3$

Is there a solution? 
* If $x > 5$, the minimum value of $x$ is $6$.
* If $y > 3$, the minimum value of $y$ is $4$.
* But if $x = 6$ and $y = 4$, then $x + y = 10$, which violates $x + y < 10$.
* Thus, this system is **UNSATISFIABLE (UNSAT)**.

In the next chapter, we will write our first Python script to let Z3 prove this logic automatically!
