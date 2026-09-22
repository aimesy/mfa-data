# Source reports

Every file in this directory is a **complete original government report**, byte for byte as retrieved from the issuing agency or its publishing platform. Nothing here is a summary, a re-typeset copy or a screenshot. Each file's SHA-256 is recorded in [`index.csv`](index.csv), in [`../manifest.json`](../manifest.json) and beside every data row that cites it, and the copy in this repository was re-hashed after copying to confirm the bytes did not change.

This directory holds **52 files carrying 61 publication records**, covering 43 receiving entities and fiscal years 2013–14 to 2024–25. There are fewer files than publications because some agencies file inside a shared document: nine El Dorado County special districts appear in one combined county filing, and the American Canyon Fire Protection District's two fiscal years are in one document. A shared document is published once under a hash-derived name, and every publication that uses those bytes cites the same file with its own page. Each publication still has its own row in [`index.csv`](index.csv).

## How to find a figure in a report

Each published data row gives the `physical_pdf_page` of the original, the `printed_page` where the page carries a folio, and the `internal_identifier` — the table, exhibit or line label as printed. Two derived files let you go straight to it without opening the whole report:

- `evidence/extracts/…` is that single page, cut from the original.
- `evidence/outlined/…` is the same page with a rectangle around **that figure and no other**. Pages carrying several published figures have one outlined file per figure.

The rectangle's coordinates are published as `outline_rect_pdf_points` so you can check the mark independently.

## Report types

The collection mixes several kinds of document, because agencies publish their fee information in different places:

- `annual_fee_report_66006` — the agency's own annual development impact fee report
- `five_year_findings_66001` — combined annual and five-year reports
- `combined_annual_and_five_year`
- `acfr_audited_financial_statements` — audited statements, used only where the agency's fee reporting appears in them
- `capacity_charge_compliance_report` — Government Code section 66013 capacity charge reports, which are a **different statutory scheme** from Mitigation Fee Act impact fees

`publication_type` in `index.csv` records which. Rows drawn from a section 66013 report, a Quimby Act in-lieu account or a development-agreement fee say so in their `source_limitations`.

## Where a source appears here but a figure does not

Publishing a report does not mean every number in it was accepted. Several reports in this directory contributed some published figures and had others refused — a revenue line that includes property-sale proceeds, a negative net-of-refund amount, a residential figure derived rather than printed. The published data files contain only the accepted figures; the reports retain all of their original contents, and those other figures are not promoted into the data tables.

Sources whose figures were **all** refused are not published here at all, with one deliberate exception. Two reports — the City of Corona's FY2024-25 AB1600 report and the Evergreen Elementary School District's FY2023-24 developer fee report — were published by an earlier release as **source-only** records whose extracted figures remain held. They are carried forward here rather than withdrawn, because taking an already-public record back off the public record is not an improvement. Their `index.csv` entries show `published_data_rows_from_this_source = 0`, and no figure from either appears in any data file.

## Rights

These are third-party government publications. They retain their original bytes and any rights of their issuers. No open-source licence is asserted over them, and this release makes no claim of government endorsement.
