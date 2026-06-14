# Part 7 — Reverse Engineering Patterns

When analyzing binaries in CTFs or malware analysis, you will see the same mathematical patterns repeated over and over. In this chapter, we build a **Pattern Catalog** showing how to recognize these patterns in assembly or decompilation, and how to model them in Z3.

---

## Pattern 1: Rolling XOR Obfuscation

* **Decompiler Pattern**: A loop where each byte of the key is XORed with a constant and the *previous* byte of the flag.
  ```c
  ciphertext[0] = plaintext[0] ^ 0x42;
  for (int i = 1; i < n; i++) {
      ciphertext[i] = plaintext[i] ^ plaintext[i-1] ^ 0x42;
  }
  ```
* **Z3 Model**:
  ```python
  # plaintext = list of BitVecs
  solver.add(plaintext[0] ^ 0x42 == ciphertext[0])
  for i in range(1, n):
      solver.add(plaintext[i] ^ plaintext[i-1] ^ 0x42 == ciphertext[i])
  ```

---

## Pattern 2: Custom CRC8 / Checksum Checks

* **Decompiler Pattern**: A loop that processes an input bit-by-bit, checking the MSB and applying a XOR-polynomial (e.g. `0x07` or `0x31`).
  ```c
  for (int j = 0; j < 8; j++) {
      if (crc & 0x80) crc = (crc << 1) ^ 0x07;
      else crc <<= 1;
  }
  ```
* **Z3 Model**: We model the loop using `z3.If` to handle the conditional branching for each shift:
  ```python
  # crc = BitVec('crc', 8)
  for j in range(8):
      msb = z3.Extract(7, 7, crc)
      crc = z3.If(msb == 1, (crc << 1) ^ 0x07, crc << 1)
  ```

---

## Pattern 3: Byte Relations (Linear Congruences)

* **Decompiler Pattern**: Systems of equations relating input buffer indexes. Often used in password or license key validations.
  ```c
  if (key[0] + key[1] == 160 && key[1] - key[2] == 10) { ... }
  ```
* **Z3 Model**:
  ```python
  solver.add(key[0] + key[1] == 160)
  solver.add(key[1] - key[2] == 10)
  ```
  > [!TIP]
  > When modeling multiplication or division on byte relations, be aware of **overflows**. If the decompiler uses larger integer types for arithmetic (e.g. `int` instead of `char`), use `ZeroExt` or `SignExt` to extend your Z3 variables before multiplying:
  > ```python
  > # Avoid 8-bit overflow (e.g. 50 * 100 = 5000, which overflows 255)
  > solver.add(z3.ZeroExt(8, key[2]) * z3.ZeroExt(8, key[0]) == 5000)
  > ```

---

## Pattern 4: VM Opcode Handlers

* **Decompiler Pattern**: A large switch-case structure inside a virtual machine interpreter.
  ```c
  switch(opcode) {
      case 0x01: regA += regB; break;
      case 0x02: regA ^= regB; break;
      case 0x03: regA *= 2; break;
  }
  ```
* **Z3 Model**: Use nested `z3.If` statements to represent the state of the registers after a VM cycle:
  ```python
  regA_out = z3.If(opcode == 0x01, regA_in + regB,
             z3.If(opcode == 0x02, regA_in ^ regB,
             z3.If(opcode == 0x03, regA_in * 2,
             regA_in))) # default case (no change)
  ```

---

## Pattern 5: Self-Modifying Checks (Dynamic Keys)

* **Decompiler Pattern**: Algorithms where the key validation logic dynamically overrides the key bytes during execution, checking the final state.
  ```c
  key[2] ^= key[0];
  key[1] += key[2];
  if (key[1] == 0x7F) success();
  ```
* **Z3 Model**: Treat each variable modification as a new SSA assignment step:
  ```python
  k0 = key[0]
  k1_0 = key[1]
  k2_0 = key[2]
  k3 = key[3]
  
  k2_1 = k2_0 ^ k0
  k1_1 = k1_0 + k2_1
  
  solver.add(k1_1 == 0x7F)
  ```

---

## Why Beginners Fail

* **Ignoring Integer Sizes in Relations**:
  Reversing a C multiplication `a * b` where variables are `uint8_t` but the arithmetic is compiled as 32-bit registers. If you do `a * b == 0x1000` on 8-bit Z3 bitvectors, Z3 will return `unsat` because the maximum value of an 8-bit multiplication (without overflow wrapping) is 255.
  *Fix*: Always extend variables to match the compilation type (e.g., 32-bit registers) before doing math.

---

## Challenge 7 — The Logical Labyrinth

Reconstruct a 4-byte key passing rolling XOR and byte relation checks:
1. `key[0] ^ key[1] == 0x05`
2. `key[1] + key[2] == 150`
3. `key[2] ^ key[3] == 0x08`
4. `key[3] * key[0] == 4818` (ensure you extend to 16-bit to prevent overflow).
5. All bytes must be printable uppercase ASCII letters (`A` to `Z`).

Write a Z3 Python solver to find this key. 

Check the solution in [code/07_re_patterns.py](file:///home/i5l3m/Desktop/CTF/tutorials/z3-tutorial/code/07_re_patterns.py).
