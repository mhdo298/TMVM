# Hardware routines

- These are meant to be reusable routines that can be used to implement the instruction set itself.
- None of the information required to run these instructions would be stored on tape.
- The typical setup would be:
  - Decode pipeline stage.
  - Execute routine.
  - Return.
- Unless specified, routines don't return any data - as in they will simply use `ret` instead of a specialized `ret` state.

## Pointer operations
### mov_start_pointer_{register}_{offset}

Moves the start pointer of a `register` by `offset` in range [-32, 32].

- Scan until we see `register` marker.
- Move to first blank after marker.
- Move start marker based on `offset`.
- Return.

### mov_end_pointer_{register}_{offset}

Moves the end pointer of a `register` by `offset` in range [-32, 32].

- Scan until we see `register` marker.
- Move to second blank after marker.
- Move start marker based on `offset`.
- Return.

### reset_{register}

Moves the start pointer to the start, the end pointer to the end.
- Scan until we see `register` marker.
- Move to first blank after marker.
- Move blank to the left until we hit blank.
- Move to second blank after marker.
- Move blank to the right until we hit blank.

### mov_stack_pointer_both_{offset}

Moves the stack pointers by `offset` in range [-32, 32]

- Scan until we see stack marker.
- Move to blank after marker.
- Move both markers based on `offset`.
- Return.

### mov_stack_pointer_end_{offset}

Moves the `end` stack pointers by `offset` in range [0, 32]

- Scan until we see stack marker.
- Move to second blank after marker.
- Move end marker based on `offset`.
- Return.


## Memory operations

### write_start_{register}_{value}
Write `value` (from 0 to 255) from the `start` of `register`.

- Scan until we see `register` marker.
- Move to first blank after marker.
- Write `value` (stop if `end` marker is hit)
- Return.


### write_end_{register}_{value}
Write `value` (from 0 to 255) from the `end` of `register`.

- Scan until we see `register` marker.
- Move to second blank after marker.
- Write `value` (stop if `start` marker is hit)
- Return.

### read_start_{register}_{n}
Read `n` (from 1 to 8) bits from the `start` marker of `reg`, or until the `start` marker, and return the value read.

- Scan until we see `register` marker.
- Move to first blank after marker.
- Read `n` bits to the right then return `1_{value}`.
- Read until blank then return `0_{value}`.


### read_end_{register}_{n}
Read `n` (from 1 to 8) bits from the `end` marker of `reg`, or until the `start` marker, and return the value read.

- Scan until we see `register` marker.
- Move to second blank after marker.
- Read `n` bits to the left then return `1_{value}`.
- Read until blank then return `0_{value}`.

## ALU operations

### AND

Write `a1 & a2` into `a3`.

- Move to `a1`.
- Read 1 bit.
- Move to `a2`.
- Read 1 bit.
- Move to `a3`.
- Write ANDed bit.
- Loop back to `a1` until done.

### OR

Write `a1 | a2` into `a3`.

- Move to `a1`.
- Read 1 bit.
- Move to `a2`.
- Read 1 bit.
- Move to `a3`.
- Write ORed bit.
- Loop back to `a1` until done.


### XOR

Write `a1 ^ a2` into `a3`.

- Move to `a1`.
- Read 1 bit.
- Move to `a2`.
- Read 1 bit.
- Move to `a3`.
- Write XORed bit.
- Loop back to `a1` until done.


### ADD

Write `a1 + a2` into `a3` (ignore overflow).

- Set `carry` to 0.
- Move to `a1`.
- Read 1 bit.
- Move to `a2`.
- Read 1 bit.
- Move to `a3`.
- Write `carry + a1 + a2` bit, set `carry` as needed.
- Loop back to `a1` until done.


### SUB

Write `a1 - a2` into `a3` (ignore underflow).

- Set `carry` to 1.
- Move to `a1`.
- Read 1 bit.
- Move to `a2`.
- Read 1 bit.
- Move to `a3`.
- Write `carry + a1 + 1 - a2` bit, set `carry` as needed.
- Loop back to `a1` until done.

### SLT

If `a1 < a2` (as signed), return 1, else return 0.

- Move to `a1`.
- Read 1 bit.
- Move to `a2`.
- Read 1 bit.
- if `a1` is 1 and `a2` is 0 then return 1.
- elif `a1` is 0 and `a2` is 1 then return 0.
- else switch to `SLTU`.

### SLTU

If `a1 < a2` (as unsigned), return 1, else return 0.

- Move to `a1`.
- Read 1 bit.
- Move to `a2`.
- Read 1 bit.
- if `a1` is 0 and `a2` is 1 then return 1.
- elif `a1` is 1 and `a2` is 0 then return 0.
- else repeat.
- if reached end then return 0.

### EXT
Extend the sign from the `start` marker of `a3`.

- Scan until we see `register` marker.
- Move to first blank after marker.
- Read 1 bit.
- Write that bit to left until we reach blank.
- Write blank to the right.
- Return.

### CHK
Check if `a3` is 0 or not.

- Move to `a3`.
- Read until 1 is found, then return 1.
- Else return 0.


# Routine macros

## Align data (`set_ptr`)
There are a couple of variants:
- `set_ptr_se_{r1}_{l1}_{h1}`
- `set_ptr_sl_{r1}_{l1}_{b}`
- `set_ptr_el_{r1}_{h1}_{b}`

Moves pointer to correct position based on need.
1. Move `start` of `r1`
2. Move `end` of `r1`


## Move macros
### `mov_{r1}_{r2}`
1. Read from `r1` from `start` to `end`
2. Write to `r2`
3. Reset `r1`
4. Reset `r2`

## Read macros (`read`)
- `read_se_{r1}_{l1}_{h1}`

Align then read.
1. `set_ptr_se_{r1}_{l1}_{h1}`
2. Read from `r1` from `start` to `end` (no moving pointer)

## Stack macros

### `stack_to_(a1)`
1. Move MP to `a2`
2. Move `a1` to MP
3. SUB
4. Write 32 to `a2`. (then reset)
5. Check if `a3` is 0.
   1. If it is not 0:
      1. Move `a3` into `a1`
      2. SLT
         1. If `a1 < a2`:
            1. Read `a1`
            2. Move stack pointer by +value
            3. Reset `a1`
            4. Break
         2. Else read last bit of `a1`:
            1. If 0, SUB, then move stack pointer by 32.
            2. Else, ADD, then move stack pointer by -32.
            3. Reset `a1`
            4. Loop
   2. Else break.