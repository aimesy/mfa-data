# California impact-fee reports and reviewed data

This preliminary collection contains **three complete public reports and two reviewed reported-collection rows**. It is a small research sample, not statewide coverage. The selected figures have source, land-use, page, exact-PDF and visual review; **cash accounting and residential-funded capital shares are not established**.

| Receiving entity | Fiscal year | Fee program | Reported collections | Evidence |
|---|---|---|---:|---|
| City of Fremont | 2020–21 | Parkland Fee | $7,398,609 | [Report p. 4](sources/fremont-2020-21.pdf#page=4), [outlined extract](evidence/highlights/fremont-2020-21-p004.pdf) |
| City of Fremont | 2020–21 | Park Facilities Fee | $7,856,947 | [Report p. 6](sources/fremont-2020-21.pdf#page=6), [outlined extract](evidence/highlights/fremont-2020-21-p006.pdf) |

Both fees apply to residential development; [the report's master schedule, Notes 2–3](evidence/highlights/fremont-2020-21-p017.pdf), supports that attribution. These are the source's annual collection amounts, not fee rates, estimates from permits, or verified cash receipts. Refund treatment is not fully established. The separately described in-kind park is excluded.

Download the [spreadsheet](data/mfa-preliminary.xlsx), [CSV](data/reported-fee-collections.csv), or [JSON](data/reported-fee-collections.json). Each data row includes the publication title, fiscal period, fee category, physical and printed page, internal identifier, source hash, exact extract, outlined evidence and review scope. The [source index](sources/README.md) links all complete reports, including sources whose figures remain withheld.

The cash-receipt, capital-spending and funded-share tables are deliberately empty: no values in this release meet those stronger requirements. Empty means unknown or unaccepted, never zero. Do not sum this sample into a statewide estimate or divide current collections by spending and call it a funding share.

Read [coverage and gaps](docs/coverage.md), [methodology](docs/methodology.md), [data dictionary](docs/data-dictionary.md), and [review results](validation/review.json). To reproduce the mechanical checks, install the pinned [Python dependencies](validation/requirements.txt) and run `python validation/validate.py` from the repository root. Mechanical checks do not substitute for source interpretation or actual visual review.

The original government reports retain their original bytes and any rights of their issuers. No open-source license is asserted over third-party publications. This release makes no claim of government endorsement.
