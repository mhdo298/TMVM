S = "||start"
A = "||end"
R = "REJECT"


class TuringMachine:
    def __init__(self):
        self.transitions = {}
        self.alphabet = {'0', '1', 'B'}

    def add_transition(self, current, read, write, direction, next_state):
        if read not in self.alphabet or write not in self.alphabet or direction not in 'LR':
            raise ValueError(f"{read} or {write} not in the alphabet!")
        self.transitions[(current, read)] = (write, 1 if direction == 'R' else -1, next_state)


class Runner:
    def __init__(self, tm: TuringMachine, tape=None):
        self.tm = tm
        self.current = S
        self.cursor = 0
        self.tape = [] if tape is None else [c for c in tape] if type(tape) is str else tape

    def print(self):
        if self.cursor >= len(self.tape):
            self.tape += ['B'] * 1000
        print(self.current, self.tape[self.cursor])
        tape = ''.join(self.tape).replace('B', '.').rstrip('.')
        tape = (tape[:self.cursor] + '|' + tape[self.cursor:]).rstrip('B')
        print(tape)

    def one_step(self):
        if self.cursor == -1:
            return 'HIT WALL'
        if self.cursor == R:
            return 'REJECT'
        if self.current == A:
            return 'ACCEPT'
        if self.cursor >= len(self.tape):
            self.tape += ['B'] * 1000
        print((self.current, self.tape[self.cursor]))
        if (self.current, self.tape[self.cursor]) not in self.tm.transitions:
            return 'NO TRANSITION'
        write, direction, next_state = self.tm.transitions[(self.current, self.tape[self.cursor])]
        self.tape[self.cursor] = write
        self.current = next_state
        self.cursor += direction
        return 'CONTINUE'

    def run(self):
        while self.one_step() == 'CONTINUE':
            self.print()
        print(self.one_step())
        self.print()