config:
spaces = 6
program_registers = 2
alu_registers = 4
hardware_registers = 0
total_registers = program_registers + alu_registers + hardware_registers
address_size = 32
pipeline_stages = {
    '00': 'fetch',
    '01': 'read',
    '10': 'execute',
    '11': 'write'
}

code:

step setup_spaces:
    |start, {r} -> B, R, move_right_one_0_{r}
    for i in range(spaces):
        |move_right_one_{i}_{w}, {r} -> {w}, R, move_right_one_{i}_{r}
        if i == spaces - 1:
            |move_right_one_{spaces - 1}_{w}, B -> {w}, R, end
        else:
            |move_right_one_{i}_{w}, B -> {w}, L, return_to_blank_{i}
            |return_to_blank_{i}, {r} -> , L,
            |return_to_blank_{i}, B -> , R, start_{i}
            |start_{i}, {r} -> B, R, move_right_one_{i+1}_{r}
done

step setup_alu:
    |start, B -> B, R, write_0
    for i in range(total_registers):
        |write_{i}, B -> B, R, write_{i}_0
        for j in range(address_size):
            if j == address_size - 1:
                if i == total_registers - 1:
                    |write_{i}_{j}, B -> 0, R, end
                else:
                    |write_{i}_{j}, B -> 0, R, write_{i+1}
            else:
                |write_{i}_{j}, B -> 0, R, write_{i}_{j+1}
done

step init_to_start:
    |start, B -> , L, init_0
    for i in range(spaces - 1):
        |init_{i}, {r} -> , L, init_0
        |init_{i}, B -> , L, init_{i+1}
    |init_{spaces - 1}, B -> 0, R, extra
    |extra, B -> 0, R, end
done

step pipeline:
    |start, B -> , L, skip
    |skip, {r} -> , L, read
    |read, {r} -> , R, read{r}
    |read{w}, {r} -> , R, read{w}{r}
    for k in pipeline_stages:
        |{'read' + k}, B -> , R, {pipeline_stages[k]}||start
done


hook:
 -> setup_spaces
setup_spaces -> setup_alu
setup_alu -> init_to_start
init_to_start -> pipeline