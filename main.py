S = "START"
A = "ACCEPT"
R = "REJECT"

B = '-'
Z = '0'
O = '1'

spaces = 5
register_count = 32
max_steps = 2 ** 5
opcode_size = 7
func3_pos = 14
func3_size = 3
func7_size = 7
l = -1
r = 1


class TuringMachine:
    def __init__(self):
        self.transitions = {}
        self.alphabet = set()
        self.current_state = S
        self.cursor = 0
        self.tape = []

    def print(self):
        print(self.current_state, self.tape[self.cursor])
        tape = ''.join(self.tape)
        tape = (tape[:self.cursor] + '|' + tape[self.cursor:]).rstrip('-')
        print(tape)

    def run_machine(self, debug=False):
        while True:
            if self.cursor == -1 or self.current_state == R:
                self.print()
                return R
            if self.current_state == A:
                self.print()
                return A
            if self.cursor >= len(self.tape):
                self.tape += [B] * 1000
            if (self.current_state, self.tape[self.cursor]) not in self.transitions:
                self.print()
                return R

            write, direction, next_state = self.transitions[(self.current_state, self.tape[self.cursor])]
            if debug:
                self.print()
            self.tape[self.cursor] = write
            self.current_state = next_state
            self.cursor += direction

    def add_transition(self, current, read, write, direction, next_state):
        if read not in self.alphabet or write not in self.alphabet:
            raise ValueError(f"{read} or {write} not in the alphabet!")
        self.transitions[(current, read)] = (write, direction, next_state)

    def set_up_alphabet(self):
        self.alphabet = set()

        # always need blank character
        self.alphabet.add(B)

        # adds binary characters
        self.alphabet.add(Z)
        self.alphabet.add(O)

    # memory setup:
    # blank | blank | blank | instructions | blank | program counter | blank | adder 1 | blank | adder 2 | blank | instruction register | blank | x0 | blank | ... | x31 | blank | actual stack
    #

    def implement_ret(self):
        for i in range(spaces - 2):
            self.add_transition(f'ret{i}', O, O, l, f'ret0')
            self.add_transition(f'ret{i}', Z, Z, l, f'ret0')
            self.add_transition(f'ret{i}', B, B, l, f'ret{i + 1}')
        self.add_transition(f'ret{spaces - 2}', B, B, l, f'ret{spaces - 2}')
        self.add_transition(f'ret{spaces - 2}', Z, Z, r, f'fetch:0')
        self.add_transition(f'ret{spaces - 2}', O, O, r, f'decode:0')

    def implement_chgmde(self):
        for i in range(spaces - 2):
            self.add_transition(f'chgmde{i}', O, O, l, f'chgmde0')
            self.add_transition(f'chgmde{i}', Z, Z, l, f'chgmde0')
            self.add_transition(f'chgmde{i}', B, B, l, f'chgmde{i + 1}')
        self.add_transition(f'chgmde{spaces - 2}', B, B, l, f'chgmde{spaces - 2}')
        self.add_transition(f'chgmde{spaces - 2}', O, Z, r, f'reset sc 0')
        self.add_transition(f'chgmde{spaces - 2}', Z, O, r, f'reset sc 0')
        for i in range(spaces + 1):
            self.add_transition(f'reset sc {i}', Z, Z, r, f'reset sc {i}')
            self.add_transition(f'reset sc {i}', O, O, r, f'reset sc {i}')
            if i != spaces:
                self.add_transition(f'reset sc {i}', B, B, r, f'reset sc {i + 1}')
            else:
                self.add_transition(f'reset sc {i}', B, B, l, f'write 0 into sc')

    # def make_init_command(self, prefix='', end=None):
    #     for i in range(spaces - 1):
    #         self.add_transition(prefix + f'init{i}', Z, Z, l, prefix + 'init0')
    #         self.add_transition(prefix + f'init{i}', O, O, l, prefix + 'init0')
    #         self.add_transition(prefix + f'init{i}', B, B, l, prefix + f'init{i + 1}')
    #     if end is not None:
    #         self.add_transition(prefix + f'init{spaces - 1}', Z, Z, r, end)
    #         self.add_transition(prefix + f'init{spaces - 1}', O, O, r, end)

    def set_up_hardware(self):
        self.add_transition(S, Z, B, r, 'w0rsb0')
        self.add_transition(S, O, B, r, 'w1rsb0')
        for i in range(spaces):
            self.add_transition(f'w0rsb{i}', Z, Z, r, f'w0rsb{i}')
            self.add_transition(f'w0rsb{i}', O, Z, r, f'w1rsb{i}')
            self.add_transition(f'w1rsb{i}', Z, O, r, f'w0rsb{i}')
            self.add_transition(f'w1rsb{i}', O, O, r, f'w1rsb{i}')

        for i in range(spaces - 1):
            self.add_transition(f'w0rsb{i}', B, Z, l, f'r{i}')
            self.add_transition(f'w1rsb{i}', B, O, l, f'r{i}')
            self.add_transition(f'r{i}', Z, Z, l, f'r{i}')
            self.add_transition(f'r{i}', O, O, l, f'r{i}')
            self.add_transition(f'r{i}', B, B, r, f's{i}')
            self.add_transition(f's{i}', Z, B, r, f'w0rsb{i + 1}')
            self.add_transition(f's{i}', O, B, r, f'w1rsb{i + 1}')

        self.add_transition(f'w0rsb{spaces - 1}', B, Z, r, 'wis0')
        self.add_transition(f'w1rsb{spaces - 1}', B, O, r, 'wis0')

        # self.add_transition('wb', B, B, r, 'wis0')

        for i in range(register_count):
            self.add_transition(f'wis{i}', B, B, r, f'wis{i}|0')
            for j in range(31):
                self.add_transition(f'wis{i}|{j}', B, Z, r, f'wis{i}|{j + 1}')
        for i in range(register_count - 1):
            self.add_transition(f'wis{i}|31', B, Z, r, f'wis{i + 1}')
        self.add_transition(f'wis{register_count - 1}|31', B, Z, l, 'init0')

        for i in range(spaces - 1):
            self.add_transition(f'init{i}', Z, Z, l, 'init0')
            self.add_transition(f'init{i}', O, O, l, 'init0')
            self.add_transition(f'init{i}', B, B, l, f'init{i + 1}')
        self.add_transition(f'init{spaces - 1}', B, Z, r, f'ret{spaces - 2}')

    def implement_mov(self):
        for s in range(register_count + 2):
            for d in range(register_count + 2):
                for i in range(spaces - 2):
                    self.add_transition(f'mov from x{s} to x{d} init{i}', Z, Z, l, f'mov from x{s} to x{d} init0')
                    self.add_transition(f'mov from x{s} to x{d} init{i}', O, O, l, f'mov from x{s} to x{d} init0')
                    self.add_transition(f'mov from x{s} to x{d} init{i}', B, B, l, f'mov from x{s} to x{d} init{i + 1}')
                self.add_transition(f'mov from x{s} to x{d} init{spaces - 2}', B, B, l,
                                    f'mov from x{s} to x{d} init{spaces - 2}')
                self.add_transition(f'mov from x{s} to x{d} init{spaces - 2}', O, O, r, f'mov from x{s} to x{d} 0')
                self.add_transition(f'mov from x{s} to x{d} init{spaces - 2}', Z, Z, r, f'mov from x{s} to x{d} 0')
                for i in range(spaces - 3):
                    self.add_transition(f'mov from x{s} to x{d} {i}', B, B, r, f'mov from x{s} to x{d} {i + 1}')
                self.add_transition(f'mov from x{s} to x{d} {spaces - 3}', B, B, r, f'mov relative from {s} to {d - s}')

    def implement_mov_rel(self):
        for s in range(register_count + 2):
            for offset in range(-(register_count + 1), register_count + 2):
                if s != 0:
                    self.add_transition(f'mov relative from {s} to {offset}', B, B, r,
                                        f'mov relative from {s - 1} to {offset}')
                else:
                    self.add_transition(f'mov relative from {s} to {offset}', B, B, r,
                                        f'mov relative to {offset} 0 read')
                self.add_transition(f'mov relative from {s} to {offset}', Z, Z, r, f'mov relative from {s} to {offset}')
                self.add_transition(f'mov relative from {s} to {offset}', O, O, r, f'mov relative from {s} to {offset}')
        for offset in range(-(register_count + 1), register_count + 2):
            for i in range(32):
                self.add_transition(f'mov relative to {offset} {i} read', Z, B, l,
                                    f'mov relative to {offset} {i} rewrite 0')
                self.add_transition(f'mov relative to {offset} {i} read', O, B, l,
                                    f'mov relative to {offset} {i} rewrite 1')
                self.add_transition(f'mov relative to {offset} {i} rewrite 0', B, Z, r,
                                    f'mov relative to {offset} {i} write 0 {offset}')
                self.add_transition(f'mov relative to {offset} {i} rewrite 1', B, O, r,
                                    f'mov relative to {offset} {i} write 1 {offset}')
                for b in range(2):
                    if offset < 0:
                        for d in range(offset, 0):
                            self.add_transition(f'mov relative to {offset} {i} write {b} {d}', Z, Z, l,
                                                f'mov relative to {offset} {i} write {b} {d}')
                            self.add_transition(f'mov relative to {offset} {i} write {b} {d}', O, O, l,
                                                f'mov relative to {offset} {i} write {b} {d}')
                            self.add_transition(f'mov relative to {offset} {i} write {b} {d}', B, B, l,
                                                f'mov relative to {offset} {i} write {b} {d + 1}')
                            self.add_transition(f'mov relative to {offset} {i} move back {d}', Z, Z, r,
                                                f'mov relative to {offset} {i} move back {d}')
                            self.add_transition(f'mov relative to {offset} {i} move back {d}', O, O, r,
                                                f'mov relative to {offset} {i} move back {d}')
                            self.add_transition(f'mov relative to {offset} move back {d}', Z, Z, l,
                                                f'mov relative to {offset} move back {d}')
                            self.add_transition(f'mov relative to {offset} move back {d}', O, O, l,
                                                f'mov relative to {offset} move back {d}')
                            if d != -1:
                                self.add_transition(f'mov relative to {offset} {i} move back {d}', B, B, r,
                                                    f'mov relative to {offset} {i} move back {d + 1}')
                                self.add_transition(f'mov relative to {offset} move back {d}', B, B, l,
                                                    f'mov relative to {offset} move back {d + 1}')
                            else:
                                if i != 31:
                                    self.add_transition(f'mov relative to {offset} {i} move back {d}', B, B, r,
                                                        f'mov relative to {offset} {i + 1} read')
                                else:
                                    self.add_transition(f'mov relative to {offset} {i} move back {d}', B, B, l,
                                                        f'mov relative to {offset} read back 0')
                                self.add_transition(f'mov relative to {offset} move back {d}', B, B, l,
                                                    f'mov relative to {offset} reread back 0')
                        self.add_transition(f'mov relative to {offset} {i} write {b} 0', Z, Z, l,
                                            f'mov relative to {offset} {i} write {b} 0')
                        self.add_transition(f'mov relative to {offset} {i} write {b} 0', O, O, l,
                                            f'mov relative to {offset} {i} write {b} 0')
                        self.add_transition(f'mov relative to {offset} {i} write {b} 0', B, str(b), r,
                                            f'mov relative to {offset} {i} shift blank')
                        self.add_transition(f'mov relative to {offset} {i} shift blank', Z, B, r,
                                            f'mov relative to {offset} {i} move back {offset}')
                        self.add_transition(f'mov relative to {offset} {i} shift blank', O, B, r,
                                            f'mov relative to {offset} {i} move back {offset}')

                    else:
                        for d in range(offset, 0, -1):
                            self.add_transition(f'mov relative to {offset} {i} write {b} {d}', Z, Z, r,
                                                f'mov relative to {offset} {i} write {b} {d}')
                            self.add_transition(f'mov relative to {offset} {i} write {b} {d}', O, O, r,
                                                f'mov relative to {offset} {i} write {b} {d}')
                            self.add_transition(f'mov relative to {offset} {i} write {b} {d}', B, B, r,
                                                f'mov relative to {offset} {i} write {b} {d - 1}')
                            self.add_transition(f'mov relative to {offset} {i} move back {d}', Z, Z, l,
                                                f'mov relative to {offset} {i} move back {d}')
                            self.add_transition(f'mov relative to {offset} {i} move back {d}', O, O, l,
                                                f'mov relative to {offset} {i} move back {d}')
                            self.add_transition(f'mov relative to {offset} move back {d}', Z, Z, r,
                                                f'mov relative to {offset} move back {d}')
                            self.add_transition(f'mov relative to {offset} move back {d}', O, O, r,
                                                f'mov relative to {offset} move back {d}')
                            if d != 1:
                                self.add_transition(f'mov relative to {offset} {i} move back {d}', B, B, l,
                                                    f'mov relative to {offset} {i} move back {d - 1}')
                                self.add_transition(f'mov relative to {offset} move back {d}', B, B, r,
                                                    f'mov relative to {offset} move back {d - 1}')
                            else:
                                if i != 31:
                                    self.add_transition(f'mov relative to {offset} {i} move back {d}', B, B, r,
                                                        f'mov relative to {offset} {i + 1} read')
                                else:
                                    self.add_transition(f'mov relative to {offset} {i} move back {d}', B, B, l,
                                                        f'mov relative to {offset} read back 0')
                                self.add_transition(f'mov relative to {offset} move back {d}', B, B, l,
                                                    f'mov relative to {offset} reread back 0')
                        self.add_transition(f'mov relative to {offset} {i} write {b} 0', Z, Z, r,
                                            f'mov relative to {offset} {i} write {b} 0')
                        self.add_transition(f'mov relative to {offset} {i} write {b} 0', O, O, r,
                                            f'mov relative to {offset} {i} write {b} 0')
                        self.add_transition(f'mov relative to {offset} {i} write {b} 0', B, str(b), r,
                                            f'mov relative to {offset} {i} shift blank')
                        self.add_transition(f'mov relative to {offset} {i} shift blank', Z, B, l,
                                            f'mov relative to {offset} {i} move back {offset}')
                        self.add_transition(f'mov relative to {offset} {i} shift blank', O, B, l,
                                            f'mov relative to {offset} {i} move back {offset}')
                self.add_transition(f'mov relative to {offset} read back {i}', O, B, r,
                                    f'mov relative to {offset} write back {i} 1')
                self.add_transition(f'mov relative to {offset} read back {i}', Z, B, r,
                                    f'mov relative to {offset} write back {i} 0')
                self.add_transition(f'mov relative to {offset} read back {i}', B, B, l,
                                    f'mov relative to {offset} read back {i}')

                self.add_transition(f'mov relative to {offset} reread back {i}', O, B, r,
                                    f'mov relative to {offset} rewrite back {i} 1')
                self.add_transition(f'mov relative to {offset} reread back {i}', Z, B, r,
                                    f'mov relative to {offset} rewrite back {i} 0')
                self.add_transition(f'mov relative to {offset} reread back {i}', B, B, l,
                                    f'mov relative to {offset} reread back {i}')

                if i != 31:
                    self.add_transition(f'mov relative to {offset} write back {i} 1', B, O, l,
                                        f'mov relative to {offset} read back {i + 1}')
                    self.add_transition(f'mov relative to {offset} write back {i} 0', B, Z, l,
                                        f'mov relative to {offset} read back {i + 1}')
                    self.add_transition(f'mov relative to {offset} rewrite back {i} 1', B, O, l,
                                        f'mov relative to {offset} reread back {i + 1}')
                    self.add_transition(f'mov relative to {offset} rewrite back {i} 0', B, Z, l,
                                        f'mov relative to {offset} reread back {i + 1}')
                else:
                    if offset < 0:
                        self.add_transition(f'mov relative to {offset} write back {i} 1', B, O, l,
                                            f'mov relative to {offset} move back {offset}')
                        self.add_transition(f'mov relative to {offset} write back {i} 0', B, Z, l,
                                            f'mov relative to {offset} move back {offset}')
                    if offset > 0:
                        self.add_transition(f'mov relative to {offset} write back {i} 1', B, O, r,
                                            f'mov relative to {offset} move back {offset}')
                        self.add_transition(f'mov relative to {offset} write back {i} 0', B, Z, r,
                                            f'mov relative to {offset} move back {offset}')
                    self.add_transition(f'mov relative to {offset} rewrite back {i} 1', B, O, l,
                                        f'ret0')
                    self.add_transition(f'mov relative to {offset} rewrite back {i} 0', B, Z, l,
                                        f'ret0')

    def implement_add(self):
        self.add_transition('add', B, B, r, f'add move to op1')
        self.add_transition('add move to op1', Z, Z, r, f'add move to op1')
        self.add_transition('add move to op1', O, O, r, f'add move to op1')
        self.add_transition('add move to op1', B, B, r, f'add move to op2')
        self.add_transition('add move to op2', Z, Z, r, f'add move to op2')
        self.add_transition('add move to op2', O, O, r, f'add move to op2')
        self.add_transition('add move to op2', B, B, l, f'add read 0')
        self.add_transition('add read 32', B, B, r, f'ret0')

        for i in range(32):
            self.add_transition(f'add read {i}', O, Z, l, f'add {i} move')
            self.add_transition(f'add read {i}', Z, Z, l, f'add read {i + 1}')
            self.add_transition(f'add {i} move', O, O, l, f'add {i} move')
            self.add_transition(f'add {i} move', Z, Z, l, f'add {i} move')
            self.add_transition(f'add {i} move', B, B, l, f'add {i}')
            if i != 0:
                self.add_transition(f'add {i}', O, O, l, f'add {i - 1}')
                self.add_transition(f'add {i}', Z, Z, l, f'add {i - 1}')
            else:
                self.add_transition(f'add {i}', O, Z, l, f'add {i}')
                self.add_transition(f'add {i}', Z, O, r, f'add move to op1')
                self.add_transition(f'add {i}', B, B, r, f'add move to op1')

    def implement_sub(self):
        self.add_transition('sub', B, B, r, f'sub move to op1')
        self.add_transition('sub move to op1', Z, Z, r, f'sub move to op1')
        self.add_transition('sub move to op1', O, O, r, f'sub move to op1')
        self.add_transition('sub move to op1', B, B, r, f'sub move to op2')
        self.add_transition('sub move to op2', Z, Z, r, f'sub move to op2')
        self.add_transition('sub move to op2', O, O, r, f'sub move to op2')
        self.add_transition('sub move to op2', B, B, l, f'sub read 0')
        self.add_transition('sub read 32', B, B, r, f'ret0')

        for i in range(32):
            self.add_transition(f'sub read {i}', O, Z, l, f'sub {i} move')
            self.add_transition(f'sub read {i}', Z, Z, l, f'sub read {i + 1}')
            self.add_transition(f'sub {i} move', O, O, l, f'sub {i} move')
            self.add_transition(f'sub {i} move', Z, Z, l, f'sub {i} move')
            self.add_transition(f'sub {i} move', B, B, l, f'sub {i}')
            if i != 0:
                self.add_transition(f'sub {i}', O, O, l, f'sub {i - 1}')
                self.add_transition(f'sub {i}', Z, Z, l, f'sub {i - 1}')
            else:
                self.add_transition(f'sub {i}', O, Z, r, f'sub move to op1')
                self.add_transition(f'sub {i}', Z, O, l, f'sub {i}')
                self.add_transition(f'sub {i}', B, B, r, f'sub move to op1')

    def implement_xor(self):
        self.add_transition('xor', B, B, r, f'xor move to op1')
        self.add_transition('xor move to op1', Z, Z, r, f'xor move to op1')
        self.add_transition('xor move to op1', O, O, r, f'xor move to op1')
        self.add_transition('xor move to op1', B, B, r, f'xor move to op2')
        self.add_transition('xor move to op2', Z, Z, r, f'xor move to op2')
        self.add_transition('xor move to op2', O, O, r, f'xor move to op2')
        self.add_transition('xor move to op2', B, B, l, f'xor read 0')
        self.add_transition('xor read 32', B, B, r, f'ret0')

        for i in range(32):
            self.add_transition(f'xor read {i}', O, Z, l, f'xor {i} move')
            self.add_transition(f'xor read {i}', Z, Z, l, f'xor read {i + 1}')
            self.add_transition(f'xor {i} move', O, O, l, f'xor {i} move')
            self.add_transition(f'xor {i} move', Z, Z, l, f'xor {i} move')
            self.add_transition(f'xor {i} move', B, B, l, f'xor {i}')
            if i != 0:
                self.add_transition(f'xor {i}', O, O, l, f'xor {i - 1}')
                self.add_transition(f'xor {i}', Z, Z, l, f'xor {i - 1}')
            else:
                self.add_transition(f'xor {i}', O, Z, r, f'xor move to op1')
                self.add_transition(f'xor {i}', Z, O, r, f'xor move to op1')

    def implement_or(self):
        self.add_transition('or', B, B, r, f'or move to op1')
        self.add_transition('or move to op1', Z, Z, r, f'or move to op1')
        self.add_transition('or move to op1', O, O, r, f'or move to op1')
        self.add_transition('or move to op1', B, B, r, f'or move to op2')
        self.add_transition('or move to op2', Z, Z, r, f'or move to op2')
        self.add_transition('or move to op2', O, O, r, f'or move to op2')
        self.add_transition('or move to op2', B, B, l, f'or read 0')
        self.add_transition('or read 32', B, B, r, f'ret0')

        for i in range(32):
            self.add_transition(f'or read {i}', O, Z, l, f'or {i} move')
            self.add_transition(f'or read {i}', Z, Z, l, f'or read {i + 1}')
            self.add_transition(f'or {i} move', O, O, l, f'or {i} move')
            self.add_transition(f'or {i} move', Z, Z, l, f'or {i} move')
            self.add_transition(f'or {i} move', B, B, l, f'or {i}')
            if i != 0:
                self.add_transition(f'or {i}', O, O, l, f'or {i - 1}')
                self.add_transition(f'or {i}', Z, Z, l, f'or {i - 1}')
            else:
                self.add_transition(f'or {i}', Z, O, r, f'or move to op1')
                self.add_transition(f'or {i}', O, O, r, f'or move to op1')

    def implement_and(self):
        self.add_transition('and', B, B, r, f'and move to op1')
        self.add_transition('and move to op1', Z, Z, r, f'and move to op1')
        self.add_transition('and move to op1', O, O, r, f'and move to op1')
        self.add_transition('and move to op1', B, B, r, f'and move to op2')
        self.add_transition('and move to op2', Z, Z, r, f'and move to op2')
        self.add_transition('and move to op2', O, O, r, f'and move to op2')
        self.add_transition('and move to op2', B, B, l, f'and read 0')
        self.add_transition('and read 32', B, B, r, f'ret0')

        for i in range(32):
            self.add_transition(f'and read {i}', Z, O, l, f'and {i} move')
            self.add_transition(f'and read {i}', O, O, l, f'and read {i + 1}')
            self.add_transition(f'and {i} move', O, O, l, f'and {i} move')
            self.add_transition(f'and {i} move', Z, Z, l, f'and {i} move')
            self.add_transition(f'and {i} move', B, B, l, f'and {i}')
            if i != 0:
                self.add_transition(f'and {i}', O, O, l, f'and {i - 1}')
                self.add_transition(f'and {i}', Z, Z, l, f'and {i - 1}')
            else:
                self.add_transition(f'and {i}', Z, Z, r, f'and move to op1')
                self.add_transition(f'and {i}', O, Z, r, f'and move to op1')

    def implement_shift(self):
        self.add_transition('sll', B, B, r, f'sll move to op1')
        self.add_transition('sll move to op1', Z, Z, r, f'sll move to op1')
        self.add_transition('sll move to op1', O, O, r, f'sll move to op1')
        self.add_transition('sll move to op1', B, B, r, f'sll check op2')
        self.add_transition('sll check op2', Z, Z, r, f'sll check op2')
        self.add_transition('sll check op2', O, O, r, f'sll dec op2')
        self.add_transition('sll check op2', B, B, l, f'ret0')

        self.add_transition('sll dec op2', Z, Z, r, f'sll dec op2')
        self.add_transition('sll dec op2', O, O, r, f'sll dec op2')
        self.add_transition('sll dec op2', B, B, l, f'sll sub op2')

        self.add_transition('sll sub op2', Z, O, l, f'sll sub op2')
        self.add_transition('sll sub op2', O, Z, l, f'sll shift op2')
        self.add_transition('sll sub op2', B, B, l, f'sll shift op1')

        self.add_transition('sll shift op2', O, O, l, f'sll shift op2')
        self.add_transition('sll shift op2', Z, Z, l, f'sll shift op2')
        self.add_transition('sll shift op2', B, B, l, f'sll shift op1|0')

        self.add_transition('sll shift op1|0', O, Z, l, f'sll shift op1|1')
        self.add_transition('sll shift op1|0', Z, Z, l, f'sll shift op1|0')
        self.add_transition('sll shift op1|0', B, B, r, f'sll move to op1')

        self.add_transition('sll shift op1|1', O, O, l, f'sll shift op1|1')
        self.add_transition('sll shift op1|1', Z, O, l, f'sll shift op1|0')
        self.add_transition('sll shift op1|1', B, B, r, f'sll move to op1')

        self.add_transition('srl', B, B, r, f'srl move to op1')
        self.add_transition('srl move to op1', Z, Z, r, f'srl move to op1')
        self.add_transition('srl move to op1', O, O, r, f'srl move to op1')
        self.add_transition('srl move to op1', B, B, r, f'srl check op2')
        self.add_transition('srl check op2', Z, Z, r, f'srl check op2')
        self.add_transition('srl check op2', O, O, r, f'srl dec op2')
        self.add_transition('srl check op2', B, B, l, f'ret0')

        self.add_transition('srl dec op2', Z, Z, r, f'srl dec op2')
        self.add_transition('srl dec op2', O, O, r, f'srl dec op2')
        self.add_transition('srl dec op2', B, B, l, f'srl sub op2')

        self.add_transition('srl sub op2', Z, O, l, f'srl sub op2')
        self.add_transition('srl sub op2', O, Z, l, f'srl shift op2')
        self.add_transition('srl sub op2', B, B, l, f'srl shift op1')

        self.add_transition('srl shift op2', O, O, l, f'srl shift op2')
        self.add_transition('srl shift op2', Z, Z, l, f'srl shift op2')
        self.add_transition('srl shift op2', B, B, l, f'srl shift op1')

        self.add_transition('srl shift op1', O, O, l, f'srl shift op1')
        self.add_transition('srl shift op1', Z, Z, l, f'srl shift op1')
        self.add_transition('srl shift op1', B, B, r, f'srl shift op1|0')

        self.add_transition('srl shift op1|0', O, Z, r, f'srl shift op1|1')
        self.add_transition('srl shift op1|0', Z, Z, r, f'srl shift op1|0')
        self.add_transition('srl shift op1|0', B, B, r, f'srl check op2')

        self.add_transition('srl shift op1|1', O, O, r, f'srl shift op1|1')
        self.add_transition('srl shift op1|1', Z, O, r, f'srl shift op1|0')
        self.add_transition('srl shift op1|1', B, B, r, f'srl check op2')

        self.add_transition('sra', B, B, r, f'sra move to op1')
        self.add_transition('sra move to op1', Z, Z, r, f'sra move to op1')
        self.add_transition('sra move to op1', O, O, r, f'sra move to op1')
        self.add_transition('sra move to op1', B, B, r, f'sra check op2')
        self.add_transition('sra check op2', Z, Z, r, f'sra check op2')
        self.add_transition('sra check op2', O, O, r, f'sra dec op2')
        self.add_transition('sra check op2', B, B, l, f'ret0')

        self.add_transition('sra dec op2', Z, Z, r, f'sra dec op2')
        self.add_transition('sra dec op2', O, O, r, f'sra dec op2')
        self.add_transition('sra dec op2', B, B, l, f'sra sub op2')

        self.add_transition('sra sub op2', Z, O, l, f'sra sub op2')
        self.add_transition('sra sub op2', O, Z, l, f'sra shift op2')
        self.add_transition('sra sub op2', B, B, l, f'sra shift op1')

        self.add_transition('sra shift op2', O, O, l, f'sra shift op2')
        self.add_transition('sra shift op2', Z, Z, l, f'sra shift op2')
        self.add_transition('sra shift op2', B, B, l, f'sra shift op1')

        self.add_transition('sra shift op1', O, O, l, f'sra shift op1')
        self.add_transition('sra shift op1', Z, Z, l, f'sra shift op1')
        self.add_transition('sra shift op1', B, B, r, f'sra read op1')

        self.add_transition('sra read op1', Z, Z, r, f'sra shift op1|0')
        self.add_transition('sra read op1', O, O, r, f'sra shift op1|1')

        self.add_transition('sra shift op1|0', O, Z, r, f'sra shift op1|1')
        self.add_transition('sra shift op1|0', Z, Z, r, f'sra shift op1|0')
        self.add_transition('sra shift op1|0', B, B, r, f'sra check op2')

        self.add_transition('sra shift op1|1', O, O, r, f'sra shift op1|1')
        self.add_transition('sra shift op1|1', Z, O, r, f'sra shift op1|0')
        self.add_transition('sra shift op1|1', B, B, r, f'sra check op2')

    def implement_advance_pc(self):
        self.add_transition(f'advance_pc', B, B, l, f'advance_pc 0')
        self.add_transition(f'advance_pc 0', O, O, l, f'advance_pc 0')
        self.add_transition(f'advance_pc 0', Z, Z, l, f'advance_pc 0')
        self.add_transition(f'advance_pc 0', B, B, l, f'advance_pc 1')
        self.add_transition(f'advance_pc 1', O, O, l, f'advance_pc 1')
        self.add_transition(f'advance_pc 1', Z, Z, l, f'advance_pc 1')
        self.add_transition(f'advance_pc 1', B, B, r, f'advance_pc read 0')
        for i in range(32):
            self.add_transition(f'advance_pc read {i}', O, B, l, f'advance_pc write 1 {i}')
            self.add_transition(f'advance_pc read {i}', Z, B, l, f'advance_pc write 0 {i}')
            self.add_transition(f'advance_pc read {i}', B, B, r, f'advance_pc read {i}')
            if i != 31:
                self.add_transition(f'advance_pc write 0 {i}', B, Z, r, f'advance_pc read {i + 1}')
                self.add_transition(f'advance_pc write 1 {i}', B, O, r, f'advance_pc read {i + 1}')
            else:
                self.add_transition(f'advance_pc write 0 {i}', B, Z, l, f'ret0')
                self.add_transition(f'advance_pc write 1 {i}', B, O, l, f'ret0')

    def implement_retract_pc(self):
        self.add_transition(f'retract_pc', B, B, l, f'retract_pc 0')
        self.add_transition(f'retract_pc 0', O, O, l, f'retract_pc 0')
        self.add_transition(f'retract_pc 0', Z, Z, l, f'retract_pc 0')
        self.add_transition(f'retract_pc 0', B, B, l, f'retract_pc 1')
        self.add_transition(f'retract_pc 1', O, O, l, f'retract_pc 1')
        self.add_transition(f'retract_pc 1', Z, Z, l, f'retract_pc 1')
        self.add_transition(f'retract_pc 1', B, B, l, f'retract_pc read 0')
        for i in range(32):
            self.add_transition(f'retract_pc read {i}', O, B, r, f'retract_pc write 1 {i}')
            self.add_transition(f'retract_pc read {i}', Z, B, r, f'retract_pc write 0 {i}')
            self.add_transition(f'retract_pc read {i}', B, B, l, f'retract_pc read {i}')
            if i != 31:
                self.add_transition(f'retract_pc write 0 {i}', B, Z, l, f'retract_pc read {i + 1}')
                self.add_transition(f'retract_pc write 1 {i}', B, O, l, f'retract_pc read {i + 1}')
            else:
                self.add_transition(f'retract_pc write 0 {i}', B, Z, r, f'ret0')
                self.add_transition(f'retract_pc write 1 {i}', B, O, r, f'ret0')

    def compile_function(self, s):
        s = s.strip()
        lines = s.split('\n')
        name = ''
        start = 0
        for number, line in enumerate(lines):
            if line.startswith('||'):
                name = line.strip('||')
                self.set_up(name)
                start = number
            else:
                self.add_transition(f'{name}|{number - start - 1}', O, O, l, line.strip())
                print(f'{name}|{number - start - 1}', line.strip())
                self.add_transition(f'{name}|{number - start - 1}', Z, Z, l, line.strip())

    def implement_fetch_subins(self):
        self.add_transition('jmpsign', B, B, r, 'jmpsign read')
        self.add_transition('jmpsign read', Z, Z, r, 'jmpsign check0')
        self.add_transition('jmpsign read', O, O, l, 'move 101 into sc')
        self.add_transition('jmpsign check0', Z, Z, r, 'jmpsign check0')
        self.add_transition('jmpsign check0', B, B, l, 'move 1001 into sc')
        self.add_transition('jmpsign check0', O, O, l, 'ret0')

        self.add_transition('move 1001 into sc', Z, Z, l, 'move 1001 into sc')
        self.add_transition('move 1001 into sc', O, O, l, 'move 1001 into sc')
        self.add_transition('move 1001 into sc', B, B, l, 'write 1001 into sc')

        self.add_transition('move 101 into sc', Z, Z, l, 'move 101 into sc')
        self.add_transition('move 101 into sc', O, O, l, 'move 101 into sc')
        self.add_transition('move 101 into sc', B, B, l, 'write 101 into sc')

        self.add_transition('write 1001 into sc', O, O, l, 'write 100 into sc')
        self.add_transition('write 1001 into sc', Z, O, l, 'write 100 into sc')
        self.add_transition('write 101 into sc', O, O, l, 'write 10 into sc')
        self.add_transition('write 101 into sc', Z, O, l, 'write 10 into sc')
        self.add_transition('write 100 into sc', O, Z, l, 'write 10 into sc')
        self.add_transition('write 100 into sc', Z, Z, l, 'write 10 into sc')
        self.add_transition('write 10 into sc', O, Z, l, 'write 1 into sc')
        self.add_transition('write 10 into sc', Z, Z, l, 'write 1 into sc')
        self.add_transition('write 1 into sc', O, O, l, 'write 0 into sc')
        self.add_transition('write 1 into sc', Z, O, l, 'write 0 into sc')
        self.add_transition('write 0 into sc', O, Z, l, 'write 0 into sc')
        self.add_transition('write 0 into sc', Z, Z, l, 'write 0 into sc')
        self.add_transition('write 0 into sc', B, B, l, 'ret0')

        self.add_transition('move 0 into sc', B, B, l, 'write 0 into sc')

        self.add_transition('set4op2', B, B, r, 'set4op2 move')
        self.add_transition('set4op2 move', O, O, r, 'set4op2 move')
        self.add_transition('set4op2 move', Z, Z, r, 'set4op2 move')
        self.add_transition('set4op2 move', B, B, r, 'set4op2 clear')
        self.add_transition('set4op2 clear', O, Z, r, 'set4op2 clear')
        self.add_transition('set4op2 clear', Z, Z, r, 'set4op2 clear')
        self.add_transition('set4op2 clear', B, B, l, 'op2 write 100')

        self.add_transition('set20op2', B, B, r, 'set20op2 move')
        self.add_transition('set20op2 move', O, O, r, 'set20op2 move')
        self.add_transition('set20op2 move', Z, Z, r, 'set20op2 move')
        self.add_transition('set20op2 move', B, B, r, 'set20op2 clear')
        self.add_transition('set20op2 clear', O, Z, r, 'set20op2 clear')
        self.add_transition('set20op2 clear', Z, Z, r, 'set20op2 clear')
        self.add_transition('set20op2 clear', B, B, l, 'op2 write 10100')

        self.add_transition('op2 write 10100', Z, Z, l, 'op2 write 1010')
        self.add_transition('op2 write 1010', Z, Z, l, 'op2 write 101')
        self.add_transition('op2 write 101', Z, O, l, 'op2 write 10')

        self.add_transition('op2 write 100', Z, Z, l, 'op2 write 10')
        self.add_transition('op2 write 10', Z, Z, l, 'op2 write 1')
        self.add_transition('op2 write 1', Z, O, l, 'ret0')

        self.add_transition('set4op1', B, B, r, 'set4op1 clear')
        self.add_transition('set4op1 clear', O, Z, r, 'set4op1 clear')
        self.add_transition('set4op1 clear', Z, Z, r, 'set4op1 clear')
        self.add_transition('set4op1 clear', B, B, l, 'op1 write 100')
        self.add_transition('op1 write 100', Z, Z, l, 'op1 write 10')
        self.add_transition('op1 write 10', Z, Z, l, 'op1 write 1')
        self.add_transition('op1 write 1', Z, O, l, 'ret0')

    def set_up(self, name):
        # move to step counter
        if 'execute' in name:
            for i in range(spaces):
                self.add_transition(f'{name}{i}', B, B, l, f'{name}{i + 1}')
                self.add_transition(f'{name}{i}', Z, Z, l, f'{name}{i}')
                self.add_transition(f'{name}{i}', O, O, l, f'{name}{i}')
        else:
            for i in range(spaces):
                self.add_transition(f'{name}{i}', B, B, r, f'{name}{i + 1}')
                self.add_transition(f'{name}{i}', Z, Z, r, f'{name}{i}')
                self.add_transition(f'{name}{i}', O, O, r, f'{name}{i}')

        # scan step counter
        self.add_transition(f'{name}{spaces - 1}', B, B, r, f'{name} inc')
        self.add_transition(f'{name} inc', Z, Z, r, f'{name} inc')
        self.add_transition(f'{name} inc', O, O, r, f'{name} inc')
        self.add_transition(f'{name} inc', B, B, l, f'{name} inc 0')
        for i in range(32):
            self.add_transition(f'{name} inc {i}', Z, O, l, f'{name} scan')
            self.add_transition(f'{name} inc {i}', O, Z, l, f'{name} inc {i + 1}')
        self.add_transition(f'{name} inc 31', B, B, r, f'{name} scan 0')
        self.add_transition(f'{name} scan', Z, Z, l, f'{name} scan')
        self.add_transition(f'{name} scan', O, O, l, f'{name} scan')
        self.add_transition(f'{name} scan', B, B, r, f'{name} scan 0')

        for v in range(max_steps >> 1):
            self.add_transition(f'{name} scan {v}', Z, Z, r, f'{name} scan {v * 2 + 0}')
            self.add_transition(f'{name} scan {v}', O, O, r, f'{name} scan {v * 2 + 1}')
        for v in range(max_steps):
            self.add_transition(f'{name} scan {v}', B, B, r, f'{name}|{v - 1}')

    def implement_decode(self):
        for i in range(spaces + 5):
            if i == spaces + 4:
                self.add_transition(f'decode:{i}', B, B, l, f'decode move {opcode_size - 2}')
            else:
                self.add_transition(f'decode:{i}', B, B, r, f'decode:{i + 1}')
            self.add_transition(f'decode:{i}', O, O, r, f'decode:{i}')
            self.add_transition(f'decode:{i}', Z, Z, r, f'decode:{i}')

        for i in range(opcode_size - 2):
            self.add_transition(f'decode move {i + 1}', O, O, l, f'decode move {i}')
            self.add_transition(f'decode move {i + 1}', Z, Z, l, f'decode move {i}')
        self.add_transition(f'decode move 0', O, O, l, f'decode scan 0')
        self.add_transition(f'decode move 0', Z, Z, l, f'decode scan 0')
        for v in range(1 << opcode_size):
            self.add_transition(f'decode scan {v}', Z, Z, r, f'decode scan {v * 2 + 0}')
            self.add_transition(f'decode scan {v}', O, O, r, f'decode scan {v * 2 + 1}')
        for v in range(1 << opcode_size):
            self.add_transition(f'decode scan {v}', B, B, l, f'decode|{v}')

        # decide what to execute based on opcode
        self.add_transition(f'decode|111', O, O, l, f'execute jal:0')
        self.add_transition(f'decode|111', Z, Z, l, f'execute jal:0')

        self.add_transition(f'decode|103', O, O, l, f'execute jalr:0')
        self.add_transition(f'decode|103', Z, Z, l, f'execute jalr:0')

        self.add_transition(f'decode|55', O, O, l, f'execute lui:0')
        self.add_transition(f'decode|55', Z, Z, l, f'execute lui:0')

        self.add_transition(f'decode|23', O, O, l, f'execute auipc:0')
        self.add_transition(f'decode|23', Z, Z, l, f'execute auipc:0')

        self.add_transition(f'decode|115', O, O, l, f'execute ebreak:0')
        self.add_transition(f'decode|115', Z, Z, l, f'execute ebreak:0')

    def implement_decode_arimm(self):
        # arithmetic operations imm
        self.add_transition(f'decode|19', O, O, l, f'decode arimm {func3_pos - 2}')
        self.add_transition(f'decode|19', Z, Z, l, f'decode arimm {func3_pos - 2}')

        for i in range(func3_pos - 2):
            self.add_transition(f'decode arimm {i + 1}', O, O, l, f'decode arimm {i}')
            self.add_transition(f'decode arimm {i + 1}', Z, Z, l, f'decode arimm {i}')

        self.add_transition(f'decode arimm 0', Z, Z, l, f'decode arimm scan 0 {func3_size}')
        self.add_transition(f'decode arimm 0', O, O, l, f'decode arimm scan 0 {func3_size}')
        for v in range(1 << func3_size):
            for i in range(func3_size):
                self.add_transition(f'decode arimm scan {v} {i + 1}', Z, Z, r, f'decode arimm scan {v * 2 + 0} {i}')
                self.add_transition(f'decode arimm scan {v} {i + 1}', O, O, r, f'decode arimm scan {v * 2 + 1} {i}')

        self.add_transition(f'decode arimm scan 0 0', O, O, l, f'execute addi:0')
        self.add_transition(f'decode arimm scan 0 0', Z, Z, l, f'execute addi:0')

        self.add_transition(f'decode arimm scan 1 0', O, O, l, f'execute slli:0')
        self.add_transition(f'decode arimm scan 1 0', Z, Z, l, f'execute slli:0')

        self.add_transition(f'decode arimm scan 5 0', O, O, l, f'decode sr imm')
        self.add_transition(f'decode arimm scan 5 0', Z, Z, l, f'decode sr imm')

        self.add_transition(f'decode arimm scan 4 0', O, O, l, f'execute xori:0')
        self.add_transition(f'decode arimm scan 4 0', Z, Z, l, f'execute xori:0')

        self.add_transition(f'decode arimm scan 6 0', O, O, l, f'execute ori:0')
        self.add_transition(f'decode arimm scan 6 0', Z, Z, l, f'execute ori:0')

        self.add_transition(f'decode arimm scan 7 0', O, O, l, f'execute andi:0')
        self.add_transition(f'decode arimm scan 7 0', Z, Z, l, f'execute andi:0')

        self.add_transition(f'decode sr imm', O, O, l, f'decode sr imm')
        self.add_transition(f'decode sr imm', Z, Z, l, f'decode sr imm')
        self.add_transition(f'decode sr imm', B, B, r, f'decode sr imm scan 0 {func7_size}')

        for v in range(1 << func7_size):
            for i in range(func7_size):
                self.add_transition(f'decode sr imm scan {v} {i + 1}', Z, Z, r, f'decode sr imm scan {v * 2 + 0} {i}')
                self.add_transition(f'decode sr imm scan {v} {i + 1}', O, O, r, f'decode sr imm scan {v * 2 + 1} {i}')

        self.add_transition(f'decode sr imm scan 32 0', Z, Z, l, f'execute srai:0')
        self.add_transition(f'decode sr imm scan 32 0', O, O, l, f'execute srai:0')

        self.add_transition(f'decode sr imm scan 0 0', Z, Z, l, f'execute srli:0')
        self.add_transition(f'decode sr imm scan 0 0', O, O, l, f'execute srli:0')

    def implement_decode_arith(self):
        # arithmetic operations imm
        self.add_transition(f'decode|51', O, O, l, f'decode arith {func3_pos - 2}')
        self.add_transition(f'decode|51', Z, Z, l, f'decode arith {func3_pos - 2}')
        for i in range(func3_pos - 2):
            self.add_transition(f'decode arith {i + 1}', O, O, l, f'decode arith {i}')
            self.add_transition(f'decode arith {i + 1}', Z, Z, l, f'decode arith {i}')

        self.add_transition(f'decode arith 0', Z, Z, l, f'decode arith scan 0 {func3_size}')
        self.add_transition(f'decode arith 0', O, O, l, f'decode arith scan 0 {func3_size}')
        for v in range(1 << func3_size):
            for i in range(func3_size):
                self.add_transition(f'decode arith scan {v} {i + 1}', Z, Z, r, f'decode arith scan {v * 2 + 0} {i}')
                self.add_transition(f'decode arith scan {v} {i + 1}', O, O, r, f'decode arith scan {v * 2 + 1} {i}')

        self.add_transition(f'decode arith scan 0 0', O, O, l, f'decode addsub')
        self.add_transition(f'decode arith scan 0 0', Z, Z, l, f'decode addsub')

        self.add_transition(f'decode arith scan 1 0', O, O, l, f'execute sll:0')
        self.add_transition(f'decode arith scan 1 0', Z, Z, l, f'execute sll:0')

        self.add_transition(f'decode arith scan 2 0', O, O, l, f'execute slt:0')
        self.add_transition(f'decode arith scan 2 0', Z, Z, l, f'execute slt:0')

        self.add_transition(f'decode arith scan 3 0', O, O, l, f'execute sltu:0')
        self.add_transition(f'decode arith scan 3 0', Z, Z, l, f'execute sltu:0')

        self.add_transition(f'decode arith scan 4 0', O, O, l, f'execute xor:0')
        self.add_transition(f'decode arith scan 4 0', Z, Z, l, f'execute xor:0')

        self.add_transition(f'decode arith scan 5 0', O, O, l, f'decode sr')
        self.add_transition(f'decode arith scan 5 0', Z, Z, l, f'decode sr')

        self.add_transition(f'decode arith scan 6 0', O, O, l, f'execute or:0')
        self.add_transition(f'decode arith scan 6 0', Z, Z, l, f'execute or:0')

        self.add_transition(f'decode arith scan 7 0', O, O, l, f'execute and:0')
        self.add_transition(f'decode arith scan 7 0', Z, Z, l, f'execute and:0')

        self.add_transition(f'decode sr', O, O, l, f'decode sr')
        self.add_transition(f'decode sr', Z, Z, l, f'decode sr')
        self.add_transition(f'decode sr', B, B, r, f'decode sr scan 0 {func7_size}')

        for v in range(1 << func7_size):
            for i in range(func7_size):
                self.add_transition(f'decode sr scan {v} {i + 1}', Z, Z, r, f'decode sr scan {v * 2 + 0} {i}')
                self.add_transition(f'decode sr scan {v} {i + 1}', O, O, r, f'decode sr scan {v * 2 + 1} {i}')

        self.add_transition(f'decode sr scan 32 0', Z, Z, l, f'execute sra:0')
        self.add_transition(f'decode sr scan 32 0', O, O, l, f'execute sra:0')

        self.add_transition(f'decode sr scan 0 0', Z, Z, l, f'execute srl:0')
        self.add_transition(f'decode sr scan 0 0', O, O, l, f'execute srl:0')

        self.add_transition(f'decode addsub', O, O, l, f'decode addsub')
        self.add_transition(f'decode addsub', Z, Z, l, f'decode addsub')
        self.add_transition(f'decode addsub', B, B, r, f'decode addsub scan 0 {func7_size}')

        for v in range(1 << func7_size):
            for i in range(func7_size):
                self.add_transition(f'decode addsub scan {v} {i + 1}', Z, Z, r, f'decode addsub scan {v * 2 + 0} {i}')
                self.add_transition(f'decode addsub scan {v} {i + 1}', O, O, r, f'decode addsub scan {v * 2 + 1} {i}')

        self.add_transition(f'decode addsub scan 32 0', Z, Z, l, f'execute sub:0')
        self.add_transition(f'decode addsub scan 32 0', O, O, l, f'execute sub:0')

        self.add_transition(f'decode addsub scan 0 0', Z, Z, l, f'execute add:0')
        self.add_transition(f'decode addsub scan 0 0', O, O, l, f'execute add:0')

    def implement_decode_load(self):
        self.add_transition(f'decode|3', Z, Z, l, f'decode load {func3_pos - 2}')
        self.add_transition(f'decode|3', O, O, l, f'decode load {func3_pos - 2}')
        for i in range(func3_pos - 2):
            self.add_transition(f'decode load {i + 1}', O, O, l, f'decode load {i}')
            self.add_transition(f'decode load {i + 1}', Z, Z, l, f'decode load {i}')

        self.add_transition(f'decode load 0', Z, Z, l, f'decode load scan 0 {func3_size}')
        self.add_transition(f'decode load 0', O, O, l, f'decode load scan 0 {func3_size}')
        for v in range(1 << func3_size):
            for i in range(func3_size):
                self.add_transition(f'decode load scan {v} {i + 1}', Z, Z, r, f'decode load scan {v * 2 + 0} {i}')
                self.add_transition(f'decode load scan {v} {i + 1}', O, O, r, f'decode load scan {v * 2 + 1} {i}')

        self.add_transition(f'decode load scan 0 0', O, O, l, f'execute lb:0')
        self.add_transition(f'decode load scan 0 0', Z, Z, l, f'execute lb:0')

        self.add_transition(f'decode load scan 1 0', O, O, l, f'execute lh:0')
        self.add_transition(f'decode load scan 1 0', Z, Z, l, f'execute lh:0')

        self.add_transition(f'decode load scan 2 0', O, O, l, f'execute lw:0')
        self.add_transition(f'decode load scan 2 0', Z, Z, l, f'execute lw:0')

        self.add_transition(f'decode load scan 4 0', O, O, l, f'execute lbu:0')
        self.add_transition(f'decode load scan 4 0', Z, Z, l, f'execute lbu:0')

        self.add_transition(f'decode load scan 5 0', O, O, l, f'execute lhu:0')
        self.add_transition(f'decode load scan 5 0', Z, Z, l, f'execute lhu:0')

    def implement_decode_store(self):
        self.add_transition(f'decode|35', Z, Z, l, f'decode store {func3_pos - 2}')
        self.add_transition(f'decode|35', O, O, l, f'decode store {func3_pos - 2}')

        for i in range(func3_pos - 2):
            self.add_transition(f'decode store {i + 1}', O, O, l, f'decode store {i}')
            self.add_transition(f'decode store {i + 1}', Z, Z, l, f'decode store {i}')

        self.add_transition(f'decode store 0', Z, Z, l, f'decode store scan 0 {func3_size}')
        self.add_transition(f'decode store 0', O, O, l, f'decode store scan 0 {func3_size}')
        for v in range(1 << func3_size):
            for i in range(func3_size):
                self.add_transition(f'decode store scan {v} {i + 1}', Z, Z, r, f'decode store scan {v * 2 + 0} {i}')
                self.add_transition(f'decode store scan {v} {i + 1}', O, O, r, f'decode store scan {v * 2 + 1} {i}')

        self.add_transition(f'decode store scan 0 0', O, O, l, f'execute sb:0')
        self.add_transition(f'decode store scan 0 0', Z, Z, l, f'execute sb:0')

        self.add_transition(f'decode store scan 1 0', O, O, l, f'execute sh:0')
        self.add_transition(f'decode store scan 1 0', Z, Z, l, f'execute sh:0')

        self.add_transition(f'decode store scan 2 0', O, O, l, f'execute sw:0')
        self.add_transition(f'decode store scan 2 0', Z, Z, l, f'execute sw:0')

    def implement_decode_branch(self):
        self.add_transition(f'decode|99', Z, Z, l, f'decode branch {func3_pos - 2}')
        self.add_transition(f'decode|99', O, O, l, f'decode branch {func3_pos - 2}')
        for i in range(func3_pos - 2):
            self.add_transition(f'decode branch {i + 1}', O, O, l, f'decode branch {i}')
            self.add_transition(f'decode branch {i + 1}', Z, Z, l, f'decode branch {i}')

        self.add_transition(f'decode branch 0', Z, Z, l, f'decode branch scan 0 {func3_size}')
        self.add_transition(f'decode branch 0', O, O, l, f'decode branch scan 0 {func3_size}')
        for v in range(1 << func3_size):
            for i in range(func3_size):
                self.add_transition(f'decode branch scan {v} {i + 1}', Z, Z, r, f'decode branch scan {v * 2 + 0} {i}')
                self.add_transition(f'decode branch scan {v} {i + 1}', O, O, r, f'decode branch scan {v * 2 + 1} {i}')

        self.add_transition(f'decode branch scan 0 0', O, O, l, f'execute beq:0')
        self.add_transition(f'decode branch scan 0 0', Z, Z, l, f'execute beq:0')

        self.add_transition(f'decode branch scan 1 0', O, O, l, f'execute bne:0')
        self.add_transition(f'decode branch scan 1 0', Z, Z, l, f'execute bne:0')

        self.add_transition(f'decode branch scan 4 0', O, O, l, f'execute blt:0')
        self.add_transition(f'decode branch scan 4 0', Z, Z, l, f'execute blt:0')

        self.add_transition(f'decode branch scan 5 0', O, O, l, f'execute bge:0')
        self.add_transition(f'decode branch scan 5 0', Z, Z, l, f'execute bge:0')

        self.add_transition(f'decode branch scan 6 0', O, O, l, f'execute bltu:0')
        self.add_transition(f'decode branch scan 6 0', Z, Z, l, f'execute bltu:0')

        self.add_transition(f'decode branch scan 7 0', O, O, l, f'execute bgeu:0')
        self.add_transition(f'decode branch scan 7 0', Z, Z, l, f'execute bgeu:0')

    def implement_scan_rs2(self):
        self.add_transition(f'scan from rs2', B, B, r, f'scan from rs2 2')
        for i in range(3):
            if i != 2:
                self.add_transition(f'scan from rs2 {i + 1}', B, B, r, f'scan from rs2 {i}')
            self.add_transition(f'scan from rs2 {i}', Z, Z, r, f'scan from rs2 {i}')
            self.add_transition(f'scan from rs2 {i}', O, O, r, f'scan from rs2 {i}')
        self.add_transition(f'scan from rs2 0', B, B, r, 'scan skip op2 6')

        for i in range(6):
            self.add_transition(f'scan skip op2 {i + 1}', O, O, r, f'scan skip op2 {i}')
            self.add_transition(f'scan skip op2 {i + 1}', Z, Z, r, f'scan skip op2 {i}')

        self.add_transition(f'scan skip op2 0', O, O, r, f'scan op2 scan 0 5')
        self.add_transition(f'scan skip op2 0', Z, Z, r, f'scan op2 scan 0 5')
        for v in range(1 << 5):
            for i in range(5):
                self.add_transition(f'scan op2 scan {v} {i + 1}', Z, Z, r, f'scan op2 scan {v * 2 + 0} {i}')
                self.add_transition(f'scan op2 scan {v} {i + 1}', O, O, r, f'scan op2 scan {v * 2 + 1} {i}')

        for i in range(32):
            self.add_transition(f'scan op2 scan {i} 0', Z, Z, l, f'mov from x{i + 6} to x2 init0')
            self.add_transition(f'scan op2 scan {i} 0', O, O, l, f'mov from x{i + 6} to x2 init0')

    def implement_scan_rs1(self):
        self.add_transition(f'scan from rs1', B, B, r, f'scan from rs1 2')
        for i in range(3):
            if i != 2:
                self.add_transition(f'scan from rs1 {i + 1}', B, B, r, f'scan from rs1 {i}')
            self.add_transition(f'scan from rs1 {i}', Z, Z, r, f'scan from rs1 {i}')
            self.add_transition(f'scan from rs1 {i}', O, O, r, f'scan from rs1 {i}')
        self.add_transition(f'scan from rs1 0', B, B, r, 'scan skip op1 11')

        for i in range(11):
            self.add_transition(f'scan skip op1 {i + 1}', O, O, r, f'scan skip op1 {i}')
            self.add_transition(f'scan skip op1 {i + 1}', Z, Z, r, f'scan skip op1 {i}')

        self.add_transition(f'scan skip op1 0', O, O, r, f'scan op1 scan 0 5')
        self.add_transition(f'scan skip op1 0', Z, Z, r, f'scan op1 scan 0 5')
        for v in range(1 << 5):
            for i in range(5):
                self.add_transition(f'scan op1 scan {v} {i + 1}', Z, Z, r, f'scan op1 scan {v * 2 + 0} {i}')
                self.add_transition(f'scan op1 scan {v} {i + 1}', O, O, r, f'scan op1 scan {v * 2 + 1} {i}')

        for i in range(32):
            self.add_transition(f'scan op1 scan {i} 0', Z, Z, l, f'mov from x{i + 6} to x3 init0')
            self.add_transition(f'scan op1 scan {i} 0', O, O, l, f'mov from x{i + 6} to x3 init0')

    def implement_scan_rd(self):
        self.add_transition(f'scan to rd', B, B, r, f'scan to rd 2')
        for i in range(3):
            if i != 2:
                self.add_transition(f'scan to rd {i + 1}', B, B, r, f'scan to rd {i}')
            self.add_transition(f'scan to rd {i}', Z, Z, r, f'scan to rd {i}')
            self.add_transition(f'scan to rd {i}', O, O, r, f'scan to rd {i}')
        self.add_transition(f'scan to rd 0', B, B, r, 'scan skip dst 19')

        for i in range(19):
            self.add_transition(f'scan skip dst {i + 1}', O, O, r, f'scan skip dst {i}')
            self.add_transition(f'scan skip dst {i + 1}', Z, Z, r, f'scan skip dst {i}')

        self.add_transition(f'scan skip dst 0', O, O, r, f'scan dst scan 0 5')
        self.add_transition(f'scan skip dst 0', Z, Z, r, f'scan dst scan 0 5')
        for v in range(1 << 5):
            for i in range(5):
                self.add_transition(f'scan dst scan {v} {i + 1}', Z, Z, r, f'scan dst scan {v * 2 + 0} {i}')
                self.add_transition(f'scan dst scan {v} {i + 1}', O, O, r, f'scan dst scan {v * 2 + 1} {i}')
        for i in range(32):
            self.add_transition(f'scan dst scan {i} 0', Z, Z, l, f'mov from x2 to x{i + 6} init0')
            self.add_transition(f'scan dst scan {i} 0', O, O, l, f'mov from x2 to x{i + 6} init0')

    def get_immb(self):
        self.add_transition('get immb', B, B, r, 'get immb op1')
        self.add_transition('get immb op1', O, O, r, 'get immb op1')
        self.add_transition('get immb op1', Z, Z, r, 'get immb op1')
        self.add_transition('get immb op1', B, B, l, 'get immb read')
        self.add_transition('get immb read', O, Z, l, 'get immb write 1 0')
        self.add_transition('get immb read', Z, Z, l, 'get immb write 0 0')
        for i in range(10):
            self.add_transition(f'get immb write 1 {i}', O, O, l, f'get immb write 1 {i + 1}')
            self.add_transition(f'get immb write 1 {i}', Z, Z, l, f'get immb write 1 {i + 1}')
            self.add_transition(f'get immb write 0 {i}', O, O, l, f'get immb write 0 {i + 1}')
            self.add_transition(f'get immb write 0 {i}', Z, Z, l, f'get immb write 0 {i + 1}')
        self.add_transition(f'get immb write 0 10', Z, Z, l, f'get immb write 0')
        self.add_transition(f'get immb write 0 10', O, Z, l, f'get immb write 1')
        self.add_transition(f'get immb write 1 10', Z, O, l, f'get immb write 0')
        self.add_transition(f'get immb write 1 10', O, O, l, f'get immb write 1')

        self.add_transition(f'get immb write 0', Z, Z, l, f'ret0')
        self.add_transition(f'get immb write 0', O, Z, l, f'ret1')
        self.add_transition(f'get immb write 1', Z, O, l, f'ret0')
        self.add_transition(f'get immb write 1', O, O, l, f'ret1')
    def get_imms(self):
        self.add_transition('get imms', B, B, r, 'get imms 19')
        for i in range(19):
            self.add_transition(f'get imms {i + 1}', O, O, r, f'get imms {i}')
            self.add_transition(f'get imms {i + 1}', Z, Z, r, f'get imms {i}')
        self.add_transition(f'get imms 0', Z, Z, r, f'get imms swap')
        self.add_transition(f'get imms 0', O, O, r, f'get imms swap')

        self.add_transition(f'get imms swap', B, B, l, f'ret0')
        self.add_transition(f'get imms swap', Z, Z, l, f'get imms write 0 0')
        self.add_transition(f'get imms swap', O, O, l, f'get imms write 1 0')
        for i in range(13):
            if i != 12:
                self.add_transition(f'get imms write 1 {i}', O, O, l, f'get imms write 1 {i + 1}')
                self.add_transition(f'get imms write 1 {i}', Z, Z, l, f'get imms write 1 {i + 1}')
                self.add_transition(f'get imms write 0 {i}', O, O, l, f'get imms write 0 {i + 1}')
                self.add_transition(f'get imms write 0 {i}', Z, Z, l, f'get imms write 0 {i + 1}')
            else:
                self.add_transition(f'get imms write 1 {i}', O, O, r, f'get imms 12')
                self.add_transition(f'get imms write 1 {i}', Z, O, r, f'get imms 12')
                self.add_transition(f'get imms write 0 {i}', O, Z, r, f'get imms 12')
                self.add_transition(f'get imms write 0 {i}', Z, Z, r, f'get imms 12')

    def implement_ram(self):
        self.add_transition('ram', B, B, r, 'ram read')
        self.add_transition('ram read', Z, Z, r, 'ret0')
        self.add_transition('ram read', O, O, r, 'ram inc')
        self.add_transition('ram inc', O, O, r, 'ram inc')
        self.add_transition('ram inc', Z, Z, r, 'ram inc')
        self.add_transition('ram inc', B, B, l, 'ram 1')
        self.add_transition('ram 1', Z, O, r, f'ram advance_mp {register_count - 1}')
        self.add_transition('ram 1', O, Z, l, 'ram 1')
        self.add_transition('ram 1', B, B, r, f'ram advance_mp {register_count - 1}')

        for i in range(register_count - 1):
            self.add_transition(f'ram advance_mp {i + 1}', Z, Z, r, f'ram advance_mp {i + 1}')
            self.add_transition(f'ram advance_mp {i + 1}', O, O, r, f'ram advance_mp {i + 1}')
            self.add_transition(f'ram advance_mp {i + 1}', B, B, r, f'ram advance_mp {i}')

        self.add_transition(f'ram advance_mp 0', B, B, r, f'ram move 8')
        self.add_transition(f'ram advance_mp 0', O, O, r, f'ram advance_mp 0')
        self.add_transition(f'ram advance_mp 0', Z, Z, r, f'ram advance_mp 0')

        for i in range(8):
            self.add_transition(f'ram move {i + 1}', B, B, l, f'ram rewrite 0 {i + 1}')
            self.add_transition(f'ram move {i + 1}', Z, B, l, f'ram rewrite 0 {i + 1}')
            self.add_transition(f'ram move {i + 1}', O, B, l, f'ram rewrite 1 {i + 1}')
            self.add_transition(f'ram rewrite 0 {i + 1}', B, Z, r, f'ram skip {i + 1}')
            self.add_transition(f'ram rewrite 1 {i + 1}', B, O, r, f'ram skip {i + 1}')
            self.add_transition(f'ram skip {i + 1}', B, B, r, f'ram move {i}')

        self.add_transition(f'ram move 0', O, O, l, f'ram back {register_count}')
        self.add_transition(f'ram move 0', Z, Z, l, f'ram back {register_count}')
        self.add_transition(f'ram move 0', B, B, l, f'ram back {register_count}')
        for i in range(register_count):
            self.add_transition(f'ram back {i + 1}', B, B, l, f'ram back {i}')
            self.add_transition(f'ram back {i + 1}', Z, Z, l, f'ram back {i + 1}')
            self.add_transition(f'ram back {i + 1}', O, O, l, f'ram back {i + 1}')
        self.add_transition(f'ram back 0', B, B, r, 'ram read')
        self.add_transition(f'ram back 0', Z, Z, l, f'ram back 0')
        self.add_transition(f'ram back 0', O, O, l, f'ram back 0')

    def write_to_ram_32(self):
        self.add_transition('writeram32', B, B, r, 'writeram32 op1')
        self.add_transition('writeram32 op1', Z, Z, r, 'writeram32 op1')
        self.add_transition('writeram32 op1', O, O, r, 'writeram32 op1')
        self.add_transition('writeram32 op1', B, B, l, 'writeram32 scan 0 0')
        for i in range(32):
            for j in range(i):
                self.add_transition(f'writeram32 scan {i} {j}', Z, Z, l, f'writeram32 scan {i} {j + 1}')
                self.add_transition(f'writeram32 scan {i} {j}', O, O, l, f'writeram32 scan {i} {j + 1}')
            self.add_transition(f'writeram32 scan {i} {i}', O, O, r, f'writeram32 move {i} {register_count - 1} 1')
            self.add_transition(f'writeram32 scan {i} {i}', Z, Z, r, f'writeram32 move {i} {register_count - 1} 0')
            for j in range(register_count):
                self.add_transition(f'writeram32 move {i} {j} 1', O, O, r, f'writeram32 move {i} {j} 1')
                self.add_transition(f'writeram32 move {i} {j} 1', Z, Z, r, f'writeram32 move {i} {j} 1')
                self.add_transition(f'writeram32 move {i} {j + 1} 1', B, B, r, f'writeram32 move {i} {j} 1')
                self.add_transition(f'writeram32 move {i} {j} 0', O, O, r, f'writeram32 move {i} {j} 0')
                self.add_transition(f'writeram32 move {i} {j} 0', Z, Z, r, f'writeram32 move {i} {j} 0')
                self.add_transition(f'writeram32 move {i} {j + 1} 0', B, B, r, f'writeram32 move {i} {j} 0')

                self.add_transition(f'writeram32 back {i} {j}', O, O, l, f'writeram32 back {i} {j}')
                self.add_transition(f'writeram32 back {i} {j}', Z, Z, l, f'writeram32 back {i} {j}')
                self.add_transition(f'writeram32 back {i} {j + 1}', B, B, l, f'writeram32 back {i} {j}')

            self.add_transition(f'writeram32 move {i} 0 0', B, Z, l, f'writeram32 blank {i}')
            self.add_transition(f'writeram32 move {i} 0 1', B, O, l, f'writeram32 blank {i}')

            if i != 31:
                self.add_transition(f'writeram32 back {i} 0', B, B, l, f'writeram32 scan {i + 1} 0')
            else:
                self.add_transition(f'writeram32 back {i} 0', B, B, l, f'ret0')
            self.add_transition(f'writeram32 blank {i}', O, B, l, f'writeram32 back {i} {register_count - 2}')
            self.add_transition(f'writeram32 blank {i}', Z, B, l, f'writeram32 back {i} {register_count - 2}')

    def write_to_ram_16(self):
        self.add_transition('writeram16', B, B, r, 'writeram16 op1')
        self.add_transition('writeram16 op1', Z, Z, r, 'writeram16 op1')
        self.add_transition('writeram16 op1', O, O, r, 'writeram16 op1')
        self.add_transition('writeram16 op1', B, B, l, 'writeram16 scan 0 0')
        for i in range(16):
            for j in range(i):
                self.add_transition(f'writeram16 scan {i} {j}', Z, Z, l, f'writeram16 scan {i} {j + 1}')
                self.add_transition(f'writeram16 scan {i} {j}', O, O, l, f'writeram16 scan {i} {j + 1}')
            self.add_transition(f'writeram16 scan {i} {i}', O, O, r, f'writeram16 move {i} {register_count - 1} 1')
            self.add_transition(f'writeram16 scan {i} {i}', Z, Z, r, f'writeram16 move {i} {register_count - 1} 0')
            for j in range(register_count):
                self.add_transition(f'writeram16 move {i} {j} 1', O, O, r, f'writeram16 move {i} {j} 1')
                self.add_transition(f'writeram16 move {i} {j} 1', Z, Z, r, f'writeram16 move {i} {j} 1')
                self.add_transition(f'writeram16 move {i} {j + 1} 1', B, B, r, f'writeram16 move {i} {j} 1')
                self.add_transition(f'writeram16 move {i} {j} 0', O, O, r, f'writeram16 move {i} {j} 0')
                self.add_transition(f'writeram16 move {i} {j} 0', Z, Z, r, f'writeram16 move {i} {j} 0')
                self.add_transition(f'writeram16 move {i} {j + 1} 0', B, B, r, f'writeram16 move {i} {j} 0')

                self.add_transition(f'writeram16 back {i} {j}', O, O, l, f'writeram16 back {i} {j}')
                self.add_transition(f'writeram16 back {i} {j}', Z, Z, l, f'writeram16 back {i} {j}')
                self.add_transition(f'writeram16 back {i} {j + 1}', B, B, l, f'writeram16 back {i} {j}')

            self.add_transition(f'writeram16 move {i} 0 0', B, Z, l, f'writeram16 blank {i}')
            self.add_transition(f'writeram16 move {i} 0 1', B, O, l, f'writeram16 blank {i}')

            if i != 15:
                self.add_transition(f'writeram16 back {i} 0', B, B, l, f'writeram16 scan {i + 1} 0')
            else:
                self.add_transition(f'writeram16 back {i} 0', B, B, l, f'ret0')
            self.add_transition(f'writeram16 blank {i}', O, B, l, f'writeram16 back {i} {register_count - 2}')
            self.add_transition(f'writeram16 blank {i}', Z, B, l, f'writeram16 back {i} {register_count - 2}')

    def write_to_ram_8(self):
        self.add_transition('writeram8', B, B, r, 'writeram8 op1')
        self.add_transition('writeram8 op1', Z, Z, r, 'writeram8 op1')
        self.add_transition('writeram8 op1', O, O, r, 'writeram8 op1')
        self.add_transition('writeram8 op1', B, B, l, 'writeram8 scan 0 0')
        for i in range(8):
            for j in range(i):
                self.add_transition(f'writeram8 scan {i} {j}', Z, Z, l, f'writeram8 scan {i} {j + 1}')
                self.add_transition(f'writeram8 scan {i} {j}', O, O, l, f'writeram8 scan {i} {j + 1}')
            self.add_transition(f'writeram8 scan {i} {i}', O, O, r, f'writeram8 move {i} {register_count - 1} 1')
            self.add_transition(f'writeram8 scan {i} {i}', Z, Z, r, f'writeram8 move {i} {register_count - 1} 0')
            for j in range(register_count):
                self.add_transition(f'writeram8 move {i} {j} 1', O, O, r, f'writeram8 move {i} {j} 1')
                self.add_transition(f'writeram8 move {i} {j} 1', Z, Z, r, f'writeram8 move {i} {j} 1')
                self.add_transition(f'writeram8 move {i} {j + 1} 1', B, B, r, f'writeram8 move {i} {j} 1')
                self.add_transition(f'writeram8 move {i} {j} 0', O, O, r, f'writeram8 move {i} {j} 0')
                self.add_transition(f'writeram8 move {i} {j} 0', Z, Z, r, f'writeram8 move {i} {j} 0')
                self.add_transition(f'writeram8 move {i} {j + 1} 0', B, B, r, f'writeram8 move {i} {j} 0')

                self.add_transition(f'writeram8 back {i} {j}', O, O, l, f'writeram8 back {i} {j}')
                self.add_transition(f'writeram8 back {i} {j}', Z, Z, l, f'writeram8 back {i} {j}')
                self.add_transition(f'writeram8 back {i} {j + 1}', B, B, l, f'writeram8 back {i} {j}')

            self.add_transition(f'writeram8 move {i} 0 0', B, Z, l, f'writeram8 blank {i}')
            self.add_transition(f'writeram8 move {i} 0 1', B, O, l, f'writeram8 blank {i}')

            if i != 7:
                self.add_transition(f'writeram8 back {i} 0', B, B, l, f'writeram8 scan {i + 1} 0')
            else:
                self.add_transition(f'writeram8 back {i} 0', B, B, l, f'ret0')
            self.add_transition(f'writeram8 blank {i}', O, B, l, f'writeram8 back {i} {register_count - 2}')
            self.add_transition(f'writeram8 blank {i}', Z, B, l, f'writeram8 back {i} {register_count - 2}')

    def read_from_ram_32(self):
        self.add_transition('readram32', B, B, r, 'readram32 move to ram 0 0')
        for i in range(32):
            for j in range(register_count):
                if j != register_count - 1:
                    self.add_transition(f'readram32 move back {i} {j} 0', B, B, l, f'readram32 move back {i} {j + 1} 0')
                    self.add_transition(f'readram32 move back {i} {j} 1', B, B, l, f'readram32 move back {i} {j + 1} 1')
                    self.add_transition(f'readram32 move to ram {i} {j}', B, B, r, f'readram32 move to ram {i} {j + 1}')
                else:
                    self.add_transition(f'readram32 move back {i} {j} 0', B, B, l, f'readram32 write {i} 0 0')
                    self.add_transition(f'readram32 move back {i} {j} 1', B, B, l, f'readram32 write {i} 0 1')
                    self.add_transition(f'readram32 move to ram {i} {j}', B, B, l, f'readram32 read {i}')

                self.add_transition(f'readram32 move to ram {i} {j}', O, O, r, f'readram32 move to ram {i} {j}')
                self.add_transition(f'readram32 move to ram {i} {j}', Z, Z, r, f'readram32 move to ram {i} {j}')

                self.add_transition(f'readram32 move back {i} {j} 0', O, O, l, f'readram32 move back {i} {j} 0')
                self.add_transition(f'readram32 move back {i} {j} 0', Z, Z, l, f'readram32 move back {i} {j} 0')

                self.add_transition(f'readram32 move back {i} {j} 1', O, O, l, f'readram32 move back {i} {j} 1')
                self.add_transition(f'readram32 move back {i} {j} 1', Z, Z, l, f'readram32 move back {i} {j} 1')

            self.add_transition(f'readram32 read {i}', Z, B, r, f'readram32 rewrite {i} 0')
            self.add_transition(f'readram32 read {i}', O, B, r, f'readram32 rewrite {i} 1')
            self.add_transition(f'readram32 rewrite {i} 0', B, Z, l, f'readram32 move back {i} 0 0')
            self.add_transition(f'readram32 rewrite {i} 1', B, O, l, f'readram32 move back {i} 0 1')

            for j in range(i):
                self.add_transition(f'readram32 write {i} {j} 0', O, O, l, f'readram32 write {i} {j + 1} 0')
                self.add_transition(f'readram32 write {i} {j} 0', Z, Z, l, f'readram32 write {i} {j + 1} 0')
                self.add_transition(f'readram32 write {i} {j} 1', O, O, l, f'readram32 write {i} {j + 1} 1')
                self.add_transition(f'readram32 write {i} {j} 1', Z, Z, l, f'readram32 write {i} {j + 1} 1')

            if i != 31:
                self.add_transition(f'readram32 write {i} {i} 0', Z, Z, r, f'readram32 move to ram {i + 1} 0')
                self.add_transition(f'readram32 write {i} {i} 0', O, Z, r, f'readram32 move to ram {i + 1} 0')
                self.add_transition(f'readram32 write {i} {i} 1', Z, O, r, f'readram32 move to ram {i + 1} 0')
                self.add_transition(f'readram32 write {i} {i} 1', O, O, r, f'readram32 move to ram {i + 1} 0')
            else:
                self.add_transition(f'readram32 write {i} {i} 0', Z, Z, l, f'ret0')
                self.add_transition(f'readram32 write {i} {i} 0', O, Z, l, f'ret0')
                self.add_transition(f'readram32 write {i} {i} 1', Z, O, l, f'ret0')
                self.add_transition(f'readram32 write {i} {i} 1', O, O, l, f'ret0')

    def read_from_ram_16u(self):
        self.add_transition('readram16u', B, B, r, 'readram16u move to ram 0 0')
        for i in range(16):
            for j in range(register_count):
                if j != register_count - 1:
                    self.add_transition(f'readram16u move back {i} {j} 0', B, B, l,
                                        f'readram16u move back {i} {j + 1} 0')
                    self.add_transition(f'readram16u move back {i} {j} 1', B, B, l,
                                        f'readram16u move back {i} {j + 1} 1')
                    self.add_transition(f'readram16u move to ram {i} {j}', B, B, r,
                                        f'readram16u move to ram {i} {j + 1}')
                else:
                    self.add_transition(f'readram16u move back {i} {j} 0', B, B, l, f'readram16u write {i} 0 0')
                    self.add_transition(f'readram16u move back {i} {j} 1', B, B, l, f'readram16u write {i} 0 1')
                    self.add_transition(f'readram16u move to ram {i} {j}', B, B, l, f'readram16u read {i}')

                self.add_transition(f'readram16u move to ram {i} {j}', O, O, r, f'readram16u move to ram {i} {j}')
                self.add_transition(f'readram16u move to ram {i} {j}', Z, Z, r, f'readram16u move to ram {i} {j}')

                self.add_transition(f'readram16u move back {i} {j} 0', O, O, l, f'readram16u move back {i} {j} 0')
                self.add_transition(f'readram16u move back {i} {j} 0', Z, Z, l, f'readram16u move back {i} {j} 0')

                self.add_transition(f'readram16u move back {i} {j} 1', O, O, l, f'readram16u move back {i} {j} 1')
                self.add_transition(f'readram16u move back {i} {j} 1', Z, Z, l, f'readram16u move back {i} {j} 1')

            self.add_transition(f'readram16u read {i}', Z, B, r, f'readram16u rewrite {i} 0')
            self.add_transition(f'readram16u read {i}', O, B, r, f'readram16u rewrite {i} 1')
            self.add_transition(f'readram16u rewrite {i} 0', B, Z, l, f'readram16u move back {i} 0 0')
            self.add_transition(f'readram16u rewrite {i} 1', B, O, l, f'readram16u move back {i} 0 1')

            for j in range(i):
                self.add_transition(f'readram16u write {i} {j} 0', O, O, l, f'readram16u write {i} {j + 1} 0')
                self.add_transition(f'readram16u write {i} {j} 0', Z, Z, l, f'readram16u write {i} {j + 1} 0')
                self.add_transition(f'readram16u write {i} {j} 1', O, O, l, f'readram16u write {i} {j + 1} 1')
                self.add_transition(f'readram16u write {i} {j} 1', Z, Z, l, f'readram16u write {i} {j + 1} 1')

            if i != 15:
                self.add_transition(f'readram16u write {i} {i} 0', Z, Z, r, f'readram16u move to ram {i + 1} 0')
                self.add_transition(f'readram16u write {i} {i} 0', O, Z, r, f'readram16u move to ram {i + 1} 0')
                self.add_transition(f'readram16u write {i} {i} 1', Z, O, r, f'readram16u move to ram {i + 1} 0')
                self.add_transition(f'readram16u write {i} {i} 1', O, O, r, f'readram16u move to ram {i + 1} 0')
            else:
                self.add_transition(f'readram16u write {i} {i} 0', Z, Z, l, f'readram16 extend 0')
                self.add_transition(f'readram16u write {i} {i} 0', O, Z, l, f'readram16 extend 0')
                self.add_transition(f'readram16u write {i} {i} 1', Z, O, l, f'readram16 extend 0')
                self.add_transition(f'readram16u write {i} {i} 1', O, O, l, f'readram16 extend 0')

    def read_from_ram_8u(self):
        self.add_transition('readram8u', B, B, r, 'readram8u move to ram 0 0')
        for i in range(8):
            for j in range(register_count):
                if j != register_count - 1:
                    self.add_transition(f'readram8u move back {i} {j} 0', B, B, l,
                                        f'readram8u move back {i} {j + 1} 0')
                    self.add_transition(f'readram8u move back {i} {j} 1', B, B, l,
                                        f'readram8u move back {i} {j + 1} 1')
                    self.add_transition(f'readram8u move to ram {i} {j}', B, B, r,
                                        f'readram8u move to ram {i} {j + 1}')
                else:
                    self.add_transition(f'readram8u move back {i} {j} 0', B, B, l, f'readram8u write {i} 0 0')
                    self.add_transition(f'readram8u move back {i} {j} 1', B, B, l, f'readram8u write {i} 0 1')
                    self.add_transition(f'readram8u move to ram {i} {j}', B, B, l, f'readram8u read {i}')

                self.add_transition(f'readram8u move to ram {i} {j}', O, O, r, f'readram8u move to ram {i} {j}')
                self.add_transition(f'readram8u move to ram {i} {j}', Z, Z, r, f'readram8u move to ram {i} {j}')

                self.add_transition(f'readram8u move back {i} {j} 0', O, O, l, f'readram8u move back {i} {j} 0')
                self.add_transition(f'readram8u move back {i} {j} 0', Z, Z, l, f'readram8u move back {i} {j} 0')

                self.add_transition(f'readram8u move back {i} {j} 1', O, O, l, f'readram8u move back {i} {j} 1')
                self.add_transition(f'readram8u move back {i} {j} 1', Z, Z, l, f'readram8u move back {i} {j} 1')

            self.add_transition(f'readram8u read {i}', Z, B, r, f'readram8u rewrite {i} 0')
            self.add_transition(f'readram8u read {i}', O, B, r, f'readram8u rewrite {i} 1')
            self.add_transition(f'readram8u rewrite {i} 0', B, Z, l, f'readram8u move back {i} 0 0')
            self.add_transition(f'readram8u rewrite {i} 1', B, O, l, f'readram8u move back {i} 0 1')

            for j in range(i):
                self.add_transition(f'readram8u write {i} {j} 0', O, O, l, f'readram8u write {i} {j + 1} 0')
                self.add_transition(f'readram8u write {i} {j} 0', Z, Z, l, f'readram8u write {i} {j + 1} 0')
                self.add_transition(f'readram8u write {i} {j} 1', O, O, l, f'readram8u write {i} {j + 1} 1')
                self.add_transition(f'readram8u write {i} {j} 1', Z, Z, l, f'readram8u write {i} {j + 1} 1')

            if i != 7:
                self.add_transition(f'readram8u write {i} {i} 0', Z, Z, r, f'readram8u move to ram {i + 1} 0')
                self.add_transition(f'readram8u write {i} {i} 0', O, Z, r, f'readram8u move to ram {i + 1} 0')
                self.add_transition(f'readram8u write {i} {i} 1', Z, O, r, f'readram8u move to ram {i + 1} 0')
                self.add_transition(f'readram8u write {i} {i} 1', O, O, r, f'readram8u move to ram {i + 1} 0')
            else:
                self.add_transition(f'readram8u write {i} {i} 0', Z, Z, l, f'readram8 extend 0')
                self.add_transition(f'readram8u write {i} {i} 0', O, Z, l, f'readram8 extend 0')
                self.add_transition(f'readram8u write {i} {i} 1', Z, O, l, f'readram8 extend 0')
                self.add_transition(f'readram8u write {i} {i} 1', O, O, l, f'readram8 extend 0')

    def read_from_ram_16(self):
        self.add_transition('readram16', B, B, r, 'readram16 move to ram 0 0')
        for i in range(16):
            for j in range(register_count):
                if j != register_count - 1:
                    self.add_transition(f'readram16 move back {i} {j} 0', B, B, l,
                                        f'readram16 move back {i} {j + 1} 0')
                    self.add_transition(f'readram16 move back {i} {j} 1', B, B, l,
                                        f'readram16 move back {i} {j + 1} 1')
                    self.add_transition(f'readram16 move to ram {i} {j}', B, B, r,
                                        f'readram16 move to ram {i} {j + 1}')
                else:
                    self.add_transition(f'readram16 move back {i} {j} 0', B, B, l, f'readram16 write {i} 0 0')
                    self.add_transition(f'readram16 move back {i} {j} 1', B, B, l, f'readram16 write {i} 0 1')
                    self.add_transition(f'readram16 move to ram {i} {j}', B, B, l, f'readram16 read {i}')

                self.add_transition(f'readram16 move to ram {i} {j}', O, O, r, f'readram16 move to ram {i} {j}')
                self.add_transition(f'readram16 move to ram {i} {j}', Z, Z, r, f'readram16 move to ram {i} {j}')

                self.add_transition(f'readram16 move back {i} {j} 0', O, O, l, f'readram16 move back {i} {j} 0')
                self.add_transition(f'readram16 move back {i} {j} 0', Z, Z, l, f'readram16 move back {i} {j} 0')

                self.add_transition(f'readram16 move back {i} {j} 1', O, O, l, f'readram16 move back {i} {j} 1')
                self.add_transition(f'readram16 move back {i} {j} 1', Z, Z, l, f'readram16 move back {i} {j} 1')

            self.add_transition(f'readram16 read {i}', Z, B, r, f'readram16 rewrite {i} 0')
            self.add_transition(f'readram16 read {i}', O, B, r, f'readram16 rewrite {i} 1')
            self.add_transition(f'readram16 rewrite {i} 0', B, Z, l, f'readram16 move back {i} 0 0')
            self.add_transition(f'readram16 rewrite {i} 1', B, O, l, f'readram16 move back {i} 0 1')

            for j in range(i):
                self.add_transition(f'readram16 write {i} {j} 0', O, O, l, f'readram16 write {i} {j + 1} 0')
                self.add_transition(f'readram16 write {i} {j} 0', Z, Z, l, f'readram16 write {i} {j + 1} 0')
                self.add_transition(f'readram16 write {i} {j} 1', O, O, l, f'readram16 write {i} {j + 1} 1')
                self.add_transition(f'readram16 write {i} {j} 1', Z, Z, l, f'readram16 write {i} {j + 1} 1')

            if i != 15:
                self.add_transition(f'readram16 write {i} {i} 0', Z, Z, r, f'readram16 move to ram {i + 1} 0')
                self.add_transition(f'readram16 write {i} {i} 0', O, Z, r, f'readram16 move to ram {i + 1} 0')
                self.add_transition(f'readram16 write {i} {i} 1', Z, O, r, f'readram16 move to ram {i + 1} 0')
                self.add_transition(f'readram16 write {i} {i} 1', O, O, r, f'readram16 move to ram {i + 1} 0')
            else:
                self.add_transition(f'readram16 write {i} {i} 0', Z, Z, l, f'readram16 extend 0')
                self.add_transition(f'readram16 write {i} {i} 0', O, Z, l, f'readram16 extend 0')
                self.add_transition(f'readram16 write {i} {i} 1', Z, O, l, f'readram16 extend 1')
                self.add_transition(f'readram16 write {i} {i} 1', O, O, l, f'readram16 extend 1')
        self.add_transition(f'readram16 extend 0', O, Z, l, f'readram16 extend 0')
        self.add_transition(f'readram16 extend 0', Z, Z, l, f'readram16 extend 0')
        self.add_transition(f'readram16 extend 0', B, B, l, f'ret0')
        self.add_transition(f'readram16 extend 1', O, O, l, f'readram16 extend 1')
        self.add_transition(f'readram16 extend 1', Z, O, l, f'readram16 extend 1')
        self.add_transition(f'readram16 extend 1', B, B, l, f'ret0')

    def read_from_ram_8(self):
        self.add_transition('readram8', B, B, r, 'readram8 move to ram 0 0')
        for i in range(8):
            for j in range(register_count):
                if j != register_count - 1:
                    self.add_transition(f'readram8 move back {i} {j} 0', B, B, l,
                                        f'readram8 move back {i} {j + 1} 0')
                    self.add_transition(f'readram8 move back {i} {j} 1', B, B, l,
                                        f'readram8 move back {i} {j + 1} 1')
                    self.add_transition(f'readram8 move to ram {i} {j}', B, B, r,
                                        f'readram8 move to ram {i} {j + 1}')
                else:
                    self.add_transition(f'readram8 move back {i} {j} 0', B, B, l, f'readram8 write {i} 0 0')
                    self.add_transition(f'readram8 move back {i} {j} 1', B, B, l, f'readram8 write {i} 0 1')
                    self.add_transition(f'readram8 move to ram {i} {j}', B, B, l, f'readram8 read {i}')

                self.add_transition(f'readram8 move to ram {i} {j}', O, O, r, f'readram8 move to ram {i} {j}')
                self.add_transition(f'readram8 move to ram {i} {j}', Z, Z, r, f'readram8 move to ram {i} {j}')

                self.add_transition(f'readram8 move back {i} {j} 0', O, O, l, f'readram8 move back {i} {j} 0')
                self.add_transition(f'readram8 move back {i} {j} 0', Z, Z, l, f'readram8 move back {i} {j} 0')

                self.add_transition(f'readram8 move back {i} {j} 1', O, O, l, f'readram8 move back {i} {j} 1')
                self.add_transition(f'readram8 move back {i} {j} 1', Z, Z, l, f'readram8 move back {i} {j} 1')

            self.add_transition(f'readram8 read {i}', Z, B, r, f'readram8 rewrite {i} 0')
            self.add_transition(f'readram8 read {i}', O, B, r, f'readram8 rewrite {i} 1')
            self.add_transition(f'readram8 rewrite {i} 0', B, Z, l, f'readram8 move back {i} 0 0')
            self.add_transition(f'readram8 rewrite {i} 1', B, O, l, f'readram8 move back {i} 0 1')

            for j in range(i):
                self.add_transition(f'readram8 write {i} {j} 0', O, O, l, f'readram8 write {i} {j + 1} 0')
                self.add_transition(f'readram8 write {i} {j} 0', Z, Z, l, f'readram8 write {i} {j + 1} 0')
                self.add_transition(f'readram8 write {i} {j} 1', O, O, l, f'readram8 write {i} {j + 1} 1')
                self.add_transition(f'readram8 write {i} {j} 1', Z, Z, l, f'readram8 write {i} {j + 1} 1')

            if i != 7:
                self.add_transition(f'readram8 write {i} {i} 0', Z, Z, r, f'readram8 move to ram {i + 1} 0')
                self.add_transition(f'readram8 write {i} {i} 0', O, Z, r, f'readram8 move to ram {i + 1} 0')
                self.add_transition(f'readram8 write {i} {i} 1', Z, O, r, f'readram8 move to ram {i + 1} 0')
                self.add_transition(f'readram8 write {i} {i} 1', O, O, r, f'readram8 move to ram {i + 1} 0')
            else:
                self.add_transition(f'readram8 write {i} {i} 0', Z, Z, l, f'readram8 extend 0')
                self.add_transition(f'readram8 write {i} {i} 0', O, Z, l, f'readram8 extend 0')
                self.add_transition(f'readram8 write {i} {i} 1', Z, O, l, f'readram8 extend 1')
                self.add_transition(f'readram8 write {i} {i} 1', O, O, l, f'readram8 extend 1')
        self.add_transition(f'readram8 extend 0', O, Z, l, f'readram8 extend 0')
        self.add_transition(f'readram8 extend 0', Z, Z, l, f'readram8 extend 0')
        self.add_transition(f'readram8 extend 0', B, B, l, f'ret0')
        self.add_transition(f'readram8 extend 1', O, O, l, f'readram8 extend 1')
        self.add_transition(f'readram8 extend 1', Z, O, l, f'readram8 extend 1')
        self.add_transition(f'readram8 extend 1', B, B, l, f'ret0')
    def reset_ram(self):
        self.add_transition('reset ram', B, B, r, 'reset ram 0')
        for i in range(register_count):
            if i != register_count - 1:
                self.add_transition(f'reset ram {i}', B, B, r, f'reset ram {i + 1}')
            else:
                self.add_transition(f'reset ram {i}', B, B, l, f'reset ram read')
            self.add_transition(f'reset ram {i}', Z, Z, r, f'reset ram {i}')
            self.add_transition(f'reset ram {i}', O, O, r, f'reset ram {i}')
        self.add_transition(f'reset ram read', O, B, r, f'reset ram write 1')
        self.add_transition(f'reset ram read', Z, B, r, f'reset ram write 0')
        self.add_transition(f'reset ram read', B, B, r, f'ret0')
        self.add_transition(f'reset ram write 1', B, O, l, f'reset ram skip')
        self.add_transition(f'reset ram write 0', B, Z, l, f'reset ram skip')
        self.add_transition(f'reset ram skip', B, B, l, f'reset ram read')


tm = TuringMachine()
tm.set_up_alphabet()
tm.set_up_hardware()

tm.implement_ret()
tm.implement_chgmde()
tm.implement_mov()
tm.implement_mov_rel()

tm.implement_add()
tm.implement_sub()
tm.implement_xor()
tm.implement_or()
tm.implement_and()
tm.implement_shift()

tm.implement_advance_pc()
tm.implement_retract_pc()
tm.implement_fetch_subins()

tm.implement_decode()
tm.implement_decode_arimm()
tm.implement_decode_arith()
tm.implement_decode_load()
tm.implement_decode_store()
tm.implement_decode_branch()

tm.implement_scan_rs1()
tm.implement_scan_rs2()
tm.implement_scan_rd()

tm.get_imms()
tm.get_immb()

tm.implement_ram()
tm.write_to_ram_32()
tm.write_to_ram_16()
tm.write_to_ram_8()
tm.read_from_ram_32()
tm.read_from_ram_16()
tm.read_from_ram_16u()
tm.read_from_ram_8()
tm.read_from_ram_8u()
tm.reset_ram()
# tm.implement_scan_skip()
fetch = """
||fetch:
    jmpsign
    advance_pc
    set4op2
    sub
    move 0 into sc
    retract_pc
    set4op2
    add
    move 0 into sc
    mov from x0 to x5 init0
    chgmde0
||execute add:
    scan from rs2
    scan from rs1
    add
    scan to rd
    set4op1
    mov from x4 to x3 init0
    add
    mov from x2 to x4 init0
    set4op1
    chgmde0
||execute addi:
    mov from x0 to x2 init0
    set20op2
    sra
    scan from rs1
    add
    scan to rd
    set4op1
    mov from x4 to x3 init0
    add
    mov from x2 to x4 init0
    set4op1
    chgmde0
||execute sw:
    mov from x0 to x2 init0
    get imms
    set20op2
    sra
    scan from rs1
    add
    ram
    scan from rs2
    writeram32
    reset ram
    set4op1
    mov from x4 to x3 init0
    add
    mov from x2 to x4 init0
    set4op1
    chgmde0
||execute sh:
    mov from x0 to x2 init0
    get imms
    set20op2
    sra
    scan from rs1
    add
    ram
    scan from rs2
    writeram16
    reset ram
    set4op1
    mov from x4 to x3 init0
    add
    mov from x2 to x4 init0
    set4op1
    chgmde0
||execute sb:
    mov from x0 to x2 init0
    get imms
    set20op2
    sra
    scan from rs1
    add
    ram
    scan from rs2
    writeram8
    reset ram
    set4op1
    mov from x4 to x3 init0
    add
    mov from x2 to x4 init0
    set4op1
    chgmde0
||execute lw:
    mov from x0 to x2 init0
    set20op2
    sra
    scan from rs1
    add
    ram
    readram32
    scan to rd
    reset ram
    set4op1
    mov from x4 to x3 init0
    add
    mov from x2 to x4 init0
    set4op1
    chgmde0    
||execute lhu:
    mov from x0 to x2 init0
    set20op2
    sra
    scan from rs1
    add
    ram
    readram16u
    scan to rd
    reset ram
    set4op1
    mov from x4 to x3 init0
    add
    mov from x2 to x4 init0
    set4op1
    chgmde0    
||execute lh:
    mov from x0 to x2 init0
    set20op2
    sra
    scan from rs1
    add
    ram
    readram16
    scan to rd
    reset ram
    set4op1
    mov from x4 to x3 init0
    add
    mov from x2 to x4 init0
    set4op1
    chgmde0    
||execute lb:
    mov from x0 to x2 init0
    set20op2
    sra
    scan from rs1
    add
    ram
    readram8
    scan to rd
    reset ram
    set4op1
    mov from x4 to x3 init0
    add
    mov from x2 to x4 init0
    set4op1
    chgmde0 
||execute lbu:
    mov from x0 to x2 init0
    set20op2
    sra
    scan from rs1
    add
    ram
    readram8u
    scan to rd
    reset ram
    set4op1
    mov from x4 to x3 init0
    add
    mov from x2 to x4 init0
    set4op1
    chgmde0
||execute bgeu:
    scan from rs1
    scan from rs2
    sub
    sgnchk
    mov from x0 to x2 init0
    get imms
    set20op2
    sra
    get immb
    
    set4op1
"""

tm.compile_function(fetch)

print(len(tm.transitions))
code = ['fe010113', '00112e23', '00812c23', '02010413', 'f0100793', 'fef41623', 'fec44703', '00100793', '00e7f663', '00100793', '0080006f', '00000793', '00078513', '01c12083', '01812403', '02010113', '00008067']
for c in code:
    tm.tape += (['0'] * 32 + [c for c in bin(int(c, 16))[2:]])[-32:]
tm.run_machine()
