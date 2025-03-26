# Hardware routines

- These are meant to be reusable routines that can be used to implement the instruction set itself.
- The typical set up would be:
  - Read pipeline stage.
  - Call routine corresponding to stage.
  - Upon return, read stage and update stage accordingly.
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

Moves the stack pointers by `offset` in range [-256, 256]

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



### write_{register}_{value}
Write `value` (from 0 to 255) from the `end` of `register`.

- Scan until we see `register` marker.
- Move to second blank after marker.
- Write `value` (stop if `start` marker is hit)
- Return.


### read_{register}_{n}
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


### SHL

Write `a1 << a2` into `a3`.

- `read_{a2}_5`
- `mov_end_pointer_{a3}_{-value}`
- `read_{a1}`
- `write_{a3}_{value}`, repeat until read gives 0 instead.


### SHR

Write `a1 >> a2` into `a3` (zero-extend).
- `read_{a2}_5`
- `mov_end_pointer_{a1}_{-value}`
- `read_{a1}`
- `write_{a3}_{value}`, repeat until read gives 0 instead.

### SLT

If `a1 < a2` (as signed), write 1 into `a3`, else write 0.

- Move to `a1`.
- Read 1 bit.
- Move to `a2`.
- Read 1 bit.
- if `a1` is 0 and `a2` is 1 then write 1 to `a3`.
- elif `a1` is 1 and `a2` is 0 then return.
- else continue like `SLTU`.

### SLTU

If `a1 < a2` (as unsigned), write 1 into `a3`, else write 0.

- Move to `a1`.
- Read 1 bit.
- Move to `a2`.
- Read 1 bit.
- if `a1` is 1 and `a2` is 0 then write 1 to `a3`.
- elif `a1` is 0 and `a2` is 1 then return.
- else repeat.
- if reached end then return.

### EXT
Extend the sign from the `start` marker of `reg`.

- Scan until we see `register` marker.
- Move to first blank after marker.
- Read 1 bit.
- Write that bit to left until we reach blank.
- Write blank to the right.
- Return.

