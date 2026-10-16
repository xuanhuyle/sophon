# Scores (mechanical, second pass)

Protocol c87df4b773045f3b…. Exact counts; rows in scores.json. First pass kept in SCORES_firstpass.md.

## Change tasks

| task | arm | changed articles hit | IR strict (flagged/needs-review/den) | FS strict (high) | IR refined (flagged/needs-review/den) | FS refined (high) | over-flag | TC (correct / incorrect / not transposed / replay failed) | quotes not found / cited | build ok | tool calls |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1a | A | 2/2 | 4/4/9 | 1 (1) | 4/4/8 | 0 (0) | 0 | 0 / 0 / 9 / 0 | 0/36 | True | 25 |
| T1a | B | 2/2 | 0/8/9 | 1 (0) | 0/8/8 | 0 (0) | 1 | 0 / 0 / 9 / 0 | 0/11 | True | 22 |
| T1b | A | 5/5 | 9/0/11 | 2 (2) | 9/0/10 | 1 (1) | 11 | 7 / 0 / 0 / 0 | 0/34 | True | 27 |
| T1b | B | 5/5 | 9/1/11 | 1 (1) | 9/1/10 | 0 (0) | 13 | 7 / 0 / 0 / 0 | 0/20 | True | 25 |
| M0 | A | 0/0 | 0/0/0 | 0 (0) | 0/0/0 | 0 (0) | 0 | 0 / 0 / 0 / 0 | 1/45 | True | 32 |
| M0 | B | 0/0 | 0/0/0 | 0 (0) | 0/0/0 | 0 (0) | 8 | 0 / 0 / 0 / 0 | 0/48 | True | 27 |
| M1 | A | 2/2 | 20/0/21 | 1 (1) | 20/0/20 | 0 (0) | 10 | 21 / 0 / 0 / 0 | 0/0 | True | 32 |
| M1 | B | 2/2 | 20/0/21 | 1 (1) | 20/0/20 | 0 (0) | 34 | 21 / 0 / 0 / 0 | 0/282 | True | 32 |
| M2 | A | 1/1 | 7/0/9 | 2 (2) | 7/0/7 | 0 (0) | 6 | 1 / 0 / 0 / 0 | 0/0 | True | 43 |
| M2 | B | 1/1 | 7/1/9 | 1 (1) | 7/0/7 | 0 (0) | 11 | 1 / 0 / 0 / 0 | 0/0 | True | 39 |

## Reverse checks

| task | arm | label (confidence) | acceptable | CFC | quotes not found / cited | tool calls |
|---|---|---|---|---|---|---|
| R1 | A | HARMLESS_REFACTOR (high) | yes | 0 | 0/1 | 16 |
| R1 | B | HARMLESS_REFACTOR (high) | yes | 0 | 0/2 | 20 |
| R2 | A | HARMLESS_REFACTOR (high) | yes | 0 | 0/4 | 25 |
| R2 | B | HARMLESS_REFACTOR (high) | yes | 0 | 0/3 | 26 |
| R3 | A | MISMATCH (high) | yes | 0 | 0/8 | 27 |
| R3 | B | MISMATCH (high) | yes | 0 | 0/10 | 24 |
| R4 | A | LEGITIMATE_INDEPENDENT_CHANGE (medium) | yes | 0 | 0/4 | 35 |
| R4 | B | LEGITIMATE_INDEPENDENT_CHANGE (high) | yes | 0 | 0/2 | 36 |
| R5 | A | UNRESOLVED (medium) | yes | 0 | 0/5 | 21 |
| R5 | B | UNRESOLVED (medium) | yes | 0 | 0/6 | 24 |

## Initial binding (T0)

| arm | links | by status | VERIFIED checks hold / fail on replay | expected rule families bound | quotes not found / cited | approvals claimed | tool calls |
|---|---|---|---|---|---|---|---|
| A | 34 | {'INFERRED': 5, 'VERIFIED': 26, 'UNKNOWN': 3} | 25 / 1 | 8/9 | 0/34 | ['none recorded'] | 31 |
| B | 55 | {'VERIFIED': 34, 'FAILED': 3, 'UNKNOWN': 8, 'INFERRED': 10} | 34 / 0 | 9/9 | 0/55 | ['none recorded'] | 26 |
