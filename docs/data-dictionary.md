# Data dictionary

`data/reported-fee-collections.csv` and `.json` carry one row per published observation. `data/mfa-reviewed-collections.xlsx` carries the same rows plus a source sheet and a read-me sheet.

## Identity and period

| Column | Meaning |
|---|---|
| `record_id` | stable identifier for this row within the release |
| `receiving_entity` | legal government that received the fee, as recorded in the research register |
| `entity_type` | `city`, `school_district` or `special_district` |
| `county` | county, where recorded |
| `fiscal_year` | fiscal year the figure is reported for |
| `fiscal_year_start`, `fiscal_year_end` | ISO dates bounding that fiscal year |
| `fiscal_year_basis` | **how the fiscal year was established from the source** — the report title, a printed period sentence, a printed column header, a printed fiscal-year row, or the section 66006 statement |

## The figure

| Column | Meaning |
|---|---|
| `fee_program` | fund or fee **as the source names it**. Where the inherited record said the fund name was not established but the source in fact names it, this release uses the source's name |
| `fee_category` | standardised category; `unknown` where the research register has not classified the programme |
| `measure` | research measure type: `total_fees_collected`, `mixed_or_unallocated_fees_collected` or `gross_residential_fees_collected` |
| `measure_as_printed` | **the exact printed row or column label the number sits on**, for example `Receipts`, `Impact Fee Revenue`, `Fees Collected`, `Mitigation Fees`, `Amount of Reportable Fees Collected`, `Charges for Services` |
| `value_usd` | the amount, in US dollars, exactly as printed |
| `source_value_text` | the currency token exactly as printed, including any parentheses or separators |
| `value_is_printed_zero` | `true` where the source prints a zero. A printed zero is a reported zero. An unknown is never recorded as zero and never appears in this table |

## Do not double count

| Column | Meaning |
|---|---|
| `figure_group_id` | rows sharing this value restate **one** printed figure at different measure grains |
| `is_primary_in_figure_group` | `true` on exactly one row per group. **Sum only these rows.** 189 of 357 rows are primary |
| `measure_role` | `primary_reported_figure` or `secondary_measure_restatement` |

## Scope read from the source

| Column | Meaning |
|---|---|
| `land_use_scope` | one of: `not_split_in_source`, `residential_and_nonresidential_not_split`, `residential_only_stated_in_source`, `residential_only_printed_subtotal`, `nonresidential_only_stated_in_source` |
| `land_use_basis` | the sentence or schedule in the source that establishes that scope |
| `accounting_basis_source_read` | `cash` where the source states it, otherwise `not_stated_in_source` |
| `gross_or_net_source_read` | `gross_refunds_reported_separately`, `gross_no_refunds_stated`, `net_of_refunds_where_footnoted`, `not_stated_in_source` and similar, always as the source states it |
| `measure_read_from_source` | what the reviewer read on the page to identify the measure |
| `arithmetic_check` | the source's own arithmetic that confirms the figure was read from the right row and column |
| `source_limitations` | pipe-separated list of the specific defects and caveats found in that source, including where a figure is a Quimby Act in-lieu account, a section 66013 capacity charge or a development-agreement fee rather than a section 66006 impact fee |

`land_use_scope` is **never** an inference from the fee's name or purpose. Where the source prints one undivided amount, the residential share is unknown and is recorded as unknown.

## Provenance

| Column | Meaning |
|---|---|
| `publication_title`, `publication_type` | the source document and its kind |
| `source_id` | key into `sources/index.csv` |
| `source_pdf` | path to the **complete original report** in this repository |
| `source_sha256` | SHA-256 of the original bytes, verified after copying |
| `official_source_url` | where the original was retrieved from |
| `retrieved_utc` | when it was retrieved |
| `physical_pdf_page` | 1-based page of the original PDF |
| `printed_page` | the page's printed folio, where it has one |
| `internal_identifier` | the table, section, exhibit or line label as printed |
| `page_extract_pdf` | single-page PDF cut from the original, carrying that page |
| `outlined_figure_pdf` | the same page with a rectangle around **this figure and no other** |
| `outline_rect_pdf_points` | `[x0, y0, x1, y1]` of that rectangle in original page coordinates |

Several agencies file inside one combined county document. That document is published once and every publication that uses those bytes cites the same `source_pdf` with its own `physical_pdf_page`.

## Review

| Column | Meaning |
|---|---|
| `validation_status` | `published_reported_collection_reviewed_in_release_03` for every row here |
| `review_batch` | the review batch the decision was recorded in |
| `reviewed_utc` | when the primary decision was recorded |

## Other files

| File | Contents |
|---|---|
| `data/cohort-accounting.json` | disposition of every row in the reviewed cohort, counts only: cohort total, reviewed, published, refused, and rows left undecided (zero). The validator checks that published plus refused equals reviewed equals the total, that the refusal reason counts sum to the refused total, and that the published count equals the rows actually in the data file |
| `data/refusals-by-reason.csv` | reason codes and counts for the 3,016 refused rows. **No amounts.** No refused figure appears anywhere in this repository |
| `data/residential-cash-receipts.csv` | header only. Verified residential cash is not established |
| `data/capital-spending.csv` | header only. Actual capital spending on a comparable scope is not established |
| `data/residential-funded-shares.csv` | header only. No residential fee-funded share is established |
| `sources/index.csv`, `sources/index.json` | one row per source publication, with hash, size, page count, official URL and how many published rows came from it |
| `evidence/index.json` | one entry per figure, with both evidence PDFs, their hashes, the printed label and value token, and the outline rectangle. The surrounding printed row is deliberately **not** reproduced, because on a table page it carries neighbouring cells and some of those are figures this release refused |
| `validation/privacy-patterns.json` | the patterns the validator requires to be absent from every published text file |
| `manifest.json` | path, size and SHA-256 of every published file |
