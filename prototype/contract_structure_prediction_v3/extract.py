"""Structure extraction for the V3 masked contract-structure pilot (standard library only).

Turns a locally downloaded public document (SEC EDGAR exhibit HTML or a vendor SLA web page)
into a list of top-level units (article / bold heading) with nested sub-units, literal headings
and source order. Developed on TRAINING documents only; applied unchanged to heldout documents.
Raw documents are never committed; only the extracted headings, hashes and short evidence.
"""
from __future__ import annotations

import html
import re

ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50}


def roman(s: str) -> int | None:
    s = s.upper()
    if not s or any(c not in ROMAN for c in s):
        return None
    total = 0
    for i, c in enumerate(s):
        v = ROMAN[c]
        total += -v if i + 1 < len(s) and ROMAN[s[i + 1]] > v else v
    return total


def decode(b: bytes) -> str:
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", errors="replace")


def html_lines(raw: str) -> list[str]:
    s = re.sub(r"(?is)<(script|style|noscript|svg)\b[^>]*>.*?</\1\s*>", " ", raw)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>|</li>|</h\d>|</td>", "\n", s)
    s = re.sub(r"(?i)<(h\d|p|div|li|tr)\b", r"\n<\1", s)
    s = re.sub(r"(?i)<(h[1-4])\b[^>]*>", lambda m: "\x03" + m.group(1)[1], s)   # mark HTML headings
    s = re.sub(r"(?i)<(strong|b)\b[^>]*>", "\x01", s)          # mark bold starts
    s = re.sub(r"(?i)</(strong|b)>", "\x02", s)
    t = html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("\xa0", " ").replace("﻿", "").replace("​", "")
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    out = []
    for line in t.split("\n"):
        line = re.sub(r"[ \t\r\f\v]+", " ", line).strip()
        if line.strip("\x01\x02 "):
            out.append(line)
    return out


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[\x01\x02]|\x03\d", " ", s)).strip(" .:-")


ART = re.compile(r"^(?:ARTICLE|Article)\s+([IVXL]+|\d+)\b\.?\s*(.*)$")
SEC = re.compile(r"^(?:SECTION|Section|§)\s+(\d+)\.(\d+)\.?\s*(.*)$")


def credit_agreement_structure(raw: str) -> dict:
    """Parse the table of contents of a credit agreement exhibit.

    Returns {"units": [{"num", "heading", "subunits": [{"num", "heading"}]}], "segmentation": ...}.
    Falls back to grouping numbered sections by their major number when no ARTICLE markers exist.
    """
    lines = [clean(l) for l in html_lines(raw)]
    lines = [l for l in lines if l]
    units, seen_secs, notes = [], set(), []
    cur = None
    i = 0
    toc_done = False
    while i < len(lines) and not toc_done:
        l = lines[i]
        m, s = ART.match(l), SEC.match(l)
        if m:
            n = roman(m.group(1)) if not m.group(1).isdigit() else int(m.group(1))
            if any(u["num"] == n for u in units):        # second ARTICLE I => body begins
                toc_done = True
                break
            title = m.group(2).strip()
            if not title and i + 1 < len(lines) and not ART.match(lines[i + 1]) and not SEC.match(lines[i + 1]):
                title = lines[i + 1]
            cur = {"num": n, "heading": title or "HEADING_ABSENT", "subunits": []}
            units.append(cur)
        elif s:
            key = (int(s.group(1)), int(s.group(2)))
            if key in seen_secs:
                toc_done = True
                break
            seen_secs.add(key)
            title = s.group(3).strip()
            if (not title or re.fullmatch(r"\d+", title)) and i + 1 < len(lines) and not ART.match(lines[i + 1]) and not SEC.match(lines[i + 1]):
                title = lines[i + 1]
            title = re.sub(r"\s+\d+$", "", title)            # trailing TOC page number
            sub = {"num": f"{key[0]}.{key[1]:02d}", "heading": title or "HEADING_ABSENT"}
            if cur is not None and cur["num"] == key[0]:
                cur["subunits"].append(sub)
            else:
                grp = next((u for u in units if u["num"] == key[0]), None)
                if grp is None:
                    grp = {"num": key[0], "heading": "HEADING_ABSENT", "subunits": []}
                    units.append(grp)
                    notes.append(f"section {sub['num']} without ARTICLE heading; grouped by major number")
                grp["subunits"].append(sub)
                cur = grp
        i += 1
    for u in units:
        u["heading"] = re.sub(r"\s+\d+$", "", u["heading"])
    return {"units": units, "segmentation": "TOC_ARTICLE_SECTION", "notes": notes[:5] + ([f"... {len(notes)-5} more"] if len(notes) > 5 else []),
            "full_text": " ".join(lines)}


SLA_TITLE = re.compile(r"(?i)service level agreement|\bSLA\b")
SLA_CONTENT = re.compile(r"(?i)credit|uptime|availab|exclusion|downtime|service level")


def sla_structure(raw: str) -> dict:
    """Units of a vendor SLA web page.

    Content starts at the first HTML heading naming a Service Level Agreement / SLA. Units split at HTML
    h1-h4 headings and at bold-only paragraphs that are not table header cells (a bold-only line adjacent
    to another bold-only line is treated as a table header). Content ends with the last unit whose text
    mentions an SLA keyword; later units (site chrome) are dropped. Empty units are dropped.
    """
    lines = html_lines(raw)
    start = next((k for k, l in enumerate(lines) if re.match(r"^\x03[1-4]", l) and SLA_TITLE.search(clean(l))), None)
    if start is None:
        return {"units": [], "segmentation": "SLA_TITLE_NOT_FOUND", "notes": ["no heading names an SLA"], "full_text": ""}
    is_bold = [bool(re.fullmatch(r"\x01([^\x01\x02]{3,90})\x02[ .:]*", l)) for l in lines]
    units = [{"heading": "HEADING_ABSENT", "kind": "OPENING", "text": []}]
    for k in range(start + 1, len(lines)):
        l = lines[k]
        hm = re.match(r"^\x03([1-4])\s*(.*)$", l)
        table_hdr = is_bold[k] and ((k > 0 and is_bold[k - 1]) or (k + 1 < len(lines) and is_bold[k + 1]))
        if hm and clean(hm.group(2)):
            units.append({"heading": clean(hm.group(2)), "kind": f"H{hm.group(1)}", "text": []})
        elif is_bold[k] and not table_hdr and len(clean(l)) < 90:
            units.append({"heading": clean(l), "kind": "BOLD_PARAGRAPH", "text": []})
        else:
            if clean(l):
                units[-1]["text"].append(clean(l))
    for u in units:
        u["text"] = " ".join(u["text"])
    units = [u for u in units if u["text"] and not re.fullmatch(r"(?i)on this page|table of contents|contents", u["heading"])]
    last = max((k for k, u in enumerate(units) if SLA_CONTENT.search(u["heading"] + " " + u["text"])), default=-1)
    dropped = len(units) - (last + 1)
    units = units[: last + 1]
    return {"units": units, "segmentation": "SLA_HEADINGS_V1", "notes": [f"dropped {dropped} trailing non-SLA units"],
            "title": clean(lines[start]), "full_text": " ".join(clean(l) for l in lines[start:])}
