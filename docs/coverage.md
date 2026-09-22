# Coverage and gaps

## What is covered

| | |
|---|---:|
| Published data rows | 357 |
| Distinct printed figures behind them | 189 |
| Receiving entities | 43 |
| Agency-years | 79 |
| Fee programmes | 131 |
| Original report files published | 52 |
| Publication records they carry | 61 |
| Fiscal years spanned | 2013–14 to 2024–25 |

52 files carry 61 publication records because some agencies file inside a shared document: nine El Dorado County special districts appear in one combined county filing, and the American Canyon Fire Protection District's two years are in one document. Two of the 52 files are carried forward from an earlier release as source-only records whose own figures remain held, so 50 files sit behind published figures.

By entity type, the 189 primary figures are 160 from cities, 19 from special districts and 10 from school districts. No county, community college district, joint powers authority or utility enterprise is represented at all.

## What is not covered

**This is not statewide coverage and no coverage percentage is justified.** California has thousands of bodies that may levy development impact fees. 43 appear here. The selection is not a sample drawn from a frame: it is whatever survived a fresh evidence review of one frozen research input, and that input's own composition reflects where collection happened to have reached.

A discovered URL, a saved web response, a PDF file, a registry entry and a verified annual disclosure are five different things. An absent report does not establish that an agency is exempt or failed to report.

## What was reviewed and refused

3,373 rows were reviewed for this release. 357 were published and 3,016 were refused, leaving none undecided. That disposition is published as counts in [`data/cohort-accounting.json`](../data/cohort-accounting.json) and broken down by reason code in [`data/refusals-by-reason.csv`](../data/refusals-by-reason.csv), and `validation/validate.py` checks that it reconciles — published plus refused equals reviewed equals the cohort total, and the reason counts sum to the refused total. You do not have to take the accounting on trust. No refused amount appears anywhere in this repository.

The dominant group, 2,974 rows across 787 school districts for fiscal years 2023–24 and 2024–25, comes from a single California Department of Education SACS unaudited actuals download. Those rows have no report page, so no page extract, no outlined figure and no visual review of an original are possible; the dataset is also the state's financial reporting rather than each district's own Government Code section 66006 disclosure, and it carries no land-use split. Those figures may well be correct. They are not published because the evidence needed to publish a figure under this release's bar does not exist for them.

The remaining 42 refusals are individual source defects: a printed row that combines fees with other revenue, a revenue line footnoted as including property-sale proceeds, a negative net-of-refund amount, residential figures derived from a fee schedule rather than printed, a figure whose recorded fiscal year contradicts its printed column, a cited page with no readable row label, amounts collected for an unnamed separate district, and a narrative sentence used as if it were a reported amount for three different years.

## Known defects in published sources

These are disclosed on the affected rows and repeated here so they are not missed.

- **City of Beaumont FY2024-25.** The fund table's balance column headers read "July 1, 2023" and "June 30, 2024" while the cover, the table heading and the Government Code section 66006 statement all say the fiscal year ended June 30, 2025. No second Beaumont city report is held, so the conflict cannot be resolved against another source. The three concurring statements of the report's own scope were taken as the reporting period.
- **City of Arcadia FY2023-24.** Exhibit A prints "2022-23" on two consecutive rows. Resolved from the fund roll-forward and from the same report's Exhibit B, and confirmed by the City's later FY2024-25 report.
- **Esparto Fire Protection District FY2023-24.** Balance dates printed one year earlier than the report's own fiscal year. Resolved against the following year's report.
- **Beaumont Unified FY2024-25.** The balance table's ending row is labelled June 30, 2024 in a fiscal year 2024-25 report whose rate table runs to June 30, 2025.
- **City of Willows FY2020-21.** The narrative above the Fire Impact Fee table misnames the fund as the Police Impact Fee Fund and repeats the Police fund's ending balance. The Fire table's own figures reconcile correctly.
- **Georgetown Fire Protection District FY2024-25.** The county form was completed by hand; the figure was read visually and confirmed by the roll-forward closing exactly.
- **American Canyon Fire Protection District FY2024-25.** The ending balance is printed with a full stop where the thousands separator belongs. The published fees figure is unaffected.
- **City of Rialto, the City of Manteca's audited statements and the Elk Grove landscape corridor fund** were refused outright and appear in neither the data nor the sources.

## Multi-year restatements

Several published figures come from a later report's multi-year history rather than from that year's own report: the City of Arcadia, the City of Manteca's fund 260, the City of San Leandro's fund 120, the City of Riverbank's fund 140, the City of East Palo Alto, the City of San Bruno and the City of Stockton. Each such row says so in `source_limitations`. A figure an agency restates years later is the agency's own statement, but it is not the same artefact as the original year's disclosure.

## Shared source documents

Nine El Dorado County special districts file inside one combined county document. That document is published once, under a hash-derived name, and every district's rows cite the same file with their own page. The `sources/index.csv` entry names each publication separately.

## What remains unresolved

Verified residential cash receipts, comprehensive refund reconciliation, actual capital spending on a comparable scope, transfers and accumulated balances between funds, and any residential fee-funded share of capital spending. The three tables for those quantities are deliberately empty.
