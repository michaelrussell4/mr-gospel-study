import os
import re
import html
import json
import struct
from datetime import datetime

# Canonical Scripture Books: (Canonical Name, Standard Work, URL Path Prefix, Regex Aliases)
SCRIPTURE_BOOKS = [
    # Book of Mormon
    ("1 Nephi", "Book of Mormon", "bofm/1-ne", [r"1\s*Nephi", r"1\s*Ne\.?"]),
    ("2 Nephi", "Book of Mormon", "bofm/2-ne", [r"2\s*Nephi", r"2\s*Ne\.?"]),
    ("Jacob", "Book of Mormon", "bofm/jacob", [r"Jacob"]),
    ("Enos", "Book of Mormon", "bofm/enos", [r"Enos"]),
    ("Jarom", "Book of Mormon", "bofm/jarom", [r"Jarom"]),
    ("Omni", "Book of Mormon", "bofm/omni", [r"Omni"]),
    ("Words of Mormon", "Book of Mormon", "bofm/w-of-m", [r"Words\s+of\s+Mormon"]),
    ("Mosiah", "Book of Mormon", "bofm/mosiah", [r"Mosiah"]),
    ("Alma", "Book of Mormon", "bofm/alma", [r"Alma"]),
    ("Helaman", "Book of Mormon", "bofm/hel", [r"Helaman", r"Hel\.?"]),
    ("3 Nephi", "Book of Mormon", "bofm/3-ne", [r"3\s*Nephi", r"3\s*Ne\.?"]),
    ("4 Nephi", "Book of Mormon", "bofm/4-ne", [r"4\s*Nephi", r"4\s*Ne\.?"]),
    ("Mormon", "Book of Mormon", "bofm/morm", [r"Mormon", r"Morm\.?"]),
    ("Ether", "Book of Mormon", "bofm/ether", [r"Ether"]),
    ("Moroni", "Book of Mormon", "bofm/moro", [r"Moroni", r"Moro\.?"]),
    # Doctrine and Covenants
    ("D&C", "Doctrine & Covenants", "dc-testament/dc", [r"D&C", r"Doctrine\s+and\s+Covenants", r"D\.\s*&\s*C\."]),
    # Pearl of Great Price
    ("Moses", "Pearl of Great Price", "pgp/moses", [r"Moses"]),
    ("Abraham", "Pearl of Great Price", "pgp/abr", [r"Abraham", r"Abr\.?"]),
    ("Joseph Smith—Matthew", "Pearl of Great Price", "pgp/js-m", [r"Joseph\s+Smith[—\-–]Matthew", r"JS[—\-–]M"]),
    ("Joseph Smith—History", "Pearl of Great Price", "pgp/js-h", [r"Joseph\s+Smith[—\-–]History", r"JS[—\-–]H"]),
    ("Articles of Faith", "Pearl of Great Price", "pgp/a-of-f", [r"Articles\s+of\s+Faith"]),
    # Old Testament
    ("Genesis", "Old Testament", "ot/gen", [r"Genesis", r"Gen\.?"]),
    ("Exodus", "Old Testament", "ot/ex", [r"Exodus", r"Ex\.?"]),
    ("Leviticus", "Old Testament", "ot/lev", [r"Leviticus", r"Lev\.?"]),
    ("Numbers", "Old Testament", "ot/num", [r"Numbers", r"Num\.?"]),
    ("Deuteronomy", "Old Testament", "ot/deut", [r"Deuteronomy", r"Deut\.?"]),
    ("Joshua", "Old Testament", "ot/josh", [r"Joshua", r"Josh\.?"]),
    ("Judges", "Old Testament", "ot/judg", [r"Judges", r"Judg\.?"]),
    ("Ruth", "Old Testament", "ot/ruth", [r"Ruth"]),
    ("1 Samuel", "Old Testament", "ot/1-sam", [r"1\s*Samuel", r"1\s*Sam\.?"]),
    ("2 Samuel", "Old Testament", "ot/2-sam", [r"2\s*Samuel", r"2\s*Sam\.?"]),
    ("1 Kings", "Old Testament", "ot/1-kgs", [r"1\s*Kings", r"1\s*Kgs\.?"]),
    ("2 Kings", "Old Testament", "ot/2-kgs", [r"2\s*Kings", r"2\s*Kgs\.?"]),
    ("1 Chronicles", "Old Testament", "ot/1-chr", [r"1\s*Chronicles", r"1\s*Chr\.?"]),
    ("2 Chronicles", "Old Testament", "ot/2-chr", [r"2\s*Chronicles", r"2\s*Chr\.?"]),
    ("Ezra", "Old Testament", "ot/ezra", [r"Ezra"]),
    ("Nehemiah", "Old Testament", "ot/neh", [r"Nehemiah", r"Neh\.?"]),
    ("Esther", "Old Testament", "ot/esth", [r"Esther", r"Esth\.?"]),
    ("Job", "Old Testament", "ot/job", [r"Job"]),
    ("Psalms", "Old Testament", "ot/ps", [r"Psalms?", r"Ps\.?"]),
    ("Proverbs", "Old Testament", "ot/prov", [r"Proverbs", r"Prov\.?"]),
    ("Ecclesiastes", "Old Testament", "ot/eccl", [r"Ecclesiastes", r"Eccl\.?"]),
    ("Song of Solomon", "Old Testament", "ot/song", [r"Song\s+of\s+Solomon"]),
    ("Isaiah", "Old Testament", "ot/isa", [r"Isaiah", r"Isa\.?"]),
    ("Jeremiah", "Old Testament", "ot/jer", [r"Jeremiah", r"Jer\.?"]),
    ("Lamentations", "Old Testament", "ot/lam", [r"Lamentations", r"Lam\.?"]),
    ("Ezekiel", "Old Testament", "ot/ezek", [r"Ezekiel", r"Ezek\.?"]),
    ("Daniel", "Old Testament", "ot/dan", [r"Daniel", r"Dan\.?"]),
    ("Hosea", "Old Testament", "ot/hosea", [r"Hosea"]),
    ("Joel", "Old Testament", "ot/joel", [r"Joel"]),
    ("Amos", "Old Testament", "ot/amos", [r"Amos"]),
    ("Obadiah", "Old Testament", "ot/obad", [r"Obadiah", r"Obad\.?"]),
    ("Jonah", "Old Testament", "ot/jonah", [r"Jonah"]),
    ("Micah", "Old Testament", "ot/micah", [r"Micah"]),
    ("Nahum", "Old Testament", "ot/nahum", [r"Nahum"]),
    ("Habakkuk", "Old Testament", "ot/hab", [r"Habakkuk", r"Hab\.?"]),
    ("Zephaniah", "Old Testament", "ot/zeph", [r"Zephaniah", r"Zeph\.?"]),
    ("Haggai", "Old Testament", "ot/hag", [r"Haggai", r"Hag\.?"]),
    ("Zechariah", "Old Testament", "ot/zech", [r"Zechariah", r"Zech\.?"]),
    ("Malachi", "Old Testament", "ot/mal", [r"Malachi", r"Mal\.?"]),
    # New Testament
    ("Matthew", "New Testament", "nt/matt", [r"Matthew", r"Matt\.?"]),
    ("Mark", "New Testament", "nt/mark", [r"Mark"]),
    ("Luke", "New Testament", "nt/luke", [r"Luke"]),
    ("John", "New Testament", "nt/john", [r"John"]),
    ("Acts", "New Testament", "nt/acts", [r"Acts"]),
    ("Romans", "New Testament", "nt/rom", [r"Romans", r"Rom\.?"]),
    ("1 Corinthians", "New Testament", "nt/1-cor", [r"1\s*Corinthians", r"1\s*Cor\.?"]),
    ("2 Corinthians", "New Testament", "nt/2-cor", [r"2\s*Corinthians", r"2\s*Cor\.?"]),
    ("Galatians", "New Testament", "nt/gal", [r"Galatians", r"Gal\.?"]),
    ("Ephesians", "New Testament", "nt/eph", [r"Ephesians", r"Eph\.?"]),
    ("Philippians", "New Testament", "nt/philip", [r"Philippians", r"Philip\.?", r"Phil\.?"]),
    ("Colossians", "New Testament", "nt/col", [r"Colossians", r"Col\.?"]),
    ("1 Thessalonians", "New Testament", "nt/1-thes", [r"1\s*Thessalonians", r"1\s*Thes\.?"]),
    ("2 Thessalonians", "New Testament", "nt/2-thes", [r"2\s*Thessalonians", r"2\s*Thes\.?"]),
    ("1 Timothy", "New Testament", "nt/1-tim", [r"1\s*Timothy", r"1\s*Tim\.?"]),
    ("2 Timothy", "New Testament", "nt/2-tim", [r"2\s*Timothy", r"2\s*Tim\.?"]),
    ("Titus", "New Testament", "nt/titus", [r"Titus"]),
    ("Philemon", "New Testament", "nt/philem", [r"Philemon", r"Philem\.?"]),
    ("Hebrews", "New Testament", "nt/heb", [r"Hebrews", r"Heb\.?"]),
    ("James", "New Testament", "nt/james", [r"James"]),
    ("1 Peter", "New Testament", "nt/1-pet", [r"1\s*Peter", r"1\s*Pet\.?"]),
    ("2 Peter", "New Testament", "nt/2-pet", [r"2\s*Peter", r"2\s*Pet\.?"]),
    ("1 John", "New Testament", "nt/1-jn", [r"1\s*John", r"1\s*Jn\.?"]),
    ("2 John", "New Testament", "nt/2-jn", [r"2\s*John", r"2\s*Jn\.?"]),
    ("3 John", "New Testament", "nt/3-jn", [r"3\s*John", r"3\s*Jn\.?"]),
    ("Jude", "New Testament", "nt/jude", [r"Jude"]),
    ("Revelation", "New Testament", "nt/rev", [r"Revelation", r"Rev\.?"]),
]

BOOK_LOOKUP = {}
ALIAS_PATTERNS = []
for canon, work, slug, aliases in SCRIPTURE_BOOKS:
    BOOK_LOOKUP[canon] = (canon, work, slug)
    for al in aliases:
        ALIAS_PATTERNS.append((al, canon))

# Sort aliases longest first
ALIAS_PATTERNS.sort(key=lambda x: -len(x[0]))
COMBINED_BOOK_RE = "|".join(f"(?:{al})" for al, _ in ALIAS_PATTERNS)

# Match book followed by chapter/verse specification
SCRIPTURE_CITATION_RE = re.compile(
    rf"\b({COMBINED_BOOK_RE})\s+(\d{{1,3}}(?:\s*\(:?\d+\))?(?:\s*:\s*\d{{1,3}}(?:\s*[-–—,]\s*\d{{1,3}})*)?(?:\s*[-–—]\s*\d{{1,3}}(?::\d{{1,3}})?)*(?:\s*;\s*\d{{1,3}}:\d{{1,3}}(?:\s*[-–—,]\s*\d{{1,3}})*|\s*,\s*\d{{1,3}}(?!\d))*)",
    re.IGNORECASE
)

def resolve_book_name(raw_book):
    raw_clean = re.sub(r"\s+", " ", raw_book.strip())
    for al, canon in ALIAS_PATTERNS:
        if re.fullmatch(al, raw_clean, re.IGNORECASE):
            return canon
    return None

def build_scripture_url(canon_book, ch_num, verse_num=None):
    _, _, slug = BOOK_LOOKUP[canon_book]
    url = f"https://www.churchofjesuschrist.org/study/scriptures/{slug}/{ch_num}?lang=eng"
    if verse_num:
        url += f"&id=p{verse_num}#p{verse_num}"
    return url

def extract_scriptures_from_text(text):
    """
    Extracts structured scripture citations from text:
    returns list of dicts: {
      "ref": "Alma 32:21",
      "book": "Alma",
      "work": "Book of Mormon",
      "chapter": 32,
      "verses": "21",
      "url": "https://..."
    }
    """
    results = []
    seen = set()
    if not text:
        return results
    # Clean (#Matthew -> Matthew)
    cleaned = re.sub(r"#([A-Za-z])", r"\1", text)
    for m in SCRIPTURE_CITATION_RE.finditer(cleaned):
        raw_book = m.group(1)
        spec = m.group(2).strip()
        canon = resolve_book_name(raw_book)
        if not canon:
            continue
        # Special guard: "Mormon" followed by a year or non-chapter if > 9, etc.
        max_chapters = {
            "1 Nephi": 22, "2 Nephi": 33, "Jacob": 7, "Enos": 1, "Jarom": 1, "Omni": 1,
            "Words of Mormon": 1, "Mosiah": 29, "Alma": 63, "Helaman": 16, "3 Nephi": 30,
            "4 Nephi": 1, "Mormon": 9, "Ether": 15, "Moroni": 10, "D&C": 138,
            "Moses": 8, "Abraham": 5, "Joseph Smith—Matthew": 1, "Joseph Smith—History": 1, "Articles of Faith": 1
        }
        _, work, _ = BOOK_LOOKUP[canon]
        # Handle specs like "11(:11)" -> "11:11"
        spec_norm = re.sub(r"\(:?(\d+)\)", r":\1", spec)
        spec_norm = re.sub(r",\s*-", "-", spec_norm)
        spec_norm = re.sub(r"\s+", " ", spec_norm).strip(" ,;.")
        
        # Split semicolon-separated chapter:verse continuations like "Genesis 24:9; 47:29" or "Matt. 5:31-32; 19:3-12"
        sub_specs = [s.strip() for s in spec_norm.split(";") if s.strip()]
        for sub in sub_specs:
            # Check if it's comma-separated chapters without colons, e.g. "Alma 34, 41, 42" or "Alma 2-3, 21-24, 27, 43"
            if ":" not in sub and "," in sub:
                ch_parts = [c.strip() for c in sub.split(",") if c.strip()]
            else:
                ch_parts = [sub]
            for cp in ch_parts:
                ch_m = re.match(r"^(\d{1,3})(?::\s*(\d{1,3}(?:\s*[-–—,]\s*\d{1,3})*))?", cp)
                if not ch_m:
                    continue
                ch_int = int(ch_m.group(1))
                if canon in max_chapters and (ch_int < 1 or ch_int > max_chapters[canon]):
                    continue
                if ch_int < 1 or ch_int > 150:
                    continue
                v_part = ch_m.group(2)
                first_v = None
                if v_part:
                    fv_m = re.match(r"^(\d+)", v_part.strip())
                    if fv_m:
                        first_v = int(fv_m.group(1))
                ref_display = f"{canon} {cp}"
                if ref_display not in seen:
                    seen.add(ref_display)
                    results.append({
                        "ref": ref_display,
                        "book": canon,
                        "work": work,
                        "chapter": ch_int,
                        "verses": v_part.strip() if v_part else None,
                        "url": build_scripture_url(canon, ch_int, first_v)
                    })
    return results

def extract_header_scriptures(source_text):
    """
    Extracts scripture citations from the s16 header source field, including whole-book references
    like '1 Nephi; 2 Nephi' or 'BOM, Hebrews'.
    """
    results = extract_scriptures_from_text(source_text)
    seen_books = {r["book"] for r in results}
    if not source_text:
        return results
    for part in re.split(r"[;,]", source_text):
        p_clean = part.strip().lstrip("#").strip()
        canon = resolve_book_name(p_clean)
        if canon and canon not in seen_books:
            seen_books.add(canon)
            _, work, slug = BOOK_LOOKUP[canon]
            results.append({
                "ref": canon,
                "book": canon,
                "work": work,
                "chapter": None,
                "verses": None,
                "url": f"https://www.churchofjesuschrist.org/study/scriptures/{slug}?lang=eng"
            })
    return results

