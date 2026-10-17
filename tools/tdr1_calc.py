"""TDR1 SDRAM v0.1.0 - rekenmodel. Alle getallen in de blueprint komen hieruit."""
import math, json

out = {}

# ---------- 1. Snelheidsklassen ----------
bins = [7200, 8400, 9600, 10800, 21600]   # 21600 = toekomstklasse (rev 0.2.0)
DATA_BITS = 64            # 2 subkanalen x 32 DQ
BL, DATA_BEATS = 18, 16   # BL18: 16 data + 2 ECC-beats
speed = []
for mts in bins:
    f_ck = mts / 3                      # MHz, 3 transfers per klok
    tck = 1e3 / f_ck                    # ns
    ui = 1e6 / mts                      # ps
    raw = mts * DATA_BITS / 8 / 1000    # GB/s
    eff_bl18 = raw * DATA_BEATS / BL
    ddr_ck = mts / 2
    speed.append(dict(bin=f"TDR1-{mts}", mts=mts, ck_mhz=round(f_ck,1), tck_ns=round(tck,4),
                      ui_ps=round(ui,1), raw_gbs=round(raw,1), data_bl18_gbs=round(eff_bl18,1),
                      data_bl16p_gbs=round(raw,1), ddr5_equiv_ck_mhz=ddr_ck,
                      burst_ns=round(6*tck,3), per_pin_gbps=mts/1000))
out["speed"] = speed

# ---------- 2. Timings (kernlatency gelijk aan DDR5-klasse, Aanname) ----------
core = dict(tAA=16.0, tRCD=16.0, tRP=16.0, tRAS=32.0, tRFC1=410.0, tRFCsb=130.0, tREFI=3900.0)
tim = []
for s in speed:
    tck = 1e3 / s["ck_mhz"]
    row = dict(bin=s["bin"])
    for k in ["tAA", "tRCD", "tRP", "tRAS"]:
        cyc = math.ceil(core[k] / tck - 1e-9)
        if k == "tAA" and cyc % 2: cyc += 1          # even CL zoals DDR5
        row[k] = dict(cycles=cyc, ns=round(cyc * tck, 2))
    row["CWL"] = row["tAA"]["cycles"] - 2
    row["tRFC1"] = dict(cycles=math.ceil(core["tRFC1"]/tck), ns=core["tRFC1"])
    # wat DDR5 bij dezelfde MT/s nodig zou hebben (klok = MT/s / 2)
    tck_ddr = 2e3 / s["mts"]
    row["ddr5_CL_same_mts"] = math.ceil(core["tAA"] / tck_ddr)
    tim.append(row)
out["timings"] = tim
out["refresh_overhead_allbank_pct"] = round(core["tRFC1"]/core["tREFI"]*100, 1)

# ---------- 3. Packed mode BL16P ----------
# burst = 16/3 tCK; startfase roteert 0 -> 1/3 -> 2/3
phases = [(16*k) % 3 for k in range(6)]
out["bl16p_phase_sequence"] = phases
out["bl16p_bursts_per_16tck"] = 3

# ---------- 4. Energiemodel (pJ per afgeleverde databit, lezen) ----------
# Basis DDR5-6400 UDIMM, Aanname (literatuur geeft grofweg 10-20+ pJ/bit):
base = dict(array=6.0, io=5.0, clock_ca=2.5)
OVH = 0.10  # PMIC/regelverlies + modulelogica

def total(d):
    s = sum(d.values()); return round(s*(1+OVH), 2), {k: round(v,2) for k,v in d.items()}

def ddr5(mts, ecc=False):
    io_eq = 1.0 + 0.10*(mts-6400)/3200          # extra equalisatie bij hogere snelheid
    width = 80/64 if ecc else 1.0                # ECC-DIMM: 80 pinnen voor 64 data
    ckd = 1.0 + (0.08 if mts >= 6400 else 0)     # CKD-chip op module
    return total(dict(array=base["array"]*width,
                      io=base["io"]*io_eq*width,
                      clock_ca=base["clock_ca"]*ckd))

def tdr1(mts, mode="BL18"):
    io_eq = 1.0 + 0.10*(mts-6400)/3200
    v = (0.95/1.10)**2                           # VDDQ 0,95 V i.p.v. 1,1 V
    beats = 18/16 if mode == "BL18" else 1.0
    cells = 144/136 if mode == "BL18" else 1.0   # t.o.v. DDR5 met on-die ECC (136/128)
    clk = (2/3) * 1.15 * 1.08                    # klok per bit 2/3, +15% 3-fasen-DLL, +8% TCKD
    return total(dict(array=base["array"]*cells,
                      io=base["io"]*v*io_eq*beats,
                      clock_ca=base["clock_ca"]*clk))

energy = {}
for name, fn in [("DDR5-6400 (non-ECC)", lambda: ddr5(6400)),
                 ("DDR5-9600 (non-ECC, hypothetisch)", lambda: ddr5(9600)),
                 ("DDR5-9600 ECC (80-bit)", lambda: ddr5(9600, ecc=True)),
                 ("TDR1-9600 BL18 (met ECC)", lambda: tdr1(9600)),
                 ("TDR1-9600 BL16P (zonder ECC)", lambda: tdr1(9600, "BL16P")),
                 ("TDR1-10800 BL18 (met ECC)", lambda: tdr1(10800)),
                 ("DDR5-21600 (non-ECC, hypothetisch)", lambda: ddr5(21600)),
                 ("TDR1-21600 BL18 (met ECC)", lambda: tdr1(21600))]:
    t, parts = fn()
    energy[name] = dict(total=t, parts=parts)
out["energy"] = energy
ref = energy["DDR5-9600 (non-ECC, hypothetisch)"]["total"]
refecc = energy["DDR5-9600 ECC (80-bit)"]["total"]
out["energy_rel"] = {k: round((v["total"]/ref-1)*100,1) for k,v in energy.items()}
out["tdr_vs_ddr5ecc_pct"] = round((energy["TDR1-9600 BL18 (met ECC)"]["total"]/refecc-1)*100,1)

# Vermogen I/O+kern bij volle bandbreedte (W per module) = pJ/bit * Gbit/s
for k, v in energy.items():
    mts = int(k.split("-")[1].split(" ")[0])
    data_gbps = mts*64/1000 * (16/18 if "BL18" in k else 1)
    v["module_W_at_full_bw"] = round(v["total"]*data_gbps/1000, 2)
    v["GBs_per_W"] = round((data_gbps/8)/v["module_W_at_full_bw"], 1)

# ---------- 5. Pinbudget 288-pins UDIMM ----------
pins = {"DQ (2x32)": 64, "DQS_t/DQS_c (8 paren)": 16, "CA (2x10, DDR)": 20, "CS_n (2 per subkanaal)": 4,
        "CK_t/CK_c ingang naar TCKD": 2, "PAR (CA-pariteit)": 2, "ALERT_n": 1, "RESET_n": 1,
        "HSCL/HSDA/HSA (I3C zijband)": 3, "PWR_EN / PWR_GOOD": 2, "VIN_BULK 5 V": 8}
sig = sum(pins.values())
pins["VSS (massa)"] = 150
pins["RFU (gereserveerd)"] = 288 - sig - 150
out["pins"] = pins
out["pins_total"] = sum(pins.values())

# ---------- 6. Capaciteit ----------
out["capacity"] = {
    "die": "32 Gb data + 4 Gb check = 36 Gb fysiek (x8)",
    "1Rx8": f"{8*32//8} GB, 8 chips",
    "2Rx8": f"{16*32//8} GB, 16 chips",
    "2Rx8 met 48 Gb dies": f"{16*48//8} GB, 16 chips",
}

# ---------- 7. ECC per chip per burst ----------
out["ecc"] = dict(bits_per_chip_burst=8*18, data=8*16, check=8*2,
                  secded_bits_needed=9, crc_bits=7, overhead_pct=round(16/128*100,1),
                  ddr5_ecc_dimm_overhead_pct=25.0)

json.dump(out, open("tdr1_numbers.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
