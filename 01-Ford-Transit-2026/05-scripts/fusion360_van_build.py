"""
Ford Transit 148" ELWB High Roof – Fusion 360 Parametric Van Build
===================================================================
Run this script inside Fusion 360:
  1.  Open Fusion 360
  2.  Menu → UTILITIES → Scripts and Add-Ins  (or press Shift+S)
  3.  Click ＋ next to "My Scripts" → Create New Script → Python
  4.  Replace the generated code with this file's contents
  5.  Click ▶ Run
  6.  The van interior will be built in the active design.

After running, import the Ford Transit STEP body shells from:
   03-inputs/ford-transit-3d-models/  (extract .zip → .stp files)

All units: CENTIMETERS (Fusion default) — we convert from inches internally.
"""

import adsk.core
import adsk.fusion
import traceback

# ═══════════════════════════════════════════════════════════════════════════
# UNIT CONVERSION
# ═══════════════════════════════════════════════════════════════════════════
def in2cm(inches: float) -> float:
    """Convert inches to centimeters (Fusion's internal unit)."""
    return inches * 2.54

# ═══════════════════════════════════════════════════════════════════════════
# DIMENSIONS  (all in INCHES — converted to cm at draw-time)
# ═══════════════════════════════════════════════════════════════════════════

# Cargo interior envelope
CL = 172.2   # length (front partition → rear doors)
CW = 70.2    # width  (port wall → starboard wall)
CH = 81.5    # height (floor → ceiling)

# Wheel wells
WW_CLR = 54.8
WW_W   = (CW - WW_CLR) / 2   # ≈7.7″ protrusion each side
WW_Y0  = 60.0
WW_Y1  = 118.0
WW_H   = 13.5

# Zone boundaries  (Y measured from front partition toward rear)
Z1  = (0.0,   28.0)    # Forward-facing sofa bed
Z5  = (28.0,  70.0)    # Dining / living aisle
Z34 = (70.0,  114.0)   # Wet bath (port) + Galley (stbd)
ZTR = (114.0, 130.0)   # Transition
Z2  = (130.0, 172.2)   # East-west bed platform

# Zone 1: Sofa bed
SO_W  = 48.0
SO_D  = 24.0
SO_X  = (CW - SO_W) / 2   # centred
SO_SH = 16.0               # seat height
SO_BH = 18.0               # backrest height

# Zone 3: Wet bath (port)
BA_W  = 26.0
BA_Y0 = Z34[0]
BA_L  = 44.0
CT_H  = 36.0   # counter height

# Toilet
TO_W, TO_D = 16.0, 16.0
TO_X  = 5.0
TO_Y  = BA_Y0 + BA_L - TO_D - 2

# Zone 4: Galley (starboard)
GA_D  = 22.0
GA_X0 = CW - GA_D
GA_Y0 = Z34[0]
GA_L  = 44.0

# Fridge
FR_W, FR_D, FR_H = 24.0, 20.0, 23.0
FR_X, FR_Y = GA_X0, GA_Y0

# Sink
SK_W, SK_D, SK_H = 15.0, 13.0, 7.0
SK_X = GA_X0 + FR_W
SK_Y = GA_Y0

# Zone 2: Bed platform
BED_Y0 = Z2[0]
BED_D  = Z2[1] - Z2[0]
BED_H  = 28.0
MAT_W  = 60.0
MAT_D  = 40.0
MAT_H  = 10.0
MAT_X  = (CW - MAT_W) / 2
MAT_Y  = BED_Y0 + (BED_D - MAT_D) / 2

# Roof fans
FAN_Y  = [49.0, 92.0]
FAN_SZ = 14.0

# ═══════════════════════════════════════════════════════════════════════════
# COLOUR TABLE  (R, G, B each 0-255)
# ═══════════════════════════════════════════════════════════════════════════
COLOURS = {
    "floor":      (210, 198, 175),
    "wall_ghost": (180, 190, 200),
    "wheel_well": (149, 165, 166),
    "sofa_base":  (125, 90,  20),
    "sofa_cush":  (201, 168, 76),
    "backrest":   (160, 120, 64),
    "bath_cab":   (26,  82,  118),
    "bath_counter": (189, 195, 199),
    "toilet":     (213, 216, 220),
    "galley_cab": (109, 58,  14),
    "galley_ctr": (189, 195, 199),
    "fridge":     (46,  134, 193),
    "sink":       (133, 193, 233),
    "bed_plat":   (30,  107, 58),
    "mattress":   (169, 223, 191),
    "fan":        (229, 152, 102),
    "transition": (200, 200, 200),
}


# ═══════════════════════════════════════════════════════════════════════════
# HELPER: create a box (rectangular prism) body in the given component
# ═══════════════════════════════════════════════════════════════════════════
def make_box(comp, name, x, y, z, dx, dy, dz, rgb):
    """
    Create a named rectangular-prism body at (x, y, z) with size (dx, dy, dz).
    Coordinates are in INCHES — converted to cm for Fusion.
    rgb = (R, G, B) 0-255.
    
    Fusion coordinate mapping:
       Our X (port→stbd) → Fusion +X
       Our Y (front→rear) → Fusion +Y
       Our Z (floor→ceiling) → Fusion +Z
    """
    sketches = comp.sketches
    xy_plane = comp.xYConstructionPlane

    # --- Sketch a rectangle on XY plane ---
    sketch = sketches.add(xy_plane)
    sketch.name = f"{name}_sketch"
    lines = sketch.sketchCurves.sketchLines
    x_cm  = in2cm(x)
    y_cm  = in2cm(y)
    dx_cm = in2cm(dx)
    dy_cm = in2cm(dy)
    dz_cm = in2cm(dz)
    z_cm  = in2cm(z)

    p0 = adsk.core.Point3D.create(x_cm,        y_cm,        0)
    p1 = adsk.core.Point3D.create(x_cm + dx_cm, y_cm,        0)
    p2 = adsk.core.Point3D.create(x_cm + dx_cm, y_cm + dy_cm, 0)
    p3 = adsk.core.Point3D.create(x_cm,        y_cm + dy_cm, 0)
    lines.addByTwoPoints(p0, p1)
    lines.addByTwoPoints(p1, p2)
    lines.addByTwoPoints(p2, p3)
    lines.addByTwoPoints(p3, p0)

    # --- Extrude ---
    prof = sketch.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(dz_cm))

    ext = extrudes.add(ext_input)
    body = ext.bodies.item(0)
    body.name = name

    # --- Move up to Z offset ---
    if abs(z) > 0.001:
        move_feats = comp.features.moveFeatures
        bodies_coll = adsk.core.ObjectCollection.create()
        bodies_coll.add(body)
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, z_cm)
        move_input = move_feats.createInput2(bodies_coll)
        move_input.defineAsFreeMove(transform)
        move_feats.add(move_input)

    # --- Appearance / colour ---
    try:
        r, g, b = rgb
        app = adsk.core.Application.get()
        des = app.activeProduct
        appearances = des.appearances
        # clone a generic appearance
        base_lib = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
        if base_lib:
            generic = None
            for i in range(base_lib.appearances.count):
                a = base_lib.appearances.item(i)
                if "generic" in a.name.lower() or "plastic" in a.name.lower():
                    generic = a
                    break
            if generic:
                new_app = appearances.addByCopy(generic, f"{name}_colour")
                # set colour
                colour_prop = None
                for prop_idx in range(new_app.appearanceProperties.count):
                    prop = new_app.appearanceProperties.item(prop_idx)
                    if hasattr(prop, "value") and isinstance(
                        getattr(prop, "value", None), adsk.core.Color
                    ):
                        colour_prop = prop
                        break
                if colour_prop:
                    colour_prop.value = adsk.core.Color.create(r, g, b, 255)
                body.appearance = new_app
    except Exception:
        pass   # colouring is best-effort

    return body


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
def run(context):
    app = adsk.core.Application.get()
    ui  = app.userInterface

    try:
        # --- Create new design ---
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        root = design.rootComponent
        root.name = "Ford Transit 148 ELWB – Van Build"

        ui.messageBox(
            "Building Ford Transit van interior layout…\n\n"
            "This will create parametric 3-D bodies for:\n"
            "  • Floor slab + ghost walls\n"
            "  • Wheel wells\n"
            "  • Zone 1: Forward-facing sofa bed\n"
            "  • Zone 3: Wet bath (port side)\n"
            "  • Zone 4: Galley kitchen (stbd side)\n"
            "  • Zone 2: East-west bed platform + mattress\n"
            "  • Roof fans\n\n"
            "After completion, import the Transit body STEP files\n"
            "from 03-inputs/ to overlay the shell.\n\n"
            "Click OK to start.",
            "Van Build 3-D Generator"
        )

        # ══════════════════════════════════════════════════════════════════
        # FLOOR
        # ══════════════════════════════════════════════════════════════════
        make_box(root, "Floor_Slab",
                 0, 0, -1.5,  CW, CL, 1.5,
                 COLOURS["floor"])

        # ══════════════════════════════════════════════════════════════════
        # GHOST WALLS  (thin, translucent-ish reference)
        # ══════════════════════════════════════════════════════════════════
        make_box(root, "Wall_Port",
                 -2, 0, 0,  2, CL, CH,
                 COLOURS["wall_ghost"])
        make_box(root, "Wall_Starboard",
                 CW, 0, 0,  2, CL, CH,
                 COLOURS["wall_ghost"])
        make_box(root, "Wall_Rear",
                 0, CL, 0,  CW, 2, CH,
                 COLOURS["wall_ghost"])
        make_box(root, "Ceiling_Ghost",
                 0, 0, CH,  CW, CL, 1.5,
                 COLOURS["wall_ghost"])

        # ══════════════════════════════════════════════════════════════════
        # WHEEL WELLS
        # ══════════════════════════════════════════════════════════════════
        make_box(root, "WheelWell_Port",
                 0, WW_Y0, 0,  WW_W, WW_Y1 - WW_Y0, WW_H,
                 COLOURS["wheel_well"])
        make_box(root, "WheelWell_Stbd",
                 CW - WW_W, WW_Y0, 0,  WW_W, WW_Y1 - WW_Y0, WW_H,
                 COLOURS["wheel_well"])

        # ══════════════════════════════════════════════════════════════════
        # ZONE 1 — FORWARD-FACING SOFA BED
        # ══════════════════════════════════════════════════════════════════
        make_box(root, "Z1_Sofa_Base",
                 SO_X, Z1[0], 0,
                 SO_W, SO_D, SO_SH,
                 COLOURS["sofa_base"])

        make_box(root, "Z1_Seat_Cushion",
                 SO_X + 1.5, Z1[0] + 1.5, SO_SH,
                 SO_W - 3, SO_D * 0.6, 4,
                 COLOURS["sofa_cush"])

        # Backrest — toward front of van (lower Y values)
        make_box(root, "Z1_Backrest",
                 SO_X + 1, Z1[0] + SO_D - 5, SO_SH,
                 SO_W - 2, 5, SO_BH,
                 COLOURS["backrest"])

        # Under-seat storage cavity (visual)
        make_box(root, "Z1_UnderSeat_Storage",
                 SO_X + 2, Z1[0] + 2, 0,
                 SO_W - 4, SO_D - 4, 12,
                 (215, 219, 221))

        # ══════════════════════════════════════════════════════════════════
        # ZONE 3 — WET BATH  (port / left side)
        # ══════════════════════════════════════════════════════════════════
        # Base cabinet
        make_box(root, "Z3_Bath_Cabinet",
                 0, BA_Y0, 0,
                 BA_W, BA_L, CT_H,
                 COLOURS["bath_cab"])

        # Countertop
        make_box(root, "Z3_Bath_Counter",
                 0, BA_Y0, CT_H,
                 BA_W, BA_L, 2.0,
                 COLOURS["bath_counter"])

        # Toilet (Laveo dry flush)
        make_box(root, "Z3_Toilet",
                 TO_X, TO_Y, CT_H + 2,
                 TO_W, TO_D, 14,
                 COLOURS["toilet"])

        # Upper storage (open shelving above counter)
        make_box(root, "Z3_Upper_Shelf",
                 0, BA_Y0, CT_H + 18,
                 BA_W, BA_L, 14,
                 (214, 234, 248))

        # ══════════════════════════════════════════════════════════════════
        # ZONE 4 — GALLEY KITCHEN  (starboard / right side)
        # ══════════════════════════════════════════════════════════════════
        # Base cabinet
        make_box(root, "Z4_Galley_Cabinet",
                 GA_X0, GA_Y0, 0,
                 GA_D, GA_L, CT_H,
                 COLOURS["galley_cab"])

        # Countertop
        make_box(root, "Z4_Galley_Counter",
                 GA_X0, GA_Y0, CT_H,
                 GA_D, GA_L, 2.0,
                 COLOURS["galley_ctr"])

        # Fridge (front-opening 90L)
        make_box(root, "Z4_Fridge_90L",
                 FR_X, FR_Y, 0,
                 FR_W, FR_D, FR_H,
                 COLOURS["fridge"])

        # Sink recess
        make_box(root, "Z4_Sink",
                 SK_X, SK_Y, CT_H - SK_H,
                 SK_W, SK_D, SK_H,
                 COLOURS["sink"])

        # Upper cabinets
        make_box(root, "Z4_Upper_Cabinet",
                 GA_X0, GA_Y0, CT_H + 18,
                 GA_D, GA_L, 18,
                 (139, 98, 72))

        # ══════════════════════════════════════════════════════════════════
        # TRANSITION ZONE
        # ══════════════════════════════════════════════════════════════════
        make_box(root, "Transition_Floor_Marker",
                 0, ZTR[0], -0.5,
                 CW, ZTR[1] - ZTR[0], 0.5,
                 COLOURS["transition"])

        # ══════════════════════════════════════════════════════════════════
        # ZONE 2 — BED PLATFORM + MATTRESS
        # ══════════════════════════════════════════════════════════════════
        # Platform
        make_box(root, "Z2_Bed_Platform",
                 1, BED_Y0, 0,
                 CW - 2, BED_D, BED_H,
                 COLOURS["bed_plat"])

        # Mattress
        make_box(root, "Z2_Mattress_RVQueen",
                 MAT_X, MAT_Y, BED_H,
                 MAT_W, MAT_D, MAT_H,
                 COLOURS["mattress"])

        # Under-bed water tank (port)
        make_box(root, "Z2_WaterTank_25gal",
                 2, BED_Y0 + 1, 1,
                 26, 20, BED_H - 2,
                 (52, 152, 219))

        # Under-bed EcoFlow batteries (stbd)
        make_box(root, "Z2_EcoFlow_10kWh",
                 CW - 28, BED_Y0 + 1, 1,
                 26, 20, BED_H - 2,
                 (243, 156, 18))

        # ══════════════════════════════════════════════════════════════════
        # ROOF FANS  (MaxxAir Deluxe 14×14″)
        # ══════════════════════════════════════════════════════════════════
        for i, fy in enumerate(FAN_Y):
            make_box(root, f"RoofFan_{i+1}",
                     CW / 2 - FAN_SZ / 2, fy - FAN_SZ / 2, CH - 3,
                     FAN_SZ, FAN_SZ, 3,
                     COLOURS["fan"])

        # ══════════════════════════════════════════════════════════════════
        # LAGUN TABLE  (deployed position in Zone 5 aisle)
        # ══════════════════════════════════════════════════════════════════
        make_box(root, "Z5_Lagun_Table",
                 BA_W + 2, Z5[0] + 12, CT_H - 2,
                 28, 20, 1.5,
                 (142, 68, 173))
        # table pedestal
        make_box(root, "Z5_Table_Pedestal",
                 BA_W + 2 + 12, Z5[0] + 12 + 8, 0,
                 4, 4, CT_H - 2,
                 (100, 50, 130))

        # ══════════════════════════════════════════════════════════════════
        # FIT VIEW
        # ══════════════════════════════════════════════════════════════════
        viewport = app.activeViewport
        viewport.fit()

        ui.messageBox(
            "✅  Van interior layout created successfully!\n\n"
            "Bodies created:\n"
            f"  • {root.bRepBodies.count} solid bodies\n\n"
            "Next steps:\n"
            "  1. Import Transit body STEP files from 03-inputs/\n"
            "     (File → Open → select .stp files)\n"
            "  2. Position the shell around this interior\n"
            "  3. Export as STEP / render as needed\n\n"
            "All dimensions are to-scale from the spec.\n"
            "Bodies are named by zone for easy editing.",
            "Van Build Complete"
        )

    except Exception:
        if ui:
            ui.messageBox(
                f"Error:\n{traceback.format_exc()}",
                "Van Build Script Error"
            )
