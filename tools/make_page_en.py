"""Builds the English blueprint page (HTML) from the SVG sheets and tdr1_numbers.json."""
import json, re
EN = {"DDR5-6400 (non-ECC)": "DDR5-6400 (non-ECC)", "DDR5-9600 (non-ECC, hypothetisch)": "DDR5-9600 (non-ECC, hypothetical)",
      "DDR5-9600 ECC (80-bit)": "DDR5-9600 ECC (80-bit)", "TDR1-9600 BL18 (met ECC)": "TDR1-9600 BL18 (with ECC)",
      "TDR1-9600 BL16P (zonder ECC)": "TDR1-9600 BL16P (no ECC)", "TDR1-10800 BL18 (met ECC)": "TDR1-10800 BL18 (with ECC)",
      "DDR5-21600 (non-ECC, hypothetisch)": "DDR5-21600 (non-ECC, hypothetical)", "TDR1-21600 BL18 (met ECC)": "TDR1-21600 BL18 (with ECC)",
      "DQ (2x32)": "DQ (2x32)", "DQS_t/DQS_c (8 paren)": "DQS_t/DQS_c (8 pairs)", "CA (2x10, DDR)": "CA (2x10, DDR)",
      "CS_n (2 per subkanaal)": "CS_n (2 per subchannel)", "CK_t/CK_c ingang naar TCKD": "CK_t/CK_c input to TCKD",
      "PAR (CA-pariteit)": "PAR (CA parity)", "HSCL/HSDA/HSA (I3C zijband)": "HSCL/HSDA/HSA (I3C sideband)",
      "VSS (massa)": "VSS (ground)", "RFU (gereserveerd)": "RFU (reserved)"}
N = json.load(open("tdr1_numbers.json"))
sheets = [re.sub(r' width="\d+" height="\d+"', ' preserveAspectRatio="xMidYMid meet"',
                 open(f"sheet{i}-en.svg").read(), count=1) for i in (1, 2, 3)]
nl = lambda x: f"{x:.1f}"
nl2 = lambda x: f"{x:.2f}"

speed_rows = "".join(
    f"<tr><td>{s['bin']}</td><td>{s['ck_mhz']:.0f}</td><td>{s['ddr5_equiv_ck_mhz']:.0f}</td>"
    f"<td>{nl(s['ui_ps'])}</td><td>{nl(s['raw_gbs'])}</td><td>{nl(s['data_bl18_gbs'])}</td>"
    f"<td>{nl2(s['burst_ns'])}</td></tr>" for s in N["speed"])
tim_rows = "".join(
    f"<tr><td>{r['bin']}</td><td>{r['tAA']['cycles']} <small>({nl2(r['tAA']['ns'])})</small></td>"
    f"<td>{r['tRCD']['cycles']}</td><td>{r['tRP']['cycles']}</td><td>{r['tRAS']['cycles']}</td>"
    f"<td>{r['CWL']}</td><td>{r['ddr5_CL_same_mts']}</td></tr>" for r in N["timings"])
en_rows = ""
for k, v in N["energy"].items():
    tdr = k.startswith("TDR1")
    rel = N["energy_rel"][k]
    en_rows += (f"<tr class=\"{'hl' if tdr else ''}\"><td>{EN.get(k, k)}</td><td>{nl2(v['parts']['array'])}</td>"
                f"<td>{nl2(v['parts']['io'])}</td><td>{nl2(v['parts']['clock_ca'])}</td>"
                f"<td><b>{nl2(v['total'])}</b></td><td>{'+' if rel > 0 else ''}{nl(rel)}%</td>"
                f"<td>{nl(v['GBs_per_W'])}</td></tr>")
pin_rows = "".join(f"<tr><td>{EN.get(k, k)}</td><td>{v}</td></tr>" for k, v in N["pins"].items())
s96 = N["speed"][2]

html = f"""<title>TDR1 SDRAM Blueprint</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>
/* Layout: one drawing-sheet column, sheets as framed drawings, data as dimension tables. One deliberate world: blueprint. */
:root {{
  --paper: #123a6b; --paper-2: #0f3260; --grid: #1d4a80;
  --ink: #e8f1ff; --ink-2: #9fc0e8; --pencil: #f4c95d;
  --f-head: "Barlow Condensed", "Arial Narrow", sans-serif;
  --f-body: "IBM Plex Sans", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
  color-scheme: dark;
}}
body {{ background: var(--paper); color: var(--ink); font-family: var(--f-body); line-height: 1.55;
  background-image: linear-gradient(var(--grid) 1px, transparent 1px), linear-gradient(90deg, var(--grid) 1px, transparent 1px);
  background-size: 24px 24px; }}
.wrap {{ max-width: 1040px; margin: 0 auto; padding-block: 40px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 40px; }}
header {{ border: 1.5px solid var(--ink); padding: 20px 22px; background: var(--paper-2);
  display: grid; grid-template-columns: 1fr auto; gap: 8px 24px; align-items: end; }}
.eyebrow {{ font-family: var(--f-mono); font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--pencil); margin: 0; }}
h1 {{ font-family: var(--f-head); font-weight: 700; font-size: clamp(40px, 7vw, 72px); line-height: .95; margin: 4px 0 0; letter-spacing: .01em; text-wrap: balance; }}
.rev {{ font-family: var(--f-mono); font-size: 12px; color: var(--ink-2); text-align: right; line-height: 1.7; }}
.lede {{ grid-column: 1 / -1; max-width: 68ch; color: var(--ink-2); margin: 10px 0 0; }}
.figs {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); border: 1px solid var(--ink-2); }}
.fig {{ padding: 14px 16px; border-right: 1px solid var(--grid); border-bottom: 1px solid var(--grid); min-width: 0; }}
.fig b {{ display: block; font-family: var(--f-head); font-size: 30px; font-weight: 600; line-height: 1.1; font-variant-numeric: tabular-nums; }}
.fig span {{ font-size: 12.5px; color: var(--ink-2); }}
.fig.acc b {{ color: var(--pencil); }}
section {{ display: grid; gap: 14px; min-width: 0; }}
h2 {{ font-family: var(--f-head); font-weight: 600; font-size: 28px; margin: 0; letter-spacing: .02em; text-wrap: balance; }}
h2 small {{ font-family: var(--f-mono); font-size: 12px; color: var(--pencil); letter-spacing: .1em; margin-right: 10px; vertical-align: middle; }}
p {{ margin: 0; max-width: 70ch; }}
.muted {{ color: var(--ink-2); }}
.sheet {{ overflow-x: auto; border: 1.5px solid var(--ink); background: var(--paper); }}
.sheet svg {{ display: block; width: 100%; min-width: 720px; height: auto; }}
.tbl {{ overflow-x: auto; border: 1px solid var(--ink-2); }}
table {{ border-collapse: collapse; width: 100%; font-family: var(--f-mono); font-size: 13px; font-variant-numeric: tabular-nums; }}
th, td {{ padding: 8px 12px; text-align: right; border-bottom: 1px solid var(--grid); white-space: nowrap; }}
th:first-child, td:first-child {{ text-align: left; }}
th {{ font-weight: 600; color: var(--ink-2); font-size: 11.5px; letter-spacing: .06em; text-transform: uppercase; background: var(--paper-2); }}
tr.hl td {{ color: var(--pencil); }}
td small {{ color: var(--ink-2); }}
.two {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }}
.two > * {{ min-width: 0; }}
.note {{ border-left: 3px solid var(--pencil); padding: 10px 14px; background: var(--paper-2); font-size: 14px; color: var(--ink-2); }}
.note b {{ color: var(--ink); }}
ul {{ margin: 0; padding-left: 20px; display: grid; gap: 6px; max-width: 72ch; }}
footer {{ font-family: var(--f-mono); font-size: 11.5px; color: var(--ink-2); border-top: 1px solid var(--ink-2); padding-top: 14px; }}
@media (max-width: 560px) {{ header {{ grid-template-columns: 1fr; }} .rev {{ text-align: left; }} }}
</style>

<div class="wrap">
<header>
  <div><p class="eyebrow">Concept specification · Triple Data Rate</p><h1>TDR1 SDRAM</h1></div>
  <div class="rev">REV 0.2.0<br>2026-10-17<br>STATUS: CONCEPT</div>
  <p class="lede">Main memory that moves <b>three</b> data transfers per clock period. One external clock, three internal phases at 0°, 120° and 240°, and ECC built into every burst. Laid out as a JEDEC-style module that can sit alongside DDR5.</p>
</header>

<div class="figs">
  <div class="fig acc"><b>3×</b><span>transfers per clock period</span></div>
  <div class="fig"><b>{nl(s96['raw_gbs'])} GB/s</b><span>TDR1-9600, raw per module</span></div>
  <div class="fig"><b>{s96['ck_mhz']:.0f} MHz</b><span>clock (DDR5 needs {s96['ddr5_equiv_ck_mhz']:.0f})</span></div>
  <div class="fig"><b>16/128</b><span>ECC bits per chip, no extra chip</span></div>
  <div class="fig acc"><b>{nl(N['tdr_vs_ddr5ecc_pct'])}%</b><span>energy per bit vs DDR5 ECC (model)</span></div>
  <div class="fig"><b>288</b><span>pins, DIMM form factor</span></div>
</div>

<section>
  <h2><small>SHEET 1</small>Module layout</h2>
  <p class="muted">Top view of a single-rank TDR1 UDIMM with x8 chips. The outline matches a 288-pin DDR5 UDIMM, but the key notch sits elsewhere, so the module cannot go into a DDR5 slot. The clock driver (TCKD) generates the three phases on the module itself.</p>
  <div class="sheet">{sheets[0]}</div>
</section>

<section>
  <h2><small>SHEET 2</small>Timing and burst</h2>
  <p class="muted">Each clock period carries three bits per data pin, one on each phase. A burst has 18 transfers: 16 data and 2 ECC. That makes a burst exactly 6 clock periods long, and a 64-byte cache line fits it cleanly.</p>
  <div class="sheet">{sheets[1]}</div>
</section>

<section>
  <h2><small>SHEET 3</small>Chip architecture</h2>
  <p class="muted">One 36 Gb TDR1 chip: 32 Gb for data and 4 Gb for check bits. The memory core resembles DDR5, with 8 bank groups of 4 banks. New are the 3-phase DLL, the 18:1 serializer per data pin, and the ECC/CRC check on writes.</p>
  <div class="sheet">{sheets[2]}</div>
</section>

<section>
  <h2><small>TABLE A</small>Speed bins</h2>
  <div class="tbl"><table>
    <thead><tr><th>Bin</th><th>CK MHz</th><th>DDR5 clock at same MT/s</th><th>UI ps</th><th>Raw GB/s</th><th>Data GB/s (BL18)</th><th>Burst ns</th></tr></thead>
    <tbody>{speed_rows}</tbody></table></div>
  <p class="muted">GB/s per module with 64 data pins. The ECC beats cost 11% of bandwidth. In exchange, a DDR5 ECC module needs 80 pins and 10 chips for the same 64 data bits.</p>
  <p class="note"><b>TDR1-21600 is a future bin.</b> A bit lasts 46 ps there, less than half that of today's fastest DDR5. A normal plug-in module cannot do that: it needs CAMM2 or memory soldered right next to the processor, as GDDR7 does (32 Gb/s per pin). According to the model the module then draws about 20 W and needs a heat spreader.</p>
</section>

<section>
  <h2><small>TABLE B</small>Timings in clock periods</h2>
  <div class="tbl"><table>
    <thead><tr><th>Bin</th><th>CL (ns)</th><th>tRCD</th><th>tRP</th><th>tRAS</th><th>CWL</th><th>DDR5 CL at same MT/s</th></tr></thead>
    <tbody>{tim_rows}</tbody></table></div>
  <p class="muted">The core has the same latency as DDR5-class memory (assumption: tAA, tRCD and tRP ≈ 16 ns, tRAS ≈ 32 ns, tRFC 410 ns). Because the clock ticks slower, the cycle counts are lower, but the time in nanoseconds stays the same. All-bank refresh takes about {nl(N['refresh_overhead_allbank_pct'])}% of the time; same-bank refresh reduces that.</p>
</section>

<section class="two">
  <div style="display:grid;gap:14px;min-width:0">
    <h2><small>TABLE C</small>Energy model</h2>
    <div class="tbl"><table>
      <thead><tr><th>Memory</th><th>Array</th><th>I/O</th><th>Clock/CA</th><th>pJ/bit</th><th>vs DDR5-9600</th><th>GB/s per W</th></tr></thead>
      <tbody>{en_rows}</tbody></table></div>
    <p class="note"><b>Model, not a measurement.</b> The baseline is an assumed DDR5-6400 at ±15 pJ/bit; published figures range from roughly 10 to 40 pJ/bit. TDR1 gains come from the lower clock frequency per bit, the lower I/O voltage (0.95 V) and having no extra ECC chips.</p>
  </div>
  <div style="display:grid;gap:14px;min-width:0;align-content:start">
    <h2><small>TABLE D</small>Pin budget</h2>
    <div class="tbl"><table>
      <thead><tr><th>Signal</th><th>Pins</th></tr></thead>
      <tbody>{pin_rows}<tr class="hl"><td>Total</td><td>{N['pins_total']}</td></tr></tbody></table></div>
  </div>
</section>

<section>
  <h2><small>NOTE</small>Limits of this design</h2>
  <ul>
    <li>Per pin, TDR1 is no easier than DDR5: at 9600 MT/s a bit lasts 104 ps, just like DDR5-9600. The gain is in the clock and the power, not in the signal itself.</li>
    <li>The three phases must match to within about 2% of a bit time. Any mismatch costs margin and is trained out at boot.</li>
    <li>A new memory controller is required. A standard DDR5 processor cannot drive TDR1.</li>
    <li>A real TDR1 chip needs a DRAM fab. The first feasible prototype is a simulation and an FPGA model, as laid out in the specification.</li>
  </ul>
</section>

<footer>TDR1 SDRAM · blueprint rev 0.2.0 (sheets rev 0.1.0) · Concept design, not an existing standard. Figures come from a calculation model; assumptions are stated.</footer>
</div>
"""
open("TDR1-blueprint-en.html", "w").write(html)
print(len(html) // 1024, "KB")
