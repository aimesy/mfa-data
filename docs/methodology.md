# Methodology

## What this release did

A frozen research input held 3,373 fee-collection observations across 832 agencies that had already passed the research project's mechanical validation checks. Passing a mechanical check is not an acceptance for publication. Every one of those 3,373 rows was reviewed again, from the source, specifically for this release. 357 were published. 3,016 were refused and each refusal is recorded with its own source-specific reason.

## The bar every published figure had to clear

1. **The complete original report is held and published.** Not a summary, not a screenshot. Original bytes, verified by SHA-256 after copying into the repository.
2. **An exact page extract.** A single-page PDF cut from the original, carrying the page the figure is printed on.
3. **An outlined figure.** The same page with a rectangle drawn around that figure and no other. Where a page carries many figures, each has its own outline file.
4. **Actual visual review of the original and the outlined page together.** A reviewer looked at a side-by-side sheet showing the untouched page beside the outlined page, plus a zoomed crop of every outlined cell with its row and column labels visible, and confirmed that each outline sits on the correct row of the correct column.
5. **Land-use and measure scope read from the source text.** What the printed label says, what the fee description says about who pays, what the footnotes qualify. Not inferred from the fee's name or purpose.
6. **Publication, page and internal-identifier provenance.** Publication title and type, physical PDF page, printed page where the page carries a folio, the table or section label as printed, the official source URL and the source hash.
7. **Independent review before publication.** A second pass re-derived every published value from the published outlined page, independently of the review that proposed it.

A row that failed any element was refused with a reason naming the specific source, page and defect, and stays out of the public repository.

## Outlines were rebuilt for this release

The inherited evidence carried page-level highlighted PDFs that marked every candidate number on a page. 148 of the 202 evidence records shared such a page with other records, so those artefacts could not identify which cell a given row's figure was. Each evidence record did carry an exact rectangle in original page coordinates. This release regenerated a **per-figure outline** from the preserved original for every evidence record, tightening the rectangle onto the printed token where the recorded rectangle was loose enough to catch a neighbouring cell, and recorded the resulting rectangle in the data as `outline_rect_pdf_points`. The text inside the outline was then compared with the printed token; disagreements were investigated individually rather than cleared in bulk.

## The evidence files rebuild byte for byte

The 378 evidence PDFs in `evidence/extracts` and `evidence/outlined` are generated from the preserved originals, and generation is **deterministic**: rebuilding the release from the same inputs reproduces every one of them with the same SHA-256 that `manifest.json` records. Two things had to be fixed for that to be true. Generated PDFs carried a wall-clock creation timestamp, which is now pinned; and the second element of each file's trailer `/ID` array is regenerated at random on every save, which is now rewritten to copy the first element. The trailer sits after the cross-reference table and every offset points to an earlier position, so that rewrite cannot disturb the file's structure — and each of the 378 files is re-opened and re-read after generation to confirm it did not.

This matters because the release's integrity claim is a hash per file. A hash you cannot reproduce is only a record that a particular byte sequence once existed; a hash you can reproduce lets you check that the evidence page really is the page the source says it is.

## Arithmetic was used to confirm the reading, not to create values

No published figure was computed. Where a source prints a fund roll-forward, the review checked that beginning balance plus the published figure plus interest minus expenditures equals the printed ending balance. That closure is what confirms the figure was read from the right row and column; it is recorded per row in `arithmetic_check`. Where a source prints a total across accounts, the review checked the published figures sum to it. Where years chain across a multi-year table, the review checked each year's printed ending balance equals the next year's printed beginning balance.

This closure test resolved two source defects that would otherwise have forced a refusal:

- The City of Arcadia's FY2023-24 report prints "2022-23" on two consecutive rows of Exhibit A. The second row's roll-forward closes to the first row's beginning balance, and the same report's Exhibit B prints 2023-24 in the same position, so the first row is fiscal year 2023-24. The City's later FY2024-25 report independently confirms it.
- The Esparto Fire Protection District's FY2023-24 report prints balance dates one year earlier than its own stated fiscal year. Its FY2024-25 report carries the same closing figure forward as the next year's opening balance, which establishes that the dates, not the fiscal year, are stale.

Both resolutions are disclosed on every affected row.

Those closures were worked out by a reviewer reading the page, so they are prose and could in principle be wrong. `validation/validate.py` therefore parses every equation out of the `arithmetic_check` field and checks that it actually balances — 50 equations across 38 distinct claims, all of which do. If a future correction breaks one, the check fails rather than leaving a wrong sum sitting in the data.

### Not every row has an arithmetic corroboration

**253 of the 357 published rows carry an `arithmetic_check` statement; 104 do not.** The field is simply empty on those rows, and it is worth saying plainly what that means rather than leaving it to be inferred from a blank cell.

The 104 are the City of Sacramento (46), the City of Arcadia (31), the City of Colton (18), the City of Riverbank (6) and the Consolidated Fire Protection District of Los Angeles County (3). For them the evidence is the visual review of the outlined page together with what the source itself prints — the column header the figure sits under, the fund name on its row, and the footnotes attached to that row. Sacramento's figures, for instance, were read from the "Impact Fee Revenue" column with each row's footnote markers mapped positionally, which is how the property-sale-proceeds and net-of-refund qualifications were found; but the page was not additionally reconciled as a fund roll-forward.

So a row with a non-empty `arithmetic_check` has an extra, independently checkable confirmation that the figure was taken from the right row and column. A row with an empty one does not. Both were read from the page and both passed the same independent re-derivation from their own outlined PDF; the difference is the presence of a second, arithmetic corroboration. If your use is sensitive to that, filter on the field.

## Two measure grains, one printed figure

The research input records some printed amounts twice: once as a total across land uses and once at a mixed or unallocated land-use grain. Both are true statements about the same printed number. Rather than silently drop one, this release publishes both, links them with `figure_group_id` and flags exactly one as `is_primary_in_figure_group`. 357 rows carry 189 distinct printed figures. **Sum primary rows only.**

## Residential attribution

The research goal behind this collection is residential impact-fee revenue. That makes it tempting to attribute a park or school fee to residential payers because its rate schedule lists dwelling types. This release does not do that.

A residential land-use scope is published only where the source itself establishes it, in one of two ways: the report states the fee is levied on, or to serve, residential development **and** its printed rate schedule contains no non-residential rate (City of Fremont's Parkland and Park Facilities fees), or the agency prints a residential subtotal of what it collected (Natomas Unified).

The input carried sixteen rows that assign a whole reported amount to residential payers. One met the test above and is published. Twelve were refused as derived residential attributions with no printed subtotal, affecting the City of Arcadia, the City of Garden Grove, Cameron Park Community Service District, El Dorado Hills Community Service District and Georgetown Divide Recreation District. The remaining three, all City of Manteca, were refused on separate grounds that defeated them first: two cite a page carrying no readable row label, and one is a park in-lieu account whose measure scope is not established. In every case the same printed amount is still published as a reported collection, with the residential share recorded as unknown.

A fee schedule establishes who the fee applies to. It does not establish the residential share of what was collected.

## Not every published row is a Mitigation Fee Act fee

Agencies report Quimby Act park dedication in-lieu accounts, Government Code section 66013 capacity charges, development-agreement fees under section 65865(e) and utility connection charges inside the same annual report as their section 66006 impact fees. Where a published figure is one of those, `source_limitations` says so explicitly. Filter on it if your analysis needs section 66006 fees only.

## What was not attempted

Verified cash receipts, comprehensive refund reconciliation, actual capital spending on a comparable scope, tracing transfers and accumulated balances between funds, and any residential fee-funded share of capital spending. None of those is established by this release and all three corresponding tables are empty.
