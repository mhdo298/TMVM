# Transition macros
Here are some common patterns used by the machine to do things:
## `seek_l2r_{target}_`
- `seek_l2r_{target}_{current}, {c} -> , R, seek_l2r_{target}_{current[-len(target) + 1:] + c}`
- `seek_l2r_{target}_{target}, {c} -> , R, {next_state}`

## `seek_r2l_{target}_`
- `seek_r2l_{target}_{current}, {c} -> , L, seek_r2l_{target}_{c + current[: len(target) - 1]}`
- `seek_r2l_{target}_{target}, {c} -> , L, {next_state}`

