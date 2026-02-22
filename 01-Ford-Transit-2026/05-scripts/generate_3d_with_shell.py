#!/usr/bin/env python3
"""
Ford Transit 148" ELWB High Roof – 3-D Visualization with Transit Shell
========================================================================
Parses pre-tessellated geometry from Ford's AP242 STEP files, aligns
them with the interior layout coordinate system, and generates an
interactive Plotly HTML with the Transit shell overlaying the build
layout.

AP242 STEP files contain COORDINATES_LIST (vertices) and
COMPLEX_TRIANGULATED_FACE (normals + triangle index strips) entities
that we extract directly—no OpenCascade bindings required.

The Roof STEP file (AP203, B-Rep only) has no tessellation, so we
generate a parametric curved roof mesh instead.

Output:
  04-outputs/20260220-1700-3d-transit-shell.html

Usage:
  python generate_3d_with_shell.py
"""

import os, re, time, gc, sys
import numpy as np
import plotly.graph_objects as go

# ── paths ─────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUT_DIR     = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "04-outputs"))
EXTRACT_DIR = os.path.normpath(os.path.join(
    SCRIPT_DIR, "..", "03-inputs", "ford-transit-3d-models", "_extracted"))
os.makedirs(OUT_DIR, exist_ok=True)

# ═════════════════════════════════════════════════════════════════════════
# INTERIOR LAYOUT DIMENSIONS  (all in inches)
# ═════════════════════════════════════════════════════════════════════════

CL = 155.0;  CW = 70.2;  CH = 81.5        # cargo interior - CORRECTED (usable length measured)

# Wheel wells - CORRECTED per user measurements
WW_W = 8.0;  WW_Y0 = 79.0;  WW_Y1 = 114.0;  WW_H = 11.0

# Zone boundaries (Y from front partition → rear)
Z1  = (-5.0, 28.0)   # FENTON sofa (extends into cab)
Z34 = (28.0, 79.0)   # Galley + Wet bath
Z5  = (79.0, 114.0)  # Clear aisle
Z6  = (79.0, 114.0)  # Entertainment area (over wheel wells)
ZTR = (114.0, 114.0) # Transition eliminated
Z2  = (114.0, 155.0) # Bed platform

# Zone 1: forward-facing sofa bed
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
#  STEP AP242 TESSELLATION PARSER
# ═════════════════════════════════════════════════════════════════════════

def parse_step_tessellation(filepath, max_triangles=80_000):
    """
    Parse pre-tessellated geometry from an AP242 STEP file.

    Returns dict with:
        vertices : np.ndarray  (N, 3) float64 – in millimetres
        faces    : np.ndarray  (M, 3) int      – triangle indices
        bbox     : tuple ((xmin,ymin,zmin), (xmax,ymax,zmax))

    The parser is deliberately simple and fast: it reads the file line-by-
    line, accumulates entity text between '#nnn=' delimiters, and extracts
    only COORDINATES_LIST and COMPLEX_TRIANGULATED_FACE entities.
    """
    print(f"  📂 Parsing: {os.path.basename(filepath)} "
          f"({os.path.getsize(filepath)/1024/1024:.0f} MB)")
    t0 = time.time()

    # ── Phase 1: stream the file and collect entities of interest ──────
    coord_entities = {}   # id → text
    face_entities  = {}   # id → text
    current_id     = None
    current_text   = []
    collecting      = False

    with open(filepath, 'r', errors='replace') as fh:
        for line in fh:
            stripped = line.strip()

            # Start of a new entity
            m = re.match(r'#(\d+)\s*=\s*(\w+)', stripped)
            if m:
                # flush previous entity
                if collecting and current_id is not None:
                    full = ''.join(current_text)
                    if 'COORDINATES_LIST' in full[:50]:
                        coord_entities[current_id] = full
                    elif 'COMPLEX_TRIANGULATED_FACE' in full[:50]:
                        face_entities[current_id] = full

                eid  = int(m.group(1))
                etype = m.group(2)
                if etype in ('COORDINATES_LIST', 'COMPLEX_TRIANGULATED_FACE'):
                    current_id   = eid
                    current_text = [stripped]
                    collecting   = True
                else:
                    collecting = False
                    current_id = None
                continue

            if collecting:
                current_text.append(stripped)

        # flush last entity
        if collecting and current_id is not None:
            full = ''.join(current_text)
            if 'COORDINATES_LIST' in full[:50]:
                coord_entities[current_id] = full
            elif 'COMPLEX_TRIANGULATED_FACE' in full[:50]:
                face_entities[current_id] = full

    print(f"    Found {len(coord_entities)} coordinate lists, "
          f"{len(face_entities)} triangulated faces  "
          f"({time.time()-t0:.1f}s)")

    if not coord_entities:
        return None

    # ── Phase 2: parse COORDINATES_LIST → vertex arrays ────────────────
    all_verts = {}   # coord_id → np.ndarray (N,3)
    float_pat = re.compile(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?')

    for cid, text in coord_entities.items():
        # Extract the vertex count
        m = re.match(r"#\d+=COORDINATES_LIST\('.*?',(\d+),", text)
        if not m:
            continue
        n_verts = int(m.group(1))
        if n_verts == 0:
            continue

        # Extract all floats after the opening (( of coordinates
        idx = text.index('((')
        nums = float_pat.findall(text[idx:])
        if len(nums) < n_verts * 3:
            # Truncated – use what we have
            n_verts = len(nums) // 3
        arr = np.array([float(x) for x in nums[:n_verts*3]],
                       dtype=np.float64).reshape(-1, 3)
        all_verts[cid] = arr

    total_verts = sum(v.shape[0] for v in all_verts.values())
    print(f"    Parsed {total_verts:,} vertices")

    # ── Phase 3: parse COMPLEX_TRIANGULATED_FACE → triangles ───────────
    all_tris = []
    tri_pat  = re.compile(r'\((\d+),(\d+),(\d+)\)')

    for fid, text in face_entities.items():
        # Find the COORDINATES_LIST reference  → #NNNN
        m = re.match(r"#\d+=COMPLEX_TRIANGULATED_FACE\('.*?',#(\d+),", text)
        if not m:
            continue
        coord_ref = int(m.group(1))
        if coord_ref not in all_verts:
            continue

        verts = all_verts[coord_ref]

        # The triangle index triplets are the LAST set of nested ((...))
        # in the entity.  They look like:  (i1,i2,i3),(i4,i5,i6),...
        # and indices are 1-based in STEP.
        # Find them after the normals list.
        # Strategy: scan backwards for the last '))' and work from there.
        # The triangle section is enclosed in an outer pair of parens.

        # Find all (a,b,c) triplets where a,b,c are pure integers
        tris = tri_pat.findall(text)
        if not tris:
            continue

        # Convert to 0-based
        face_arr = np.array([[int(a)-1, int(b)-1, int(c)-1]
                             for a, b, c in tris], dtype=np.int32)

        # Validate indices
        mask = np.all(face_arr >= 0, axis=1) & np.all(face_arr < verts.shape[0], axis=1)
        face_arr = face_arr[mask]

        if face_arr.shape[0] == 0:
            continue

        # Offset indices by cumulative vertex count
        all_tris.append((coord_ref, face_arr))

    # ── Phase 4: combine into single mesh ──────────────────────────────
    # Build vertex offset map
    vert_list = []
    vert_offset = {}
    offset = 0
    for cid in sorted(all_verts.keys()):
        vert_offset[cid] = offset
        vert_list.append(all_verts[cid])
        offset += all_verts[cid].shape[0]

    if not vert_list:
        return None
    vertices = np.vstack(vert_list)

    # Offset face indices
    tri_list = []
    for coord_ref, face_arr in all_tris:
        if coord_ref in vert_offset:
            tri_list.append(face_arr + vert_offset[coord_ref])
    if not tri_list:
        return None
    faces = np.vstack(tri_list)

    print(f"    Combined: {vertices.shape[0]:,} vertices, "
          f"{faces.shape[0]:,} triangles")

    # ── Phase 5: decimate if needed ────────────────────────────────────
    if faces.shape[0] > max_triangles:
        step = max(1, faces.shape[0] // max_triangles)
        faces = faces[::step]
        # Re-index: only keep referenced vertices
        used = np.unique(faces.ravel())
        remap = np.full(vertices.shape[0], -1, dtype=np.int32)
        remap[used] = np.arange(len(used), dtype=np.int32)
        vertices = vertices[used]
        faces = remap[faces]
        print(f"    Decimated to {vertices.shape[0]:,} vertices, "
              f"{faces.shape[0]:,} triangles  (step={step})")

    bbox = (tuple(vertices.min(axis=0)), tuple(vertices.max(axis=0)))
    print(f"    Bounding box (mm): "
          f"({bbox[0][0]:.0f}, {bbox[0][1]:.0f}, {bbox[0][2]:.0f}) → "
          f"({bbox[1][0]:.0f}, {bbox[1][1]:.0f}, {bbox[1][2]:.0f})")

    return dict(vertices=vertices, faces=faces, bbox=bbox)


# ═════════════════════════════════════════════════════════════════════════
#  COORDINATE ALIGNMENT: Ford mm → Layout inches
# ═════════════════════════════════════════════════════════════════════════
#
# Ford STEP files use mm in their own coordinate system.
# We need to:
#   1. Convert mm → inches (÷ 25.4)
#   2. Translate + rotate to align with our layout origin where:
#        X = 0 is port wall,   X = CW is starboard wall
#        Y = 0 is front partition, Y = CL is rear
#        Z = 0 is floor,          Z = CH is ceiling
#
# The alignment is computed from bounding boxes of the
# interior-defining parts (Interior Side Trim + Rear Cargo Doors).

def compute_alignment(named_meshes):
    """
    From parsed mesh bounding boxes (in mm), compute a transform that
    maps Ford coordinates → layout coordinates (inches).

    Ford's SAE coordinate system (from bounding box analysis):
        Ford X → vehicle longitudinal (front→rear) → our Y
        Ford Y → vehicle lateral (centred at 0)     → our X
        Ford Z → vehicle vertical                   → our Z

    Alignment anchors:
      • The Rear Cargo Doors max X (minus door thickness) defines the
        interior rear of the cargo area (Layout Y = CL = 172.2").
      • Ford Y = 0 is the vehicle centreline → Layout X = CW/2.
      • Ford Z = 0 is GROUND level.  The cargo floor is elevated by
        the frame/axles/floor structure.  We calibrate ford_floor_z
        from the top of the rear cargo doors (= interior ceiling).

    Returns dict consumed by transform_mesh().
    """
    meshes = [m for _, m in named_meshes]
    all_min = np.array([m['bbox'][0] for m in meshes if m])
    all_max = np.array([m['bbox'][1] for m in meshes if m])
    ford_min = all_min.min(axis=0)
    ford_max = all_max.max(axis=0)
    ford_size = ford_max - ford_min

    print(f"\n  Combined Ford BB (mm): "
          f"({ford_min[0]:.0f}, {ford_min[1]:.0f}, {ford_min[2]:.0f}) → "
          f"({ford_max[0]:.0f}, {ford_max[1]:.0f}, {ford_max[2]:.0f})")
    print(f"  Ford size (mm): {ford_size[0]:.0f} × {ford_size[1]:.0f} × {ford_size[2]:.0f}")
    print(f"  Ford size (in): {ford_size[0]/25.4:.1f} × "
          f"{ford_size[1]/25.4:.1f} × {ford_size[2]/25.4:.1f}")

    # Fixed axis mapping:
    #   Ford X → Layout Y (length)
    #   Ford Y → Layout X (width)
    #   Ford Z → Layout Z (height)
    axis_map = {0: 1, 1: 0, 2: 2}
    print(f"  Axis mapping: Ford(X,Y,Z) → Layout(Y,X,Z)")

    cargo_length_mm = CL * 25.4   # 172.2" = 4373.88 mm
    cargo_width_mm  = CW * 25.4   # 70.2"  = 1783.08 mm
    cargo_height_mm = CH * 25.4   # 81.5"  = 2070.1 mm
    DOOR_THICKNESS  = 76.0        # ~3 inches door panel thickness

    # ── Rear anchor: Rear Cargo Doors max X ────────────────────────────
    # The Rear Cargo Doors max X is the EXTERIOR rear surface of the
    # doors.  Subtracting door thickness gives the INTERIOR rear of the
    # cargo area (Layout Y = CL).
    rear_doors_x = None
    rear_doors_z = None
    for name, mesh in named_meshes:
        if "Rear Cargo Doors" in name:
            rear_doors_x = mesh['bbox'][1][0]   # max Ford X (exterior)
            rear_doors_z = mesh['bbox'][1][2]   # max Ford Z (door top)
            print(f"  Rear anchor ('{name}' max X): {rear_doors_x:.0f} mm")
            print(f"  Door top    ('{name}' max Z): {rear_doors_z:.0f} mm")
            break
    if rear_doors_x is None:
        # Fallback to Rear Door Trim
        for name, mesh in named_meshes:
            if "Rear Door Trim" in name:
                rear_doors_x = mesh['bbox'][1][0]
                rear_doors_z = mesh['bbox'][1][2]
                break
        if rear_doors_x is None:
            rear_doors_x = ford_max[0]
            rear_doors_z = ford_max[2]
        print(f"  Rear anchor (fallback): {rear_doors_x:.0f} mm")

    # Interior rear of cargo = exterior door surface minus door thickness
    rear_ref_x = rear_doors_x - DOOR_THICKNESS
    ford_partition_x = rear_ref_x - cargo_length_mm

    # ── Z calibration: Ford Z = 0 is GROUND, not cargo floor ──────────
    # The top of the rear cargo doors (max Z) corresponds to the top
    # of the door opening = approximately the interior ceiling height.
    # So:  ford_floor_z = door_top_z − cargo_height_mm
    ford_floor_z = rear_doors_z - cargo_height_mm

    print(f"  Partition at Ford X = {ford_partition_x:.0f} mm  "
          f"({ford_partition_x/25.4:.1f}\")")
    print(f"  Cargo rear at Ford X = {rear_ref_x:.0f} mm  "
          f"({rear_ref_x/25.4:.1f}\")")
    print(f"  Ford floor Z = {ford_floor_z:.0f} mm  "
          f"({ford_floor_z/25.4:.1f}\" above ground)")
    print(f"  Ford ceiling Z = {rear_doors_z:.0f} mm  "
          f"(door top → layout Z ≈ {CH:.1f}\")")

    return dict(
        ford_min=ford_min, ford_max=ford_max,
        axis_map=axis_map,
        scale=1.0 / 25.4,
        ford_partition_x=ford_partition_x,
        ford_rear_x=rear_ref_x,
        ford_floor_z=ford_floor_z,
        cargo_width_mm=cargo_width_mm,
    )


def transform_mesh(mesh, alignment):
    """Apply alignment transform to mesh vertices.

    Ford SAE coordinates → Layout coordinates:
        Ford X → Layout Y  (longitudinal → length axis)
        Ford Y → Layout X  (lateral → width axis, centered)
        Ford Z → Layout Z  (vertical → height axis)

    Returns (new_vertices, faces) in layout coordinates (inches).
    """
    if mesh is None:
        return None, None

    verts = mesh['vertices'].copy()  # (N, 3) in mm
    faces = mesh['faces']

    a = alignment
    new_verts = np.zeros_like(verts)

    # Ford X → Layout Y:  Y_layout = (ford_x - partition_x) / 25.4
    # This puts the front partition at Y=0 and rear at Y≈CL
    new_verts[:, 1] = (verts[:, 0] - a['ford_partition_x']) / 25.4

    # Ford Y → Layout X:  Ford Y is centred at 0, port side is negative Y.
    # Layout X = 0 is port, X = CW is starboard.
    # So X_layout = (ford_y + cargo_width_mm/2) / 25.4
    # But the shell is wider than the cargo, so we centre it:
    # X_layout = CW/2 + ford_y / 25.4
    new_verts[:, 0] = CW / 2.0 + verts[:, 1] / 25.4

    # Ford Z → Layout Z:  Z_layout = (ford_z - floor_z) / 25.4
    new_verts[:, 2] = (verts[:, 2] - a['ford_floor_z']) / 25.4

    return new_verts, faces


# ═════════════════════════════════════════════════════════════════════════
#  PARAMETRIC ROOF (for AP203 file that lacks tessellation)
# ═════════════════════════════════════════════════════════════════════════

def make_parametric_roof():
    """
    Generate a curved roof mesh matching the Transit High Roof profile.

    The Transit High Roof cross-section is NOT a semicircle – it has
    mostly vertical walls that curve into a relatively FLAT top.  We
    model this with a superellipse (Lamé curve):  |x/a|^n + |z/b|^n = 1
    where n ≈ 3–4 gives the characteristic "squarish" Transit profile.

    Returns (vertices, faces) in layout coordinates (inches).
    """
    n_long    = 40   # points along the length
    n_profile = 48   # points around the cross-section profile

    y_pts = np.linspace(-5, CL + 5, n_long)

    # Profile parameters (exterior dimensions)
    half_w  = CW / 2 + 4        # half-width of exterior roof (~39")
    wall_h  = 58                 # walls are vertical to 58" above floor
    peak_h  = CH + 6             # exterior roof peak (87.5")
    arch_h  = peak_h - wall_h    # curved arch from wall top to peak (29.5")
    n_exp   = 3.5                # superellipse exponent (flatter top)

    # Superellipse parametric: theta from π (port wall) to 0 (stbd wall)
    theta = np.linspace(np.pi, 0, n_profile)
    # x = a · sign(cos θ) · |cos θ|^(2/n)
    # z = b · sign(sin θ) · |sin θ|^(2/n)
    profile_x = half_w * np.sign(np.cos(theta)) * np.abs(np.cos(theta)) ** (2.0 / n_exp)
    profile_z = wall_h + arch_h * np.abs(np.sin(theta)) ** (2.0 / n_exp)

    verts = []
    for yy in y_pts:
        for xi, zi in zip(profile_x, profile_z):
            verts.append([CW / 2 + xi, yy, zi])
    verts = np.array(verts)

    faces = []
    for yi in range(n_long - 1):
        for pi in range(n_profile - 1):
            v00 = yi * n_profile + pi
            v10 = (yi + 1) * n_profile + pi
            v01 = yi * n_profile + pi + 1
            v11 = (yi + 1) * n_profile + pi + 1
            faces.append([v00, v10, v01])
            faces.append([v01, v10, v11])
    faces = np.array(faces)

    return verts, faces


# ═════════════════════════════════════════════════════════════════════════
#  PLOTLY MESH BUILDER
# ═════════════════════════════════════════════════════════════════════════

def box(name, x, y, z, dx, dy, dz, color, opacity=0.92, group=""):
    """Axis-aligned box as Mesh3d."""
    vx = [x, x+dx, x+dx, x,    x,    x+dx, x+dx, x   ]
    vy = [y, y,    y+dy, y+dy, y,    y,     y+dy, y+dy]
    vz = [z, z,    z,    z,    z+dz, z+dz,  z+dz, z+dz]
    i = [0,0, 4,4, 0,0, 1,1, 0,0, 2,2]
    j = [1,2, 5,6, 1,4, 2,5, 3,4, 3,6]
    k = [2,3, 6,7, 4,5, 5,6, 4,7, 6,7]
    return go.Mesh3d(
        x=vx, y=vy, z=vz, i=i, j=j, k=k,
        color=color, opacity=opacity,
        name=name, legendgroup=group or name, showlegend=True,
        hovertext=name, hoverinfo="text", flatshading=True,
        lighting=dict(ambient=0.55, diffuse=0.65, specular=0.25,
                      roughness=0.6, fresnel=0.15),
        lightposition=dict(x=200, y=-100, z=300),
    )


def wireframe(name, x, y, z, dx, dy, dz, color="rgba(40,40,40,0.35)"):
    """Box edge wireframe."""
    c = np.array([
        [x,y,z],[x+dx,y,z],[x+dx,y+dy,z],[x,y+dy,z],[x,y,z],[None]*3,
        [x,y,z+dz],[x+dx,y,z+dz],[x+dx,y+dy,z+dz],[x,y+dy,z+dz],
        [x,y,z+dz],[None]*3,
        [x,y,z],[x,y,z+dz],[None]*3,
        [x+dx,y,z],[x+dx,y,z+dz],[None]*3,
        [x+dx,y+dy,z],[x+dx,y+dy,z+dz],[None]*3,
        [x,y+dy,z],[x,y+dy,z+dz],
    ], dtype=object)
    return go.Scatter3d(
        x=c[:,0], y=c[:,1], z=c[:,2],
        mode="lines", line=dict(color=color, width=1.5),
        name=name+" (edge)", showlegend=False, hoverinfo="skip",
    )


def label3d(text, x, y, z, color="#ffffff", size=11):
    return go.Scatter3d(
        x=[x], y=[y], z=[z], mode="text",
        text=[text], textfont=dict(size=size, color=color, family="Arial Black"),
        showlegend=False, hoverinfo="skip",
    )


def dim_line(x0, y0, z0, x1, y1, z1, text, color="#aaaaaa"):
    mx, my, mz = (x0+x1)/2, (y0+y1)/2, (z0+z1)/2
    return [
        go.Scatter3d(
            x=[x0,x1], y=[y0,y1], z=[z0,z1],
            mode="lines+markers",
            line=dict(color=color, width=2, dash="dot"),
            marker=dict(size=3, color=color, symbol="diamond"),
            showlegend=False, hoverinfo="skip",
        ),
        label3d(text, mx, my, mz+3, color=color, size=9),
    ]


# ═════════════════════════════════════════════════════════════════════════
#  BUILD INTERIOR LAYOUT  (same as existing script)
# ═════════════════════════════════════════════════════════════════════════

def build_interior():
    traces = []

    def add(name, x, y, z, dx, dy, dz, color, opacity=0.92, group="",
            wire=True):
        traces.append(box(name, x, y, z, dx, dy, dz, color, opacity, group))
        if wire:
            traces.append(wireframe(name, x, y, z, dx, dy, dz))

    # ── SHELL (ghost) ─────────────────────────────────────────────────
    add("Floor", 0, 0, -1.5, CW, CL, 1.5, "#b8a88a", 0.40, "Shell", wire=False)

    # ── WHEEL WELLS ───────────────────────────────────────────────────
    add("Wheel Well – Port",  0,       WW_Y0, 0, WW_W, WW_Y1-WW_Y0, WW_H,
        "#7f8c8d", 0.75, "Wheel Wells")
    add("Wheel Well – Stbd",  CW-WW_W, WW_Y0, 0, WW_W, WW_Y1-WW_Y0, WW_H,
        "#7f8c8d", 0.75, "Wheel Wells")

    # ── ZONE 1: FORWARD-FACING SOFA BED ──────────────────────────────
    add("Z1 – Sofa Base",     SO_X, Z1[0], 0,     SO_W, SO_D, SO_SH,
        "#7D5A14", 0.90, "Zone 1 – Sofa Bed")
    add("Z1 – Seat Cushion",  SO_X+1.5, Z1[0]+1.5, SO_SH, SO_W-3, SO_D*0.6, 4,
        "#C9A84C", 0.95, "Zone 1 – Sofa Bed")
    add("Z1 – Backrest",      SO_X+1, Z1[0]+SO_D-5, SO_SH, SO_W-2, 5, SO_BH,
        "#A07840", 0.95, "Zone 1 – Sofa Bed")
    traces.append(label3d("SOFA BED\n(forward-facing)", CW/2, Z1[0]+12,
                          SO_SH+SO_BH+6, "#FFD966", 12))

    for bx in [SO_X+8, CW/2, SO_X+SO_W-8]:
        traces.append(go.Scatter3d(
            x=[bx], y=[Z1[0]+2], z=[2], mode="markers",
            marker=dict(size=5, color="#2C3E50", symbol="circle"),
            name="Seat belt anchor", showlegend=False,
            hovertext="3-pt seat belt",
        ))

    # ── ZONE 5: AISLE + LAGUN TABLE ──────────────────────────────────
    add("Z5 – Lagun Table",    BA_W+2, Z5[0]+12, CT_H-2, 28, 20, 1.5,
        "#8E44AD", 0.85, "Zone 5 – Aisle")
    add("Z5 – Table Pedestal", BA_W+14, Z5[0]+20, 0, 4, 4, CT_H-2,
        "#6C3483", 0.80, "Zone 5 – Aisle")
    traces.append(label3d("AISLE\n(24–26\" clear)", CW/2, (Z5[0]+Z5[1])/2, 45,
                          "#D2B4DE", 10))

    # ── ZONE 3: WET BATH (port) ──────────────────────────────────────
    add("Z3 – Bath Cabinet",   0, BA_Y0, 0,     BA_W, BA_L, CT_H,
        "#1A5276", 0.65, "Zone 3 – Wet Bath")
    add("Z3 – Counter",        0, BA_Y0, CT_H,  BA_W, BA_L, 2,
        "#BDC3C7", 0.90, "Zone 3 – Wet Bath")
    add("Z3 – Toilet",         TO_X, TO_Y, CT_H+2, TO_W, TO_D, 14,
        "#D5D8DC", 0.90, "Zone 3 – Wet Bath")
    add("Z3 – Upper Shelf",    0, BA_Y0, CT_H+18, BA_W, BA_L, 14,
        "#2E86C1", 0.35, "Zone 3 – Wet Bath")
    traces.append(label3d("WET BATH\n(hideaway)", BA_W/2, BA_Y0+BA_L/2, CT_H+38,
                          "#85C1E9", 11))

    # ── ZONE 4: GALLEY KITCHEN (starboard) ────────────────────────────
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

    # ── ZONE 2: BED PLATFORM + MATTRESS ───────────────────────────────
    add("Z2 – Bed Platform",   1, BED_Y0, 0,     CW-2, BED_D, BED_H,
        "#1E6B3A", 0.60, "Zone 2 – Bed")
    add("Z2 – Mattress",       MAT_X, MAT_Y, BED_H, MAT_W, MAT_D, MAT_H,
        "#A9DFBF", 0.92, "Zone 2 – Bed")
    add("Z2 – Water Tank",     2, BED_Y0+1, 1,    26, 20, BED_H-2,
        "#3498DB", 0.30, "Zone 2 – Bed", wire=False)
    add("Z2 – EcoFlow 10kWh",  CW-28, BED_Y0+1, 1, 26, 20, BED_H-2,
        "#F39C12", 0.30, "Zone 2 – Bed", wire=False)
    traces.append(label3d("BED PLATFORM\n(28\" high)", CW/2, BED_Y0+BED_D/2,
                          BED_H+MAT_H+8, "#82E0AA", 12))
    traces.append(label3d("RV Queen\n60\"×40\"", CW/2, MAT_Y+MAT_D/2,
                          BED_H+MAT_H+1, "#FFFFFF", 9))

    # ── ROOF FANS ─────────────────────────────────────────────────────
    for i, fy in enumerate(FAN_Y):
        add(f"Roof Fan {i+1}", CW/2-FAN_SZ/2, fy-FAN_SZ/2, CH-3,
            FAN_SZ, FAN_SZ, 3, "#E59866", 0.85, "Roof Fans")
        traces.append(label3d("MaxxAir\n14×14\"", CW/2, fy, CH+2, "#E59866", 8))

    # ── WINDOWS ───────────────────────────────────────────────────────
    wins = [(30, 68), (72, 112), (133, 170)]
    for i, (wy0, wy1) in enumerate(wins):
        add(f"Window Port {i+1}",  -1, wy0, 36, 1, wy1-wy0, 22,
            "#5DADE2", 0.25, "Windows", wire=False)
        add(f"Window Stbd {i+1}",   CW, wy0, 36, 1, wy1-wy0, 22,
            "#5DADE2", 0.25, "Windows", wire=False)

    # ── DIMENSION LINES ───────────────────────────────────────────────
    for t in dim_line(0, -8, 0, CW, -8, 0,     "◄─ 70.2\" width ─►"):
        traces.append(t)
    for t in dim_line(-8, 0, 0, -8, CL, 0,     "172.2\" length"):
        traces.append(t)
    for t in dim_line(CW+8, 0, 0, CW+8, 0, CH, "81.5\" height"):
        traces.append(t)

    # ── FRONT ARROW ───────────────────────────────────────────────────
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
        colorscale=[[0,"#E74C3C"],[1,"#E74C3C"]],
        sizemode="absolute", sizeref=6,
        showlegend=False, showscale=False, hoverinfo="skip",
    ))

    return traces


# ═════════════════════════════════════════════════════════════════════════
#  LOAD & PROCESS TRANSIT SHELL
# ═════════════════════════════════════════════════════════════════════════

SHELL_FILES = {
    "Interior Side Trim": "V363CDV F2 MY25 ELWB HR VAN INTERIOR SIDE TRIM.stp",
    "Rear Cargo Doors":   "V363CDV F2 MY25 ELWB HR REAR CARGO DOORS W WINDOWS.stp",
    "Rear Door Trim":     "V363CDV F2 MY25 HR ELWB VAN REAR CARGO DOOR INTERIOR TRIM PANELS.stp",
    # Front Seat Trim excluded — cab component, not cargo area
}

# Colors for each shell part
SHELL_COLORS = {
    "Interior Side Trim": "#a0b8cc",
    "Rear Cargo Doors":   "#90a8bc",
    "Rear Door Trim":     "#8098ac",
    "Roof (parametric)":  "#b0c8dc",
}

# Max triangles per part (keep total manageable for browser)
MAX_TRIS = {
    "Interior Side Trim": 100_000,   # largest file
    "Rear Cargo Doors":    60_000,
    "Rear Door Trim":      60_000,
}


def load_shell_parts():
    """Load and parse all AP242 STEP files, return list of (name, mesh)."""
    meshes = []

    for name, filename in SHELL_FILES.items():
        filepath = os.path.join(EXTRACT_DIR, filename)
        if not os.path.isfile(filepath):
            print(f"\n  ⚠ Missing: {filename}")
            continue

        mesh = parse_step_tessellation(filepath, max_triangles=MAX_TRIS[name])
        if mesh:
            meshes.append((name, mesh))
        gc.collect()

    return meshes


def shell_traces(meshes, alignment):
    """Convert parsed shell meshes into Plotly Mesh3d traces."""
    traces = []

    for name, mesh in meshes:
        verts, faces = transform_mesh(mesh, alignment)
        if verts is None:
            continue

        color = SHELL_COLORS.get(name, "#8899aa")
        traces.append(go.Mesh3d(
            x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
            i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
            color=color, opacity=0.15,
            name=f"Shell – {name}",
            legendgroup="Transit Shell",
            showlegend=True,
            hovertext=f"Ford Transit – {name}",
            hoverinfo="text",
            flatshading=True,
            lighting=dict(ambient=0.7, diffuse=0.5, specular=0.1,
                          roughness=0.8, fresnel=0.05),
            lightposition=dict(x=200, y=-100, z=300),
        ))
        print(f"  ✅ Added shell trace: {name} "
              f"({verts.shape[0]:,} verts, {faces.shape[0]:,} tris)")

    # ── Parametric roof ───────────────────────────────────────────────
    rv, rf = make_parametric_roof()
    traces.append(go.Mesh3d(
        x=rv[:, 0], y=rv[:, 1], z=rv[:, 2],
        i=rf[:, 0], j=rf[:, 1], k=rf[:, 2],
        color=SHELL_COLORS["Roof (parametric)"], opacity=0.10,
        name="Shell – Roof (parametric)",
        legendgroup="Transit Shell",
        showlegend=True,
        hovertext="Ford Transit – Roof (parametric)",
        hoverinfo="text",
        flatshading=True,
        lighting=dict(ambient=0.7, diffuse=0.5, specular=0.1,
                      roughness=0.8, fresnel=0.05),
    ))
    print(f"  ✅ Added parametric roof "
          f"({rv.shape[0]:,} verts, {rf.shape[0]:,} tris)")

    return traces


# ═════════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 66)
    print(" Ford Transit Van Build – 3-D with Transit Shell")
    print("=" * 66)

    # ── Step 1: Parse STEP files ──────────────────────────────────────
    print("\n▶ Loading Transit shell geometry from STEP files...")
    shell_meshes = load_shell_parts()

    if not shell_meshes:
        print("\n⚠ No shell meshes loaded. Check that STEP files are "
              "extracted to:\n  " + EXTRACT_DIR)
        print("  Falling back to parametric-only shell.")
        alignment = None
    else:
        # ── Step 2: Compute alignment ─────────────────────────────────
        print("\n▶ Computing coordinate alignment...")
        alignment = compute_alignment(shell_meshes)

    # ── Step 3: Build scene ───────────────────────────────────────────
    print("\n▶ Building interior layout...")
    traces = build_interior()

    print("\n▶ Adding Transit shell overlay...")
    if shell_meshes and alignment:
        traces.extend(shell_traces(shell_meshes, alignment))
    else:
        # Fallback: simple parametric walls + roof
        def add_simple(name, x, y, z, dx, dy, dz, color, opacity):
            traces.append(box(name, x, y, z, dx, dy, dz, color, opacity,
                              "Transit Shell"))
            traces.append(wireframe(name, x, y, z, dx, dy, dz))

        add_simple("Wall – Port",  -2, 0, 0,   2,  CL, CH, "#8899aa", 0.08)
        add_simple("Wall – Stbd",   CW, 0, 0,  2,  CL, CH, "#8899aa", 0.08)
        add_simple("Wall – Rear",   0, CL, 0,  CW, 2,  CH, "#8899aa", 0.08)
        add_simple("Ceiling",       0, 0, CH,  CW, CL, 1,  "#667788", 0.06)

        rv, rf = make_parametric_roof()
        traces.append(go.Mesh3d(
            x=rv[:,0], y=rv[:,1], z=rv[:,2],
            i=rf[:,0], j=rf[:,1], k=rf[:,2],
            color="#b0c8dc", opacity=0.10,
            name="Roof (parametric)", legendgroup="Transit Shell",
            showlegend=True, hovertext="Parametric roof",
            hoverinfo="text", flatshading=True,
        ))

    # ── Step 4: Create figure ─────────────────────────────────────────
    print("\n▶ Building Plotly figure...")
    fig = go.Figure(data=traces)

    fig.update_layout(
        title=dict(
            text=("Ford Transit 148\" ELWB High Roof – Van Build Layout "
                  "with Transit Shell<br>"
                  "<sup>Interactive 3-D · STEP geometry overlay · "
                  "All dimensions in inches</sup>"),
            font=dict(size=16, color="white", family="Arial"),
            x=0.5, xanchor="center",
        ),
        scene=dict(
            xaxis=dict(title="Width (port → stbd) [in]",
                       range=[-35, CW + 35],
                       backgroundcolor="#1a1a2e",
                       gridcolor="#2a2a4a", showbackground=True,
                       color="#8888aa"),
            yaxis=dict(title="Length (front → rear) [in]",
                       range=[-40, CL + 30],
                       backgroundcolor="#16213e",
                       gridcolor="#2a2a4a", showbackground=True,
                       color="#8888aa"),
            zaxis=dict(title="Height [in]",
                       range=[-10, CH + 40],
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
            bordercolor="#444466", borderwidth=1,
            itemsizing="constant", groupclick="toggleitem",
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        width=1600, height=950,
    )

    # Build visibility array for "Shell Only" button
    shell_only_visibility = [
        trace.legendgroup == "Transit Shell" if hasattr(trace, 'legendgroup') else False
        for trace in fig.data
    ]

    fig.update_layout(
        updatemenus=[dict(
            type="buttons", showactive=False,
            x=0.02, y=0.98, xanchor="left", yanchor="top",
            bgcolor="rgba(30,30,60,0.8)",
            font=dict(color="white", size=10),
            buttons=[
                dict(label="🔄 Reset View", method="relayout",
                     args=[{"scene.camera.eye": dict(x=1.6, y=-1.4, z=0.9)}]),
                dict(label="⬆ Top Down", method="relayout",
                     args=[{"scene.camera.eye": dict(x=0, y=0, z=2.8)}]),
                dict(label="➡ Port Side", method="relayout",
                     args=[{"scene.camera.eye": dict(x=-2.4, y=0.1, z=0.5)}]),
                dict(label="⬅ Stbd Side", method="relayout",
                     args=[{"scene.camera.eye": dict(x=2.4, y=0.1, z=0.5)}]),
                dict(label="🚗 Front", method="relayout",
                     args=[{"scene.camera.eye": dict(x=0, y=-2.4, z=0.5)}]),
                dict(label="🚪 Rear", method="relayout",
                     args=[{"scene.camera.eye": dict(x=0, y=2.4, z=0.5)}]),
                dict(label="👁 Shell Only", method="restyle",
                     args=["visible", shell_only_visibility]),
            ],
        )],
    )

    # ── Step 5: Save ──────────────────────────────────────────────────
    html_path = os.path.join(OUT_DIR, "20260220-1700-3d-transit-shell.html")
    fig.write_html(
        html_path,
        include_plotlyjs="cdn",
        full_html=True,
        config=dict(
            displayModeBar=True,
            toImageButtonOptions=dict(format="png", width=2400,
                                      height=1500, scale=2),
        ),
    )
    size_kb = os.path.getsize(html_path) // 1024
    print(f"\n✅  HTML saved: {html_path}  ({size_kb:,} KB)")

    # Static PNG
    png_path = os.path.join(OUT_DIR, "20260220-1700-3d-transit-shell.png")
    try:
        fig.write_image(png_path, width=2400, height=1500, scale=2)
        size_kb = os.path.getsize(png_path) // 1024
        print(f"✅  PNG saved:  {png_path}  ({size_kb:,} KB)")
    except Exception as e:
        print(f"⚠️  PNG skipped: {e}")

    print(f"\n📂  Output: {os.path.abspath(OUT_DIR)}")
    print("🖱️  Open the HTML in your browser. Click + drag to rotate, "
          "scroll to zoom.")
    print("    Toggle shell/interior visibility via the legend.")


if __name__ == "__main__":
    main()
