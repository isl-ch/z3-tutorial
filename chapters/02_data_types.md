# Part 2 — Z3 Data Types

In reverse engineering, data types matter. A standard computer memory byte, a CPU register, and a floating-point unit (FPU) store and manipulate data in fundamentally different ways. In this chapter, you will learn how Z3 models these datatypes, how they map to machine-level structures, and how to write constraints for them.

---

## 2.1 Int (Mathematical Integers)

* **Memory Intuition**: *Infinite precision numbers.* They do not exist in real CPU registers. Real registers are bound by their bit-width (e.g. 32-bit or 64-bit) and overflow when they go out of bounds. Z3 `Int`s never overflow; they can grow to be infinitely large.
* **Syntax**:
  ```python
  x = z3.Int('x')
  val = z3.IntVal(42) # A constant integer
  ```
* **RE Use Cases**: High-level algorithm modeling where overflow is impossible or ignored, or counting iterations.
* **Warning**: Avoid using `Int` to model binary logic like register values.

---

## 2.2 Real (Mathematical Real Numbers)

* **Memory Intuition**: *Infinite precision decimals/fractions.* Unlike floating-point variables (which lose precision due to how they are stored in binary), Z3 `Real`s are mathematically exact fractions.
* **Syntax**:
  ```python
  r = z3.Real('r')
  val = z3.RealVal(3.14)
  ```
* **RE Use Cases**: Very rare. Only used when simulating analog devices or pure high-level mathematical algorithms.

---

## 2.3 Bool (Boolean Logic)

* **Memory Intuition**: *A single flag / status bit.* E.g., the Zero Flag (ZF) or Carry Flag (CF) in CPU status registers.
* **Syntax**:
  ```python
  is_valid = z3.Bool('is_valid')
  val = z3.BoolVal(True)
  ```
* **RE Use Cases**: Modeling CPU conditional flags, branch conditions, or check results.
* **Key logical functions**:
  * `z3.And(a, b, ...)`
  * `z3.Or(a, b, ...)`
  * `z3.Not(a)`
  * `z3.Xor(a, b)`

---

## 2.4 BitVec (Bitvectors — The RE Bread & Butter)

> [!IMPORTANT]
> If you are reversing compiled code, **always prefer `BitVec` over `Int`**.

* **Memory Intuition**: *A CPU register or a memory cell.* A Bitvector is a fixed-width sequence of bits. A `BitVec('x', 32)` corresponds exactly to a 32-bit register like `EAX` or a `uint32_t` variable.

### Syntax
```python
x = z3.BitVec('x', 8)  # 8-bit bitvector (unsigned char / uint8_t)
y = z3.BitVec('y', 32) # 32-bit bitvector (uint32_t / int)
val = z3.BitVecVal(0x1337, 16) # 16-bit constant 0x1337
```

### Machine-Level Semantics: Overflow & Underflow
Unlike mathematical integers, bitvectors exhibit realistic overflow and underflow behavior. For example, if you add 10 to the maximum value of an 8-bit unsigned integer (255), it wraps around to 9.

Let's look at this comparison:
* **Math Int**: $x + 10 = 5 \implies x = -5$
* **8-bit BitVec**: $x + 10 = 5 \implies x = 251$ (because $251 + 10 = 261 \equiv 5 \pmod{256}$)

### Signed vs. Unsigned Bitvectors
In Z3, a bitvector is just a sequence of bits. It does *not* have a signed or unsigned type. Instead, the signedness depends on the **operators** you apply to it.
* Standard operators (`+`, `-`, `*`, `<<`, `&`, `|`, `^`) behave identically for both signed and unsigned bitvectors.
* Comparisons and division have signed and unsigned variants:
  * Signed Less Than: `x < y` (uses standard Python `<`)
  * Unsigned Less Than: `z3.ULT(x, y)` (Unsigned Less Than)
  * Signed Right Shift: `x >> y` (uses standard Python `>>`, fills with sign bit)
  * Unsigned Right Shift: `z3.LShR(x, y)` (Logical Shift Right, fills with zeros)

---

## 2.5 Arrays (Memory and Buffers)

* **Memory Intuition**: *RAM or a pointer to a buffer.* Z3 Arrays map a "key sort" (address) to a "value sort" (stored value).
* **Syntax**:
  ```python
  # Models a memory space where 32-bit addresses point to 8-bit byte values
  mem = z3.Array('mem', z3.BitVecSort(32), z3.BitVecSort(8))
  ```
* **APIs**:
  * `z3.Select(array, index)`: Reads the value stored at `index`. Equivalent to `array[index]` in C.
  * `z3.Store(array, index, value)`: Writes `value` to `index`. Returns a *new* array state representing memory after the write.

### Memory Write Visual Model:

```
        State 1: mem                State 2: new_mem = Store(mem, 0x10, 0x42)
     +--------+--------+         +--------+--------+
Addr |  0x10  |  0x11  |    -->  |  0x10  |  0x11  |
     +--------+--------+         +--------+--------+
Val  |  0x00  |  0x99  |         |  0x42  |  0x99  |
     +--------+--------+         +--------+--------+
```

* **RE Use Cases**: Emulating RAM, tracking pointer writes, or modeling buffers where index offsets are symbolic (e.g. `buffer[x] = y`).

---

## 2.6 Strings

* **Memory Intuition**: *Character buffers.*
* **Syntax**:
  ```python
  s = z3.String('s')
  ```
* **APIs**:
  * `z3.Concat(s1, s2)`: Concatenates strings.
  * `z3.Length(s)`: Gets the length of the string.
  * `z3.SubString(s, offset, length)`: Extracts a substring.
* **RE Use Cases**: Parsing flag formats, validating string inputs, or reversing text-based protocols.

---

## 2.7 Floating Point

* **Memory Intuition**: *FPU registers (`xmm0`, `ST(0)`).* Complies with IEEE 754 floating-point standards.
* **Syntax**:
  ```python
  f = z3.FP('f', z3.Float32()) # Single precision (float)
  d = z3.FP('d', z3.Float64()) # Double precision (double)
  val = z3.FPVal(1.5, z3.Float64())
  ```
* **RE Use Cases**: Crackmes with coordinate checks or physical simulations (e.g. game cheats reversing, finding coordinates that trigger a boundary condition).

---

## 2.8 Datatypes (Structures/Records)

* **Memory Intuition**: *C-style structures (structs) or unions.*
* **Syntax**:
  ```python
  # Define a structure: Point { int x, int y }
  Point = z3.Datatype('Point')
  Point.declare('mk_point', ('x', z3.IntSort()), ('y', z3.IntSort()))
  Point = Point.create()
  
  p = z3.Const('p', Point)
  ```
* **RE Use Cases**: Modeling structs in decompiled code (e.g. `struct Player { int health; int ammo; }`).

---

## 2.9 Functions (Symbolic/Uninterpreted Functions)

* **Memory Intuition**: *Black-box functions.* You don't know the implementation, but you know that passing the same input must always produce the same output.
* **Syntax**:
  ```python
  # Declares f: (Int, Int) -> Int
  f = z3.Function('f', z3.IntSort(), z3.IntSort(), z3.IntSort())
  ```
* **RE Use Cases**: Simplifying cryptographic hash functions. For example, instead of fully modeling SHA256 in Z3 (which will grind the solver to a halt), you can model SHA256 as an uninterpreted function and add constraints like `SHA256(x) == hash_val`.

---

## 2.10 Why Beginners Fail

1. **Mixed-Type Errors**: Z3 does not automatically cast types. Adding an `Int` and a `BitVec` results in a crash:
   ```python
   x = z3.Int('x')
   y = z3.BitVec('y', 32)
   solver.add(x + y == 10) # ERROR: Sort mismatch!
   ```
2. **Bit-width mismatch**: Trying to perform bitwise operations on bitvectors of different sizes:
   ```python
   a = z3.BitVec('a', 8)
   b = z3.BitVec('b', 16)
   solver.add(a ^ b == 0) # ERROR: Sort mismatch!
   ```
   *Fix*: You must resize `a` using extension or extraction (covered in Part 4).

---

## Challenge 2 — The Key Overflower

A validation routine in a binary expects a 16-bit serial key that satisfies these conditions:
1. `key + 0x1337 == 0x4242` (evaluated as a 16-bit unsigned integer with potential overflow).
2. `key ^ 0x55AA == 0x7AA1` (bitwise XOR operation).

Write a Z3 Python script using 16-bit BitVectors to solve for `key`. Check your solution against [code/02_data_types.py](file:///home/i5l3m/Desktop/CTF/tutorials/z3-tutorial/code/02_data_types.py).
