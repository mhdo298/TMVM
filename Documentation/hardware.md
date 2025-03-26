# Hardware setup 

## General Layout

- Hardware flags
- ALU registers (4)
- Instruction register
- Memory pointer
- Program counter
- General purpose registers
- Offset tracker
- Stack

Each section is marked by `----###----` to make tracking easier.
## Hardware Flags (000)

16-bit register for possible "stages" of the pipeline.

## Instruction register (001)

32-bit register to store the current instruction after the fetch step. 


## ALU registers (010)

32-bit registers where all computations are carried out.

## Memory pointer (011)

32-bit register to store where memory offset is.

## Program counter (100)

32-bit register representing the PC of RISCV.

## General purpose registers (101)

32-bit registers representing actual registers of RISCV.

## Offset tracker (110)

32-bit register to track how much to move the stack pointers by.

## Stack (111)

Actual 32-bit stack. 2 spaces are used as the ``Memory pointer``.
