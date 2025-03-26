# Pipeline stages

## fetch

7.`SUB`
   - `reset_{a3}`
   - `read_{a3}_8`
     - If `1_{value}` then do `write_{a2}_{value}`.
     - Else change to step 3 and do `write_{a2}_{value}`