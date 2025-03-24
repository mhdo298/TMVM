config:
instructions = 0
current_instruction = 2
program_counter = 3
code:
step fetch:
    do mov_ins_from_{instructions}_to_{current_instruction}

done
hook: