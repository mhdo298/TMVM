# Pipeline stages

## Fetch
### `fetch`

1. `mov_{pc}_{a1}`
2. `stack_to_(a1)`
3. `mov_stack_{ins_reg}`: `decode_opcode`

## Decode
### `decode_opcode`
`read_se_{ins_reg}_6_0`
- `0110011`: `decode_funct3_0110011`
- `0010011`: `decode_funct3_0010011`
- `0000011`: `decode_funct3_0000011`
- `0100011`: `decode_funct3_0100011`
- `1100011`: `decode_funct3_1100011`
- `1101111`: `jal`
- `1100111`: `jalr`
- `0110111`: `lui`
- `0010111`: `auipc`

### `decode_funct3_0110011`
`read_se_{ins_reg}_14_12`
- `000`: `decode_0110011_000_funct7`
- `001`: `sll`
- `010`: `slt`
- `011`: `sltu`
- `100`: `xor`
- `101`: `decode_0110011_101_funct7`
- `110`: `or`
- `111`: `and`

### `decode_0110011_000_funct7`
`read_se_{ins_reg}_31_25`
- `0000000`: `add`
- `0100000`: `sub`

### `decode_0110011_101_funct7`
`read_se_{ins_reg}_31_25`
- `0000000`: `srl`
- `0100000`: `sra`

### `decode_funct3_0010011`
`read_se_{ins_reg}_14_12`
- `000`: `addi`
- `001`: `slli`
- `010`: `slti`
- `011`: `sltui`
- `100`: `xori`
- `101`: `decode_0010011_101_funct7`
- `110`: `ori`
- `111`: `andi`

### `decode_0010011_101_funct7`
`read_se_{ins_reg}_31_25`
- `0000000`: `srli`
- `0100000`: `srai`

### `decode_funct3_0000011`
`read_se_{ins_reg}_14_12`
- `000`: `lb`
- `001`: `lh`
- `010`: `lw`
- `100`: `lbu`
- `101`: `lhu`

### `decode_funct3_0100011`
`read_se_{ins_reg}_14_12`
- `000`: `sb`
- `001`: `sh`
- `010`: `sw`

### `decode_funct3_1100011`
`read_se_{ins_reg}_14_12`
- `000`: `beq`
- `001`: `bne`
- `100`: `blt`
- `101`: `bge`
- `110`: `bltu`
- `111`: `bgeu`

## Execute

### `add`
1. `get_rs1`
2. `get_rs2`
3. `ADD`
4. `put_rd`

### `sub`
1. `get_rs1`
2. `get_rs2`
3. `SUB`
4. `put_rd`

### `xor`
1. `get_rs1`
2. `get_rs2`
3. `XOR`
4. `put_rd`

### `or`
1. `get_rs1`
2. `get_rs2`
3. `OR`
4. `put_rd`

### `and`
1. `get_rs1`
2. `get_rs2`
3. `AND`
4. `put_rd`

### `sll`
1. `get_rs1`
2. `get_rs2`
3. `read_se_{a2}_4_0`: `set_ptr_se_{a1}_31_{value}`
4. `read_se_{a2}_4_0`: `set_ptr_se_{a3}_{31-value}_0`
5. `mov_{a1}_{a3}`
6. `put_rd`

### `srl`
1. `get_rs1`
2. `get_rs2`
3. `read_se_{a2}_4_0`: `set_ptr_se_{a1}_{31-value}_0`
4. `read_se_{a2}_4_0`: `set_ptr_se_{a3}_31_{value}`
5. `mov_{a1}_{a3}`
6. `put_rd`

### `sra`
1. `get_rs1`
2. `get_rs2`
3. `read_se_{a2}_4_0`: `set_ptr_se_{a1}_{31-value}_0`
4. `read_se_{a2}_4_0`: `set_ptr_se_{a3}_31_{value}`
5. `mov_{a1}_{a3}`
6. `read_se_{a2}_4_0`: `set_ptr_se_{a3}_{value}_0`
7. `EXT`
8. `put_rd`

### `slt`
1. `get_rs1`
2. `get_rs2`
3. `SLT`: `write_end_{a3}_{value}`
4. `put_rd`


### `sltu`
1. `get_rs1`
2. `get_rs2`
3. `SLTU`: `write_end_{a3}_{value}`
4. `put_rd`

### `addi`
1. `get_rs1`
2. `get_imm_I`
3. `ADD`
4. `put_rd`

### `xori`
1. `get_rs1`
2. `get_imm_I`
3. `XOR`
4. `put_rd`

### `ori`
1. `get_rs1`
2. `get_imm_I`
3. `OR`
4. `put_rd`

### `andi`
1. `get_rs1`
2. `get_imm_I`
3. `AND`
4. `put_rd`

### `slli`
1. `get_rs1`
2. `get_imm_I`
3. `read_se_{a2}_4_0`: `set_ptr_se_{a1}_31_{value}`
4. `read_se_{a2}_4_0`: `set_ptr_se_{a3}_{31-value}_0`
5. `mov_{a1}_{a3}`
6. `put_rd`

### `srli`
1. `get_rs1`
2. `get_imm_I`
3. `read_se_{a2}_4_0`: `set_ptr_se_{a1}_{31-value}_0`
4. `read_se_{a2}_4_0`: `set_ptr_se_{a3}_31_{value}`
5. `mov_{a1}_{a3}`
6. `put_rd`

### `srai`
1. `get_rs1`
2. `get_imm_I`
3. `read_se_{a2}_4_0`: `set_ptr_se_{a1}_{31-value}_0`
4. `read_se_{a2}_4_0`: `set_ptr_se_{a3}_31_{value}`
5. `mov_{a1}_{a3}`
6. `read_se_{a2}_4_0`: `set_ptr_se_{a3}_{value}_0`
7. `EXT`
8. `put_rd`

### `slti`
1. `get_rs1`
2. `get_imm_I`
3. `SLT`: `write_end_{a3}_{value}`
4. `put_rd`

### `sltiu`
1. `get_rs1`
2. `get_imm_I`
3. `SLTU`: `write_end_{a3}_{value}`
4. `put_rd`

### `lb`
1. `get_rs1`
2. `get_imm_I`
3. `ADD`
4. `mov_{a3}_{a1}`
5. `stack_to_(a1)`
6. `mov_stack_pointer_end_8`
7. `set_ptr_se_{a3}_7_0`
8. `mov_{stack}_{a3}`
9. `set_ptr_se_{a3}_7_0`
10. `EXT`
11. `put_rd`

### `lh`
1. `get_rs1`
2. `get_imm_I`
3. `ADD`
4. `mov_{a3}_{a1}`
5. `stack_to_(a1)`
6. `mov_stack_pointer_end_16`
7. `set_ptr_se_{a3}_15_0`
8. `mov_{stack}_{a3}`
9. `set_ptr_se_{a3}_15_0`
10. `EXT`
11. `put_rd`

### `lw`
1. `get_rs1`
2. `get_imm_I`
3. `ADD`
4. `mov_{a3}_{a1}`
5. `stack_to_(a1)`
6. `mov_stack_pointer_end_32`
7. `mov_{stack}_{a3}`
8. `put_rd`

### `lbu`
1. `get_rs1`
2. `get_imm_I`
3. `ADD`
4. `mov_{a3}_{a1}`
5. `stack_to_(a1)`
6. `mov_stack_pointer_end_8`
7. `set_ptr_se_{a3}_7_0`
8. `mov_{stack}_{a3}`
9. `put_rd`

### `lhu`
1. `get_rs1`
2. `get_imm_I`
3. `ADD`
4. `mov_{a3}_{a1}`
5. `stack_to_(a1)`
6. `mov_stack_pointer_end_16`
7. `set_ptr_se_{a3}_15_0`
8. `mov_{stack}_{a3}`
9. `put_rd`

### `sb`
1. `get_rs1`
2. `get_imm_S`
3. `ADD`
4. `mov_{a3}_{a1}`
5. `stack_to_(a1)`
6. `mov_stack_pointer_end_8`
7. `get_rs2`
8. `set_ptr_se_{a2}_7_0`
9. `mov_{a2}_{stack}`

### `sb`
1. `get_rs1`
2. `get_imm_S`
3. `ADD`
4. `mov_{a3}_{a1}`
5. `stack_to_(a1)`
6. `mov_stack_pointer_end_16`
7. `get_rs2`
8. `set_ptr_se_{a2}_15_0`
9. `mov_{a2}_{stack}`

### `sw`
1. `get_rs1`
2. `get_imm_S`
3. `ADD`
4. `mov_{a3}_{a1}`
5. `stack_to_(a1)`
6. `mov_stack_pointer_end_32`
7. `get_rs2`
8. `mov_{a2}_{stack}`

### `beq`
1. `get_rs1`
2. `get_rs2`
3. `XOR`
4. `CHK`:
    - If `a3` is `1`: return
5. `mov_{pc}_{a1}`
6. `get_imm_B`
7. `ADD`
8. `mov_{a3}_{pc}`

### `bne`
1. `get_rs1`
2. `get_rs2`
3. `XOR`
4. `CHK`:
    - If `a3` is `0`: return
5. `mov_{pc}_{a1}`
6. `get_imm_B`
7. `ADD`
8. `mov_{a3}_{pc}`

### `blt`
1. `get_rs1`
2. `get_rs2`
3. `SLT`
4. `CHK`:
    - If `a3` is `0`: return
5. `mov_{pc}_{a1}`
6. `get_imm_B`
7. `ADD`
8. `mov_{a3}_{pc}`

### `bltu`
1. `get_rs1`
2. `get_rs2`
3. `SLTU`
4. `CHK`:
    - If `a3` is `0`: return
5. `mov_{pc}_{a1}`
6. `get_imm_B`
7. `ADD`
8. `mov_{a3}_{pc}`

### `bge`
1. `get_rs1`
2. `get_rs2`
3. `SLT`
4. `CHK`:
    - If `a3` is `1`: return
5. `mov_{pc}_{a1}`
6. `get_imm_B`
7. `ADD`
8. `mov_{a3}_{pc}`

### `bgeu`
1. `get_rs1`
2. `get_rs2`
3. `SLTU`
4. `CHK`:
    - If `a3` is `1`: return
5. `mov_{pc}_{a1}`
6. `get_imm_B`
7. `ADD`
8. `mov_{a3}_{pc}`

### `jal`
1. `mov_{pc}_{a1}`
2. `write_{32}_{a2}`
3. `ADD`
4. `put_rd`
5. `get_imm_J`
6. `ADD`
7. `mov_{a3}_{pc}`

### `jalr`
1. `mov_{pc}_{a1}`
2. `write_{32}_{a2}`
3. `ADD`
4. `put_rd`
5. `get_rs1`
6. `get_imm_I`
7. `ADD`
8. `mov_{a3}_{pc}`

### `lui`
1. `get_imm_U`
2. `XOR`
3. `put_rd`

### `auipc`
1. `mov_{pc}_{a1}`
2. `get_imm_U`
3. `ADD`
4. `put_rd`
