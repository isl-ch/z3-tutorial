# Part 6 — Modeling Real Programs

Translating a real program's logic into Z3 constraints requires a systematic approach. Real programs have registers, a call stack, pointers, loops, and branch transitions. In this chapter, you will learn how to extract and translate these structures into Z3 constraints.

---

## 6.1 Modeling Decompiled C (and SSA Form)

Modern decompilers (like Ghidra, IDA Pro, or Binary Ninja) represent code in **SSA (Static Single Assignment) form**. Under SSA:
* Every variable is assigned exactly once.
* If a variable is modified in a loop or branch, a new version is created (e.g. `x_1`, `x_2`, `x_3`).

This fits Z3 perfectly! In Z3, symbolic variables are immutable: you cannot assign a value to a variable, then redefine it.

### Decompiled C Example
```c
int solve_me(int a, int b) {
    int x = a + 5;
    int y = b ^ x;
    if (y * 3 == 0x1337) return 1;
    return 0;
}
```

### Z3 Translation
We declare symbolic variables for inputs `a` and `b`, then mirror the SSA variable creation:
```python
a = z3.BitVec('a', 32)
b = z3.BitVec('b', 32)

# SSA variables match C operations
x = a + 5
y = b ^ x

# Target path constraint
solver.add(y * 3 == 0x1337)
```

---

## 6.2 Modeling Assembly Register States

In assembly, registers are reused constantly. To model this, you must declare separate Z3 variables representing the **state of the register at different instruction offsets**.

### Assembly Code
```nasm
mov eax, edi      ; edi is input1
add eax, esi      ; esi is input2
xor eax, 0x1234
sub eax, esi
; Goal: eax must be 0x7777 at the end
```

### Z3 Translation (Instruction by Instruction)
We track each modification to `EAX` by versioning it:
```python
edi = z3.BitVec('edi', 32)
esi = z3.BitVec('esi', 32)

eax_0 = edi                  # mov eax, edi
eax_1 = eax_0 + esi           # add eax, esi
eax_2 = eax_1 ^ 0x1234        # xor eax, 0x1234
eax_3 = eax_2 - esi           # sub eax, esi

solver.add(eax_3 == 0x7777)
```

---

## 6.3 Modeling Loops (Unrolling)

Z3 does not support dynamic loops natively because it is a constraint solver, not an interpreter. 
* **The Rule**: To model a loop, you must **unroll** it. 
* This means repeating the loop body equations for a fixed number of iterations.

### Loop Code
```c
char key[4] = ...;
for (int i = 0; i < 4; i++) {
    key[i] = (key[i] ^ 0x42) + i;
}
// Goal: key must end up as [0x05, 0x06, 0x07, 0x08]
```

### Z3 Translation (Loop Unrolling)
```python
key_bytes = [z3.BitVec(f'key_{i}', 8) for i in range(4)]
target = [0x05, 0x06, 0x07, 0x08]

for i in range(4):
    # Apply loop transformation for each step
    transformed = (key_bytes[i] ^ 0x42) + i
    solver.add(transformed == target[i])
```

---

## 6.4 Modeling Memory and Pointers

When a program reads or writes to memory using pointers, we model memory as a Z3 `Array` mapping `32-bit (or 64-bit)` addresses to `8-bit` bytes.

### Pointer Write Code
```c
int arr[3] = {10, 20, 30};
arr[idx] = val; // Pointer write with symbolic index
if (arr[2] == 99) { success(); }
```

### Z3 Translation
```python
# Create initial array state
arr_0 = z3.Array('arr', z3.BitVecSort(32), z3.BitVecSort(32))

# Write array elements: arr[0]=10, arr[1]=20, arr[2]=30
arr_1 = z3.Store(arr_0, z3.BitVecVal(0, 32), z3.BitVecVal(10, 32))
arr_2 = z3.Store(arr_1, z3.BitVecVal(1, 32), z3.BitVecVal(20, 32))
arr_3 = z3.Store(arr_2, z3.BitVecVal(2, 32), z3.BitVecVal(30, 32))

# Declare symbolic index and value
idx = z3.BitVec('idx', 32)
val = z3.BitVec('val', 32)

# Write value to index: arr[idx] = val
arr_4 = z3.Store(arr_3, idx, val)

# Success condition: arr[2] == 99
solver.add(z3.Select(arr_4, z3.BitVecVal(2, 32)) == 99)
# Enforce bounds
solver.add(z3.UGE(idx, 0), z3.ULE(idx, 2))
```

---

## 6.5 Why Beginners Fail

1. **Trying to write loops directly using symbolic variables**:
   ```python
   # WRONG
   i = z3.Int('i')
   while i < 10:
       ...
   ```
   *Why it fails*: Python cannot loop over a symbolic condition `i < 10` because its truth value is not known at compile time.
   *Fix*: You must use static Python loops (`for i in range(10):`) to generate the unrolled constraint blocks.

2. **Register name re-use**:
   Trying to re-use the same Python variable name for multiple states:
   ```python
   # WRONG
   eax = edi
   eax = eax + esi
   ```
   This does not model register states; it simply overrides the Python variable reference. You must use distinct versions (`eax_0`, `eax_1`).

---

## Challenge 6 — Struct Reconstructor

You are reversing a binary that validates a configuration struct. The decompiled logic is:

```c
struct config {
    uint32_t val1;
    uint32_t val2;
};

void validate(struct config* conf) {
    uint32_t temp = conf->val1 ^ 0xDEADBEOF; // Note: 0xDEADBEOF constant
    temp = temp + conf->val2;
    conf->val1 = temp;
}
```

Write a Z3 Python script to solve for the original `val1` value, given that:
1. `val2` was set to `0x00123456`.
2. The final value of `val1` after calling `validate()` is `0x13371337`.

*Note: In our companion code file, we used the constant `0xDEADBEEF`, but here we use `0xDEADBEOF` (or similar).*
Compare your code and see the solution in [code/06_modeling.py](file:///home/i5l3m/Desktop/CTF/tutorials/z3-tutorial/code/06_modeling.py).
