import re

from turingmachine import TuringMachine, Runner


def compile_step(name, alias: dict, code: str):
    indent = "    "
    non_blanks = {'0', '1'}
    compiled_code = f"def {name}(tm):\n"
    for line in code.splitlines():
        if line.strip().startswith('|'):
            spaces, expression = line.split('|')
            current, transition = expression.split('->')
            current_state, read = [token.strip() for token in current.split(',')]
            current_state = f'{name}||{current_state}' if '||' not in current_state else current_state
            write, direction, next_state = [token.strip() for token in transition.split(',')]
            next_state = f'{name}||{next_state}' if '||' not in next_state else next_state
            if current_state in alias:
                current_state = alias[current_state]
            if next_state in alias:
                next_state = alias[next_state]
            compiled = f"""{spaces}tm.add_transition(f'{current_state}', f'{read}', f'{write}', f'{direction}', f'{next_state}')"""
            if '{w}' in current_state:
                compiled = f"""{spaces}for w in {non_blanks}:\n""" + '\n'.join(
                    [indent + line for line in compiled.splitlines()])
            if read == '{r}':
                compiled = f"""{spaces}for r in {non_blanks}:\n""" + '\n'.join(
                    [indent + line for line in compiled.splitlines()])
            compiled_code += compiled + '\n'
        else:
            compiled_code += line + '\n'
    compiled_code += f'{name}(tm)'
    return compiled_code


def parse_code(code: str, hook: str):
    # Matches anything starting with 'step <name>:' and ending with 'end'
    alias = {}
    for line in hook.strip().splitlines():
        c, n = [token.strip() for token in line.split('->')]
        alias[f'{c}||end'] = f'{c}||->||{n}' if n != '' else f'||end'
        alias[f'{n}||start'] = f'{c}||->||{n}' if c != '' else f'||start'
    print(alias)
    pattern = re.compile(r'step (.*?):\n(.*?)\ndone\n', re.DOTALL)
    results = re.findall(pattern, code)
    compiled = [compile_step(result[0], alias, result[1]) for result in results]

    return compiled


def compile_tm(code: str, hook: str, config: str, tm=None):
    if tm is None:
        tm = TuringMachine()

    compiled_code = parse_code(code, hook)
    context = {'tm': tm}
    exec(config, context)
    for snippet in compiled_code:
        print(snippet)
        exec(snippet, dict(context))
    return tm


def compile_from_file(filename: str, tm=None):
    with open(filename, 'r') as f:
        section = [""] * 3
        current = -1
        for line in f.readlines():
            if line.strip() == 'config:':
                current = 2
            elif line.strip() == 'code:':
                current = 0
            elif line.strip() == 'hook:':
                current = 1
            else:
                section[current] += line
    return compile_tm(section[0], section[1], section[2], tm)


tm = compile_from_file('lower_level/hardware.tm')
print(tm.transitions)
runner = Runner(tm, '0' * 32)
runner.run()
