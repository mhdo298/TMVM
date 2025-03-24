config:
instructions = 0
current_instruction = 2
program_counter = 3
code:
step fetch:
    |start, B -> , R, skip0
    |skip0, B -> , R, skip1
    |skip1, {r} -> , R,
    |skip1, B -> , R, read
    |read, {r} -> B, L, write{r}
    |write{w}, B -> {w}, R, write{w}_skip
    |write{w}_skip, B -> , R, write{w}_move_to_ins_reg
    |write{w}_move_to_ins_reg, {r} -> , R,
    |write{w}_move_to_ins_reg, B -> , R, write{w}_move_to_pointer
    |write{w}_move_to_pointer, {r} -> , R,
    |write{w}_move_to_pointer, B -> {w}, R, write_skip
    |write_skip, {r} -> B, L, read_move_back
    |read_move_back, {r} -> , L,
    |read_move_back, B -> , L, read_move_to_ins
    |read_move_to_ins, {r} -> , L,
    |read_move_to_ins, B -> B, R, read
done
hook: