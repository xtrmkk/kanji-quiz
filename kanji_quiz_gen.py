import random
import io
import argparse
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from kanji_quiz_data import PAIRS

pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))

GOTHIC  = 'HeiseiKakuGo-W5'
MINCHO  = 'HeiseiMin-W3'

PAGE_W, PAGE_H = A4   # 595 × 842
ML = 28               # left margin
MR = 28               # right margin
MT = 28               # top margin
COL_GAP = 11          # gap between columns
COL_W = (PAGE_W - ML - MR - COL_GAP) / 2   # ≈ 264 pt per column


def col_x(col):
    return ML + col * (COL_W + COL_GAP)


def select_questions():
    pool = list(PAIRS)
    random.shuffle(pool)

    # Build a canonical pair set to avoid showing the same pair twice
    used_canonical = set()

    def canonical(p):
        return frozenset([p[1], p[3]])

    # Section A: 読み仮名 → 漢字 (升目)
    a_pool = []
    for p in pool:
        if len(a_pool) >= 20:
            break
        c = canonical(p)
        if c not in used_canonical:
            a_pool.append(p)
            used_canonical.add(c)

    a_used_words = set()
    a_qs = []
    for p in a_pool:
        if random.random() < 0.5:
            a_qs.append((p[2], p[1]))   # (reading, kanji)
            a_used_words.add(p[1])
        else:
            a_qs.append((p[4], p[3]))
            a_used_words.add(p[3])

    # Section B: 漢字 → 読み仮名 (A の単語と被らないペアから)
    b_pool = []
    for p in pool:
        if len(b_pool) >= 20:
            break
        c = canonical(p)
        if c in used_canonical:
            continue
        if p[1] in a_used_words or p[3] in a_used_words:
            continue
        b_pool.append(p)
        used_canonical.add(c)

    if len(b_pool) < 20:
        # Fallback: only avoid exact same canonical pairs
        b_pool = []
        for p in pool:
            if len(b_pool) >= 20:
                break
            c = canonical(p)
            if c in used_canonical:
                continue
            b_pool.append(p)
            used_canonical.add(c)

    b_qs = []
    for p in b_pool:
        if random.random() < 0.5:
            b_qs.append((p[1], p[2]))   # (kanji, reading)
        else:
            b_qs.append((p[3], p[4]))

    # Section C: 単語 → 対義語 (A・B 未使用の canonical pair から)
    c_pool = []
    for p in pool:
        c = canonical(p)
        if c in used_canonical:
            continue
        c_pool.append(p)
        used_canonical.add(c)

    # Select 20 questions ensuring no duplicate question words
    c_used_q_words = set()
    c_qs = []
    random.shuffle(c_pool)
    for p in c_pool:
        if len(c_qs) >= 20:
            break
        options = []
        if p[1] not in c_used_q_words:
            options.append((p[1], p[3]))
        if p[3] not in c_used_q_words:
            options.append((p[3], p[1]))
        if not options:
            continue
        random.shuffle(options)
        q, a = options[0]
        c_used_q_words.add(q)
        c_qs.append((q, a))

    return a_qs, b_qs, c_qs


# ── drawing helpers ──────────────────────────────────────────────────────────

def draw_divider(c, y, width=1.5):
    c.setLineWidth(width)
    c.line(ML, y, PAGE_W - MR, y)
    c.setLineWidth(0.5)


def draw_header(c, y):
    c.setFont(GOTHIC, 14)
    c.drawString(ML, y, '国語テスト（対義語）')
    c.setFont(GOTHIC, 10)
    c.drawRightString(PAGE_W - MR, y, '年　　組　　番')
    y -= 18

    c.setFont(GOTHIC, 10)
    c.drawString(ML, y, '名前：')
    c.line(ML + 42, y - 2, ML + 240, y - 2)
    c.drawRightString(PAGE_W - MR, y, '合計（　　　）点')
    y -= 9

    draw_divider(c, y, 1.5)
    y -= 13

    # Section score boxes
    c.setFont(GOTHIC, 10)
    spacing = 110
    for i, label in enumerate(['一', '二', '三']):
        bx = ML + i * spacing
        c.drawString(bx, y, f'【{label}】')
        c.rect(bx + 28, y - 2, 48, 16, stroke=1, fill=0)
        c.drawString(bx + 80, y, '点')
    y -= 10

    draw_divider(c, y, 2)
    y -= 8

    return y


def _draw_section(c, y, title, questions, num_offset, row_h, draw_row_fn):
    """Draw a section with title, separator, and question rows."""
    # Section title
    c.setFont(GOTHIC, 11)
    c.drawString(ML, y, title)
    y -= 16   # title text height + breathing room

    draw_divider(c, y, 0.5)
    y -= 6    # breathing room before first question

    for i in range(10):
        row_y = y - i * row_h
        for col in range(2):
            q_idx = i + col * 10
            if q_idx >= len(questions):
                continue
            num = q_idx + num_offset
            draw_row_fn(c, questions[q_idx], num, col_x(col), row_y)

        # Thin guide line in the gap between this row and the next
        if i < 9:
            c.setStrokeColorRGB(0.82, 0.82, 0.82)
            c.line(ML, row_y - 5, PAGE_W - MR, row_y - 5)
            c.setStrokeColorRGB(0, 0, 0)

    # Vertical column divider
    mid_x = col_x(0) + COL_W + COL_GAP / 2
    c.setStrokeColorRGB(0.65, 0.65, 0.65)
    c.line(mid_x, y, mid_x, y - 10 * row_h)
    c.setStrokeColorRGB(0, 0, 0)

    y -= 10 * row_h + 6
    draw_divider(c, y, 1)
    y -= 8

    return y


def _row_a(c, q, num, x, row_y):
    reading, kanji = q
    BOX_SZ = 18

    c.setFont(GOTHIC, 9)
    c.drawRightString(x + 24, row_y, f'{num}.')

    c.setFont(MINCHO, 11)
    c.drawString(x + 26, row_y, reading)

    # Masume boxes (one per kanji character, all words are 2-char 熟語)
    box_x = x + 124
    for b in range(len(kanji)):
        c.rect(box_x + b * (BOX_SZ + 2), row_y - 3, BOX_SZ, BOX_SZ, stroke=1, fill=0)


def _row_b(c, q, num, x, row_y):
    kanji, _ = q
    c.setFont(GOTHIC, 9)
    c.drawRightString(x + 24, row_y, f'{num}.')
    c.setFont(MINCHO, 12)
    c.drawString(x + 26, row_y, kanji)
    line_x = x + 58
    c.line(line_x, row_y - 2, line_x + 100, row_y - 2)


def _row_c(c, q, num, x, row_y):
    word, _ = q
    c.setFont(GOTHIC, 9)
    c.drawRightString(x + 24, row_y, f'{num}.')
    c.setFont(MINCHO, 12)
    c.drawString(x + 26, row_y, word)

    # Draw arrow →
    ax = x + 58
    c.setLineWidth(0.8)
    c.line(ax, row_y + 4, ax + 10, row_y + 4)
    c.line(ax + 6, row_y + 7, ax + 10, row_y + 4)
    c.line(ax + 6, row_y + 1, ax + 10, row_y + 4)
    c.setLineWidth(0.5)

    line_x = x + 73
    c.line(line_x, row_y - 2, line_x + 95, row_y - 2)


# ── main generator ────────────────────────────────────────────────────────────

def generate_pdf(output_path=None):
    a_qs, b_qs, c_qs = select_questions()

    buf = io.BytesIO()
    cv = canvas.Canvas(buf, pagesize=A4)
    cv.setLineWidth(0.5)

    y = PAGE_H - MT
    y = draw_header(cv, y)
    y = _draw_section(cv, y, '【一】読み仮名を見て漢字を書きなさい', a_qs, 1,  22, _row_a)
    y = _draw_section(cv, y, '【二】漢字の読み仮名をひらがなで書きなさい', b_qs, 21, 20, _row_b)
    y = _draw_section(cv, y, '【三】対義語を書きなさい', c_qs, 41, 20, _row_c)

    cv.showPage()
    cv.save()

    pdf_bytes = buf.getvalue()
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f'生成: {output_path}')
    return pdf_bytes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='漢字テストPDF生成')
    parser.add_argument('--count', type=int, default=1, help='生成枚数')
    args = parser.parse_args()

    for i in range(args.count):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        suffix = f'_{i+1}' if args.count > 1 else ''
        path = f'/Users/yizhenchen/Desktop/test_random/漢字テスト_{ts}{suffix}.pdf'
        generate_pdf(path)
