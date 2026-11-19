# Error log spreadsheet

Read this when building `achados.json` (the findings file). The format of each field is in the header of `scripts/error_log.py`. The JSON keys are the ones the script reads (`erros` for errors, `nao_corrigidos` for not fixed, `padroes` for standards, and so on), so keep them as written there.

## Tabs

Three tabs, in the format the project already uses:

| Tab | Columns |
|---|---|
| `Errors v<N>` | ID, Slide, Category, Item, Current, Should be, Priority, Fixed, Note |
| `Not fixed` | ID, Slide, Category, Item, Priority, Reason, Detail |
| `Standards` | Dimension, Element, Standard, Note |

`Fixed` records in which version of the deck the fix went in, as `Yes (<name of the corrected version>)`.

## Reason, in the not-fixed tab

It translates what happened to the item after the conversation in step 4. The script validates the reason against a fixed taxonomy (the `MOTIVOS` set in `error_log.py`), so write the value exactly as in the third column; the second column is only its meaning. To use labels in another language, change the set in the script and this table together.

| Situation | Reason (meaning) | Value in the JSON |
|---|---|---|
| Marked as doubt and not resolved | Doubt | `Dúvida` |
| User said not to fix | User decision | `Decisão do usuário` |
| Fixed, but reverted for breaking the layout | Breaks layout/design | `Desconfigura layout/design` |
| Investigated and was not an error | Not an error (reclassified) | `Não é erro (reclassificado)` |
| Depends on information nobody has yet | Pending decision | `Decisão pendente` |
| Fix possible, but with disproportionate risk | High risk / low benefit | `Risco alto / benefício baixo` |

Include the reclassifications in the `Standards` tab, so the next review does not raise the same false positive.
