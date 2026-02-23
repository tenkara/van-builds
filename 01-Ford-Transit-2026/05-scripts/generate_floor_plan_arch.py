#!../../.venv/Scripts/python.exe
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
TO_W, TO_D = 24.0, 22.0        # toilet area (full width, 22" depth)
TO_X  = BA_X0                  # starts at driver wall (full width)
TO_Y  = BA_Y0 + BA_L - TO_D    # positioned at end of zone (Y=57-79)
SH_W  = 24.0                   # shower width 24" (full width)
SH_D  = BA_L - TO_D            # shower depth (rest of zone, Y=28-57, 29")
SH_X, SH_Y = BA_X0, BA_Y0      # shower starts at bath zone

# ── Zone 4: Galley kitchen  (stbd / passenger side) - OPTIMIZED for slim fridge ──
GA_D   = 24.0                   # counter depth (reduced for SMETA slim fridge)
GA_X0  = CW - GA_D              # starts at passenger wall (46.2")
GA_Y0  = Z34[0]                 # starts at Y=28"
GA_L   = Z34[1] - Z34[0]        # 51″ total length (28-79)
FR_W, FR_D, FR_H = 15.8, 17.9, 22.0   # SMETA 1.2 cu ft compact fridge
FR_X, FR_Y = GA_X0 + 2, GA_Y0   # fridge inside counter, 2" from edge (X=48.2, Y=28-45.9)
SK_W, SK_D = 15.0, 13.0         # sink with cutting board cover
SK_X, SK_Y = GA_X0 + 2, GA_Y0 + FR_D + 15  # sink after fridge, moved further south (Y≈60.9-73.9)
CT_H = 36.0                     # counter height (fridge is 22"H and fits underneath)

# ── Zone 2: Bed platform - MAXIMIZED depth, pushed to rear ──────────────
BED_Y0 = Z2[0]                 # Y=114" (right after wheel wells)
BED_Y1 = Z2[1]                 # Y=155" (rear door)
BED_D  = BED_Y1 - BED_Y0       # 41″ (155 - 114)
BED_H  = 28.0                  # optimized for window view, garage access, bed entry
MAT_W  = 70.0                  # RV-Queen east-west (increased to 70")
MAT_D  = 55.0                  # north-south (increased to 55" - note: exceeds bed platform depth of 41")
MAT_X  = (CW - MAT_W) / 2
MAT_Y  = BED_Y0 + (BED_D - MAT_D) / 2

# EcoFlow batteries + water tank (under bed, shown in plan)
WT_W, WT_D = 28.0, 22.0        # water tank (port side)
ECO_W, ECO_D = 28.0, 22.0     # EcoFlow batteries (stbd side)

# ── Zone 6: Entertainment/Dining area (over wheel wells) ─────────────────
# Sofas on both sides over wheel wells
SOFA6_W = 18.0                 # sofa width (depth from wall) - kept at original 18"
# Sofa length recalculated: from wheel well start to where mattress starts
SOFA6_L = MAT_Y - WW_Y0        # Length from WW start (Y=79) to mattress start
SOFA6_Y0 = WW_Y0               # starts at wheel well Y=79"
SOFA6_Y1 = MAT_Y               # ends where mattress starts
# Driver side sofa
SOFA6_PORT_X = 0.0
# Passenger side sofa
SOFA6_STBD_X = CW - SOFA6_W
# Sliding table from bed base
TABLE_W = 28.0                 # table width
# Table depth recalculated: from Zone 6 start to where mattress starts
TABLE_D = MAT_Y - Z6[0]        # Depth from Z6 start (Y=79) to mattress start
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


def LB(ax, x, y, txt, fs=7.5, c=None, ha="center", va="center",
       rot=0, bold=False, bg=True, zorder=9):
    """Draw a text label with optional white background box."""
    c = c or C["label_fg"]
    bbox = (dict(boxstyle="round,pad=0.18", fc=C["label_bg"],
                 ec="none", alpha=0.82) if bg else None)
    ax.text(x, y, txt, fontsize=fs, color=c, ha=ha, va=va, rotation=rot,
            fontweight="bold" if bold else "normal",
            bbox=bbox, zorder=zorder)


def DH(ax, x0, x1, y, txt, yo=5.0, fs=7.5):
    """Horizontal dimension line with arrows + label."""
    ax.plot([x0, x0], [y, y + yo * 0.9], color=C["dim"], lw=0.5, zorder=6)
    ax.plot([x1, x1], [y, y + yo * 0.9], color=C["dim"], lw=0.5, zorder=6)
    ax.annotate("", xy=(x1, y + yo * 0.65), xytext=(x0, y + yo * 0.65),
                arrowprops=dict(arrowstyle="<->", color=C["dim"],
                                lw=0.7, mutation_scale=6))
    ax.text((x0 + x1) / 2, y + yo, txt, fontsize=fs, ha="center", va="bottom",
            color=C["dim_txt"], zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.1))


def DV(ax, x, y0, y1, txt, xo=5.0, fs=7.5):
    """Vertical dimension line with arrows + label."""
    ax.plot([x, x + xo * 0.9], [y0, y0], color=C["dim"], lw=0.5, zorder=6)
    ax.plot([x, x + xo * 0.9], [y1, y1], color=C["dim"], lw=0.5, zorder=6)
    ax.annotate("", xy=(x + xo * 0.65, y1), xytext=(x + xo * 0.65, y0),
                arrowprops=dict(arrowstyle="<->", color=C["dim"],
                                lw=0.7, mutation_scale=6))
    ax.text(x + xo, (y0 + y1) / 2, txt, fontsize=fs, ha="left", va="center",
            color=C["dim_txt"], zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.1))


def DV_rotated(ax, x, y0, y1, txt, xo=5.0, fs=7.5, rot=90, label_side="right", label_offset=2.0):
    """Vertical dimension line with arrows + rotated label."""
    ax.plot([x, x + xo * 0.9], [y0, y0], color=C["dim"], lw=0.5, zorder=6)
    ax.plot([x, x + xo * 0.9], [y1, y1], color=C["dim"], lw=0.5, zorder=6)
    ax.annotate("", xy=(x + xo * 0.65, y1), xytext=(x + xo * 0.65, y0),
                arrowprops=dict(arrowstyle="<->", color=C["dim"],
                                lw=0.7, mutation_scale=6))
    # Position label to the left or right of the arrow line
    label_x = x - label_offset if label_side == "left" else x + xo
    ax.text(label_x, (y0 + y1) / 2, txt, fontsize=fs, ha="center", va="center",
            rotation=rot, color=C["dim_txt"], zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.1))


# ═════════════════════════════════════════════════════════════════════════════
# MAIN DRAWING FUNCTION: ARCHITECTURAL FLOOR PLAN
# ═════════════════════════════════════════════════════════════════════════════

def draw_floor_plan_arch():
    """
    Generate a professional architectural top-down floor plan.
    Portrait orientation, 11x17 inches, optimized for printing.
    """
    # ── Figure setup: Portrait orientation, white background ──────────────────
    MX, MY = 18, 15  # Reduced margins to maximize layout size
    fig, ax = plt.subplots(figsize=(11, 17), facecolor="#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_aspect("equal")
    ax.set_xlim(-MX, CW + MX)
    ax.set_ylim(CL + MY, -CAB_D - MY)  # INVERTED: front (Y=0) at top, rear (Y=155) at bottom
    ax.axis("off")

    # ── Title ─────────────────────────────────────────────────────────────────
    ax.set_title("Ford Transit 148\" ELWB – Architectural Floor Plan\n(Top-Down View)",
                 fontsize=15, fontweight="bold", pad=12)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 1: FLOOR AND SHELL
    # ══════════════════════════════════════════════════════════════════════════

    # Floor base
    R(ax, 0, 0, CW, CL, C["floor"], ec=C["wall"], lw=1.5, zorder=1)

    # Cab stub (above partition, in negative Y space)
    R(ax, 0, -CAB_D, CW, CAB_D, C["cab"], ec=C["wall"], lw=1.0, zorder=1)

    # Cab seats (driver on left, passenger on right)
    R(ax, 5, -CAB_D + 6, 18, 18, C["cab_seat"], ec=C["wall"], lw=0.6, zorder=2)
    R(ax, CW - 23, -CAB_D + 6, 18, 18, C["cab_seat"], ec=C["wall"], lw=0.6, zorder=2)
    LB(ax, 14, -CAB_D + 15, "DRIVER\nSEAT", fs=8.5, bold=True)
    LB(ax, CW - 14, -CAB_D + 15, "PASS.\nSEAT", fs=8.5, bold=True)
    LB(ax, CW / 2, -CAB_D + 26, "CAB  (factory – not converted)", fs=7, bg=False, c="#666666")

    # Partition (bulkhead) - dashed line at Y=0
    ax.plot([0, CW], [0, 0], color=C["partition"], lw=1.5, linestyle="--", zorder=5, dashes=(5, 3))
    LB(ax, CW / 2, -4, "BULKHEAD / PARTITION  (optional insulated divider)", fs=6.5, c="#666666")

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 2: ZONE BACKGROUNDS
    # ══════════════════════════════════════════════════════════════════════════

    # Zone 1: Entrance Lounge (Y=-5 to 28, driver side)
    R(ax, 0, Z1[0], SO_D + SO_X + 4, Z1[1] - Z1[0], "#FFF8E7", ec="none", lw=0, alpha=0.5, zorder=1)

    # Zone 2: Hidden Bath / Wet Bath (Y=28-79, left side)
    R(ax, BA_X0, BA_Y0, BA_W, BA_L, C["bath_bg"], ec="none", lw=0, alpha=0.6, zorder=1)

    # Zone 3: Galley (Y=28-79, right side)
    R(ax, GA_X0, GA_Y0, GA_D, GA_L, C["galley_bg"], ec="none", lw=0, alpha=0.6, zorder=1)

    # Zone 4: Living Aisle (Y=28-79, center)
    aisle_x0 = BA_W
    aisle_x1 = GA_X0
    aisle_w = aisle_x1 - aisle_x0
    R(ax, aisle_x0, Z34[0], aisle_w, Z34[1] - Z34[0], C["aisle"], ec="none", lw=0, alpha=0.4, zorder=1)

    # Zone 5: Entertainment (Y=79-114, over wheel wells)
    R(ax, 0, Z6[0], CW, Z6[1] - Z6[0], C["tbl_bg"], ec="none", lw=0, alpha=0.4, zorder=1)

    # Zone 6: Bed Platform (Y=114-155)
    R(ax, 0, BED_Y0, CW, BED_D, C["bed_bg"], ec="none", lw=0, alpha=0.5, zorder=1)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 3: WHEEL WELLS
    # ══════════════════════════════════════════════════════════════════════════

    # Left (driver) wheel well
    R(ax, 0, WW_Y0, WW_W, WW_Y1 - WW_Y0, C["ww"], ec=C["wall"], lw=0.8, hatch="///", zorder=2)
    # Wheel well dimension with arrows (left side) - vertical label
    DV_rotated(ax, -12, WW_Y0, WW_Y1, 'WHEEL WELL 35"', xo=5, fs=7, rot=90, label_side="right", label_offset=0.5)

    # Right (passenger) wheel well
    R(ax, CW - WW_W, WW_Y0, WW_W, WW_Y1 - WW_Y0, C["ww"], ec=C["wall"], lw=0.8, hatch="///", zorder=2)
    # Wheel well dimension with arrows (right side) - vertical label
    DV_rotated(ax, CW + 4, WW_Y0, WW_Y1, 'WHEEL WELL 35"', xo=5, fs=7, rot=90, label_side="right", label_offset=0.5)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 4: ZONE 1 - ENTRANCE LOUNGE (FENTON SOFA)
    # ══════════════════════════════════════════════════════════════════════════

    # Sofa base (folded position)
    R(ax, SO_X, SO_Y, SO_D, SO_W, C["sofa"], ec=C["wall"], lw=0.8, zorder=3)
    # Sofa cushion
    R(ax, SO_X + 1, SO_Y + 1, SO_D - 2, SO_W - 2, C["sofa_cush"], ec="none", lw=0, zorder=4)
    # Flip-up sofa label with dimensions
    LB(ax, SO_X + SO_D / 2, SO_Y + SO_W / 2, "FOLD UP SOFA BED\n33\"L × 8\"D", fs=7, bold=True, rot=90)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 5: ZONE 2 - HIDDEN BATH / WET BATH
    # ══════════════════════════════════════════════════════════════════════════

    # Bath zone outline
    R(ax, BA_X0, BA_Y0, BA_W, BA_L, "none", ec=C["bath"], lw=1.2, zorder=4)

    # Shower area
    R(ax, SH_X, SH_Y, SH_W, SH_D, C["shower"], ec=C["bath"], lw=0.8, zorder=3)
    LB(ax, SH_X + SH_W / 2, SH_Y + SH_D / 2, f"SHOWER\n24\"W×{SH_D:.0f}\"L", fs=8.5, bold=True)

    # Toilet area - no rectangle, just label centered in the space
    LB(ax, TO_X + TO_W / 2, TO_Y + TO_D / 2, f"TOILET\n24\"W×{TO_D:.0f}\"L", fs=8.5, bold=True)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 6: ZONE 3 - GALLEY
    # ══════════════════════════════════════════════════════════════════════════

    # Counter base
    R(ax, GA_X0, GA_Y0, GA_D, GA_L, C["counter"], ec=C["galley"], lw=1.2, zorder=3)

    # Fridge
    R(ax, FR_X, FR_Y, FR_W, FR_D, C["fridge"], ec=C["wall"], lw=0.8, zorder=4)
    LB(ax, FR_X + FR_W / 2, FR_Y + FR_D / 2, "FRIDGE", fs=7, bold=True)

    # Sink
    R(ax, SK_X, SK_Y, SK_W, SK_D, C["sink"], ec=C["wall"], lw=0.8, zorder=4)
    LB(ax, SK_X + SK_W / 2, SK_Y + SK_D / 2, "SINK", fs=7, bold=True)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 7: ZONE 5 - ENTERTAINMENT (SOFAS OVER WHEEL WELLS)
    # ══════════════════════════════════════════════════════════════════════════

    # Driver side sofa (over wheel well)
    R(ax, SOFA6_PORT_X, SOFA6_Y0, SOFA6_W, SOFA6_L, C["sofa"], ec=C["wall"], lw=0.8, zorder=4)
    R(ax, SOFA6_PORT_X + 1, SOFA6_Y0 + 1, SOFA6_W - 2, SOFA6_L - 2, C["sofa_cush"], ec="none", lw=0, zorder=5)
    LB(ax, SOFA6_PORT_X + SOFA6_W / 2, SOFA6_Y0 + SOFA6_L / 2, f"SOFA\n{SOFA6_W:.1f}\"W×{SOFA6_L:.0f}\"L", fs=7, bold=True, rot=90, bg=False)

    # Passenger side sofa (over wheel well)
    R(ax, SOFA6_STBD_X, SOFA6_Y0, SOFA6_W, SOFA6_L, C["sofa"], ec=C["wall"], lw=0.8, zorder=4)
    R(ax, SOFA6_STBD_X + 1, SOFA6_Y0 + 1, SOFA6_W - 2, SOFA6_L - 2, C["sofa_cush"], ec="none", lw=0, zorder=5)
    LB(ax, SOFA6_STBD_X + SOFA6_W / 2, SOFA6_Y0 + SOFA6_L / 2, f"SOFA\n{SOFA6_W:.1f}\"W×{SOFA6_L:.0f}\"L", fs=7, bold=True, rot=90, bg=False)

    # Sliding table
    R(ax, TABLE_X, TABLE_Y0, TABLE_W, TABLE_D, C["table"], ec=C["wall"], lw=0.8, zorder=4)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 8: ZONE 6 - BED PLATFORM
    # ══════════════════════════════════════════════════════════════════════════

    # Bed platform frame
    R(ax, 0, BED_Y0, CW, BED_D, "none", ec=C["bed"], lw=1.5, zorder=4)

    # Mattress
    R(ax, MAT_X, MAT_Y, MAT_W, MAT_D, C["mattress"], ec=C["bed"], lw=0.8, zorder=5)
    LB(ax, MAT_X + MAT_W / 2, MAT_Y + MAT_D / 2, f"RV QUEEN\n{MAT_W:.0f}\"×{MAT_D:.0f}\"", fs=9, bold=True)

    # Under-bed storage boxes - symmetrical on both sides
    # Calculate symmetrical width (same on both left and right)
    storage_inset = 2  # Distance from van walls
    storage_w = (CW - MAT_W) / 2 - storage_inset - 0.5  # Symmetrical width
    storage_y = MAT_Y  # Align with mattress start
    storage_d = MAT_D  # Match mattress depth

    # Power (left side - port)
    eco_x = storage_inset
    eco_w = storage_w
    eco_y = storage_y
    eco_d = storage_d
    R(ax, eco_x, eco_y, eco_w, eco_d, C["elec"], ec=C["wall"], lw=0.8, alpha=0.6, zorder=3)
    LB(ax, eco_x + eco_w / 2, eco_y + eco_d / 2, "Power", fs=8.5, bold=True, rot=90, c="#000000", bg=False, zorder=10)

    # Water (right side - starboard)
    water_x = MAT_X + MAT_W + 0.5
    water_w = storage_w
    water_y = storage_y
    water_d = storage_d
    R(ax, water_x, water_y, water_w, water_d, C["water"], ec=C["wall"], lw=0.8, alpha=0.6, zorder=3)
    LB(ax, water_x + water_w / 2, water_y + water_d / 2, "Water", fs=8.5, bold=True, rot=90, c="#000000", bg=False, zorder=10)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 9: WINDOWS
    # ══════════════════════════════════════════════════════════════════════════

    win_w = 2.5  # Window representation width on plan

    # Driver side (port) windows - 3 windows
    for i, (wy0, wy1) in enumerate(P_WINS):
        R(ax, -win_w, wy0, win_w, wy1 - wy0, C["window"], ec=C["win_frame"], lw=1.0, zorder=5)
        win_len = wy1 - wy0
        # Window label "WINDOW" with dimension on same line, rotated vertically
        LB(ax, -win_w - 3, (wy0 + wy1) / 2, f'WINDOW {win_len}"', fs=7, bold=True, rot=90, c=C["win_frame"])

    # Passenger side (stbd) windows - 2 windows
    for i, (wy0, wy1) in enumerate(S_WINS):
        R(ax, CW, wy0, win_w, wy1 - wy0, C["window"], ec=C["win_frame"], lw=1.0, zorder=5)
        win_len = wy1 - wy0
        # Window label "WINDOW" with dimension on same line, rotated vertically
        LB(ax, CW + win_w + 3, (wy0 + wy1) / 2, f'WINDOW {win_len}"', fs=7, bold=True, rot=90, c=C["win_frame"])

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 10: SLIDING DOOR
    # ══════════════════════════════════════════════════════════════════════════

    # Sliding door opening indicator - changed to black color
    R(ax, CW - 1, SL_Y0, 3, SL_Y1 - SL_Y0, "#E8F6F3", ec="#000000", lw=1.5, zorder=4)
    # Sliding door label - larger font, rotated 90 degrees, with dimension, black color
    LB(ax, CW + 4, (SL_Y0 + SL_Y1) / 2, f'SLIDING DOOR 51"', fs=8, bold=True, rot=90, c="#000000")

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 11: ZONE LABELS
    # ══════════════════════════════════════════════════════════════════════════

    # Zone 1: Entrance Lounge - centered horizontally and vertically in zone box (right of sofa)
    zone1_center_x = (SO_X + SO_D + CW) / 2  # Center between sofa right edge and right wall
    zone1_center_y = (Z1[0] + Z1[1]) / 2  # (-5 + 28) / 2 = 11.5
    LB(ax, zone1_center_x, zone1_center_y, "ZONE 1\nENTRANCE\nLOUNGE", fs=8, bold=True, c=C["label_fg"], bg=False)

    # Zone 2: Hidden Bath - centered in zone area, black font, horizontal
    zone2_center_x = BA_X0 + BA_W / 2
    zone2_center_y = BA_Y0 + BA_L / 2
    LB(ax, zone2_center_x, zone2_center_y, 'ZONE 2\nHIDDEN BATH\n24"W × 51"L', fs=8, bold=True, c="#000000", bg=False)

    # Zone 3: Galley - centered in zone
    zone3_center_x = GA_X0 + GA_D / 2
    zone3_center_y = GA_Y0 + GA_L / 2
    LB(ax, zone3_center_x, zone3_center_y, "ZONE 3\nGALLEY", fs=8, bold=True, c=C["galley"], bg=False)

    # Zone 4: Living Aisle - rotated 90 degrees vertically with dimensions
    zone4_center_x = aisle_x0 + aisle_w / 2
    zone4_center_y = Z34[0] + (Z34[1] - Z34[0]) / 2
    zone4_length = Z34[1] - Z34[0]  # 51"
    LB(ax, zone4_center_x, zone4_center_y, f"ZONE 4\nLIVING AISLE\n{aisle_w:.1f}\"W × {zone4_length:.0f}\"L", fs=8, bold=True, rot=90, c=C["label_fg"], bg=False)

    # Zone 5: Entertainment Table - rotated 90 degrees vertically
    zone5_center_x = CW / 2
    zone5_center_y = Z6[0] + (Z6[1] - Z6[0]) / 2
    # Calculate aisle width in Zone 5 (between sofas)
    zone5_aisle_w = CW - 2 * SOFA6_W  # 70.2 - 36 = 34.2"
    LB(ax, zone5_center_x, zone5_center_y, f'ZONE 5\nENTERTAINMENT TABLE\n{zone5_aisle_w:.0f}"W × 35"L',
       fs=8, bold=True, rot=90, c=C["label_fg"], bg=False)

    # Zone 6: Bed Platform
    zone6_center_x = CW / 2
    zone6_center_y = BED_Y0 + BED_D / 2
    LB(ax, zone6_center_x, zone6_center_y + 12, "ZONE 6\nBED PLATFORM", fs=8, bold=True, c=C["bed"], bg=False)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 12: DIMENSION LINES
    # ══════════════════════════════════════════════════════════════════════════

    # Cargo width dimension at top (interior width)
    DH(ax, 0, CW, CL + 8, f'{CW:.1f}" INTERIOR WIDTH', yo=6, fs=7.5)

    # Cargo length dimension on right side - rotated 270 degrees vertically
    # Position at CW + 18, CL / 2
    # Draw manual dimension lines for cargo length
    cargo_dim_x = CW + 14
    ax.plot([cargo_dim_x, cargo_dim_x + 4], [0, 0], color=C["dim"], lw=0.5, zorder=6)
    ax.plot([cargo_dim_x, cargo_dim_x + 4], [CL, CL], color=C["dim"], lw=0.5, zorder=6)
    ax.annotate("", xy=(cargo_dim_x + 2.5, CL), xytext=(cargo_dim_x + 2.5, 0),
                arrowprops=dict(arrowstyle="<->", color=C["dim"], lw=0.7, mutation_scale=6))
    ax.text(CW + 18, CL / 2, f'{CL:.0f}" CARGO LENGTH', fontsize=7.5, ha="center", va="center",
            rotation=270, color=C["dim_txt"], zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.1))

    # Entrance width dimension (opening between bulkhead Y=0 and galley edge Y=28)
    entrance_width = Z34[0] - 0  # 28"
    DV(ax, CW + 6, 0, Z34[0], f'{entrance_width:.0f}" ENTRANCE', xo=5, fs=7)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 13: Y-AXIS RULER (aligned to bulkhead at Y=0)
    # ══════════════════════════════════════════════════════════════════════════

    # Y-axis tick marks aligned to bulkhead (Y=0), not Y=-5
    ruler_x = -12
    y_ticks = [0, 28, 79, 114, 155]
    for yt in y_ticks:
        ax.plot([ruler_x, ruler_x + 3], [yt, yt], color=C["dim"], lw=0.6, zorder=6)
        ax.text(ruler_x - 1, yt, f'{yt}"', fontsize=6.5, ha="right", va="center", color=C["dim_txt"])

    # Main ruler line
    ax.plot([ruler_x + 1.5, ruler_x + 1.5], [0, CL], color=C["dim"], lw=0.8, zorder=5)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYER 14: NORTH ARROW AND SCALE
    # ══════════════════════════════════════════════════════════════════════════

    # North arrow - positioned at top of page, arrow pointing down from N to FRONT
    arrow_x, arrow_y = CW + 12, -CAB_D - 10
    ax.annotate("", xy=(arrow_x, arrow_y), xytext=(arrow_x, arrow_y + 10),
                arrowprops=dict(arrowstyle="-|>", color=C["wall"], lw=1.5, mutation_scale=12))
    ax.text(arrow_x, arrow_y + 14, "N", fontsize=11, fontweight="bold", ha="center", va="bottom")
    ax.text(arrow_x, arrow_y - 3, "(FRONT)", fontsize=6, ha="center", va="top", color=C["dim_txt"])

    # ══════════════════════════════════════════════════════════════════════════
    # SAVE OUTPUT
    # ══════════════════════════════════════════════════════════════════════════

    plt.tight_layout(pad=0.5)

    out_path = os.path.join(OUT_DIR, "20260220-1700-floor-plan-top-down-arch.png")
    fig.savefig(out_path, dpi=DPI, facecolor="#FFFFFF", bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)

    print(f"[OK] Architectural floor plan saved: {out_path}")
    return out_path


# ═════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("Ford Transit 148\" ELWB – Architectural Floor Plan Generator")
    print("=" * 70)

    output_file = draw_floor_plan_arch()

    print("-" * 70)
    print(f"Output file: {output_file}")
    print("=" * 70)
