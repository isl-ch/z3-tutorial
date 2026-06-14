# Part 4 — Bitvectors for Reverse Engineering

In this chapter, you will learn the most critical tools for binary analysis: **Bitvector operations**. CPU registers do not understand infinite-precision algebra; they operate on raw bits. We will learn how to slice, stitch, shift, rotate, and extend registers in Z3 to perfectly emulate machine-level assembly instructions.

---

## 4.1 Extract (Slicing Bits)

When a program reads only a part of a register (like accessing `AL`, `AH`, or `AX` from `EAX`), you must model this in Z3 using `Extract`.

* **Syntax**:
  ```python
  z3.Extract(high_bit, low_bit, bitvector)
  ```
  *Note: Bits are 0-indexed, starting from the rightmost Least Significant Bit (LSB) up to the leftmost Most Significant Bit (MSB).*

### Visual Model (32-bit register `EAX`)

```
 MSB                                                   LSB
  31            23            15             7             0
 +-------------+-------------+-------------+-------------+
 |   Byte 3    |   Byte 2    |   Byte 1    |   Byte 0    |  <- EAX
 +-------------+-------------+-------------+-------------+
                              \___________/ \___________/
                                    AH            AL
                              \_________________________/
                                          AX

 - AL = z3.Extract(7, 0, eax)
 - AH = z3.Extract(15, 8, eax)
 - AX = z3.Extract(15, 0, eax)
```

---

## 4.2 Concat (Stitching Bits)

When a program reads multiple bytes from memory and combines them to form a larger integer (like reading four separate bytes to form a `uint32_t`), you use `Concat`.

* **Syntax**:
  ```python
  z3.Concat(high_bv, low_bv, ...)
  ```
* **Example**:
  ```python
  byte1 = z3.BitVecVal(0x41, 8)
  byte2 = z3.BitVecVal(0x42, 8)
  word  = z3.Concat(byte1, byte2) # Result is 16-bit: 0x4142
  ```

---

## 4.3 Extensions: ZeroExt and SignExt

When casting a smaller integer to a larger one (e.g. `char` to `int` in C), the CPU must fill the new upper bits.
* **`ZeroExt(n, bv)`**: (Zero Extension) Prepends `n` zero bits to `bv`. Used for **unsigned casts** (like `movzx` in x86).
* **`SignExt(n, bv)`**: (Sign Extension) Prepends `n` copies of the sign bit (MSB) to `bv`. Used for **signed casts** (like `movsx` in x86).

### Visual Model of Extending `0x80` (8-bit binary: `1000 0000`)

```
   ZeroExt(8, 0x80) -> Unsigned Cast to 16-bit:
   +-------------------+-------------------+
   | 0 0 0 0   0 0 0 0 | 1 0 0 0   0 0 0 0 | -> 0x0080
   +-------------------+-------------------+
     Zero-fill           Original Byte

   SignExt(8, 0x80) -> Signed Cast to 16-bit:
   +-------------------+-------------------+
   | 1 1 1 1   1 1 1 1 | 1 0 0 0   0 0 0 0 | -> 0xFF80
   +-------------------+-------------------+
     Sign-fill           Original Byte (MSB was 1)
```

---

## 4.4 Shifts: Arithmetic vs. Logical Right Shift

In assembly, there are two types of right shifts:
1. **Logical Right Shift (`SHR` / `z3.LShR`)**: Fills empty MSB positions with zeros. Used for unsigned numbers.
2. **Arithmetic Right Shift (`SAR` / Python `>>`)**: Fills empty MSB positions with copies of the sign bit. Used for signed numbers to preserve their negative state.

```python
x = z3.BitVecVal(0x80000000, 32)

arith = x >> 1         # SAR: Result is 0xC0000000
logic = z3.LShR(x, 1)  # SHR: Result is 0x40000000
```

---

## 4.5 Rotations: RotateLeft and RotateRight

Many obfuscation and hashing algorithms use bitwise rotations (`ROL` and `ROR` in x86). 
* **Syntax**:
  ```python
  z3.RotateLeft(bv, n)
  z3.RotateRight(bv, n)
  ```
  Unlike shifts, bits pushed off one end are wrapped around to the other end.

---

## 4.6 Unsigned Comparisons

In python, `<` and `>` translate to *signed* comparisons in Z3. To perform *unsigned* comparisons, you must use:
* `z3.ULT(x, y)`: Unsigned Less Than ($x < y$)
* `z3.ULE(x, y)`: Unsigned Less or Equal ($x \le y$)
* `z3.UGT(x, y)`: Unsigned Greater Than ($x > y$)
* `z3.UGE(x, y)`: Unsigned Greater or Equal ($x \ge y$)

```python
a = z3.BitVecVal(0xFF, 8) # Signed: -1, Unsigned: 255
b = z3.BitVecVal(0x01, 8) # Signed: 1,  Unsigned: 1

print(a < b)          # Prints: True  (since -1 < 1)
print(z3.ULT(a, b))   # Prints: False (since 255 < 1 is False)
```

---

## 4.7 Translation Cheat Sheet: Assembly to Z3

| x86 Instruction | Description | Z3 Python Translation |
|---|---|---|
| `movzx eax, cl` | Move with Zero-Extend | `eax = z3.ZeroExt(24, cl)` |
| `movsx eax, cl` | Move with Sign-Extend | `eax = z3.SignExt(24, cl)` |
| `shr eax, 5` | Logical Shift Right | `eax = z3.LShR(eax, 5)` |
| `sar eax, 5` | Arithmetic Shift Right | `eax = eax >> 5` |
| `shl eax, 3` | Shift Left | `eax = eax << 3` |
| `ror eax, 4` | Rotate Right | `eax = z3.RotateRight(eax, 4)` |
| `rol eax, 4` | Rotate Left | `eax = z3.RotateLeft(eax, 4)` |
| `jb label` / `jl label` | Branch if Less | `z3.ULT(x, y)` (Unsigned) / `x < y` (Signed) |

---

## 4.8 Why Beginners Fail

1. **Rotating/Shifting with symbolic variables**:
   ```python
   shift_amt = z3.BitVec('shift_amt', 32)
   x = z3.BitVec('x', 32)
   res = z3.RotateRight(x, shift_amt) # ERROR: Shift amount must be a Python int!
   ```
   *Fix*: Z3's standard rotation APIs (`RotateRight`, `RotateLeft`) require a static Python integer for the rotation amount. If the rotation amount is symbolic, you must construct the rotation using shifts and bitwise ORs:
   ```python
   # Emulating: (x >> shift_amt) | (x << (32 - shift_amt)) logically
   res = z3.LShR(x, shift_amt) | (x << (32 - shift_amt))
   ```

2. **Sort mismatch in Concat/Extract**:
   Remember that `Extract` changes the bit-width of the variable. If you extract 8 bits from a 32-bit variable and try to add it to a 32-bit variable, it will crash.
   *Fix*: Zero-extend or sign-extend the extracted byte back to 32 bits before adding:
   ```python
   byte = z3.Extract(7, 0, eax)
   # solver.add(ebx == ebx + byte) # CRASH!
   solver.add(ebx == ebx + z3.ZeroExt(24, byte)) # Correct
   ```

---

## Challenge 4 — The Loop Emulator

You are reversing a firmware checksum validation function. The assembly looks like this:

```nasm
; esi points to a 4-byte key in memory
; edx is the checksum accumulator (initialized to 0)
loop_start:
    movzx eax, byte ptr [esi] ; Read key byte
    ror eax, 3                ; Rotate right 3 bits
    xor eax, 0x55             ; XOR with 0x55
    add edx, eax              ; Add to checksum
    inc esi
    ; (loops 4 times)
```

1. Write a Z3 Python script using a `32-bit BitVec` to represent the 4-byte key.
2. Extract the individual bytes, zero-extend them, rotate them right by 3, XOR them with `0x55`, and sum them up.
3. Enforce that all 4 bytes of the key must be readable ASCII characters (between `0x20` and `0x7E`).
4. Find a key that yields a target checksum value of `0x40000174`.

Compare your code to the solution in [code/04_bitvectors.py](file:///home/i5l3m/Desktop/CTF/tutorials/z3-tutorial/code/04_bitvectors.py).
