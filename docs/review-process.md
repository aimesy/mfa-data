# Review process

## Why the whole cohort was reviewed again

The input to this release was 3,373 fee-collection observations that had already passed every mechanical validation check in the research project that collected them. None had ever been accepted for publication. A mechanical pass establishes that a stored value is internally consistent with the record around it. It does not establish that the value was read from the right cell, that the printed label means what the measure name implies, that the fiscal year on the record matches the column the number is printed in, or that the source itself is free of defects.

Every one of the 3,373 was therefore given a fresh decision here, recorded row by row.

## What a reviewer actually looked at

For each of the 189 distinct source pages behind published figures, the release built a **review sheet**: the untouched original page on the left, the same page with every cohort figure on it individually outlined and numbered on the right, and beneath them a numbered zoomed crop of each outlined cell wide enough to show its row label and its column. The reviewer read each sheet and confirmed, figure by figure, that the outline sat on the intended row of the intended column.

That is also how the substantive findings surfaced. Reading the pages rather than the records is what produced:

- the City of Sacramento footnotes that establish those reports are on the **cash basis**, which the inherited records had as "not stated"
- the footnote attaching only to the NNFP Reg Park Land Acquisition row, stating its revenue **includes $846k of property sales proceeds**
- the negative `(531,574)` on the one Sacramento row the report marks net of refund
- the printed row label "**Fees Collected & Other**" on the City of Rialto table, which combines fees with other revenue
- the fund names that the inherited records said were "not established" but which the City of St. Helena, the City of Garden Grove, the City of Arcadia and the City of Paso Robles all print plainly
- the duplicated fiscal-year label in the City of Arcadia's Exhibit A
- the City of San Leandro figure recorded under 2024-25 that is printed in the FY 20-21 column
- the audited-statement page whose line-item captions sit on the facing page, so the cited page carries no readable row label
- the Georgetown Fire Protection District form completed **by hand**, which is why its page has no text layer at all

## Two independent passes

The primary review proposed each decision from the source and recorded the reading. An **independent review** then re-derived every published value from the published artefacts alone: it re-opened each published outlined PDF, re-extracted the text inside the recorded outline rectangle, and compared it with the published `value_usd` and `source_value_text`, without consulting the primary reviewer's notes. It also re-hashed every published file against the manifest, checked that every provenance link in the data resolves to a file that exists in the repository, confirmed that the three stronger tables are empty, and scanned every published file for private paths and operational identifiers.

Its result is in [`validation/independent-review.json`](../validation/independent-review.json).

## Refusals

A row that could not clear the bar was refused with a reason naming its own source, page and defect. Refusals were never applied in bulk to clear a backlog: the 2,974 rows that share a single structural ground each carry their own reason text naming the district, the fiscal year and the exact record locator that identifies that row in the preserved payload.

No refused amount is published anywhere in this repository, including in the refusal summary.

## Holds inherited from earlier work

An earlier release lane placed a strict hold on one inherited highlighted-PDF derivative because of duplicate destination definitions inside that file. That hold was not waived. The defective derivative remains unpublished. This release generated its own single-page outlined PDF directly from the preserved original page instead, and the independent review checks the structure of that new artefact separately.
