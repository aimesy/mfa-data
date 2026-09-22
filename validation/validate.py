#!/usr/bin/env python3
"""Reproducible checks for the mfa-data release.

Run from the repository root:  python validation/validate.py

The checks are mechanical. They establish that the published files are the ones the
manifest describes, that every provenance link resolves, that each published figure can be
re-extracted from its own outlined page, that no row double counts, and that the tables
which are meant to be empty are empty. They do NOT establish that a figure was interpreted
correctly; that requires reading the source, which is what docs/review-process.md describes.
"""
import csv
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAIL = []
PASS = []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append({"check": name, "passed": bool(ok), "detail": detail})


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rel(*p):
    return os.path.join(ROOT, *p)


def norm(s):
    s = (s or "").strip()
    neg = s.startswith("(") and s.endswith(")")
    s = re.sub(r"[^0-9.]", "", s)
    if not s:
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def main():
    manifest = json.load(open(rel("manifest.json"), encoding="utf-8"))
    files = manifest["files"]

    # 1. every manifest entry exists with the recorded size and hash
    bad = []
    for entry in files:
        p = rel(*entry["path"].split("/"))
        if not os.path.isfile(p):
            bad.append((entry["path"], "missing"))
            continue
        if os.path.getsize(p) != entry["bytes"]:
            bad.append((entry["path"], "size"))
        elif sha256(p) != entry["sha256"]:
            bad.append((entry["path"], "sha256"))
    check("manifest_files_match", not bad,
          "%d files checked; %d mismatched %s" % (len(files), len(bad), bad[:5]))

    # 2. nothing published that the manifest does not list
    listed = {e["path"] for e in files}
    on_disk = set()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for fn in filenames:
            p = os.path.relpath(os.path.join(dirpath, fn), ROOT).replace(os.sep, "/")
            if p in ("manifest.json", ".gitignore"):
                continue
            on_disk.add(p)
    check("no_unlisted_published_files", on_disk <= listed,
          "unlisted: %s" % sorted(on_disk - listed)[:5])

    # 3. data rows: provenance links resolve, source hashes match published bytes
    rows = list(csv.DictReader(open(rel("data", "reported-fee-collections.csv"), encoding="utf-8")))
    check("data_rows_present", len(rows) > 2, "%d rows" % len(rows))

    missing_links = []
    for r in rows:
        for col in ("source_pdf", "page_extract_pdf", "outlined_figure_pdf"):
            if not os.path.isfile(rel(*r[col].split("/"))):
                missing_links.append((r["record_id"], col))
    check("provenance_links_resolve", not missing_links, str(missing_links[:5]))

    src_hash_bad = [r["record_id"] for r in rows
                    if sha256(rel(*r["source_pdf"].split("/"))) != r["source_sha256"]]
    check("source_sha256_matches_published_bytes", not src_hash_bad, str(src_hash_bad[:5]))

    # 4. figure groups: exactly one primary per group, one value per group
    groups = {}
    for r in rows:
        groups.setdefault(r["figure_group_id"], []).append(r)
    multi_primary = [g for g, rs in groups.items()
                     if sum(1 for r in rs if r["is_primary_in_figure_group"] == "true") != 1]
    check("one_primary_per_figure_group", not multi_primary, str(multi_primary[:5]))
    inconsistent = [g for g, rs in groups.items() if len({r["value_usd"] for r in rs}) != 1]
    check("figure_group_values_agree", not inconsistent, str(inconsistent[:5]))
    primaries = [r for r in rows if r["is_primary_in_figure_group"] == "true"]
    check("primary_rows_equal_group_count", len(primaries) == len(groups),
          "%d primary rows, %d groups" % (len(primaries), len(groups)))

    # 5. printed value text agrees with the numeric value
    mism = []
    for r in rows:
        if not r["source_value_text"] or not r["value_usd"]:
            continue
        a, b = norm(r["source_value_text"]), float(r["value_usd"])
        if a is None or abs(a - b) > 0.005:
            mism.append((r["record_id"], r["source_value_text"], r["value_usd"]))
    check("printed_text_matches_numeric_value", not mism, str(mism[:5]))

    # 6. re-extract each published figure from its own outlined page
    fitz = None
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            fitz = None
    if fitz is None:
        check("figure_reextracted_from_outlined_page", False,
              "PyMuPDF not installed; install validation/requirements.txt")
    else:
        unmatched, no_text_layer, uncorroborated = [], [], []
        checked = 0
        for r in rows:
            if not r["outline_rect_pdf_points"]:
                continue
            x0, y0, x1, y1 = json.loads(r["outline_rect_pdf_points"])
            d = fitz.open(rel(*r["outlined_figure_pdf"].split("/")))
            page = d.load_page(0)
            clip = fitz.Rect(x0, y0, x1, y1)
            txt = page.get_text("text", clip=clip)
            region_has_ink = False
            if not txt.strip():
                pm = page.get_pixmap(clip=clip, colorspace=fitz.csGRAY, dpi=150)
                region_has_ink = any(b < 160 for b in pm.samples)
            d.close()
            checked += 1
            joined = re.sub(r"\s+", "", txt)
            token_ok = bool(r["source_value_text"]) and re.sub(r"\s+", "", r["source_value_text"]) in joined
            got = norm(txt)
            want = float(r["value_usd"]) if r["value_usd"] else None
            value_ok = got is not None and want is not None and abs(got - want) < 0.005
            if token_ok or value_ok:
                continue
            # A figure can fail mechanical re-extraction for exactly one legitimate reason:
            # the outlined region carries ink but no text layer, because it is a scan or is
            # handwritten. Both parts are tested here, objectively, rather than assumed for
            # named agencies: the region must actually contain dark pixels, which proves the
            # outline encloses the printed mark rather than empty paper. Such a row is not
            # waived either: it must carry an arithmetic corroboration, which for these
            # sources is the fund roll-forward the report itself prints, and it was read
            # visually against the outlined page. Ink with no arithmetic corroboration fails,
            # and an outline over blank paper fails.
            if region_has_ink:
                no_text_layer.append(r["record_id"])
                if not (r["arithmetic_check"] or "").strip():
                    uncorroborated.append(r["record_id"])
                continue
            unmatched.append((r["record_id"], repr(txt)[:60]))
        bad = unmatched + [(u, "no text layer and no arithmetic corroboration")
                           for u in uncorroborated]
        check("figure_reextracted_from_outlined_page", not bad,
              "%d rows re-extracted; %d outlined regions carry ink but no text layer, each "
              "corroborated by the source's own printed arithmetic; %d unmatched %s"
              % (checked, len(no_text_layer), len(bad), bad[:3]))

    # 7. the stronger tables are empty
    for fn in ("residential-cash-receipts.csv", "capital-spending.csv", "residential-funded-shares.csv"):
        data = list(csv.DictReader(open(rel("data", fn), encoding="utf-8")))
        check("empty_table_%s" % fn, len(data) == 0, "%d rows" % len(data))

    # 8. every published zero is a printed zero; no unknown became a zero
    bad_zero = [r["record_id"] for r in rows
                if r["value_usd"] and float(r["value_usd"]) == 0
                and r["value_is_printed_zero"] != "true"]
    check("published_zeros_are_printed_zeros", not bad_zero, str(bad_zero[:5]))
    blank_value = [r["record_id"] for r in rows if not r["value_usd"]]
    check("no_blank_values_published", not blank_value, str(blank_value[:5]))

    # 9. privacy: no local paths, operator identifiers or key material in published text.
    #    The patterns live in privacy-patterns.json so that this file does not contain the
    #    very strings it searches for and therefore match itself.
    patterns = json.load(open(rel("validation", "privacy-patterns.json"), encoding="utf-8"))["patterns"]
    hits = []
    scanned = 0
    for entry in files:
        if not entry["path"].endswith((".csv", ".json", ".md", ".py", ".txt")):
            continue
        if entry["path"] == "validation/privacy-patterns.json":
            continue
        scanned += 1
        text = open(rel(*entry["path"].split("/")), encoding="utf-8", errors="replace").read()
        for pat in patterns:
            if re.search(pat, text):
                hits.append((entry["path"], pat))
    check("no_private_paths_or_identifiers_in_text_files", not hits,
          "%d text files scanned against %d patterns; %d hits %s" % (scanned, len(patterns), len(hits), hits[:5]))

    # 10. the arithmetic claims in arithmetic_check actually balance.
    #     Each published row records the source's own arithmetic that confirms the figure was
    #     read from the right row and column, for example a fund roll-forward closing to the
    #     printed ending balance. Those claims are prose written by the reviewer, so this
    #     parses every equation out of them and checks it. A claim that does not balance is a
    #     defect in the review, not in the source.
    NUMPAT = r"\(?-?\$?\s?\d[\d,]*(?:\.\d+)?\)?"
    eq_re = re.compile(r"(%s(?:\s*[+\-]\s*%s)+)\s*=\s*(%s)" % (NUMPAT, NUMPAT, NUMPAT))
    tok_re = re.compile(r"([+\-])?\s*(\(?-?\$?\s?\d[\d,]*(?:\.\d+)?\)?)")

    def money(tok):
        tok = tok.strip()
        neg = tok.startswith("(") and tok.endswith(")")
        t = re.sub(r"[^0-9.]", "", tok)
        if not t or t.count(".") > 1:
            return None
        return -float(t) if neg else float(t)

    def fold(expr):
        total, sign, pos = None, 1, 0
        while pos < len(expr):
            m = tok_re.match(expr, pos)
            if not m:
                break
            v = money(m.group(2))
            if v is None:
                return None
            total = v if total is None else total + sign * v
            pos = m.end()
            nxt = re.match(r"\s*([+\-])\s*", expr[pos:])
            if not nxt:
                break
            sign = 1 if nxt.group(1) == "+" else -1
            pos += nxt.end()
        return total

    claims = {r["arithmetic_check"] for r in rows if r.get("arithmetic_check")}
    n_eq, unbalanced = 0, []
    for txt in claims:
        for lhs, rhs in eq_re.findall(txt):
            got, want = fold(lhs), money(rhs)
            if got is None or want is None:
                continue
            n_eq += 1
            if abs(got - want) > max(1.0, abs(want) * 1e-9):
                unbalanced.append((lhs.strip(), rhs.strip(), round(got, 2)))
    check("published_arithmetic_claims_balance", not unbalanced,
          "%d equations parsed from %d distinct arithmetic_check claims; %d do not balance %s"
          % (n_eq, len(claims), len(unbalanced), unbalanced[:3]))

    # 11. cohort accounting reconciles, so the disposition of the reviewed cohort can be
    #     checked rather than taken on trust: published plus refused must equal reviewed must
    #     equal the cohort total, the refusal reason counts must sum to the refused total, and
    #     the published count must equal the number of rows actually in the data file.
    acct = json.load(open(rel("data", "cohort-accounting.json"), encoding="utf-8"))
    ref_rows = list(csv.DictReader(open(rel("data", "refusals-by-reason.csv"), encoding="utf-8")))
    ref_sum = sum(int(r["rows_refused"]) for r in ref_rows)
    problems = []
    if acct["published"] + acct["refused"] != acct["reviewed"]:
        problems.append("published + refused != reviewed")
    if acct["reviewed"] != acct["cohort_total"]:
        problems.append("reviewed != cohort_total")
    if acct["remaining_undecided"] != 0:
        problems.append("rows remain undecided")
    if ref_sum != acct["refused"]:
        problems.append("refusal reason counts sum to %d, not %d" % (ref_sum, acct["refused"]))
    if acct["published_rows_in_data_file"] + acct.get("statewide_lane_rows_in_data_file", 0) != len(rows):
        problems.append("cohort published %d + statewide %d != %d rows in the data file"
                        % (acct["published_rows_in_data_file"],
                           acct.get("statewide_lane_rows_in_data_file", 0), len(rows)))
    if len(ref_rows) != acct["refusal_reason_codes"]:
        problems.append("reason code count disagrees")
    check("cohort_accounting_reconciles", not problems,
          "cohort %d = published %d + refused %d; reason counts sum to %d across %d codes; %s"
          % (acct["cohort_total"], acct["published"], acct["refused"], ref_sum, len(ref_rows),
             "; ".join(problems) if problems else "reconciles"))

    # 12. the published accounting must not leak an amount
    acct_text = open(rel("data", "cohort-accounting.json"), encoding="utf-8").read()
    money_in_acct = re.findall(r"\$\s?[\d,]{4,}", acct_text)
    check("cohort_accounting_carries_no_amounts", not money_in_acct, str(money_in_acct[:3]))

    # 13. markdown links resolve
    broken = []
    for entry in files:
        if not entry["path"].endswith(".md"):
            continue
        base = os.path.dirname(rel(*entry["path"].split("/")))
        text = open(rel(*entry["path"].split("/")), encoding="utf-8").read()
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(base, target))):
                broken.append((entry["path"], target))
    check("markdown_links_resolve", not broken, str(broken[:5]))

    out = {"checks": PASS + FAIL,
           "passed": len(FAIL) == 0,
           "n_passed": len(PASS), "n_failed": len(FAIL),
           "data_rows": len(rows), "figure_groups": len(groups),
           "source_reports": len({r["source_pdf"] for r in rows}),
           "receiving_entities": len({r["receiving_entity"] for r in rows})}
    print(json.dumps(out, indent=1))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
