#!/usr/bin/env python3
"""
Ford Transit 148" ELWB High Roof – Scaled Floor Plan Generator
==============================================================
Produces three architectural drawings at 1:24 scale (½" = 1′–0″):
  Sheet 1 – Top-down floor plan  (PNG + PDF page)
  Sheet 2 – Port-side elevation  (PNG + PDF page)
  Sheet 3 – 3-D isometric view   (PNG + PDF page)

All coordinates are in real-world INCHES.
Output files land in ../04-outputs/.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.backends.backend_pdf import PdfPages

# ── output paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR     = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "04-outputs"))
os.makedirs(OUT_DIR, exist_ok=True)
DPI = 200          # 200 dpi → good screen + print quality without huge files

# ═════════════════════════════════════════════════════════════════════════════
# DIMENSIONS  (all in inches – real world)
# ═════════════════════════════════════════════════════════════════════════════

# Interior cargo envelope - CORRECTED per user measurements
CL   = 155.0    # USABLE cargo length  partition → rear door threshold (measured)
CW   = 70.2     # width   port wall → starboard wall (at beltline)
CH   = 81.5     # height  floor → ceiling

# Cab stub shown above partition in plan view
CAB_D = 32.0

# Wheel wells - CORRECTED per user measurements
WW_CLR  = 52.0                  # clear between wheel wells
WW_W    = 8.0                   # 8″ protrusion each side
WW_Y0   = 79.0                  # starts  79″ from partition (155 - 41 - 35)
WW_Y1   = 114.0                 # ends   114″ from partition (155 - 41)
WW_H    = 11.0                  # height from floor

# Zone boundaries  (Y from front partition, 0 → 155.0)
Z1  = (-5.0,  28.0)   # FENTON FDFAAP flip-up sofa (driver side) - 33" long, extends into cab
Z34 = (28.0,  79.0)   # Galley (passenger) + Wet bath (driver) - BEFORE wheel wells
Z5  = (79.0, 114.0)   # Clear living aisle (between galley/bath and wheel wells)
Z6  = (79.0, 114.0)   # Entertainment/dining area (sofas over wheel wells, sliding table)
ZTR = (114.0,114.0)   # Transition ELIMINATED to maximize bed depth
Z2  = (114.0,155.0)   # East-west bed platform (pushed to rear) with sliding table

# ── Zone 1: FENTON FDFAAP Flip-up Sofa (driver side wall) ────────────────
SO_W  = 33.0                # sofa width (33" backrest height when folded) - runs N-S along wall
SO_D  = 8.0                 # sofa depth when FOLDED UP (estimated compact)
SO_DEPLOYED_D = 20.0        # seat base depth when deployed (per specs)
SO_X  = 6.5                 # 6.5" clearance from driver wall per FENTON FDFAAP specs
SO_Y  = -5.0                # starts 5" into cab area (before partition at Y=0)
SO_SH = 18.0                # seat height (flip-up design)
SO_BH = 33.0                # backrest height (32.75" rounded to 33")
SO_TH = SO_SH + SO_BH       # 51″ total when deployed

# ── Zone 3: Wet bath  (port / driver side) - BEFORE wheel wells ────────────────
BA_W  = 24.0                   # width (wet bath area)
BA_X0 = 0.0                    # starts at driver wall
BA_Y0 = Z34[0]                 # starts at Y=28"
BA_L  = Z34[1] - Z34[0]        # 51″ length (28-79, BEFORE wheel wells)
TO_W, TO_D = 16.0, 16.0        # toilet (inside wet bath zone)
TO_X  = 2.0                    # 2" from driver wall
SH_W  = 24.0                   # shower width 24"
SH_D  = 28.0                   # shower depth (Y=28-56)
SH_X, SH_Y = BA_X0, BA_Y0      # shower starts at bath zone
TO_Y  = SH_Y + SH_D + 2.0      # positioned at Y=58-74 (aft of shower footprint, inside Zone 3)

# ── Zone 4: Galley kitchen  (stbd / passenger side) - OPTIMIZED for slim fridge ──
GA_D   = 24.0                   # counter depth (reduced for SMETA slim fridge)
GA_X0  = CW - GA_D              # starts at passenger wall (46.2")
GA_Y0  = Z34[0]                 # starts at Y=28"
GA_L   = Z34[1] - Z34[0]        # 51″ total length (28-79)
FR_W, FR_D, FR_H = 15.8, 17.9, 22.0   # SMETA 1.2 cu ft compact fridge
FR_X, FR_Y = GA_X0 + 2, GA_Y0   # fridge inside counter, 2" from edge (X=48.2, Y=28-45.9)
SK_W, SK_D = 15.0, 13.0         # sink with cutting board cover
SK_X, SK_Y = GA_X0 + 2, GA_Y0 + FR_D  # sink after fridge (Y≈45.9-58.9)
CT_H = 36.0                     # counter height (fridge is 22"H and fits underneath)

# ── Zone 2: Bed platform - MAXIMIZED depth, pushed to rear ──────────────
BED_Y0 = Z2[0]                 # Y=114" (right after wheel wells)
BED_Y1 = Z2[1]                 # Y=155" (rear door)
BED_D  = BED_Y1 - BED_Y0       # 41″ (155 - 114)
BED_H  = 28.0                  # optimized for window view, garage access, bed entry
MAT_W  = 60.0                  # RV-Queen east-west
MAT_D  = 40.0                  # north-south FULL SIZE (fits in 41")
MAT_X  = (CW - MAT_W) / 2
MAT_Y  = BED_Y0 + (BED_D - MAT_D) / 2

# EcoFlow batteries + water tank (under bed, shown in plan)
WT_W, WT_D = 28.0, 22.0        # water tank (port side)
ECO_W, ECO_D = 28.0, 22.0     # EcoFlow batteries (stbd side)

# ── Zone 6: Entertainment/Dining area (over wheel wells) ─────────────────
# Sofas on both sides over wheel wells
SOFA6_W = 18.0                 # sofa width (depth from wall)
SOFA6_L = 35.0                 # sofa length (over wheel well, 35" long)
SOFA6_Y0 = WW_Y0               # starts at wheel well Y=79"
SOFA6_Y1 = WW_Y1               # ends at wheel well Y=114"
# Driver side sofa
SOFA6_PORT_X = 0.0
# Passenger side sofa
SOFA6_STBD_X = CW - SOFA6_W
# Sliding table from bed base
TABLE_W = 28.0                 # table width
TABLE_D = 35.0                 # table depth when extended (fits in Zone 6)
TABLE_X = (CW - TABLE_W) / 2   # centered
TABLE_Y = Z2[0]                # slides from bed base at Y=114"
TABLE_Y0 = Z6[0]               # table starts at Zone 6 (Y=79")

# Windows (Y0, Y1 per side along port/stbd wall) - corrected for 155" cargo length
P_WINS = [(8, 38), (50, 82), (96, 126)]      # Driver side (port/left) - 3 windows
S_WINS = [(55, 85), (96, 126)]                # Passenger side (stbd/right) - 2 windows (sliding door at front)
WIN_SILL = 36.0
WIN_H    = 22.0

# Sliding door (passenger/stbd side, plan view) - updated to match checklist
SL_Y0, SL_Y1 = 0, 51  # Starts at partition, 51" wide

# ═════════════════════════════════════════════════════════════════════════════
# COLOUR PALETTE
# ═════════════════════════════════════════════════════════════════════════════
C = {
    "wall":       "#1C2833",
    "floor":      "#FDFEFE",
    "cab":        "#E8ECEF",
    "cab_seat":   "#D2A679",
    "partition":  "#5D6D7E",
    "sofa":       "#D2A679",
    "sofa_cush":  "#E8C4A0",
    "backrest":   "#C8A882",
    "belt":       "#2C3E50",
    "bath":       "#1A5276",
    "bath_bg":    "#D6EAF8",
    "shower":     "#AED6F1",
    "toilet":     "#D5D8DC",
    "galley":     "#784212",
    "galley_bg":  "#FDEBD0",
    "fridge":     "#5DADE2",
    "sink":       "#85C1E9",
    "counter":    "#C8B89A",
    "aisle":      "#F8F9FA",
    "transition": "#F2F3F4",
    "bed":        "#1E8449",
    "bed_bg":     "#D5F5E3",
    "mattress":   "#A9DFBF",
    "ww":         "#95A5A6",
    "window":     "#85C1E9",
    "win_frame":  "#2471A3",
    "fan":        "#E59866",
    "table":      "#D3D3D3",
    "tbl_bg":     "#E8DAEF",
    "water":      "#3498DB",
    "elec":       "#F39C12",
    "dim":        "#7F8C8D",
    "dim_txt":    "#2C3E50",
    "label_bg":   "white",
    "label_fg":   "#2C3E50",
    "arrow":      "#C0392B",
    "grid":       "#EBF0F1",
}

# ═════════════════════════════════════════════════════════════════════════════
# SHARED DRAWING HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def R(ax, x, y, w, h, fc, ec="#1C2833", lw=0.6, alpha=1.0,
      hatch=None, zorder=2):
    """Draw a filled rectangle."""
    p = mpatches.Rectangle((x, y), w, h, fc=fc, ec=ec,
                            lw=lw, alpha=alpha, hatch=hatch, zorder=zorder)
    ax.add_patch(p)
    return p


def LB(ax, x, y, txt, fs=6.5, c=None, ha="center", va="center",
       rot=0, bold=False, bg=True, zorder=9):
    """Draw a text label with optional white background box."""
    c = c or C["label_fg"]
    bbox = (dict(boxstyle="round,pad=0.18", fc=C["label_bg"],
                 ec="none", alpha=0.82) if bg else None)
    ax.text(x, y, txt, fontsize=fs, color=c, ha=ha, va=va, rotation=rot,
            fontweight="bold" if bold else "normal",
            bbox=bbox, zorder=zorder)


def DH(ax, x0, x1, y, txt, yo=5.0, fs=6.5):
    """Horizontal dimension line with arrows + label."""
    ax.plot([x0, x0], [y, y + yo * 0.9], color=C["dim"], lw=0.5, zorder=6)
    ax.plot([x1, x1], [y, y + yo * 0.9], color=C["dim"], lw=0.5, zorder=6)
    ax.annotate("", xy=(x1, y + yo * 0.65), xytext=(x0, y + yo * 0.65),
                arrowprops=dict(arrowstyle="<->", color=C["dim"],
                                lw=0.7, mutation_scale=6))
    ax.text((x0 + x1) / 2, y + yo, txt, fontsize=fs, ha="center", va="bottom",
            color=C["dim_txt"], zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.1))


def DV(ax, x, y0, y1, txt, xo=5.0, fs=6.5):
    """Vertical dimension line with arrows + label."""
    ax.plot([x, x + xo * 0.9], [y0, y0], color=C["dim"], lw=0.5, zorder=6)
    ax.plot([x, x + xo * 0.9], [y1, y1], color=C["dim"], lw=0.5, zorder=6)
    ax.annotate("", xy=(x + xo * 0.65, y1), xytext=(x + xo * 0.65, y0),
                arrowprops=dict(arrowstyle="<->", color=C["dim"],
                                lw=0.7, mutation_scale=6))
    ax.text(x + xo, (y0 + y1) / 2, txt, fontsize=fs, ha="left", va="center",
            color=C["dim_txt"], zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.1))


# ═════════════════════════════════════════════════════════════════════════════
# SHEET 1 – TOP-DOWN FLOOR PLAN
# ═════════════════════════════════════════════════════════════════════════════

def draw_floor_plan():
    MX, MY = 28, 20     # data-space margins (inches)
    fig, ax = plt.subplots(figsize=(22, 14), dpi=DPI)
    fig.patch.set_facecolor("#EAECEE")
    ax.set_facecolor("#EAECEE")
    ax.set_xlim(-MX, CW + MX)
    ax.set_ylim(CL + MY, -CAB_D - MY)  # INVERTED: front (Y=0) at top, rear (Y=155) at bottom
    ax.set_aspect("equal")
    ax.axis("off")

    # ── title ────────────────────────────────────────────────────────────────
    ax.text(CW / 2, -CAB_D - MY * 0.70,
            "FORD TRANSIT 148″ ELWB HIGH ROOF  ·  VAN BUILD FLOOR PLAN  ·  TOP-DOWN VIEW",
            fontsize=11, fontweight="bold", ha="center", color=C["wall"], zorder=12)
    ax.text(CW / 2, -CAB_D - MY * 0.45,
            "Scale  1 : 24  (½\" = 1′–0\")   ·   All dimensions in inches   ·   February 20, 2026",
            fontsize=8, ha="center", color="#555555", zorder=12)

    # ── grid ─────────────────────────────────────────────────────────────────
    for gx in range(0, int(CW) + 1, 12):
        ax.axvline(gx, color=C["grid"], lw=0.35, zorder=0)
    for gy in range(0, int(CL) + 1, 12):
        ax.axhline(gy, color=C["grid"], lw=0.35, zorder=0)

    # ── floor fill ───────────────────────────────────────────────────────────
    R(ax, 0, 0, CW, CL, C["floor"], ec="none", zorder=1)

    # ── cab (simple representation) ──────────────────────────────────────────
    # driver seat (port/left)
    R(ax, 5, -CAB_D + 6, 18, 18, C["cab_seat"], ec=C["wall"], lw=0.6, zorder=3)
    LB(ax, 14, -CAB_D + 15, "DRIVER\nSEAT", fs=5.5, bold=True)
    # passenger seat (stbd/right)
    R(ax, CW - 23, -CAB_D + 6, 18, 18, C["cab_seat"], ec=C["wall"], lw=0.6, zorder=3)
    LB(ax, CW - 14, -CAB_D + 15, "PASS.\nSEAT", fs=5.5, bold=True)
    LB(ax, CW / 2, -CAB_D + 26, "CAB  (factory – not converted)", fs=6, bg=False, c="#666666")

    # ── partition (simplified to dotted line) ────────────────────────────────
    ax.plot([0, CW], [0, 0], color=C["partition"], lw=1.5, linestyle="--", zorder=5, dashes=(5, 3))
    LB(ax, CW / 2, -4, "BULKHEAD / PARTITION  (optional insulated divider)", fs=5.5, c="#666666")

    # ── exterior walls ───────────────────────────────────────────────────────
    ax.plot([0, 0],   [0, CL], color=C["wall"], lw=3.5, zorder=7, solid_capstyle="round")
    ax.plot([CW, CW], [0, CL], color=C["wall"], lw=3.5, zorder=7, solid_capstyle="round")
    ax.plot([0, CW],  [CL, CL], color=C["wall"], lw=3.5, zorder=7)
    ax.plot([0, CW],  [0, 0],   color=C["wall"], lw=2.0, zorder=7, linestyle="--")

    # ── windows ──────────────────────────────────────────────────────────────
    WT = 1.6
    for (wy0, wy1) in P_WINS:
        R(ax, -WT, wy0, WT * 2, wy1 - wy0, C["window"], ec=C["win_frame"],
          lw=0.9, alpha=0.95, zorder=6)
    for (wy0, wy1) in S_WINS:
        R(ax, CW - WT, wy0, WT * 2, wy1 - wy0, C["window"], ec=C["win_frame"],
          lw=0.9, alpha=0.95, zorder=6)
    # frosted bath window label
    LB(ax, -8, (Z34[0] + Z34[1]) / 2 + 5, "WIN\n(frost)", fs=4.5, ha="center")
    LB(ax, CW + 8, (Z34[0] + Z34[1]) / 2 + 5, "WIN\n(frost)", fs=4.5, ha="center")

    # ── sliding door (passenger/starboard side) ──────────────────────────────
    ax.plot([CW, CW], [SL_Y0, SL_Y1], color=C["window"], lw=4, zorder=7)
    ax.plot([CW, CW], [SL_Y0, SL_Y1], color=C["win_frame"], lw=1.2, zorder=8,
            linestyle="--")
    LB(ax, CW + 10, (SL_Y0 + SL_Y1) / 2, "SLIDING\nDOOR", fs=5, ha="center")

    # rear doors label
    ax.text(CW / 2, CL + 8, "◄   REAR BARN DOORS  (2× windows each leaf)   ►",
            fontsize=6.5, ha="center", color=C["wall"], zorder=10)

    # ── wheel wells ──────────────────────────────────────────────────────────
    R(ax, 0, WW_Y0, WW_W, WW_Y1 - WW_Y0, C["ww"], ec=C["wall"],
      lw=0.7, alpha=0.75, hatch="////", zorder=4)
    R(ax, CW - WW_W, WW_Y0, WW_W, WW_Y1 - WW_Y0, C["ww"], ec=C["wall"],
      lw=0.7, alpha=0.75, hatch="////", zorder=4)
    LB(ax, WW_W / 2,      (WW_Y0 + WW_Y1) / 2, "WW", fs=5, bg=False, c="#555555")
    LB(ax, CW - WW_W / 2, (WW_Y0 + WW_Y1) / 2, "WW", fs=5, bg=False, c="#555555")

    # ═══ ZONE 1: FENTON FDFAAP FLIP-UP SOFA ══════════════════════════════════
    # Zone background (extends into cab from Y=-5 to Y=28)
    R(ax, 0, -5, CW, 33, "#FFF8EE", ec="none", zorder=1)
    # mounting base plate along driver wall (folded up, 8" deep) - starts at Y=-5
    R(ax, SO_X, -5, SO_D, SO_W, C["sofa"], ec=C["wall"], lw=1.1, zorder=4)
    # folded-up seat (vertical/compact along wall) - starts at Y=-5
    R(ax, SO_X + 1.5, -5 + 1.5, 5, SO_W - 3,
      C["sofa_cush"], ec=C["sofa"], lw=0.8, alpha=0.9, zorder=5)
    # hatch pattern to show folded position
    R(ax, SO_X + 1.5, -5 + 1.5, 5, SO_W - 3,
      "none", ec=C["sofa"], lw=0.5, hatch="///", alpha=0.5, zorder=6)
    LB(ax, SO_X + SO_D / 2, -5 + SO_W / 2,
       "FENTON FDFAAP\nFLIP-UP SOFA\n(FOLDED UP)\n33\"L × 8\"D", fs=6, bold=True)
    LB(ax, CW / 2, Z1[1] - 6,
       "ZONE 1  –  Driver Side Wall  (extends 5\" into cab)\n(33\"W × 20\"D when deployed  ·  Toilet slides under)",
       fs=7, bold=True)

    # ═══ ZONE 6: ENTERTAINMENT/DINING AREA (over wheel wells) ════════════════
    # Background - clean white
    R(ax, 0, Z6[0], CW, Z6[1] - Z6[0], "#FFFFFF", ec="none", zorder=1)
    # Sofas on both sides
    R(ax, SOFA6_PORT_X, SOFA6_Y0, SOFA6_W, SOFA6_L, C["sofa"], ec=C["wall"], lw=1.1, zorder=4)
    LB(ax, SOFA6_PORT_X + SOFA6_W / 2, SOFA6_Y0 + SOFA6_L / 2,
       "SOFA\n(over wheel\nwell)", fs=5.5, bold=True)
    R(ax, SOFA6_STBD_X, SOFA6_Y0, SOFA6_W, SOFA6_L, C["sofa"], ec=C["wall"], lw=1.1, zorder=4)
    LB(ax, SOFA6_STBD_X + SOFA6_W / 2, SOFA6_Y0 + SOFA6_L / 2,
       "SOFA\n(over wheel\nwell)", fs=5.5, bold=True)
    # Sliding table from bed base (stays within Zone 6)
    R(ax, TABLE_X, TABLE_Y0, TABLE_W, TABLE_D, C["table"], ec=C["wall"],
      lw=0.9, alpha=0.8, zorder=3)
    LB(ax, TABLE_X + TABLE_W / 2, TABLE_Y0 + TABLE_D / 2,
       "SLIDING\nTABLE\n(from bed)", fs=5.5)
    # Central aisle label in Zone 6
    aisle_w = SOFA6_STBD_X - (SOFA6_PORT_X + SOFA6_W)
    LB(ax, CW / 2, (Z6[0] + Z6[1]) / 2,
       f"ZONE 6  –  ENTERTAINMENT / DINING\n{aisle_w:.0f}\" aisle between sofas  ·  Sliding table", fs=7, bold=True)

    # ═══ ZONE 5: CLEAR LIVING AISLE ══════════════════════════════════════════
    # Label positioned in the middle aisle between wet bath and galley
    aisle_x_start = BA_X0 + BA_W
    aisle_x_end = GA_X0
    aisle_width = aisle_x_end - aisle_x_start
    aisle_center_x = (aisle_x_start + aisle_x_end) / 2
    LB(ax, aisle_center_x, (Z34[0] + Z34[1]) / 2,
       f"ZONE 5\nCLEAR LIVING\nAISLE\n{aisle_width:.1f}\" wide", fs=7, bold=True)

    # ═══ ZONE 3: WET BATH (DRIVER SIDE) ══════════════════════════════════════
    R(ax, BA_X0, BA_Y0, BA_W, BA_L, C["bath_bg"], ec=C["bath"], lw=1.1, zorder=2)
    # shower floor
    R(ax, SH_X, SH_Y, SH_W, SH_D, C["shower"], ec=C["bath"],
      lw=0.7, alpha=0.65, hatch="...", zorder=3)
    ax.plot(SH_X + SH_W / 2, SH_Y + 5, "x", ms=5, mew=1.0,
            color="#1A5276", zorder=6)   # drain
    LB(ax, SH_X + SH_W / 2, SH_Y + SH_D / 2, "SHOWER\n(handheld wand)", fs=5)
    # toilet
    R(ax, TO_X, TO_Y, TO_W, TO_D, C["toilet"], ec=C["bath"], lw=0.7, zorder=4)
    ax.add_patch(mpatches.FancyBboxPatch(
        (TO_X + 2, TO_Y + 2), TO_W - 4, TO_D - 4,
        boxstyle="round,pad=1", fc="#EAEAEA", ec=C["bath"], lw=0.5, zorder=5))
    LB(ax, TO_X + TO_W / 2, TO_Y + TO_D / 2, "TOILET\n(dry flush)", fs=5)
    LB(ax, BA_X0 + BA_W / 2, BA_Y0 + BA_L * 0.75 + 2,
       "ZONE 3\nHIDEAWAY WET BATH\n24\"W × 51\"L", fs=7, bold=True)

    # ═══ ZONE 4: GALLEY KITCHEN (PASSENGER SIDE) ═════════════════════════════
    R(ax, GA_X0, GA_Y0, GA_D, GA_L, C["galley_bg"], ec=C["galley"], lw=1.1, zorder=2)
    # fridge
    R(ax, FR_X, FR_Y, FR_W, FR_D, C["fridge"], ec=C["galley"], lw=0.7, zorder=4)
    LB(ax, FR_X + FR_W / 2, FR_Y + FR_D / 2, "FRIDGE\n90L\nfront-open", fs=4.8)
    # sink
    R(ax, SK_X, SK_Y, SK_W, SK_D, C["sink"], ec=C["galley"],
      lw=0.7, alpha=0.85, zorder=4)
    ax.add_patch(mpatches.FancyBboxPatch(
        (SK_X + 2, SK_Y + 2), SK_W - 4, SK_D - 4,
        boxstyle="round,pad=1", fc="#FAFAFA", ec=C["galley"], lw=0.4, zorder=5))
    LB(ax, SK_X + SK_W / 2, SK_Y + SK_D / 2, "SINK", fs=4.5)
    # counter (rest)
    R(ax, GA_X0, GA_Y0 + FR_D, GA_D, GA_L - FR_D, C["counter"],
      ec=C["galley"], lw=0.6, zorder=3)
    LB(ax, GA_X0 + GA_D / 2, GA_Y0 + FR_D + (GA_L - FR_D) / 2,
       "COUNTER\n& STORAGE", fs=5)
    LB(ax, GA_X0 + GA_D / 2, GA_Y0 + GA_L * 0.85,
       "ZONE 4\nGALLEY KITCHEN\n24\"D × 51\"L", fs=7, bold=True)

    # ═══ TRANSITION ══════════════════════════════════════════════════════════
    R(ax, 0, ZTR[0], CW, ZTR[1] - ZTR[0], C["transition"],
      ec="#AAAAAA", lw=0.5, hatch="--", zorder=2)
    LB(ax, CW / 2, (ZTR[0] + ZTR[1]) / 2, "TRANSITION / ACCESS", fs=5)

    # ═══ ZONE 2: BED PLATFORM ════════════════════════════════════════════════
    R(ax, 0, BED_Y0, CW, BED_D, C["bed_bg"], ec=C["bed"], lw=1.1, zorder=2)
    # platform edge
    R(ax, 1, BED_Y0 + 1, CW - 2, BED_D - 2, C["bed_bg"], ec=C["bed"],
      lw=0.5, zorder=3)
    # mattress
    R(ax, MAT_X, MAT_Y, MAT_W, MAT_D, C["mattress"], ec=C["bed"],
      lw=0.9, alpha=0.92, zorder=4)
    LB(ax, CW / 2, MAT_Y + MAT_D / 2,
       "RV QUEEN MATTRESS\n60\"  E–W  ×  40\"  N–S\n(8–10\" premium foam)", fs=5.5)
    # water tank under-bed (port)
    R(ax, 0, BED_Y0, WT_W, WT_D, C["water"], ec=C["bed"],
      lw=0.5, alpha=0.30, zorder=3)
    LB(ax, WT_W / 2, BED_Y0 + WT_D / 2, "WATER\nTANK\n25 gal", fs=4.5, c="#1A5276")
    # EcoFlow under-bed (stbd)
    R(ax, CW - ECO_W, BED_Y0, ECO_W, ECO_D, C["elec"], ec=C["bed"],
      lw=0.5, alpha=0.30, zorder=3)
    LB(ax, CW - ECO_W / 2, BED_Y0 + ECO_D / 2, "ECOFLOW\n10 kWh\nbatteries", fs=4.5, c="#784212")
    LB(ax, CW / 2, BED_Y0 + BED_D * 0.82,
       "ZONE 2  –  EAST-WEST BED PLATFORM  (28\" high)\n50+ cu ft under-bed garage  ·  side-panel access",
       fs=7, bold=True)

    # ═══ DIMENSION LINES ══════════════════════════════════════════════════════
    DH(ax, 0, CW, CL + 10, f"70.2\"  (5′–10\")  Interior Width", yo=7, fs=7)
    DV(ax, CW + 10, 0, CL, f"155.0\"  (12′–11\")  Usable Cargo Length", xo=9, fs=7)
    # Sofa dimension along driver wall (length, not width since rotated)
    # DV(ax, -6, SO_Y, SO_Y + SO_W, "40\" sofa", xo=4, fs=5)
    DH(ax, WW_W, CW - WW_W, WW_Y0 - 6, f"{WW_CLR}\"  between wheel wells", yo=4, fs=6)
    DH(ax, 0, BA_W,  Z34[0] - 6, "24\" bath", yo=4, fs=6)
    DH(ax, GA_X0, CW, Z34[0] - 6, "24\" galley", yo=4, fs=6)
    # zone boundary ticks on left
    for y, txt in [(Z1[0], "0\""), (Z1[1], "28\""), (Z34[0], "28\""),
                   (Z34[1], "79\""), (WW_Y0, "79\""), (WW_Y1, "114\""), (Z2[1], "155\"")]:
        ax.plot([-3, 0], [y, y], color="#AAAAAA", lw=0.6, zorder=4)
        ax.text(-4, y, txt, fontsize=5, ha="right", va="center", color="#666666")
    # right-side zone labels
    for (y0, y1, ztxt) in [
        (Z1[0],  Z1[1],  "Z1"), (Z5[0],  Z5[1],  "Z5"),
        (Z34[0], Z34[1], "Z3+4"), (ZTR[0], ZTR[1], "ZTR"),
        (Z2[0],  Z2[1],  "Z2"),
    ]:
        ax.text(CW + 3, (y0 + y1) / 2, ztxt, fontsize=5.5, ha="left",
                va="center", color="#444444", fontweight="bold")


    # ═══ LEGEND (COMPACT) ═══════════════════════════════════════════════════════
    lx, ly = CW + MX - 6, -CAB_D - MY + 10
    ax.text(lx, ly + 36, "LEGEND", fontsize=6, fontweight="bold", color=C["wall"])
    items = [
        (C["sofa"],      "Sofa bed (Z1)"),
        (C["bath_bg"],   "Wet bath (Z3)"),
        (C["galley_bg"], "Galley (Z4)"),
        (C["bed_bg"],    "Bed (Z2)"),
        (C["window"],    "Window"),
        (C["ww"],        "Wheel well"),
    ]
    for i, (col, txt) in enumerate(items):
        R(ax, lx, ly + 28 - i * 5.5, 4, 4, col, ec="#666666", lw=0.4, zorder=10)
        ax.text(lx + 5.5, ly + 30 - i * 5.5, txt, fontsize=4.5,
                va="center", color=C["label_fg"])

    plt.tight_layout(pad=0.3)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# SHEET 2 – PORT-SIDE INTERIOR ELEVATION
# ═════════════════════════════════════════════════════════════════════════════

def draw_elevation():
    MX, MY = 26, 18
    fig, ax = plt.subplots(figsize=(22, 10), dpi=DPI)
    fig.patch.set_facecolor("#EAECEE")
    ax.set_facecolor("#EAECEE")
    ax.set_xlim(-MX, CL + MX)
    ax.set_ylim(-MY, CH + MY)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.text(CL / 2, CH + MY * 0.82,
            "FORD TRANSIT 148″ ELWB HIGH ROOF  ·  PORT-SIDE INTERIOR ELEVATION",
            fontsize=11, fontweight="bold", ha="center", color=C["wall"], zorder=12)
    ax.text(CL / 2, CH + MY * 0.55,
            "Scale  1 : 24  (½\" = 1′–0\")   ·   Dimensions in inches",
            fontsize=8, ha="center", color="#555555", zorder=12)

    # ── zone background bands ─────────────────────────────────────────────────
    bands = [
        (Z1,   "#FFF8EE"), (Z5,  "#FAFFF8"), (Z34, "#F0F4FF"),
        (ZTR,  "#FAFAFA"), (Z2,  "#F0FFF4"),
    ]
    for (y0, y1), fc in bands:
        R(ax, y0, 0, y1 - y0, CH, fc, ec="none", zorder=1)

    # ── floor / ceiling lines ─────────────────────────────────────────────────
    ax.plot([0, CL], [0,  0],  color=C["wall"], lw=2.5, zorder=7)
    ax.plot([0, CL], [CH, CH], color=C["wall"], lw=2.0, zorder=7)
    ax.plot([0, 0],  [0,  CH], color=C["wall"], lw=2.0, zorder=7,
            linestyle="--")

    # ── grid lines ────────────────────────────────────────────────────────────
    for gy in range(0, int(CH) + 1, 12):
        ax.axhline(gy, color=C["grid"], lw=0.3, zorder=0)
    for gx in range(0, int(CL) + 1, 12):
        ax.axvline(gx, color=C["grid"], lw=0.3, zorder=0)

    # ── windows (port side) ───────────────────────────────────────────────────
    for (wy0, wy1) in P_WINS:
        R(ax, wy0, WIN_SILL, wy1 - wy0, WIN_H, C["window"],
          ec=C["win_frame"], lw=0.9, zorder=4)
        ax.plot([(wy0 + wy1) / 2] * 2, [WIN_SILL, WIN_SILL + WIN_H],
                color=C["win_frame"], lw=0.4, zorder=5)
    # frosted bath window
    idx = 1   # second window = bath zone
    R(ax, P_WINS[idx][0], WIN_SILL, P_WINS[idx][1] - P_WINS[idx][0], WIN_H,
      C["window"], ec=C["win_frame"], lw=0.9, alpha=0.55, hatch="xxx", zorder=4)
    LB(ax, (P_WINS[idx][0] + P_WINS[idx][1]) / 2, WIN_SILL + WIN_H + 3,
       "FROSTED", fs=4.5, bg=False, c=C["win_frame"])

    # ── sliding door ──────────────────────────────────────────────────────────
    R(ax, SL_Y0, 0, SL_Y1 - SL_Y0, 56, "#D5EEF8", ec=C["win_frame"],
      lw=0.9, alpha=0.6, zorder=4, hatch="/")
    LB(ax, (SL_Y0 + SL_Y1) / 2, 28, "SLIDING DOOR", fs=5.5)

    # ── ZONE 1: sofa bed (side view) ──────────────────────────────────────────
    # base platform
    R(ax, Z1[0], 0, Z1[1] - Z1[0], SO_TH, C["sofa"], ec=C["wall"], lw=1.1, zorder=3)
    # seat cushion
    R(ax, Z1[0] + 2, 0, SO_D, SO_SH, C["sofa_cush"], ec=C["sofa"], lw=0.6, zorder=4)
    # backrest (facing front → shown on left of sofa in elevation)
    R(ax, Z1[0] + 2, SO_SH, 5, SO_BH, C["backrest"], ec=C["sofa"], lw=0.6, zorder=4)
    # under-seat storage
    R(ax, Z1[0] + 2, 0, SO_D, 12, "#D5DBDB", ec="#888", lw=0.4, alpha=0.5, zorder=3)
    LB(ax, (Z1[0] + Z1[1]) / 2, SO_TH / 2,
       "SOFA BED\nFORWARD-FACING\n(↑ faces front)", fs=5.5, bold=True)
    # floor tracks
    for tx in [Z1[0] + 4, Z1[0] + 14, Z1[0] + 22]:
        R(ax, tx, -1.5, 3, 1.5, "#555555", ec="#222", lw=0.4, zorder=5)

    # ── ZONE 3+4 bath/galley (port-side counter/shower view) ─────────────────
    # counter top
    R(ax, Z34[0], CT_H, Z34[1] - Z34[0], 2.5, C["counter"],
      ec=C["bath"], lw=0.9, zorder=4)
    # cabinet below
    R(ax, Z34[0], 0, Z34[1] - Z34[0], CT_H, C["bath_bg"],
      ec=C["bath"], lw=0.7, zorder=3)
    # upper open shelving (above counter)
    R(ax, Z34[0], CT_H + 16, Z34[1] - Z34[0], 16, "#E8F4FD",
      ec=C["bath"], lw=0.5, alpha=0.6, zorder=3)
    LB(ax, (Z34[0] + Z34[1]) / 2, CT_H + 24, "open shelving", fs=5, bg=False)
    # shower wand rail
    ax.plot([Z34[0] + 5, Z34[0] + 5], [CT_H + 3, 72], color="#2980B9",
            lw=1.0, zorder=5)
    ax.plot(Z34[0] + 5, 72, "D", ms=5, color="#2980B9", zorder=6)  # shower head
    ax.plot([Z34[0] + 5, Z34[0] + 12], [42, 38], color="#2980B9",
            lw=0.7, linestyle="--", zorder=5)
    LB(ax, (Z34[0] + Z34[1]) / 2, CT_H / 2,
       "ZONE 3  WET BATH\nshower / toilet\n26\"W × 44\"L", fs=5.5, bold=True)

    # ── ZONE 5 aisle ─────────────────────────────────────────────────────────
    LB(ax, (Z5[0] + Z5[1]) / 2, 40,
       "ZONE 5\nDINING / AISLE\n24–26\" clear", fs=5.5)

    # ── ZONE 2: bed platform (side view) ─────────────────────────────────────
    R(ax, BED_Y0, 0, BED_D, BED_H, C["bed"], ec=C["bed"], lw=0.7, zorder=3)
    # mattress edge visible
    R(ax, BED_Y0, BED_H, BED_D, 10, C["mattress"], ec=C["bed"], lw=0.7, zorder=4)
    # under-bed hatch
    R(ax, BED_Y0 + 1, 1, BED_D - 2, BED_H - 2, "#E8F8F5",
      ec=C["bed"], lw=0.4, alpha=0.5, hatch="..", zorder=2)
    LB(ax, (BED_Y0 + BED_Y1) / 2, BED_H / 2,
       "UNDER-BED STORAGE\n50+ cu ft", fs=5, bg=False, c=C["bed"])
    LB(ax, (BED_Y0 + BED_Y1) / 2, BED_H + 5,
       "MATTRESS\n(60\"×40\")", fs=5)
    LB(ax, (BED_Y0 + BED_Y1) / 2, BED_H + 20,
       "ZONE 2  –  BED PLATFORM\n28\" high  ·  side-panel access", fs=5.5, bold=True)
    # sitting headroom arrow
    mid = (BED_Y0 + BED_Y1) / 2 + 8
    ax.annotate("", xy=(mid, CH), xytext=(mid, BED_H + 11),
                arrowprops=dict(arrowstyle="<->", color="#999999", lw=0.8), zorder=6)
    LB(ax, mid + 5, (CH + BED_H + 11) / 2,
       f"{CH - BED_H - 11:.0f}\"\nheadroom\n(sitting)", fs=5, ha="left")

    # ── transition ────────────────────────────────────────────────────────────
    LB(ax, (ZTR[0] + ZTR[1]) / 2, 22, "ACCESS", fs=5, bg=False)

    # ── dimension lines ───────────────────────────────────────────────────────
    DV(ax, CL + 8,  0,  CH,        f"81.5\"  (6′–9½\")  Interior Height", xo=7, fs=7)
    DV(ax, CL + 3,  0,  WIN_SILL,  f"{WIN_SILL}\" sill",                  xo=2.5, fs=6)
    DV(ax, CL + 5,  WIN_SILL, WIN_SILL + WIN_H, f"{WIN_H}\" win",         xo=2.5, fs=6)
    DV(ax, Z1[1] + 3, 0, SO_SH,   f"{SO_SH}\" seat",                     xo=2, fs=6)
    DV(ax, Z1[1] + 6, 0, SO_TH,   f"{SO_TH}\" total",                    xo=2, fs=6)
    DV(ax, Z34[1] + 3, 0, CT_H,   f"{CT_H}\" counter",                   xo=2, fs=6)
    DV(ax, BED_Y1 + 3, 0, BED_H,  f"{BED_H}\" platform",                 xo=2, fs=6)
    DH(ax, 0,       Z1[1],   -11, "28\"",      yo=4)
    DH(ax, Z5[0],   Z5[1],   -11, "35\"",      yo=4)
    DH(ax, Z34[0],  Z34[1],  -11, "51\"",      yo=4)
    # DH(ax, ZTR[0],  ZTR[1],  -11, "16\"",      yo=4)  # TRANSITION ELIMINATED
    DH(ax, Z2[0],   Z2[1],   -11, "41\"",      yo=4)
    DH(ax, 0, CL, -17, "155\"  (12′–11\")  Usable Cargo Length", yo=5, fs=7)

    # ── zone top labels ───────────────────────────────────────────────────────
    for (y0, y1, lbl, col) in [
        (Z1[0],  Z1[1],  "Z1\nSOFA",      C["sofa"]),
        (28.0,   79.0,   "Z3+4\nBATH+GALLEY", "#666666"),
        (WW_Y0,  WW_Y1,  "WHEEL\nWELLS",  C["ww"]),
        (Z2[0],  Z2[1],  "Z2\nBED",       C["bed"]),
    ]:
        LB(ax, (y0 + y1) / 2, CH + 8, lbl, fs=7, bold=True, c=col, bg=False)


    plt.tight_layout(pad=0.3)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# SHEET 3 – 3-D ISOMETRIC INTERIOR VIEW
# ═════════════════════════════════════════════════════════════════════════════

def _rgb(h):
    """Hex → (R,G,B) floats 0–1."""
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def _box_faces(x, y, z, dx, dy, dz):
    """Six face vertex lists for a box (matplotlib Poly3DCollection)."""
    verts = [
        [[x,    y,    z],    [x+dx, y,    z],    [x+dx, y+dy, z],    [x,    y+dy, z]],  # bottom
        [[x,    y,    z+dz], [x+dx, y,    z+dz], [x+dx, y+dy, z+dz], [x,    y+dy, z+dz]],  # top
        [[x,    y,    z],    [x+dx, y,    z],    [x+dx, y,    z+dz], [x,    y,    z+dz]],  # front
        [[x,    y+dy, z],    [x+dx, y+dy, z],    [x+dx, y+dy, z+dz], [x,    y+dy, z+dz]],  # back
        [[x,    y,    z],    [x,    y+dy, z],    [x,    y+dy, z+dz], [x,    y,    z+dz]],  # left
        [[x+dx, y,    z],    [x+dx, y+dy, z],    [x+dx, y+dy, z+dz], [x+dx, y,    z+dz]],  # right
    ]
    return verts


def add3(ax, x, y, z, dx, dy, dz, fc_hex, alpha=0.88, ec="#222233"):
    """Draw a shaded 3-D box."""
    r, g, b = _rgb(fc_hex)
    # simulate diffuse light – top brightest, sides darker
    shades = [0.68, 1.00, 0.82, 0.62, 0.72, 0.90]
    facecolors = [(r*s, g*s, b*s, alpha) for s in shades]
    faces = _box_faces(x, y, z, dx, dy, dz)
    pc = Poly3DCollection(faces, alpha=alpha, linewidth=0.25,
                          zsort="min")
    pc.set_facecolor(facecolors)
    pc.set_edgecolor(ec)
    ax.add_collection3d(pc)


def draw_3d():
    fig = plt.figure(figsize=(20, 13), dpi=DPI)
    fig.patch.set_facecolor("#12122A")

    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("#12122A")

    # Axes: X=E-W (0=port), Y=N-S (0=front), Z=height
    # ── floor ────────────────────────────────────────────────────────────────
    add3(ax, 0, 0, -1.5, CW, CL, 1.5, "#C8BFA8", alpha=0.55)
    # ── ghost walls (very translucent) ───────────────────────────────────────
    add3(ax, -3,  0, 0,  3,  CL, CH, "#4A5568", alpha=0.12)   # port
    add3(ax, CW,  0, 0,  3,  CL, CH, "#4A5568", alpha=0.12)   # stbd
    add3(ax, 0,  CL, 0, CW,   3, CH, "#4A5568", alpha=0.12)   # rear
    # ghost ceiling
    add3(ax, 0,   0, CH, CW, CL,   2, "#2C3E50", alpha=0.08)

    # ── wheel wells ──────────────────────────────────────────────────────────
    add3(ax, 0,            WW_Y0, 0, WW_W, WW_Y1-WW_Y0, WW_H, "#95A5A6", alpha=0.80)
    add3(ax, CW - WW_W,    WW_Y0, 0, WW_W, WW_Y1-WW_Y0, WW_H, "#95A5A6", alpha=0.80)

    # ── ZONE 1: sofa bed ─────────────────────────────────────────────────────
    add3(ax, SO_X, Z1[0], 0,       SO_W, SO_D,        SO_SH,    "#7D5A14")
    add3(ax, SO_X+1.5, Z1[0]+1.5, SO_SH, SO_W-3, SO_D-2, 4,   "#C9A84C")
    add3(ax, SO_X+1.5, Z1[0]+SO_D-4, SO_SH, SO_W-3, 4, SO_BH, "#A07840")
    ax.text(CW/2, Z1[0]+2, SO_TH+3,
            "SOFA BED\n(forward-facing)", fontsize=7, color="#FFE08A",
            ha="center", va="bottom", zorder=12)

    # ── ZONE 3: wet bath ─────────────────────────────────────────────────────
    add3(ax, 0, BA_Y0, 0, BA_W, BA_L, CT_H,    "#1A5276", alpha=0.55)
    add3(ax, 0, BA_Y0, CT_H, BA_W, BA_L, 2.5,  "#BDC3C7", alpha=0.90)  # counter
    add3(ax, 0, BA_Y0+CT_H+16, CT_H+16, BA_W, BA_L*0.4, 14, "#1A5276", alpha=0.30)  # upper cab
    add3(ax, TO_X+1, TO_Y+1, 0, TO_W-2, TO_D-2, 16, "#D5D8DC", alpha=0.85)  # toilet
    ax.text(BA_W/2, BA_Y0+BA_L/2, CT_H+4,
            "WET BATH", fontsize=7, color="#AED6F1",
            ha="center", va="bottom", zorder=12)

    # ── ZONE 4: galley kitchen ────────────────────────────────────────────────
    add3(ax, GA_X0, GA_Y0, 0,       GA_D, GA_L, CT_H,    "#6D3A0E", alpha=0.55)
    add3(ax, GA_X0, GA_Y0, CT_H,    GA_D, GA_L, 2.5,     "#BDC3C7", alpha=0.90)  # counter
    add3(ax, FR_X,  FR_Y,  0,       FR_W, FR_D, CT_H,    "#2E86C1", alpha=0.85)  # fridge
    add3(ax, GA_X0, GA_Y0, CT_H+14, GA_D, GA_L, 18,      "#8B6248", alpha=0.55)  # upper cab
    ax.text(GA_X0+GA_D/2, GA_Y0+GA_L/2, CT_H+4,
            "GALLEY", fontsize=7, color="#F0B27A",
            ha="center", va="bottom", zorder=12)

    # ── ZONE 2: bed platform ──────────────────────────────────────────────────
    add3(ax, 1,     BED_Y0, 0,     CW-2,  BED_D, BED_H,  "#1E6B3A", alpha=0.65)
    add3(ax, MAT_X, MAT_Y,  BED_H, MAT_W, MAT_D, 10,     "#A9DFBF", alpha=0.92)  # mattress
    # under-bed labels (ghost boxes)
    add3(ax, 1,       BED_Y0+1, 1, WT_W-2,  WT_D-2,  BED_H-2, "#2980B9", alpha=0.20)
    add3(ax, CW-ECO_W+1, BED_Y0+1, 1, ECO_W-2, ECO_D-2, BED_H-2, "#E67E22", alpha=0.20)
    ax.text(CW/2, (BED_Y0+BED_Y1)/2, BED_H+12,
            "BED PLATFORM\n(28\" high)", fontsize=7, color="#82E0AA",
            ha="center", va="bottom", zorder=12)

    # ── axis styling ──────────────────────────────────────────────────────────
    ax.set_xlim([0, CW]);   ax.set_xlabel("Width E↔W (in)", fontsize=7,
                                          color="#AAAACC", labelpad=8)
    ax.set_ylim([0, CL]);   ax.set_ylabel("Length N↔S (in)", fontsize=7,
                                          color="#AAAACC", labelpad=8)
    ax.set_zlim([0, CH+12]); ax.set_zlabel("Height (in)", fontsize=7,
                                            color="#AAAACC", labelpad=8)
    ax.tick_params(colors="#666688", labelsize=6)
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor("#222244")
    ax.grid(True, color="#222244", lw=0.3, alpha=0.5)
    ax.view_init(elev=24, azim=-52)

    fig.suptitle(
        "FORD TRANSIT 148\" ELWB HIGH ROOF  ·  3-D INTERIOR ISOMETRIC VIEW\n"
        "Parametric model  ·  All dimensions in inches  ·  February 20, 2026",
        fontsize=10, fontweight="bold", color="white", y=0.97)

    # ── key ───────────────────────────────────────────────────────────────────
    from matplotlib.patches import Patch
    legend_els = [
        Patch(fc="#C9A84C", label="Sofa bed (Zone 1)"),
        Patch(fc="#1A5276", label="Wet bath (Zone 3)"),
        Patch(fc="#6D3A0E", label="Galley (Zone 4)"),
        Patch(fc="#2E86C1", label="Fridge 90L"),
        Patch(fc="#1E6B3A", label="Bed platform (Zone 2)"),
        Patch(fc="#A9DFBF", label="Mattress 60\"×40\""),
        Patch(fc="#95A5A6", label="Wheel wells"),
    ]
    ax.legend(handles=legend_els, loc="upper left", fontsize=6,
              framealpha=0.35, facecolor="#1A1A3A", edgecolor="#444466",
              labelcolor="white", bbox_to_anchor=(0.01, 0.99))

    plt.tight_layout(pad=0.3)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 62)
    print(" Ford Transit Van Build – Scaled Floor Plan Generator")
    print("=" * 62)

    figs = []

    print("\n[1/3] Sheet 1 – Top-down floor plan …")
    fig1 = draw_floor_plan()
    p1 = os.path.join(OUT_DIR, "20260220-1700-floor-plan-top-down.png")
    fig1.savefig(p1, dpi=DPI, bbox_inches="tight",
                 facecolor=fig1.get_facecolor())
    print(f"      → {p1}")
    figs.append(fig1)

    print("[2/3] Sheet 2 – Port-side elevation …")
    fig2 = draw_elevation()
    p2 = os.path.join(OUT_DIR, "20260220-1700-elevation-port-side.png")
    fig2.savefig(p2, dpi=DPI, bbox_inches="tight",
                 facecolor=fig2.get_facecolor())
    print(f"      → {p2}")
    figs.append(fig2)

    print("[3/3] Sheet 3 – 3-D isometric view …")
    fig3 = draw_3d()
    p3 = os.path.join(OUT_DIR, "20260220-1700-3d-isometric.png")
    fig3.savefig(p3, dpi=DPI, bbox_inches="tight",
                 facecolor=fig3.get_facecolor())
    print(f"      → {p3}")
    figs.append(fig3)

    pdf_path = os.path.join(OUT_DIR, "20260220-1700-van-build-drawings.pdf")
    print(f"\n[PDF] Combining all sheets → {pdf_path} …")
    with PdfPages(pdf_path) as pdf:
        for fig in figs:
            pdf.savefig(fig, bbox_inches="tight", facecolor=fig.get_facecolor())
        d = pdf.infodict()
        d["Title"]    = "Ford Transit 148\" ELWB – Van Build Scaled Drawings"
        d["Author"]   = "Van Build Project – GitHub Copilot"
        d["Subject"]  = "Architectural floor plans, elevation & 3D view – 1:24 scale"
        d["Keywords"] = "Ford Transit, van build, floor plan, elevation, 3D, 2026"
        d["CreationDate"] = "2026-02-20"

    print("\n✅  All files generated successfully.")
    print(f"   Output folder: {os.path.abspath(OUT_DIR)}")
    print("\n   Files:")
    for p in [p1, p2, p3, pdf_path]:
        size_kb = os.path.getsize(p) // 1024
        print(f"     {os.path.basename(p)}  ({size_kb} KB)")

    plt.close("all")
