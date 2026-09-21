# Data dictionary

All amounts are nominal US dollars. JSON uses `null` and CSV uses empty cells for unknown or inapplicable fields; these are never numeric zero. Dates use ISO format. Physical PDF pages are one-based and printed page labels are separate. File paths are relative to the repository root, including paths stored in CSV/JSON and the workbook.

| Field | Meaning |
|---|---|
| `record_id` | Public release identifier; not an original source's identifier |
| `legal_entity` | Named receiving/reporting legal entity |
| `fiscal_year`, `fiscal_year_start`, `fiscal_year_end` | Source annual period and inclusive dates |
| `fee_program`, `fee_category` | Source program name and standardized facility category |
| `land_use` | Supported development class, without inferring dwelling subtypes |
| `measure_type` | `reported_residential_fee_collections` in this edition; not verified cash |
| `value_usd`, `source_value_text`, `source_label` | Reviewed amount, exact printed amount token and its caption |
| `publication_title`, `source_id` | Named report and public source-index join key |
| `physical_pdf_page`, `printed_page` | Page in complete original and printed label, where present |
| `chapter`, `table_or_figure`, `internal_identifier` | Separate source locators; null where absent; identifiers are not invented |
| `source_sha256`, `source_pdf`, `official_source_url` | Original-byte hash, preserved original, issuing/official archive link |
| `extract_pdf`, `highlight_pdf` | Exact source-page PDF and copy with blue review outlines |
| `attribution_evidence` | Additional source page establishing residential applicability |
| `validation_status` | `accepted_reported_collection_scope`; limited to the stated measure |
| `cash_status` | `not_established` in this edition |
| `accounting_basis`, `gross_or_net` | Unresolved basis and refund treatment; no implied cash or net conversion |
| `method`, `derived_operands`, `limitations` | Reproducible interpretation, all operands if derived, and scope restrictions |

`reported-fee-collections.csv/json` contain only accepted rows within the reported-collection scope. `residential-cash-receipts.csv`, `capital-spending.csv` and `residential-funded-shares.csv` have headers and no accepted observations. The workbook carries corresponding sheets and the source index. There are no formula-derived financial values in this release.

The source index records exact original titles, publication dates where stated, source types, categories, bytes, pages, hashes and status. The Evergreen file includes a board memorandum before its annual report exhibit; the exhibit has no separate publication date. Those file and coverage counts are metadata, not financial observations. `selected_data_rows` counts released rows, not complete entity-year coverage. The evidence index records physical source pages, exact/highlight hashes, matching graph/pixel checks and outline rectangles in PDF points. Workbook evidence cells also provide clickable public repository links.
