#!/usr/bin/env python3
"""
Ford Transit 148" ELWB High Roof – Interactive 3-D Visualization
=================================================================
Generates a fully interactive, rotatable 3-D HTML model that opens
in any modern web browser.  No CAD software required.

Output:
  04-outputs/20260220-1700-3d-interactive.html   (interactive)
  04-outputs/20260220-1700-3d-screenshot.png     (static render)

Usage:
  python generate_3d_interactive.py
"""

import os
import numpy as np
import plotly.graph_objects as go

# ── paths ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR    = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "04-outputs"))
os.makedirs(OUT_DIR, exist_ok=True)

# ═════════════════════════════════════════════════════════════════════════
# DIMENSIONS  (all in inches)
# ═════════════════════════════════════════════════════════════════════════

CL = 172.2;  CW = 70.2;  CH = 81.5        # cargo interior

# Wheel wells
WW_W = 7.7;  WW_Y0 = 60.0;  WW_Y1 = 118.0;  WW_H = 13.5

# Zone boundaries (Y from front partition → rear)
Z1  = (0,    28);   Z5  = (28,  70)
Z34 = (70,  114);   ZTR = (114, 130);   Z2 = (130, 172.2)

# Zone 1: Sofa bed
SO_W, SO_D, SO_SH, SO_BH = 48, 24, 16, 18
SO_X = (CW - SO_W) / 2

# Zone 3: Wet bath (port)
BA_W, BA_L, BA_Y0, CT_H = 26, 44, 70, 36
TO_W, TO_D, TO_X, TO_Y  = 16, 16, 5, 70 + 44 - 16 - 2

# Zone 4: Galley (starboard)
GA_D, GA_X0, GA_Y0, GA_L = 22, 70.2 - 22, 70, 44
FR_W, FR_D, FR_H = 24, 20, 23
SK_W, SK_D = 15, 13

# Zone 2: Bed platform
BED_Y0, BED_D, BED_H = 130, 42.2, 28
MAT_W, MAT_D, MAT_H  = 60, 40, 10
MAT_X = (CW - MAT_W) / 2
MAT_Y = BED_Y0 + (BED_D - MAT_D) / 2

# Roof fans
FAN_Y, FAN_SZ = [49, 92], 14

# ═════════════════════════════════════════════════════════════════════════
# MESH BUILDER – creates a box as a Plotly Mesh3d trace
# ═════════════════════════════════════════════════════════════════════════

def box(name, x, y, z, dx, dy, dz, color, opacity=0.92, group=""):
    """Return a Mesh3d trace for an axis-aligned box."""
    # 8 vertices
    vx = [x, x+dx, x+dx, x,    x,    x+dx, x+dx, x   ]
    vy = [y, y,    y+dy, y+dy, y,    y,     y+dy, y+dy]
    vz = [z, z,    z,    z,    z+dz, z+dz,  z+dz, z+dz]
    # 12 triangles (2 per face)
    i = [0,0, 4,4, 0,0, 1,1, 0,0, 2,2]
    j = [1,2, 5,6, 1,4, 2,5, 3,4, 3,6]
    k = [2,3, 6,7, 4,5, 5,6, 4,7, 6,7]

    return go.Mesh3d(
        x=vx, y=vy, z=vz, i=i, j=j, k=k,
        color=color, opacity=opacity,
        name=name,
        legendgroup=group or name,
        showlegend=True,
        hovertext=name,
        hoverinfo="text",
        flatshading=True,
        lighting=dict(ambient=0.55, diffuse=0.65, specular=0.25,
                      roughness=0.6, fresnel=0.15),
        lightposition=dict(x=200, y=-100, z=300),
    )


def wireframe(name, x, y, z, dx, dy, dz, color="rgba(40,40,40,0.35)"):
    """Return a Scatter3d trace showing box edges (wireframe)."""
    # 12 edges of a box, drawn as a single line with None breaks
    corners = np.array([
        [x, y, z], [x+dx, y, z], [x+dx, y+dy, z], [x, y+dy, z], [x, y, z],
        [None]*3,
        [x, y, z+dz], [x+dx, y, z+dz], [x+dx, y+dy, z+dz], [x, y+dy, z+dz],
        [x, y, z+dz], [None]*3,
        [x, y, z], [x, y, z+dz], [None]*3,
        [x+dx, y, z], [x+dx, y, z+dz], [None]*3,
        [x+dx, y+dy, z], [x+dx, y+dy, z+dz], [None]*3,
        [x, y+dy, z], [x, y+dy, z+dz],
    ], dtype=object)
    return go.Scatter3d(
        x=corners[:,0], y=corners[:,1], z=corners[:,2],
        mode="lines", line=dict(color=color, width=1.5),
        name=name + " (edge)", showlegend=False, hoverinfo="skip",
    )


# ═════════════════════════════════════════════════════════════════════════
# ANNOTATION HELPERS
# ═════════════════════════════════════════════════════════════════════════

def label3d(text, x, y, z, color="#ffffff", size=11):
    """Floating 3-D text annotation."""
    return go.Scatter3d(
        x=[x], y=[y], z=[z], mode="text",
        text=[text], textfont=dict(size=size, color=color, family="Arial Black"),
        showlegend=False, hoverinfo="skip",
    )


def dim_line(x0, y0, z0, x1, y1, z1, text, color="#aaaaaa"):
    """Dimension line with label."""
    mx, my, mz = (x0+x1)/2, (y0+y1)/2, (z0+z1)/2
    traces = [
        go.Scatter3d(
            x=[x0, x1], y=[y0, y1], z=[z0, z1],
            mode="lines+markers",
            line=dict(color=color, width=2, dash="dot"),
            marker=dict(size=3, color=color, symbol="diamond"),
            showlegend=False, hoverinfo="skip",
        ),
        label3d(text, mx, my, mz + 3, color=color, size=9),
    ]
    return traces


# ═════════════════════════════════════════════════════════════════════════
# BUILD THE SCENE
# ═════════════════════════════════════════════════════════════════════════

def build_scene():
    traces = []

    def add(name, x, y, z, dx, dy, dz, color, opacity=0.92, group="",
            wire=True):
        traces.append(box(name, x, y, z, dx, dy, dz, color, opacity, group))
        if wire:
            traces.append(wireframe(name, x, y, z, dx, dy, dz))

    # ── SHELL (ghost) ─────────────────────────────────────────────────────
    add("Floor",         0, 0, -1.5, CW, CL, 1.5,   "#b8a88a", 0.40, "Shell", wire=False)
    add("Wall – Port",  -2, 0, 0,    2,  CL, CH,     "#8899aa", 0.08, "Shell", wire=True)
    add("Wall – Stbd",   CW, 0, 0,   2,  CL, CH,     "#8899aa", 0.08, "Shell", wire=True)
    add("Wall – Rear",   0, CL, 0,   CW, 2,  CH,     "#8899aa", 0.08, "Shell", wire=True)
    add("Ceiling",       0, 0, CH,   CW, CL, 1.0,    "#667788", 0.06, "Shell", wire=True)

    # ── WHEEL WELLS ───────────────────────────────────────────────────────
    add("Wheel Well – Port", 0,       WW_Y0, 0, WW_W, WW_Y1-WW_Y0, WW_H,
        "#7f8c8d", 0.75, "Wheel Wells")
    add("Wheel Well – Stbd", CW-WW_W, WW_Y0, 0, WW_W, WW_Y1-WW_Y0, WW_H,
        "#7f8c8d", 0.75, "Wheel Wells")

    # ── ZONE 1: FORWARD-FACING SOFA BED ──────────────────────────────────
    add("Z1 – Sofa Base",     SO_X,     Z1[0], 0,     SO_W,   SO_D,       SO_SH,
        "#7D5A14", 0.90, "Zone 1 – Sofa Bed")
    add("Z1 – Seat Cushion",  SO_X+1.5, Z1[0]+1.5, SO_SH, SO_W-3, SO_D*0.6, 4,
        "#C9A84C", 0.95, "Zone 1 – Sofa Bed")
    add("Z1 – Backrest",      SO_X+1,   Z1[0]+SO_D-5, SO_SH, SO_W-2, 5, SO_BH,
        "#A07840", 0.95, "Zone 1 – Sofa Bed")
    traces.append(label3d("SOFA BED\n(forward-facing)", CW/2, Z1[0]+12, SO_SH+SO_BH+6,
                          "#FFD966", 12))

    # Seat belt anchors
    for bx in [SO_X+8, CW/2, SO_X+SO_W-8]:
        traces.append(go.Scatter3d(
            x=[bx], y=[Z1[0]+2], z=[2],
            mode="markers", marker=dict(size=5, color="#2C3E50", symbol="circle"),
            name="Seat belt anchor", showlegend=False, hovertext="3-pt seat belt",
        ))

    # ── ZONE 5: AISLE + LAGUN TABLE ──────────────────────────────────────
    add("Z5 – Lagun Table",    BA_W+2,   Z5[0]+12, CT_H-2, 28, 20, 1.5,
        "#8E44AD", 0.85, "Zone 5 – Aisle")
    add("Z5 – Table Pedestal", BA_W+14,  Z5[0]+20, 0,      4,  4,  CT_H-2,
        "#6C3483", 0.80, "Zone 5 – Aisle")
    traces.append(label3d("AISLE\n(24–26\" clear)", CW/2, (Z5[0]+Z5[1])/2, 45,
                          "#D2B4DE", 10))

    # ── ZONE 3: WET BATH (port) ──────────────────────────────────────────
    add("Z3 – Bath Cabinet",   0, BA_Y0, 0,        BA_W, BA_L, CT_H,
        "#1A5276", 0.65, "Zone 3 – Wet Bath")
    add("Z3 – Counter",        0, BA_Y0, CT_H,     BA_W, BA_L, 2,
        "#BDC3C7", 0.90, "Zone 3 – Wet Bath")
    add("Z3 – Toilet",         TO_X, TO_Y, CT_H+2, TO_W, TO_D, 14,
        "#D5D8DC", 0.90, "Zone 3 – Wet Bath")
    add("Z3 – Upper Shelf",    0, BA_Y0, CT_H+18,  BA_W, BA_L, 14,
        "#2E86C1", 0.35, "Zone 3 – Wet Bath")
    traces.append(label3d("WET BATH\n(hideaway)", BA_W/2, BA_Y0+BA_L/2, CT_H+38,
                          "#85C1E9", 11))

    # ── ZONE 4: GALLEY KITCHEN (starboard) ────────────────────────────────
    add("Z4 – Galley Cabinet", GA_X0, GA_Y0, 0,     GA_D, GA_L, CT_H,
        "#6D3A0E", 0.65, "Zone 4 – Galley")
    add("Z4 – Counter",        GA_X0, GA_Y0, CT_H,  GA_D, GA_L, 2,
        "#BDC3C7", 0.90, "Zone 4 – Galley")
    add("Z4 – Fridge 90L",     GA_X0, GA_Y0, 0,     FR_W, FR_D, FR_H,
        "#2E86C1", 0.88, "Zone 4 – Galley")
    add("Z4 – Sink",           GA_X0+FR_W, GA_Y0, CT_H-7, SK_W, SK_D, 7,
        "#85C1E9", 0.85, "Zone 4 – Galley")
    add("Z4 – Upper Cabinet",  GA_X0, GA_Y0, CT_H+18, GA_D, GA_L, 18,
        "#8B6248", 0.45, "Zone 4 – Galley")
    traces.append(label3d("GALLEY\nKITCHEN", GA_X0+GA_D/2, GA_Y0+GA_L/2, CT_H+42,
                          "#F0B27A", 11))

    # ── ZONE 2: BED PLATFORM + MATTRESS ───────────────────────────────────
    add("Z2 – Bed Platform",   1, BED_Y0, 0,     CW-2,  BED_D, BED_H,
        "#1E6B3A", 0.60, "Zone 2 – Bed")
    add("Z2 – Mattress",       MAT_X, MAT_Y, BED_H, MAT_W, MAT_D, MAT_H,
        "#A9DFBF", 0.92, "Zone 2 – Bed")
    # Under-bed storage
    add("Z2 – Water Tank 25gal", 2,      BED_Y0+1, 1, 26, 20, BED_H-2,
        "#3498DB", 0.30, "Zone 2 – Bed", wire=False)
    add("Z2 – EcoFlow 10kWh",   CW-28,  BED_Y0+1, 1, 26, 20, BED_H-2,
        "#F39C12", 0.30, "Zone 2 – Bed", wire=False)
    traces.append(label3d("BED PLATFORM\n(28\" high)", CW/2, BED_Y0+BED_D/2,
                          BED_H+MAT_H+8, "#82E0AA", 12))
    traces.append(label3d("RV Queen\n60\"×40\"", CW/2, MAT_Y+MAT_D/2,
                          BED_H+MAT_H+1, "#FFFFFF", 9))

    # ── ROOF FANS ─────────────────────────────────────────────────────────
    for i, fy in enumerate(FAN_Y):
        add(f"Roof Fan {i+1}", CW/2-FAN_SZ/2, fy-FAN_SZ/2, CH-3,
            FAN_SZ, FAN_SZ, 3, "#E59866", 0.85, "Roof Fans")
        traces.append(label3d("MaxxAir\n14×14\"", CW/2, fy, CH+2, "#E59866", 8))

    # ── WINDOWS (port side, shown as translucent panels) ──────────────────
    wins = [(30, 68), (72, 112), (133, 170)]
    for i, (wy0, wy1) in enumerate(wins):
        add(f"Window Port {i+1}", -1, wy0, 36, 1, wy1-wy0, 22,
            "#5DADE2", 0.25, "Windows", wire=False)
        add(f"Window Stbd {i+1}", CW, wy0, 36, 1, wy1-wy0, 22,
            "#5DADE2", 0.25, "Windows", wire=False)

    # ── DIMENSION LINES ───────────────────────────────────────────────────
    for t in dim_line(0, -8, 0, CW, -8, 0,   "◄─ 70.2\" width ─►"):
        traces.append(t)
    for t in dim_line(-8, 0, 0, -8, CL, 0,   "172.2\" length"):
        traces.append(t)
    for t in dim_line(CW+8, 0, 0, CW+8, 0, CH, "81.5\" height"):
        traces.append(t)

    # ── FRONT ARROW ───────────────────────────────────────────────────────
    traces.append(go.Scatter3d(
        x=[CW/2, CW/2], y=[-5, -20], z=[0, 0],
        mode="lines+text", text=["", "◄── FRONT\n(driving direction)"],
        textposition="bottom center",
        textfont=dict(size=11, color="#E74C3C", family="Arial Black"),
        line=dict(color="#E74C3C", width=4),
        showlegend=False, hoverinfo="skip",
    ))
    traces.append(go.Cone(
        x=[CW/2], y=[-8], z=[0], u=[0], v=[-8], w=[0],
        colorscale=[[0, "#E74C3C"], [1, "#E74C3C"]],
        sizemode="absolute", sizeref=6,
        showlegend=False, showscale=False, hoverinfo="skip",
    ))

    return traces


# ═════════════════════════════════════════════════════════════════════════
# LAYOUT & EXPORT
# ═════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 62)
    print(" Ford Transit Van Build – Interactive 3-D Generator")
    print("=" * 62)

    traces = build_scene()

    fig = go.Figure(data=traces)

    fig.update_layout(
        title=dict(
            text=("Ford Transit 148\" ELWB High Roof – Van Build Interior Layout<br>"
                  "<sup>Interactive 3-D Model · All dimensions in inches · "
                  "February 20, 2026</sup>"),
            font=dict(size=16, color="white", family="Arial"),
            x=0.5, xanchor="center",
        ),
        scene=dict(
            xaxis=dict(title="Width  (port → stbd)  [in]",
                       range=[-25, CW + 25],
                       backgroundcolor="#1a1a2e",
                       gridcolor="#2a2a4a", showbackground=True,
                       color="#8888aa"),
            yaxis=dict(title="Length  (front → rear)  [in]",
                       range=[-30, CL + 20],
                       backgroundcolor="#16213e",
                       gridcolor="#2a2a4a", showbackground=True,
                       color="#8888aa"),
            zaxis=dict(title="Height  [in]",
                       range=[-5, CH + 20],
                       backgroundcolor="#0f3460",
                       gridcolor="#2a2a4a", showbackground=True,
                       color="#8888aa"),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.6, y=-1.4, z=0.9),
                up=dict(x=0, y=0, z=1),
            ),
        ),
        paper_bgcolor="#0a0a1a",
        plot_bgcolor="#0a0a1a",
        legend=dict(
            font=dict(color="white", size=10),
            bgcolor="rgba(20,20,40,0.7)",
            bordercolor="#444466",
            borderwidth=1,
            itemsizing="constant",
            groupclick="toggleitem",
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        width=1600, height=950,
    )

    # Add a "Reset View" button and view presets
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                x=0.02, y=0.98, xanchor="left", yanchor="top",
                bgcolor="rgba(30,30,60,0.8)",
                font=dict(color="white", size=10),
                buttons=[
                    dict(label="🔄 Reset View",
                         method="relayout",
                         args=[{"scene.camera.eye": dict(x=1.6, y=-1.4, z=0.9)}]),
                    dict(label="⬆ Top Down",
                         method="relayout",
                         args=[{"scene.camera.eye": dict(x=0, y=0, z=2.8)}]),
                    dict(label="➡ Port Side",
                         method="relayout",
                         args=[{"scene.camera.eye": dict(x=-2.4, y=0.1, z=0.5)}]),
                    dict(label="⬅ Stbd Side",
                         method="relayout",
                         args=[{"scene.camera.eye": dict(x=2.4, y=0.1, z=0.5)}]),
                    dict(label="🚗 Front",
                         method="relayout",
                         args=[{"scene.camera.eye": dict(x=0, y=-2.4, z=0.5)}]),
                    dict(label="🚪 Rear",
                         method="relayout",
                         args=[{"scene.camera.eye": dict(x=0, y=2.4, z=0.5)}]),
                ],
            ),
        ],
    )

    # ── Save HTML ──────────────────────────────────────────────────────
    html_path = os.path.join(OUT_DIR, "20260220-1700-3d-interactive.html")
    fig.write_html(
        html_path,
        include_plotlyjs="cdn",
        full_html=True,
        config=dict(
            displayModeBar=True,
            modeBarButtonsToAdd=["orbitRotation", "resetCameraDefault3d"],
            toImageButtonOptions=dict(format="png", width=2400, height=1500, scale=2),
        ),
    )
    size_kb = os.path.getsize(html_path) // 1024
    print(f"\n✅  Interactive HTML: {html_path}  ({size_kb} KB)")

    # ── Save static PNG ───────────────────────────────────────────────
    png_path = os.path.join(OUT_DIR, "20260220-1700-3d-interactive-screenshot.png")
    try:
        fig.write_image(png_path, width=2400, height=1500, scale=2)
        size_kb = os.path.getsize(png_path) // 1024
        print(f"✅  Static PNG:      {png_path}  ({size_kb} KB)")
    except Exception as e:
        print(f"⚠️  PNG export skipped (kaleido issue): {e}")
        print("   The HTML file is the primary output – open it in your browser.")

    print(f"\n📂  Output folder: {os.path.abspath(OUT_DIR)}")
    print("\n🖱️  Open the HTML file in your browser to interact with the 3-D model.")
    print("    • Click + drag to rotate")
    print("    • Scroll to zoom")
    print("    • Click legend items to toggle zones on/off")
    print("    • Use the view preset buttons (top-left)")


if __name__ == "__main__":
    main()
