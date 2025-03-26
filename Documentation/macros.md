# Macros

## `mov_{r1}_{r2}_{l1}_{h1}_{l2}`
- `mov_end_pointer_{r1}_{l1}`
- `mov_start_pointer_{r1}_{h1}`
- `mov_end_pointer_{r2}_{l2}`
- `read_{r1}`
  - If `1_{value}` then `write_{r2}_{value}`.
  - If `0_{value}` then `write_{r2}_{value}` and next step.
- `reset_{r1}`
- `reset_{r2}`

## `mov_stack_to_pc`
- `mov_{mp}_{a1}_{0}_{0}_{0}`
- `mov_{pc}_{a2}_{0}_{0}_{0}`
- `SUB`
- `write_{a1}_{32}`
- `mov_{a3}_{a2}_{0}_{0}_{0}` <- loop
- `mov_end_pointer_{a2}_{31}`
- `read_{a2}`
  - If `1_{value}`:
    - `reset_{a2}`
    - `SUB`
  - If `0_{value}`:
    - `reset_{a2}`
    - `ADD`
  