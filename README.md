# California development impact fee reports and reviewed data

**357 reviewed data rows covering 189 distinct printed figures, from 43 receiving entities and 79 agency-years, spanning fiscal years 2013–14 to 2024–25.** Every published figure was read from the original report, marked with its own outline on the page it appears on, checked against the source's own arithmetic, and reviewed twice before release.

The [sources directory](sources/) holds **52 complete original report files**. They carry 61 publication records, because some agencies file inside a shared document: nine El Dorado County special districts appear in one combined county filing, and the American Canyon Fire Protection District's two years are in one document. Two of the 52 are carried forward from an earlier release as source-only records whose own figures remain held.

This is a reviewed research sample. **It is not statewide coverage, and it must not be summed into a statewide estimate.** California has thousands of fee-levying agencies; 43 are represented here.

## What is in a row

| | |
|---|---|
| Receiving entity | the legal government that received the fee |
| Fee programme | the fund or fee **as the source names it** |
| Measure as printed | the exact printed row or column label the number sits on |
| Land-use scope | what the source itself says about who pays, never inferred |
| Provenance | publication, physical page, printed page, internal identifier, source SHA-256, page extract, outlined figure |
| Limitations | the specific defects and caveats found in that source |

Download the [CSV](data/reported-fee-collections.csv), [JSON](data/reported-fee-collections.json) or [spreadsheet](data/mfa-reviewed-collections.xlsx).

## The largest published entities

Amounts are the sum of that entity's **primary** rows only (see "Do not double count" below). Each is what the agency reported collecting, across the fiscal years present here.

| Receiving entity | Years published | Primary figures | Reported collections in this dataset |
|---|---|---:|---:|
| Saddleback Valley Unified | 2015–16 to 2020–21 | 6 | $26,166,849.63 |
| City of Sacramento | 2022–23, 2024–25 | 23 | $21,123,530.00 |
| City of Arcadia | 2014–15 to 2024–25 | 21 | $16,873,825.00 |
| City of Stockton | 2021–22, 2022–23 | 6 | $15,719,048.00 |
| City of Fremont | 2020–21 | 2 | $15,255,556.00 |
| City of San Bruno | 2022–23 | 1 | $9,704,825.00 |
| City of Calimesa | 2019–20 to 2021–22 | 14 | $3,392,872.00 |
| Consolidated Fire Protection District of Los Angeles County | 2022–23 | 3 | $3,185,984.40 |
| Beaumont Unified | 2024–25 | 1 | $3,171,016.75 |
| City of Garden Grove | 2021–22 | 6 | $3,072,830.22 |
| City of Costa Mesa | 2018–19 | 3 | $2,750,339.00 |
| El Dorado Hills Community Service District | 2024–25 | 1 | $2,129,526.00 |
| City of Manteca | 2020–21 to 2024–25 | 5 | $1,843,995.00 |
| City of Beaumont | 2024–25 | 17 | $1,791,194.36 |

All 43 entities, all 189 primary figures and all 131 fee programmes are in the data files. The [source index](sources/index.csv) lists every complete original report.

## Do not double count

Each **printed figure** appears as up to two rows, because the same reported amount is recorded at two measure grains. Rows that restate one printed figure share a `figure_group_id`, and exactly one of them has `is_primary_in_figure_group = true`.

**Sum only rows where `is_primary_in_figure_group` is true.** There are 189 such rows against 357 total. Summing every row would count most amounts twice.

## What these numbers are, and are not

These are **amounts the agencies themselves reported collecting**. They are not audited, not reconciled to bank receipts, and not adjusted to a common accounting basis.

- **Residential share is unknown for almost every row.** Only four published figures carry a residential or non-residential scope stated by the source: two City of Fremont park fees the report says are levied on new residential development, one Natomas Unified line the district prints as a separate "Residential Fees" subtotal, and one Culver City fee the report says applies to non-residential use only with residential printed as N/A. For the other 185 figures the source prints one undivided amount. `land_use_scope` records this honestly; **unknown is never recorded as zero**.
- **Accounting basis is usually not stated.** Where it is, the row says so: the City of Sacramento's reports state they are prepared on the cash basis.
- **Refund treatment varies and is recorded per row.** Some sources print refunds on a separate line, some state there were none, most say nothing.
- **Some rows are not Mitigation Fee Act fees at all.** Quimby Act park in-lieu accounts, Government Code section 66013 capacity charges and development-agreement fees appear where the agency reported them alongside its impact fees. Each such row says so in `source_limitations`.

## The empty tables are empty on purpose

[`data/residential-cash-receipts.csv`](data/residential-cash-receipts.csv), [`data/capital-spending.csv`](data/capital-spending.csv) and [`data/residential-funded-shares.csv`](data/residential-funded-shares.csv) contain headers and no rows. No figure in this release meets the stronger bar those tables require. **Empty means not established — never zero.** Do not divide collections by spending and call the result a funding share.

## What was refused, and why

3,016 of the 3,373 rows reviewed for this release were refused and are not published. Each carries its own recorded, source-specific reason. [`data/refusals-by-reason.csv`](data/refusals-by-reason.csv) publishes the reason codes and counts without publishing any held figure. The largest groups:

- **2,974 rows** rest on a state financial dataset with no report page, so no page extract, no outlined figure and no visual review of an original are possible.
- Figures whose printed row combines fees with other revenue, or includes property-sale proceeds.
- A negative net-of-refund amount that is not a collection.
- Residential amounts derived from a fee schedule rather than printed as a residential subtotal by the source.
- A figure whose recorded fiscal year contradicts the column it is printed in.
- A cited page that carries no readable row label.

Read [coverage and gaps](docs/coverage.md), [methodology](docs/methodology.md), the [data dictionary](docs/data-dictionary.md) and the [review process](docs/review-process.md). Mechanical checks do not substitute for reading the source.

## Reproduce the checks

Install the pinned [dependencies](validation/requirements.txt) and run `python validation/validate.py` from the repository root. It re-hashes every source and evidence file against [`manifest.json`](manifest.json), re-extracts each published figure from its own outlined page, and confirms the empty tables are empty. Results from this release are in [validation/review.json](validation/review.json) and [validation/independent-review.json](validation/independent-review.json).

## Rights

The original government reports retain their original bytes and any rights of their issuers. No open-source licence is asserted over third-party government publications. This release makes no claim of government endorsement.
