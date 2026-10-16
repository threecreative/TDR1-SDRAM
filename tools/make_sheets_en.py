"""Generates the three TDR1 SDRAM 0.1.0 blueprint sheets as SVG (English)."""
import json

N = json.load(open("tdr1_numbers.json"))
BG, GRID, LINE, DIM, ACC = "#123a6b", "#1d4a80", "#e8f1ff", "#9fc0e8", "#f4c95d"
FONT = "IBM Plex Mono, DejaVu Sans Mono, Menlo, monospace"
HEAD = "Barlow Condensed, DejaVu Sans Condensed, Arial Narrow, sans-serif"

def svg(w, h, body, title):
    grid = (f'<defs><pattern id="g{title}" width="20" height="20" patternUnits="userSpaceOnUse">'
            f'<path d="M20 0H0V20" fill="none" stroke="{GRID}" stroke-width="1"/></pattern></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="{FONT}" role="img" aria-label="{title}">{grid}'
            f'<rect width="{w}" height="{h}" fill="{BG}"/><rect width="{w}" height="{h}" fill="url(#g{title})"/>'
            f'{body}</svg>')

def t(x, y, s, size=11, fill=LINE, anchor="start", weight="400", fam=None):
    f = f' font-family="{fam}"' if fam else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}"{f}>{s}</text>')

def r(x, y, w, h, stroke=LINE, fill="none", sw=1.4, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def ln(x1, y1, x2, y2, stroke=LINE, sw=1, extra=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def arrow_defs(id_, color):
    return (f'<defs><marker id="{id_}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{color}"/></marker></defs>')

def dim_h(x1, x2, y, label, ext_from=None):
    out = arrow_defs("ad", DIM)
    if ext_from is not None:
        out += ln(x1, ext_from, x1, y + 4, DIM, 0.8) + ln(x2, ext_from, x2, y + 4, DIM, 0.8)
    out += ln(x1, y, x2, y, DIM, 1, 'marker-start="url(#ad)" marker-end="url(#ad)"')
    out += f'<rect x="{(x1+x2)/2-34}" y="{y-9}" width="68" height="14" fill="{BG}"/>'
    out += t((x1 + x2) / 2, y + 3, label, 10.5, DIM, "middle")
    return out

def dim_v(x, y1, y2, label, ext_from=None):
    out = ""
    if ext_from is not None:
        out += ln(ext_from, y1, x - 4, y1, DIM, 0.8) + ln(ext_from, y2, x - 4, y2, DIM, 0.8)
    out += ln(x, y1, x, y2, DIM, 1, 'marker-start="url(#ad)" marker-end="url(#ad)"')
    out += t(x + 8, (y1 + y2) / 2 + 4, label, 10.5, DIM)
    return out

def title_block(w, h, sheet, name, scale):
    x, y, bw, bh = w - 330, h - 64, 314, 52
    out = r(x, y, bw, bh, LINE, BG, 1.2)
    out += ln(x, y + 26, x + bw, y + 26, LINE, 0.8) + ln(x + 210, y, x + 210, y + bh, LINE, 0.8)
    out += t(x + 8, y + 18, name, 15, LINE, weight="600", fam=HEAD)
    out += t(x + 8, y + 43, f"REV 0.1.0 · {scale}", 9.5, DIM)
    out += t(x + 218, y + 18, "SHEET", 9.5, DIM)
    out += t(x + 218, y + 43, f"{sheet} / 3", 14, ACC, weight="600", fam=HEAD)
    out += t(x + 262, y + 18, "DATE", 9.5, DIM)
    out += t(x + 262, y + 43, "2026-10", 10, LINE)
    return out

# ======================= BLAD 1: MODULE =======================
def sheet1():
    W, H = 960, 470
    S, X0, Y0 = 6.0, 70, 70             # 6 px per mm
    L, HGT = 133.35, 31.25
    mx = lambda mm: X0 + mm * S
    my = lambda mm: Y0 + mm * S
    notch_c, notch_w, notch_d = 70.50, 1.40, 3.20
    finger_h = 3.0
    b = ""
    # printplaat-contour met inkeping en zijsloten
    nl, nr = notch_c - notch_w / 2, notch_c + notch_w / 2
    path = (f"M{mx(0)} {my(0)} H{mx(L)} V{my(13)} h-{2.2*S} v{3.4*S} h{2.2*S} V{my(HGT)} "
            f"H{mx(nr)} V{my(HGT-notch_d)} H{mx(nl)} V{my(HGT)} H{mx(0)} V{my(16.4)} h{2.2*S} v-{3.4*S} h-{2.2*S} Z")
    b += f'<path d="{path}" fill="#164479" stroke="{LINE}" stroke-width="1.8"/>'
    # contactvingers (patroon 0,85 mm)
    pitch = 0.85 * S
    b += (f'<defs><pattern id="fing" x="{mx(5.5)}" width="{pitch}" height="10" patternUnits="userSpaceOnUse">'
          f'<rect x="0.9" y="0" width="{pitch-1.8}" height="10" fill="{ACC}" opacity="0.55"/></pattern></defs>')
    fy = my(HGT - finger_h)
    b += f'<rect x="{mx(5.5)}" y="{fy}" width="{(nl-0.3-5.5)*S}" height="{finger_h*S-1}" fill="url(#fing)"/>'
    b += f'<rect x="{mx(nr+0.3)}" y="{fy}" width="{(127.85-nr-0.3)*S}" height="{finger_h*S-1}" fill="url(#fing)"/>'
    # DRAM-chips
    cw, chh, cy = 8.0, 11.0, 6.0
    xs = [5.0, 18.5, 32.0, 45.5, 79.85, 93.35, 106.85, 120.35]
    for i, cx in enumerate(xs):
        b += r(mx(cx), my(cy), cw * S, chh * S, LINE, "#0f3260", 1.4)
        b += f'<circle cx="{mx(cx)+6}" cy="{my(cy)+6}" r="2.2" fill="{LINE}"/>'
        b += t(mx(cx + cw / 2), my(cy) + 26, f"U{i+1}", 12, LINE, "middle", "600")
        b += t(mx(cx + cw / 2), my(cy) + 42, "36Gb", 9.5, DIM, "middle")
        b += t(mx(cx + cw / 2), my(cy) + 54, "x8", 9.5, DIM, "middle")
    # midden: PMIC, SPD-hub, TCKD
    b += r(mx(60.5), my(5.0), 8.0 * S, 7.0 * S, ACC, "#0f3260", 1.4)
    b += t(mx(64.5), my(8.3), "PMIC", 10.5, ACC, "middle", "600")
    b += t(mx(64.5), my(10.3), "5 V input", 7.5, DIM, "middle")
    b += r(mx(62.75), my(14.0), 3.5 * S, 3.5 * S, LINE, "#0f3260", 1.2)
    b += t(mx(64.5), my(16.2), "SPD", 8.5, LINE, "middle")
    b += r(mx(60.0), my(19.5), 9.0 * S, 5.0 * S, ACC, "#0f3260", 1.4)
    b += t(mx(64.5), my(22.0), "TCKD", 10.5, ACC, "middle", "600")
    b += t(mx(64.5), my(23.8), "3-phase PLL", 7.5, DIM, "middle")
    # subkanaal-accolades
    for x1, x2, lab in [(5.0, 53.5, "SUBCHANNEL A · DQ[31:0] · CA_A[9:0]"),
                        (79.85, 128.35, "SUBCHANNEL B · DQ[63:32] · CA_B[9:0]")]:
        y = my(19.2)
        b += f'<path d="M{mx(x1)} {y-6} v6 H{mx(x2)} v-6" fill="none" stroke="{DIM}" stroke-width="1"/>'
        b += t(mx((x1 + x2) / 2), y + 15, lab, 10, DIM, "middle")
    # maatvoering
    b += dim_h(mx(0), mx(L), my(HGT) + 42, "133.35", ext_from=my(HGT) + 4)
    b += dim_h(mx(0), mx(notch_c), my(HGT) + 70, "70.50", ext_from=my(HGT) + 4)
    b += dim_v(mx(L) + 34, my(0), my(HGT), "31.25", ext_from=mx(L) + 4)
    b += dim_h(mx(xs[0]), mx(xs[0] + cw), my(cy) - 16, "8.0", ext_from=my(cy) - 2)
    b += dim_v(mx(0) - 40, my(cy), my(cy + chh), "11.0")
    # callouts
    b += ln(mx(notch_c), my(HGT) + 2, mx(notch_c) + 70, my(HGT) + 26, ACC, 1)
    b += t(mx(notch_c) + 74, my(HGT) + 30, "TDR1 key notch (differs from DDR4/DDR5)", 10, ACC)
    b += ln(mx(18), my(HGT - 1.5), mx(18) - 10, my(HGT) + 22, ACC, 1)
    b += t(mx(4.0), my(HGT) + 26, "288 pins · 0.85 pitch", 10, ACC)
    # kop
    b += t(X0, 34, "TOP VIEW · TDR1 UDIMM 1Rx8 · 32 GB", 20, LINE, weight="600", fam=HEAD)
    b += t(X0, 52, "Dimensions in mm · outline matches 288-pin DDR5 UDIMM · 8 chips, ECC travels in the burst (no 9th/10th chip)", 10, DIM)
    b += title_block(W, H, 1, "MODULE LAYOUT", "SCALE 6:1 (screen)")
    return svg(W, H, b, "sheet1")

# ======================= BLAD 2: TIMING =======================
def sheet2():
    W, H = 960, 560
    X0, P = 170, 240            # 3 klokperiodes van 240 px
    b = arrow_defs("ad", DIM)
    b += t(40, 34, "TIMING · THREE TRANSFERS PER CLOCK PERIOD", 20, LINE, weight="600", fam=HEAD)
    s = N["speed"][2]
    b += t(40, 52, f"Example TDR1-9600: CK {s['ck_mhz']:.0f} MHz · tCK {s['tck_ns']*1000:.1f} ps · UI {s['ui_ps']} ps per bit", 10, DIM)
    rows = [("CK_t", 90), ("Φ0  0°", 140), ("Φ1  120°", 180), ("Φ2  240°", 220),
            ("DQ  TDR1", 280), ("DQ  DDR (ref.)", 340)]
    for name, y in rows:
        b += t(40, y + 4, name, 11, LINE if "TDR" in name or "CK" in name else DIM)
        b += ln(X0 - 10, y + 16, X0 + 3 * P + 10, y + 16, GRID, 0.8)
    # klokrandmarkeringen
    for k in range(4):
        x = X0 + k * P
        b += ln(x, 70, x, 372, DIM, 0.7, 'stroke-dasharray="3 4"')
    # CK
    y, hgt = 90, 26
    d = f"M{X0-10} {y+hgt}"
    for k in range(3):
        x = X0 + k * P
        d += f" H{x} V{y} H{x+P/2} V{y+hgt}"
    d += f" H{X0+3*P+10}"
    b += f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.8"/>'
    # fasen
    for i, (_, yy) in enumerate(rows[1:4]):
        d = f"M{X0-10} {yy+12}"
        for k in range(3):
            x = X0 + k * P + i * P / 3
            d += f" H{x} V{yy-6} H{x+16} V{yy+12}"
        d += f" H{X0+3*P+10}"
        b += f'<path d="{d}" fill="none" stroke="{ACC}" stroke-width="1.6"/>'
    # oogjes
    def eyes(y, n_per, labels, color, fill):
        out, ui = "", P / n_per
        for j in range(3 * n_per):
            x = X0 + j * ui
            e = 7
            out += (f'<path d="M{x} {y+4} L{x+e} {y-8} H{x+ui-e} L{x+ui} {y+4} L{x+ui-e} {y+16} H{x+e} Z" '
                    f'fill="{fill}" stroke="{color}" stroke-width="1.3"/>')
            out += t(x + ui / 2, y + 8, labels[j], 10, color, "middle", "600")
        return out
    b += eyes(280, 3, [f"D{i}" for i in range(9)], ACC, "#1a4f8c")
    b += eyes(340, 2, [f"D{i}" for i in range(6)], DIM, "none")
    # maatlijnen
    b += ln(X0, 66, X0 + P, 66, DIM, 1, 'marker-start="url(#ad)" marker-end="url(#ad)"')
    b += t(X0 + P / 2, 62, "tCK = 312.5 ps", 10, DIM, "middle")
    b += ln(X0, 306, X0 + P / 3, 306, ACC, 1, 'marker-start="url(#ad)" marker-end="url(#ad)"')
    b += t(X0 + P / 6, 322, "1 UI = tCK/3", 9.5, ACC, "middle")
    b += t(X0 + 3 * P + 20, 284, "9 bits", 10, ACC)
    b += t(X0 + 3 * P + 20, 344, "6 bits", 10, DIM)
    # BL18-frame
    fy, cw = 410, 40
    b += t(40, fy - 12, "BURST BL18 PER CHIP DQ · 16 DATA + 2 ECC = EXACTLY 6 tCK", 13, LINE, weight="600", fam=HEAD)
    for j in range(18):
        x = X0 - 130 + j * cw
        ecc = j >= 16
        b += r(x, fy, cw, 30, ACC if ecc else LINE, "#3a3a1a" if ecc else "#0f3260", 1.2)
        b += t(x + cw / 2, fy + 19, f"E{j-16}" if ecc else f"D{j}", 10.5, ACC if ecc else LINE, "middle", "600")
    for k in range(7):
        x = X0 - 130 + k * 3 * cw
        b += ln(x, fy - 4, x, fy + 40, DIM, 1)
        if k < 6:
            b += t(x + 1.5 * cw, fy + 52, f"tCK {k}", 9.5, DIM, "middle")
    b += t(X0 - 130, fy + 76, "Per x8 chip per burst: 8 × 18 = 144 bits → 128 data + 16 check (9 SEC-DED + 7 CRC).", 10, DIM)
    b += t(X0 - 130, fy + 92, f"Module: 64 DQ × 16 beats = two 64 B cache lines (1 per subchannel) in {s['burst_ns']} ns.", 10, DIM)
    b += title_block(W, H, 2, "TIMING / BURST", "NOT TO SCALE")
    return svg(W, H, b, "sheet2")

# ======================= BLAD 3: CHIP =======================
def sheet3():
    W, H = 960, 590
    b = arrow_defs("aw", LINE) + arrow_defs("aa", ACC)
    b += t(40, 34, "BLOCK DIAGRAM · TDR1 36 Gb x8 DIE", 20, LINE, weight="600", fam=HEAD)
    b += t(40, 52, "32 Gb data + 4 Gb check · 8 bank groups × 4 banks · 144-bit column path · 18:1 serializer per DQ", 10, DIM)
    def box(x, y, w, h, title, sub="", c=LINE, fill="#0f3260"):
        o = r(x, y, w, h, c, fill, 1.5)
        o += t(x + w / 2, y + h / 2 - (4 if sub else -4), title, 11.5, c, "middle", "600")
        if sub:
            o += t(x + w / 2, y + h / 2 + 12, sub, 9, DIM, "middle")
        return o
    def arr(x1, y1, x2, y2, c=LINE):
        return ln(x1, y1, x2, y2, c, 1.4, f'marker-end="url(#{"aa" if c==ACC else "aw"})"')
    # pinnen links
    pins = [("CK_t/c", 100), ("CA[9:0]  DDR", 190), ("CS_n · PAR", 250), ("DQS_t/c", 400), ("DQ[7:0]", 460)]
    for name, y in pins:
        b += t(40, y + 4, name, 10.5, LINE)
    b += box(150, 80, 150, 44, "CK receiver")
    b += box(340, 76, 170, 52, "3-PHASE DLL", "Φ0 0° · Φ1 120° · Φ2 240°", ACC)
    b += arr(120, 102, 148, 102) + arr(300, 102, 338, 102, ACC)
    b += box(150, 170, 150, 100, "CA receivers", "10 pins × 2 = 20 bit/tCK")
    b += box(340, 170, 170, 100, "Command decoder", "+ mode registers (MR)")
    b += arr(120, 194, 148, 194) + arr(120, 254, 148, 254) + arr(300, 220, 338, 220)
    # bankarray
    ax, ay = 560, 70
    b += r(ax, ay, 360, 250, LINE, "none", 1.5, 'stroke-dasharray="6 4"')
    b += t(ax + 10, ay + 18, "MEMORY ARRAY · 36 Gb", 11, LINE, weight="600")
    for g in range(8):
        gx, gy = ax + 14 + (g % 4) * 86, ay + 32 + (g // 4) * 104
        b += r(gx, gy, 78, 92, DIM, "#0f3260", 1)
        b += t(gx + 39, gy + 14, f"BG{g}", 9.5, DIM, "middle", "600")
        for k in range(4):
            b += r(gx + 8 + (k % 2) * 33, gy + 22 + (k // 2) * 34, 29, 28, LINE, "#164479", 0.9)
            b += t(gx + 22.5 + (k % 2) * 33, gy + 40 + (k // 2) * 34, f"B{k}", 8.5, LINE, "middle")
    b += arr(510, 220, 558, 220)
    b += t(425, 290, "ACT · RD · WR · REF → array", 9, DIM, "middle")
    # datapad
    b += box(560, 360, 170, 56, "Column path 144 bit", "128 data + 16 check")
    b += box(560, 440, 170, 56, "ECC / CRC check", "error → ALERT_n", ACC)
    b += box(340, 400, 170, 96, "SERDES 18:1", "per DQ · 6 tCK per burst", ACC)
    b += box(150, 400, 150, 96, "DQ/DQS I/O", "POD 0.95 V · 4-tap DFE")
    b += ln(645, 320, 645, 358, LINE, 1.4, 'marker-start="url(#aw)" marker-end="url(#aw)"')
    b += ln(645, 416, 645, 438, LINE, 1.4, 'marker-start="url(#aw)" marker-end="url(#aw)"')
    b += ln(558, 468, 512, 448, ACC, 1.4, 'marker-start="url(#aa)" marker-end="url(#aa)"')
    b += ln(338, 448, 302, 448, LINE, 1.4, 'marker-start="url(#aw)" marker-end="url(#aw)"')
    b += ln(120, 404, 148, 420, LINE, 1.2, 'marker-start="url(#aw)" marker-end="url(#aw)"')
    b += ln(120, 464, 148, 470, LINE, 1.2, 'marker-start="url(#aw)" marker-end="url(#aw)"')
    b += f'<path d="M510 112 H535 V420 H514" fill="none" stroke="{ACC}" stroke-width="1.2" stroke-dasharray="4 4" marker-end="url(#aa)"/>'
    b += t(541, 350, "Φ", 11, ACC)
    # zijblokken
    b += box(760, 360, 160, 56, "Refresh control", "all-bank · same-bank")
    b += box(760, 440, 160, 56, "Temp sensor + VREF", "VDD 1.05 · VPP 1.8")
    b += title_block(W, H, 3, "CHIP ARCHITECTURE", "NOT TO SCALE")
    return svg(W, H, b, "sheet3")

import re as _re
def _compact(svgtxt):
    def fix_attr(m):
        v = _re.sub(r"-?\d+\.\d+", lambda n: ("%.2f" % float(n.group(0))).rstrip("0").rstrip("."), m.group(2))
        return m.group(1) + '="' + v + '"'
    return _re.sub(r'(\s[\w:-]+)="([^"]*)"', fix_attr, svgtxt)
for i, f in enumerate([sheet1, sheet2, sheet3], 1):
    open(f"sheet{i}-en.svg", "w").write(_compact(f()))
print("ok")
