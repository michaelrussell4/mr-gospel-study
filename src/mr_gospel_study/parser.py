import os
import re
import html
import json
import struct
from datetime import datetime
from .scriptures import extract_scriptures_from_text, extract_header_scriptures

MATH_IMAGE_MAP = {
    "__IMG_archive_1__": ('block', '<div class="math-block"><code><var>F</var> = <var>H</var> + <var>A</var></code></div>', 'F = H + A'),
    "__IMG_archive_2__": ('inline', '<code class="math-inline"><var>F</var> = Faith</code>', 'F = Faith'),
    "__IMG_archive_3__": ('inline', '<code class="math-inline"><var>H</var> = Hope</code>', 'H = Hope'),
    "__IMG_archive_4__": ('inline', '<code class="math-inline"><var>A</var> = Assurance(of hope)</code>', 'A = Assurance(of hope)'),
    "__IMG_archive_5__": ('block', '<div class="math-block"><code><var>F</var> = <var>A</var>(<var>H</var>)</code></div>', 'F = A(H)'),
    "__IMG_archive_6__": ('inline', '<code class="math-inline"><var>A</var></code>', 'A'),
    "__IMG_archive_7__": ('inline', '<code class="math-inline"><var>H</var></code>', 'H'),
    "__IMG_current_1__": ('ignore', '', ''),
    "__IMG_current_2__": ('inline', ' <code class="math-inline"><var>x</var> + <var>y</var> = <var>z</var></code>', ' x + y = z'),
    "__IMG_current_3__": ('inline', '<code class="math-inline"><var>x</var></code>', 'x'),
    "__IMG_current_4__": ('inline', '<code class="math-inline"><var>y</var></code>', 'y'),
    "__IMG_current_5__": ('inline', '<code class="math-inline"><var>z</var></code>', 'z'),
    "__IMG_current_6__": ('inline', '<code class="math-inline"><var>a</var> + 2<var>b</var> = <var>c</var><sup>3</sup></code>', 'a + 2b = c³'),
}

IMAGE_CAPTIONS = {
    "__IMG_archive_8__": "Timeline of the Second Coming of Christ and the Times of the Gentiles",
    "__IMG_archive_9__": "Size of Major Religious Groups, 2010 (Pew Research Center)",
    "__IMG_archive_10__": "Discriminant Analysis of Book of Mormon Authors vs. Joseph Smith",
    "__IMG_archive_11__": "Parallel & Chiasmus Structure in Moroni 7:11",
    "__IMG_archive_12__": "Extended Chiasmus Structure in Alma 48:14–16",
    "__IMG_archive_13__": "Principal Component Analysis of Book of Mormon and Restoration Texts",
}

TAG_TYPO_FIXES = {
    "bodybrigde": "BodyBridge",
    "mutuallyexclusivepresenseofjesusandholyghost": "MutuallyExclusivePresenceOfJesusAndHolyGhost",
    "willofgod": "WillOfGod",
    "bom": "BOM",
}

DATE_RE = re.compile(r'^\d{1,2}/\d{1,2}/\d{2,4}$')

def slugify(text):
    s = text.lower()
    s = re.sub(r"['’‘“”\"]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "entry"

def format_tag_label(tag):
    """Formats CamelCase tag like 'BookOfMormon' into 'Book of Mormon' for human-friendly display/search."""
    if tag.isupper():
        return tag
    # Insert space before capital letters preceded by lowercase or before Uppercase+lowercase
    spaced = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', tag)
    spaced = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', spaced)
    return spaced

def find_matching_brace(data, start):
    depth = 0
    i = start
    n = len(data)
    while i < n:
        ch = data[i]
        if ch == '\\':
            i += 2
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n - 1

def remove_or_replace_groups(data, pattern, handler=None):
    out = []
    pos = 0
    for m in re.finditer(pattern, data):
        start = m.start()
        if start < pos:
            continue
        out.append(data[pos:start])
        end = find_matching_brace(data, start)
        if handler:
            rep = handler(data[start:end+1])
            if rep:
                out.append(rep)
        pos = end + 1
    out.append(data[pos:])
    return ''.join(out)

def parse_colortbl(data):
    m = re.search(r'\{\\colortbl;([\s\S]*?)\}', data)
    if not m:
        return {}
    body = m.group(1)
    colors = {0: (0, 0, 0)}
    for idx, part in enumerate(body.split(';'), 1):
        r = re.search(r'\\red(\d+)', part)
        g = re.search(r'\\green(\d+)', part)
        b = re.search(r'\\blue(\d+)', part)
        if r and g and b:
            colors[idx] = (int(r.group(1)), int(g.group(1)), int(b.group(1)))
    return colors

def classify_highlight_color(rgb):
    if not rgb:
        return None
    r, g, b = rgb
    if r > 245 and g > 245 and b > 245:
        return None
    if r > 200 and g > 200 and b < 100:
        return "hl-yellow"
    if r > 230 and g > 220 and b > 180:
        return "hl-amber"
    if g > 200 and r < 100 and b < 100:
        return "hl-green"
    if g > 200 and b > 200 and r < 100:
        return "hl-cyan"
    if r > 200 and g < 120 and b < 120:
        return "hl-red"
    if r > 220 and g > 180 and b > 180:
        return "hl-rose"
    if r > 200 and g > 120 and b < 80:
        return "hl-orange"
    if r > 180 and b > 180 and g < 120:
        return "hl-magenta"
    if b > 180 and r > 120 and g < 120:
        return "hl-purple"
    if b > 200 and r > 180 and g > 180:
        return "hl-lavender"
    if b > 200 and r < 180:
        return "hl-blue"
    if abs(r - g) < 20 and abs(g - b) < 20:
        return "hl-gray"
    return "hl-amber"

def classify_text_color(rgb):
    if not rgb:
        return None
    r, g, b = rgb
    if abs(r - g) < 15 and abs(g - b) < 15:
        return None
    if (r, g, b) in ((17, 85, 204), (0, 0, 238), (11, 83, 148)):
        return None
    if r > 140 and g < 80 and b < 80:
        return "tc-red"
    if g > 70 and r < 80 and b < 60:
        return "tc-green"
    if b > 120 and r > 100 and g < 60:
        return "tc-purple"
    if b > 130 and r < 90:
        return "tc-blue"
    return None

def preprocess_rtf(data, file_prefix, img_out_dir):
    os.makedirs(img_out_dir, exist_ok=True)
    data = remove_or_replace_groups(
        data,
        r'\{(?:\\header|\\footer|\\\*\\ftnsepc?|\\nonshppict|\\shprslt)\b'
    )

    images = {}
    img_counter = [0]
    out = []
    pos = 0
    for m in re.finditer(r'\\pngblip\b', data):
        if m.start() < pos:
            continue
        fld_pos = data.rfind('{\\field', max(pos, m.start()-800), m.start())
        shppict_pos = data.rfind('{\\*\\shppict', max(pos, m.start()-400), m.start())
        shp_pos = data.rfind('{\\shp', max(pos, m.start()-800), m.start())
        if fld_pos != -1 and 'INCLUDEPICTURE' in data[fld_pos:m.start()]:
            group_start = fld_pos
        elif shppict_pos != -1:
            group_start = shppict_pos
        elif shp_pos != -1:
            group_start = shp_pos
        else:
            group_start = data.rfind('{', pos, m.start())
        group_end = find_matching_brace(data, group_start)
        group_str = data[group_start:group_end+1]
        out.append(data[pos:group_start])

        hex_start_m = re.search(r'89504e47', group_str, re.IGNORECASE)
        if hex_start_m:
            hex_part = group_str[hex_start_m.start():]
            hex_end = hex_part.find('}')
            hex_clean = re.sub(r'[^0-9a-fA-F]', '', hex_part[:hex_end])
            png_bytes = bytes.fromhex(hex_clean)
            w_px, h_px = struct.unpack('>II', png_bytes[16:24])
            img_counter[0] += 1
            idx = img_counter[0]
            token = f"__IMG_{file_prefix}_{idx}__"
            img_filename = f"{file_prefix}_img_{idx:02d}.png"
            if token not in MATH_IMAGE_MAP:
                with open(os.path.join(img_out_dir, img_filename), 'wb') as imgf:
                    imgf.write(png_bytes)
            pw = re.search(r'\\picwgoal(\d+)', group_str)
            ph = re.search(r'\\pichgoal(\d+)', group_str)
            sx = re.search(r'\\picscalex(\d+)', group_str)
            sy = re.search(r'\\picscaley(\d+)', group_str)
            w_css = round(int(pw.group(1)) * int(sx.group(1)) / 100 / 15, 1) if pw and sx else w_px
            h_css = round(int(ph.group(1)) * int(sy.group(1)) / 100 / 15, 1) if ph and sy else h_px
            images[token] = {
                "filename": img_filename,
                "w_px": w_px,
                "h_px": h_px,
                "w_css": w_css,
                "h_css": h_css,
            }
            out.append(f"{{{token}}}")
        pos = group_end + 1
    out.append(data[pos:])
    data = ''.join(out)

    footnotes = {}
    fn_counter = [0]
    def handle_fn(raw_fn):
        fn_counter[0] += 1
        tok = f"__FN_{file_prefix}_{fn_counter[0]}__"
        footnotes[tok] = raw_fn
        return f"{{{tok}}}"
    data = remove_or_replace_groups(data, r'\{\\footnote\b', handle_fn)

    listtexts = {}
    lt_counter = [0]
    def handle_lt(raw_lt):
        lt_counter[0] += 1
        tok = f"__LT_{file_prefix}_{lt_counter[0]}__"
        listtexts[tok] = raw_lt
        return tok
    data = remove_or_replace_groups(data, r'\{\\listtext\b', handle_lt)

    return data, images, footnotes, listtexts

def render_rtf_fragment(frag, colortbl, images, footnotes_map, entry_footnotes):
    links_found = []

    def replace_field(raw_field):
        m_link = re.search(r'HYPERLINK\s+"([^"]+)"', raw_field)
        m_rslt = re.search(r'\{\\fldrslt\b', raw_field)
        if m_link and m_rslt:
            url = m_link.group(1).strip()
            links_found.append(url)
            rslt_start = m_rslt.start()
            rslt_end = find_matching_brace(raw_field, rslt_start)
            inner_rtf = raw_field[rslt_start + 9 : rslt_end]
            return f"{{__LINK_START__{url}__LINK_MID__{inner_rtf}__LINK_END__}}"
        elif m_rslt:
            rslt_start = m_rslt.start()
            rslt_end = find_matching_brace(raw_field, rslt_start)
            return raw_field[rslt_start + 9 : rslt_end]
        return ""

    frag = remove_or_replace_groups(frag, r'\{\\field\b', replace_field)
    frag = remove_or_replace_groups(frag, r'\{\\\*\\[a-zA-Z0-9]+')

    init_state = {
        'b': False, 'i': False, 'ul': False, 'strike': False,
        'super': False, 'sub': False, 'cf': 0, 'cb': 0
    }
    stack = [init_state.copy()]
    segments = []
    cur_link = None

    token_re = re.compile(
        r'__LINK_START__(.*?)__LINK_MID__'
        r'|__LINK_END__'
        r'|(__IMG_[a-z]+_\d+__)'
        r'|(__FN_[a-z]+_\d+__)'
        r'|(__LT_[a-z]+_\d+__)'
        r'|\\u(-?\d+) ?'
        r"|\\'([0-9a-fA-F]{2})"
        r'|\\([\\{}~_-])'
        r'|\\([a-zA-Z]+)(-?\d*) ?'
        r'|([{}])'
        r'|([\r\n]+)'
        r'|([^\\{}\r\n_]+|_)'
    )

    for m in token_re.finditer(frag):
        g_link_start, g_img, g_fn, g_lt, g_u, g_hex, g_esc, g_cmd, g_arg, g_brace, g_nl, g_txt = m.groups()
        st = stack[-1]
        if g_link_start is not None:
            cur_link = g_link_start
        elif m.group(0) == '__LINK_END__':
            cur_link = None
        elif g_img is not None:
            if g_img in MATH_IMAGE_MAP:
                kind, m_html, m_txt = MATH_IMAGE_MAP[g_img]
                if kind != 'ignore':
                    segments.append((m_txt, st.copy(), cur_link, m_html))
            elif g_img in images:
                info = images[g_img]
                caption = IMAGE_CAPTIONS.get(g_img, "Study journal illustration")
                fig_html = (
                    f'<figure class="study-figure">'
                    f'<img src="assets/images/{info["filename"]}" alt="{html.escape(caption)}" '
                    f'width="{info["w_px"]}" height="{info["h_px"]}" loading="lazy" />'
                    f'<figcaption>{html.escape(caption)}</figcaption>'
                    f'</figure>'
                )
                segments.append((f" [{caption}] ", st.copy(), None, fig_html))
        elif g_fn is not None:
            if g_fn in footnotes_map:
                fn_raw = footnotes_map[g_fn]
                _, fn_plain, _ = render_rtf_fragment(fn_raw[9:-1], colortbl, images, {}, [])
                fn_plain = fn_plain.strip()
                fn_num = len(entry_footnotes) + 1
                entry_footnotes.append((fn_num, fn_plain))
                fn_html = (
                    f'<sup class="footnote-ref">'
                    f'<a href="#fn-{{ENTRY_ID}}-{fn_num}" id="fnref-{{ENTRY_ID}}-{fn_num}" '
                    f'data-footnote="{html.escape(fn_plain)}">[{fn_num}]</a>'
                    f'</sup>'
                )
                segments.append(("", st.copy(), None, fn_html))
        elif g_lt is not None:
            pass
        elif g_u is not None:
            code = int(g_u)
            if code < 0:
                code += 65536
            segments.append((chr(code), st.copy(), cur_link, None))
        elif g_hex is not None:
            ch = bytes.fromhex(g_hex).decode('cp1252', errors='replace')
            segments.append((ch, st.copy(), cur_link, None))
        elif g_esc is not None:
            if g_esc in ('\\', '{', '}'):
                segments.append((g_esc, st.copy(), cur_link, None))
            elif g_esc == '~':
                segments.append(('\u00a0', st.copy(), cur_link, None))
            elif g_esc == '_':
                segments.append(('\u2011', st.copy(), cur_link, None))
        elif g_cmd is not None:
            cmd = g_cmd
            val = int(g_arg) if g_arg else None
            if cmd == 'plain':
                stack[-1] = init_state.copy()
            elif cmd == 'b':
                stack[-1]['b'] = (val != 0)
            elif cmd == 'i':
                stack[-1]['i'] = (val != 0)
            elif cmd == 'ul':
                stack[-1]['ul'] = (val != 0)
            elif cmd == 'ulnone':
                stack[-1]['ul'] = False
            elif cmd == 'strike':
                stack[-1]['strike'] = (val != 0)
            elif cmd == 'super':
                stack[-1]['super'] = True
                stack[-1]['sub'] = False
            elif cmd == 'sub':
                stack[-1]['sub'] = True
                stack[-1]['super'] = False
            elif cmd == 'nosupersub':
                stack[-1]['super'] = False
                stack[-1]['sub'] = False
            elif cmd == 'cf':
                stack[-1]['cf'] = val or 0
            elif cmd == 'chcbpat':
                stack[-1]['cb'] = val or 0
            elif cmd == 'tab':
                segments.append((' ', st.copy(), cur_link, None))
            elif cmd == 'line':
                segments.append(('\n', st.copy(), cur_link, '<br />'))
            elif cmd == 'emdash':
                segments.append(('—', st.copy(), cur_link, None))
            elif cmd == 'endash':
                segments.append(('–', st.copy(), cur_link, None))
            elif cmd == 'lquote':
                segments.append(('‘', st.copy(), cur_link, None))
            elif cmd == 'rquote':
                segments.append(('’', st.copy(), cur_link, None))
            elif cmd == 'ldblquote':
                segments.append(('“', st.copy(), cur_link, None))
            elif cmd == 'rdblquote':
                segments.append(('”', st.copy(), cur_link, None))
        elif g_brace is not None:
            if g_brace == '{':
                stack.append(stack[-1].copy())
            elif g_brace == '}':
                if len(stack) > 1:
                    stack.pop()
        elif g_nl is not None:
            pass
        elif g_txt is not None:
            segments.append((g_txt, st.copy(), cur_link, None))

    merged = []
    for txt, st, lnk, raw_h in segments:
        if raw_h is not None:
            merged.append((txt, st, lnk, raw_h))
        elif merged and merged[-1][3] is None and merged[-1][1] == st and merged[-1][2] == lnk:
            prev_t, prev_st, prev_lnk, _ = merged[-1]
            merged[-1] = (prev_t + txt, prev_st, prev_lnk, None)
        else:
            merged.append((txt, st, lnk, None))

    plain_out = ''.join(t for t, _, _, _ in merged)

    html_parts = []
    for txt, st, lnk, raw_h in merged:
        if raw_h is not None:
            html_parts.append(raw_h)
            continue
        if not txt:
            continue
        esc = html.escape(txt)
        if not lnk and ('http://' in esc or 'https://' in esc):
            esc = re.sub(
                r'(https?://[^\s<>"\'\)]+)',
                r'<a href="\1" target="_blank" rel="noopener">\1</a>',
                esc
            )
        hl_cls = classify_highlight_color(colortbl.get(st['cb'])) if st['cb'] else None
        tc_cls = classify_text_color(colortbl.get(st['cf'])) if st['cf'] else None

        if txt.strip():
            if st['super']:
                esc = f"<sup>{esc}</sup>"
            elif st['sub']:
                esc = f"<sub>{esc}</sub>"
            if st['strike']:
                esc = f"<s>{esc}</s>"
            if st['ul'] and not lnk:
                esc = f"<u>{esc}</u>"
            if st['i']:
                esc = f"<em>{esc}</em>"
            if st['b']:
                esc = f"<strong>{esc}</strong>"
            if tc_cls:
                esc = f'<span class="{tc_cls}">{esc}</span>'
        if hl_cls:
            esc = f'<mark class="{hl_cls}">{esc}</mark>'
        if lnk:
            esc = f'<a href="{html.escape(lnk)}" target="_blank" rel="noopener">{esc}</a>'
        html_parts.append(esc)

    html_res = ''.join(html_parts)
    for tag in ['strong', 'em', 'u', 's']:
        html_res = re.sub(f'</{tag}><{tag}>', '', html_res)
    # Merge adjacent identical mark tags
    html_res = re.sub(r'<mark class="([^"]+)">([^<]*)</mark><mark class="\1">', r'<mark class="\1">\2', html_res)
    # Merge adjacent identical hyperlinks
    html_res = re.sub(
        r'<a href="([^"]+)" target="_blank" rel="noopener">(.*?)</a>(\s*)<a href="\1" target="_blank" rel="noopener">(.*?)</a>',
        r'<a href="\1" target="_blank" rel="noopener">\2\3\4</a>',
        html_res
    )
    return html_res.strip(), plain_out.strip(), links_found

def extract_list_marker(lt_raw):
    if not lt_raw:
        return "•"
    def repl_u(m):
        c = int(m.group(1))
        if c < 0:
            c += 65536
        return chr(c)
    s = re.sub(r'\\u(-?\d+) ?', repl_u, lt_raw)
    s = re.sub(r"\\'([0-9a-fA-F]{2})", lambda m: bytes.fromhex(m.group(1)).decode('cp1252', errors='replace'), s)
    s = re.sub(r'\\[a-zA-Z]+-?\d* ?', '', s)
    s = s.replace('{', '').replace('}', '').strip()
    return s or "•"

def parse_rtf_paragraphs_list(clean_data, colortbl, images, footnotes_map, listtexts):
    parts = re.split(r'\\pard\s*\\plain', clean_data)
    paras = []
    for idx, raw_p in enumerate(parts[1:], 1):
        # Check table cell/row markers before stripping \trowd
        ends_cell = '\\cell' in raw_p
        ends_row = '\\row' in raw_p
        # Strip trailing {\trowd ...} or \trowd ...
        p_body = re.sub(r'\{?\\trowd\b[\s\S]*$', '', raw_p)

        # Find header control words before first '{' or '__LT_'
        first_brace = p_body.find('{')
        lt_m = re.search(r'__LT_[a-z]+_\d+__', p_body)
        cut_pos = first_brace if first_brace != -1 else len(p_body)
        if lt_m and lt_m.start() < cut_pos:
            cut_pos = lt_m.start()
        header = p_body[:cut_pos]

        s_m = re.search(r'\\s(\d+)', header)
        style = f"s{s_m.group(1)}" if s_m else "s0"
        intbl = ('\\intbl' in header) or ('\\itap1' in header)
        ls_m = re.search(r'\\ls(\d+)', header)
        ls = int(ls_m.group(1)) if ls_m else None
        ilvl_m = re.search(r'\\ilvl(\d+)', header)
        ilvl = int(ilvl_m.group(1)) if ilvl_m else 0
        li_m = re.search(r'\\li(\d+)', header)
        li = int(li_m.group(1)) if li_m else 0

        list_marker = None
        if lt_m:
            lt_tok = lt_m.group(0)
            list_marker = extract_list_marker(listtexts.get(lt_tok, ""))

        fragment = p_body[first_brace:] if first_brace != -1 else ""
        # Quick plain text probe (without mutating footnotes) to identify headers/dates/titles
        probe_fns = []
        p_html, p_plain, p_links = render_rtf_fragment(fragment, colortbl, images, footnotes_map, probe_fns)

        paras.append({
            "idx": idx,
            "style": style,
            "intbl": intbl,
            "ends_cell": ends_cell,
            "ends_row": ends_row,
            "ls": ls,
            "ilvl": ilvl,
            "li": li,
            "list_marker": list_marker,
            "html": p_html,
            "plain": p_plain,
            "links": p_links,
            " footnotes": probe_fns,
        })
    return paras

def render_entry_body(entry_id, body_paras):
    """
    Converts a list of parsed paragraph dicts into semantic HTML, grouping tables, nested lists,
    indented quote/chiasmus blocks, headings, and footnotes.
    """
    out_blocks = []
    entry_footnotes = []
    headings_text = []

    # State for table accumulation
    in_table = False
    table_rows = []
    cur_row = []
    cur_cell = []

    # State for list accumulation
    list_stack = [] # list of (tag_name 'ul'|'ol', ilvl)

    # State for indented quote/chiasmus block accumulation
    indent_group = []

    def flush_indent_group():
        nonlocal indent_group
        if not indent_group:
            return
        # Check if multiple levels of indentation exist (chiasmus)
        levels = {step for step, _ in indent_group}
        cls = "study-blockquote study-chiasm-group" if len(levels) > 1 else "study-blockquote study-quote-group"
        inner = "\n".join(
            f'<div class="study-indent" style="--indent-steps: {step};">{h}</div>'
            for step, h in indent_group
        )
        out_blocks.append(f'<blockquote class="{cls}">\n{inner}\n</blockquote>')
        indent_group = []

    def flush_lists(target_level=-1):
        nonlocal list_stack
        while list_stack and list_stack[-1][1] > target_level:
            tag, _ = list_stack.pop()
            out_blocks.append(f"</{tag}>")

    def flush_table():
        nonlocal in_table, table_rows, cur_row, cur_cell
        if cur_cell:
            cur_row.append(cur_cell)
            cur_cell = []
        if cur_row:
            table_rows.append(cur_row)
            cur_row = []
        if not table_rows:
            in_table = False
            return
        # Determine max columns
        max_cols = max(len(r) for r in table_rows)
        # Check if row 0 is a bold header row
        has_thead = False
        if len(table_rows) > 1 and max_cols > 1:
            r0 = table_rows[0]
            if all(c and all(p.startswith("<strong>") and p.endswith("</strong>") for p in c if p) for c in r0 if any(c)):
                has_thead = True

        t_html = ['<div class="table-wrap"><table class="study-table">']
        for r_idx, row in enumerate(table_rows):
            if r_idx == 0 and has_thead:
                t_html.append("<thead><tr>")
                for cell in row:
                    cell_inner = "<br />".join(p for p in cell if p)
                    t_html.append(f"<th>{cell_inner}</th>")
                t_html.append("</tr></thead><tbody>")
            else:
                if r_idx == 0:
                    t_html.append("<tbody>")
                t_html.append("<tr>")
                for cell in row:
                    non_empty = [p for p in cell if p]
                    if len(non_empty) <= 1:
                        cell_inner = non_empty[0] if non_empty else ""
                    else:
                        cell_inner = "".join(f"<p>{p}</p>" for p in non_empty)
                    t_html.append(f"<td>{cell_inner}</td>")
                t_html.append("</tr>")
        t_html.append("</tbody></table></div>")
        out_blocks.append("".join(t_html))
        table_rows = []
        in_table = False

    for p in body_paras:
        p_html = p["html"]
        p_plain = p["plain"]
        for fn_num, fn_txt in p[" footnotes"]:
            new_num = len(entry_footnotes) + 1
            p_html = p_html.replace(f"#fn-{{ENTRY_ID}}-{fn_num}", f"#fn-{entry_id}-{new_num}")
            p_html = p_html.replace(f"fnref-{{ENTRY_ID}}-{fn_num}", f"fnref-{entry_id}-{new_num}")
            p_html = p_html.replace(f"[{fn_num}]", f"[{new_num}]")
            entry_footnotes.append((new_num, fn_txt))

        # 1. Table handling
        if p["intbl"]:
            flush_indent_group()
            flush_lists(-1)
            in_table = True
            if p_html:
                cur_cell.append(p_html)
            if p["ends_cell"]:
                cur_row.append(cur_cell)
                cur_cell = []
            if p["ends_row"]:
                if cur_cell:
                    cur_row.append(cur_cell)
                    cur_cell = []
                if cur_row:
                    table_rows.append(cur_row)
                    cur_row = []
            continue
        elif in_table:
            flush_table()

        # Skip empty paragraphs
        if not p_html and not p_plain:
            continue

        # 2. List handling
        if p["ls"] is not None:
            flush_indent_group()
            ilvl = p["ilvl"]
            marker = p["list_marker"] or "•"
            is_ordered = bool(re.match(r'^([0-9]+|[a-zA-Z]|[ivxIVX]+)[\.\)]$', marker.strip()))
            ltag = "ol" if is_ordered else "ul"

            if not list_stack:
                list_stack.append((ltag, ilvl))
                out_blocks.append(f"<{ltag}>")
            else:
                top_tag, top_lvl = list_stack[-1]
                if ilvl > top_lvl:
                    list_stack.append((ltag, ilvl))
                    out_blocks.append(f"<{ltag}>")
                elif ilvl < top_lvl:
                    flush_lists(ilvl)
                    if not list_stack or list_stack[-1][1] < ilvl:
                        list_stack.append((ltag, ilvl))
                        out_blocks.append(f"<{ltag}>")
                    elif list_stack[-1][0] != ltag:
                        old_t, _ = list_stack.pop()
                        out_blocks.append(f"</{old_t}><{ltag}>")
                        list_stack.append((ltag, ilvl))
                elif top_tag != ltag:
                    list_stack.pop()
                    out_blocks.append(f"</{top_tag}><{ltag}>")
                    list_stack.append((ltag, ilvl))

            out_blocks.append(f"<li>{p_html}</li>")
            continue
        else:
            flush_lists(-1)

        # 3. Headings inside entry (s3, s4, s5, s6, plus internal s2 or s16 subheadings)
        st = p["style"]
        if st in ("s2", "s3", "s4", "s5", "s6", "s16"):
            flush_indent_group()
            htag = {
                "s2": "h3",
                "s16": "h3",
                "s3": "h3",
                "s4": "h4",
                "s5": "h5",
                "s6": "h6",
            }[st]
            # Strip default Google Docs heading italics so subheadings are crisp & upright
            h_html = re.sub(r'</?em>', '', p_html).strip()
            extra_quote_lines = []
            if '<br />' in h_html:
                parts_br = [x.strip() for x in h_html.split('<br />') if x.strip()]
                h_html = parts_br[0] if parts_br else h_html
                extra_quote_lines = parts_br[1:]
            h_plain = re.sub(r'<[^>]+>', '', h_html).strip()
            headings_text.append(h_plain)

            # Check if heading is a scripture reference
            sc_refs = extract_scriptures_from_text(h_plain)
            sub_cls = "entry-subheading scripture-subheading" if (sc_refs and len(h_plain) < 95) else "entry-subheading"
            if sc_refs and "<a " not in h_html:
                sc_url = sc_refs[0]["url"]
                h_html = f'<a href="{html.escape(sc_url)}" target="_blank" rel="noopener" class="scripture-heading-link">{h_html}</a>'
            out_blocks.append(f'<{htag} class="{sub_cls}">{h_html}</{htag}>')
            for qline in extra_quote_lines:
                indent_group.append((2.0, qline))
            continue

        # 4. Indented blocks & scripture/block quotes (indented, verse-numbered, or full-paragraph quotes)
        stripped_plain = p_plain.strip()
        is_verse_para = bool(
            re.match(r'^[¹²³⁴⁵⁶⁷⁸⁹⁰]+\s*\S', stripped_plain)
            or re.match(r'^\d{1,3}\s+[A-Z“"‘\'\[]', stripped_plain)
        )
        is_full_quote_para = bool(
            len(stripped_plain) > 45
            and stripped_plain[0] in '“"'
            and (
                stripped_plain[-1] in '”"'
                or re.search(r'[”"]\s*\([^)]+\)\.?$', stripped_plain)
            )
        )
        if p["li"] >= 360 or is_verse_para or is_full_quote_para:
            step = round(p["li"] / 360, 2) if p["li"] >= 360 else 2.0
            indent_group.append((step, p_html))
            continue
        else:
            flush_indent_group()

        # 5. Standalone figure or math block
        if p_html.startswith('<figure ') or p_html.startswith('<div class="math-block">'):
            out_blocks.append(p_html)
        else:
            out_blocks.append(f"<p>{p_html}</p>")

    if in_table:
        flush_table()
    flush_lists(-1)
    flush_indent_group()

    if entry_footnotes:
        fn_items = []
        for fn_num, fn_txt in entry_footnotes:
            fn_items.append(
                f'<li id="fn-{entry_id}-{fn_num}">'
                f'{html.escape(fn_txt)} '
                f'<a href="#fnref-{entry_id}-{fn_num}" class="footnote-backref" aria-label="Back to content">↩</a>'
                f'</li>'
            )
        out_blocks.append(
            f'<aside class="entry-footnotes" aria-label="Footnotes">'
            f'<h4>Notes</h4><ol>{"".join(fn_items)}</ol></aside>'
        )

    return "\n".join(out_blocks), headings_text

def parse_s16_metadata(s16_html, s16_plain, s16_links, canonical_tags):
    """
    Parses the s16 subtitle line into:
    - sources_raw: clean string of sources/references
    - sources_html: HTML string of sources/references (preserving links, upright & balanced)
    - tags: list of canonical tag strings (without '#')
    """
    raw = s16_plain.strip()
    if '|' in raw:
        left_plain, right_plain = raw.rsplit('|', 1)
        if '|' in s16_html:
            left_html, _ = s16_html.rsplit('|', 1)
        else:
            left_html = html.escape(left_plain)
    elif raw.startswith('#'):
        left_plain, left_html = "", ""
        right_plain = raw
    else:
        left_plain, left_html = raw, s16_html
        right_plain = ""

    # Strip inline style wrappers (em/strong/u/s/span/mark) from s16 subtitle HTML
    # so splitting on '|' never leaves an unclosed <em> tag!
    left_html = re.sub(r'</?(?:em|strong|u|s|span|mark)\b[^>]*>', '', left_html)
    if left_html.count('<a ') > left_html.count('</a>'):
        left_html += '</a>' * (left_html.count('<a ') - left_html.count('</a>'))

    # Clean sources
    left_plain = left_plain.strip()
    left_html = left_html.strip()
    if left_plain.lower() in ("none", "null", "[references]", "??", "???", ""):
        left_plain = ""
        left_html = ""
    else:
        # Remove accidental leading '#' on book names like '#Matthew 14:13-21' or '#Moroni 7'
        left_plain = re.sub(r'^#([A-Za-z])', r'\1', left_plain)
        left_html = re.sub(r'^#([A-Za-z])', r'\1', left_html)

    # Extract tags from right_plain
    raw_tags = re.findall(r'#([A-Za-z0-9_\-]+)', right_plain)
    tags = []
    for rt in raw_tags:
        if rt.lower() in ("tags", "tag"):
            continue
        low = rt.lower()
        if low in TAG_TYPO_FIXES:
            canon = TAG_TYPO_FIXES[low]
            canonical_tags[canon.lower()] = canon
        elif low in canonical_tags:
            canon = canonical_tags[low]
        else:
            # Prefer UpperCamelCase if first char is lowercase
            canon = rt[0].upper() + rt[1:] if rt and rt[0].islower() else rt
            canonical_tags[low] = canon
        if canon not in tags:
            tags.append(canon)

    return left_plain, left_html, tags

def parse_journal_file(fname, file_prefix, source_label, img_out_dir, canonical_tags):
    with open(fname, 'r', encoding='latin1') as f:
        raw_data = f.read()
    colortbl = parse_colortbl(raw_data)
    clean_data, images, footnotes_map, listtexts = preprocess_rtf(raw_data, file_prefix, img_out_dir)
    paras = parse_rtf_paragraphs_list(clean_data, colortbl, images, footnotes_map, listtexts)

    # Step 1: Identify all s16 entry subtitle anchors
    anchors = []
    i = 0
    while i < len(paras):
        p = paras[i]
        if p["style"] == "s16" and p["plain"]:
            if p["plain"] == "Michael Garrett Russell":
                i += 1
                continue
            if p["plain"] in ("Chiasmuses", "Complex Narratives and Characters"):
                i += 1
                continue
            s16_start = i
            s16_end = i
            if i + 1 < len(paras) and paras[i+1]["style"] == "s16" and paras[i+1]["plain"]:
                s16_end = i + 1
                i += 1
            anchors.append((s16_start, s16_end))
        i += 1

    # Step 2: For each anchor, find title_idx and date_idx / entry_start_idx
    entry_Bounds = []
    current_date = None
    for a_idx, (s16_start, s16_end) in enumerate(anchors):
        prev_s16_end = anchors[a_idx - 1][1] if a_idx > 0 else 0
        # Find title_idx: first non-empty paragraph before s16_start
        title_idx = s16_start - 1
        while title_idx > prev_s16_end and not paras[title_idx]["plain"]:
            title_idx -= 1

        entry_start = title_idx
        # Look backwards before title_idx for s1 date or empty s1 paragraphs
        scan = title_idx - 1
        while scan > prev_s16_end:
            sp = paras[scan]
            if not sp["plain"]:
                if sp["style"] == "s1":
                    entry_start = scan
                scan -= 1
                continue
            if sp["style"] == "s1" and DATE_RE.match(sp["plain"]):
                current_date = sp["plain"]
                entry_start = scan
                scan -= 1
                while scan > prev_s16_end and not paras[scan]["plain"] and paras[scan]["style"] == "s1":
                    entry_start = scan
                    scan -= 1
            break

        entry_Bounds.append({
            "entry_start": entry_start,
            "title_idx": title_idx,
            "s16_start": s16_start,
            "s16_end": s16_end,
            "raw_date": current_date,
        })

    # Step 3: Build structured entries
    entries = []
    for idx, b in enumerate(entry_Bounds):
        body_start = b["s16_end"] + 1
        body_end = entry_Bounds[idx + 1]["entry_start"] if idx + 1 < len(entry_Bounds) else len(paras)

        title_p = paras[b["title_idx"]]
        title_plain = title_p["plain"]
        # Clean leading '#' if title starts with '#HearHim' -> keep '#HearHim' as display title

        # Combine s16 paragraphs if split across 2 lines
        s16_paras = paras[b["s16_start"] : b["s16_end"] + 1]
        s16_plain = " ".join(p["plain"] for p in s16_paras if p["plain"])
        s16_html = " ".join(p["html"] for p in s16_paras if p["html"])
        s16_links = [lnk for p in s16_paras for lnk in p["links"]]

        sources_raw, sources_html, tags = parse_s16_metadata(s16_html, s16_plain, s16_links, canonical_tags)
        if not tags:
            fallback_map = {
                "Antagonists of The Book Of Mormon": ["Antichrist", "Sherem", "Nehor", "Amlici"],
                "Alma 5": ["Alma", "Conversion", "ChangeOfHeart"],
                "The Patriarchal Order": ["Patriarch", "Family", "Priesthood"],
                "Patriarchy": ["Patriarch", "Marriage", "Family"],
                "An Appeal for Mercy from Scriptural Accounts": ["Mercy", "Atonement", "Repentance"],
            }
            for fb_t in fallback_map.get(title_plain, []):
                canon = canonical_tags.get(fb_t.lower(), fb_t)
                canonical_tags[fb_t.lower()] = canon
                tags.append(canon)

        # Normalize date
        raw_date = b["raw_date"]
        # Fix the single known typo in ARCHIVE entry #13 ('What Did the Atonement Involve as Payment for Sins?')
        # which is between two 8/1/19 entries and 8/25/19 but typed '8/1/21'
        if file_prefix == "archive" and raw_date == "8/1/21" and idx < 20:
            norm_date_str = "8/1/19"
        else:
            norm_date_str = raw_date

        m, d, y = [int(x) for x in norm_date_str.split('/')]
        if y < 100:
            y += 2000
        dt_obj = datetime(y, m, d)
        iso_date = dt_obj.strftime("%Y-%m-%d")
        display_date = dt_obj.strftime("%B %d, %Y").replace(" 0", " ")

        entry_id = f"{iso_date}-{slugify(title_plain)[:60]}"
        body_paras = paras[body_start:body_end]
        body_html, subheadings = render_entry_body(entry_id, body_paras)
        body_plain = "\n".join(p["plain"] for p in body_paras if p["plain"])

        # Extract scripture references from header AND from subheadings/body
        header_scriptures = extract_header_scriptures(sources_raw)
        body_scriptures = extract_scriptures_from_text("\n".join(subheadings) + "\n" + body_plain)

        # Combine into primary_scriptures and all_scriptures
        all_scriptures = []
        seen_refs = set()
        for sc in header_scriptures + body_scriptures:
            if sc["ref"] not in seen_refs:
                seen_refs.add(sc["ref"])
                all_scriptures.append({
                    **sc,
                    "is_primary": sc in header_scriptures
                })

        # Word count & reading time
        words = len(re.findall(r'\w+', body_plain))
        reading_mins = max(1, round(words / 200))

        # Excerpt
        first_para_texts = [
            p["plain"] for p in body_paras
            if p["plain"] and p["style"] == "s0" and not p["intbl"] and len(p["plain"]) > 30
        ]
        excerpt_src = first_para_texts[0] if first_para_texts else body_plain
        excerpt = re.sub(r'\s+', ' ', excerpt_src).strip()
        if len(excerpt) > 220:
            excerpt = excerpt[:217].rsplit(' ', 1)[0] + "…"

        entries.append({
            "id": entry_id,
            "title": title_plain,
            "date": iso_date,
            "display_date": display_date,
            "raw_date": raw_date,
            "year": y,
            "month": dt_obj.strftime("%Y-%m"),
            "month_num": m,
            "sources_raw": sources_raw,
            "sources_html": sources_html,
            "tags": tags,
            "header_scriptures": header_scriptures,
            "scriptures": all_scriptures,
            "scripture_books": sorted({sc["book"] for sc in all_scriptures}),
            "scripture_works": sorted({sc["work"] for sc in all_scriptures}),
            "subheadings": subheadings,
            "word_count": words,
            "reading_mins": reading_mins,
            "excerpt": excerpt,
            "body_html": body_html,
            "body_plain": body_plain,
            "has_table": '<table class="study-table">' in body_html,
            "has_figure": '<figure class="study-figure">' in body_html,
            "has_chiasm": 'study-chiasm-group' in body_html or 'Chiasm' in tags or 'Chiasmus' in tags,
        })

    return entries

def extract_all_entries(archive_path, current_path, img_out_dir):
    canonical_tags = {}
    first_entries = parse_journal_file(
        archive_path, "archive", "Gospel Study Journal", img_out_dir, canonical_tags
    )
    second_entries = parse_journal_file(
        current_path, "current", "Gospel Study Journal", img_out_dir, canonical_tags
    )
    all_entries = first_entries + second_entries
    # Ensure unique IDs if two entries on same day have similar titles
    seen_ids = {}
    for e in all_entries:
        base_id = e["id"]
        if base_id in seen_ids:
            seen_ids[base_id] += 1
            e["id"] = f"{base_id}-{seen_ids[base_id]}"
        else:
            seen_ids[base_id] = 1
    return all_entries
