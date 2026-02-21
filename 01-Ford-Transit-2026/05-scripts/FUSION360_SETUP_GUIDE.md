# Fusion 360 – Van Build 3-D Model Setup Guide

## Quick Start (5 minutes)

### Step 1: Open Fusion 360
Launch from: `C:\Users\Raj\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Autodesk\Autodesk Fusion.lnk`

### Step 2: Run the Interior Layout Script
1. In Fusion, go to **UTILITIES → Scripts and Add-Ins** (or press **Shift+S**)
2. Click the **＋** icon next to **"My Scripts"**
3. Choose **Create New Script → Python**
4. Name it: `VanBuild_FordTransit`
5. Fusion will open a code editor with a template — **replace all the code** with the contents of:
   ```
   05-scripts/fusion360_van_build.py
   ```
6. Click **▶ Run**
7. A dialog will confirm → click **OK** to start building

The script will create **~25 named solid bodies** representing every zone of the van interior — all to scale.

### Step 3: Import the Ford Transit Body Shell
The STEP files for the actual Transit body are in:
```
03-inputs/ford-transit-3d-models/
```

**For the cargo area shell, use these files first:**

| Priority | Folder | File to extract | What it is |
|----------|--------|-----------------|------------|
| 1 | `2025 Transit - Interior Trim/` | `V363CDV F2 MY25 ELWB HR VAN INTERIOR SIDE TRIM.zip` → `.stp` | Interior side walls |
| 2 | `2025 Transit - Rear Cargo Doors…/` | `V363CDV F2 MY25 ELWB HR REAR CARGO DOORS W WINDOWS.zip` → `.stp` | Rear barn doors with windows |
| 3 | `2025 Transit - Roof and CHMSL…/` | `V363CDV F3 MY25 ELWB HR ROOF.zip` → `.stp` | Roof panel |
| 4 | `2025 Transit - Interior/` | `V363CDV F2 MY25 FRONT SEAT TRIM.zip` → `.stp` | Front seats |
| 5 | `2025 Transit - Grab Handles/` | `V363CDV F2 MY25 MR HR ELWB D PILLAR GRAB HANDLE.zip` → `.stp` | D-pillar grab handle |

**To import in Fusion:**
1. Extract the `.zip` to get the `.stp` file
2. **File → Open** → select the `.stp` file
3. It opens in a new tab — right-click the body → **Copy**
4. Switch to the van build tab → right-click root component → **Paste**
5. Use **MOVE/COPY** (press **M**) to position the shell around the interior

### Step 4: Align the Shell
The interior layout uses this coordinate system:
- **Origin (0, 0, 0)** = front-left floor corner (port side, at partition)
- **+X** = port → starboard (0 to 70.2″ = 0 to 178.3 cm)
- **+Y** = front → rear (0 to 172.2″ = 0 to 437.4 cm)
- **+Z** = floor → ceiling (0 to 81.5″ = 0 to 207.0 cm)

The Ford STEP files use their own coordinate system — you'll need to translate/rotate them to match. The interior side trim file is the best reference for alignment since it defines the cargo walls.

---

## What the Script Creates

| Body Name | Zone | Description | Dimensions (in) |
|-----------|------|-------------|------------------|
| `Floor_Slab` | — | LVP flooring base | 70.2 × 172.2 × 1.5 |
| `Wall_Port` | — | Ghost wall (port) | 2 × 172.2 × 81.5 |
| `Wall_Starboard` | — | Ghost wall (stbd) | 2 × 172.2 × 81.5 |
| `Wall_Rear` | — | Ghost rear wall | 70.2 × 2 × 81.5 |
| `Ceiling_Ghost` | — | Ghost ceiling | 70.2 × 172.2 × 1.5 |
| `WheelWell_Port` | — | Port wheel well | 7.7 × 58 × 13.5 |
| `WheelWell_Stbd` | — | Stbd wheel well | 7.7 × 58 × 13.5 |
| `Z1_Sofa_Base` | 1 | Sofa bed frame | 48 × 24 × 16 |
| `Z1_Seat_Cushion` | 1 | Seat cushion | 45 × 14.4 × 4 |
| `Z1_Backrest` | 1 | Backrest (forward-facing) | 46 × 5 × 18 |
| `Z1_UnderSeat_Storage` | 1 | Storage cavity | 44 × 20 × 12 |
| `Z3_Bath_Cabinet` | 3 | Wet bath base cabinet | 26 × 44 × 36 |
| `Z3_Bath_Counter` | 3 | Counter surface | 26 × 44 × 2 |
| `Z3_Toilet` | 3 | Laveo dry flush toilet | 16 × 16 × 14 |
| `Z3_Upper_Shelf` | 3 | Open shelving | 26 × 44 × 14 |
| `Z4_Galley_Cabinet` | 4 | Kitchen base cabinet | 22 × 44 × 36 |
| `Z4_Galley_Counter` | 4 | Kitchen counter | 22 × 44 × 2 |
| `Z4_Fridge_90L` | 4 | Front-open fridge | 24 × 20 × 23 |
| `Z4_Sink` | 4 | Composite sink | 15 × 13 × 7 |
| `Z4_Upper_Cabinet` | 4 | Upper kitchen cabs | 22 × 44 × 18 |
| `Z2_Bed_Platform` | 2 | Bed platform frame | 68.2 × 42.2 × 28 |
| `Z2_Mattress_RVQueen` | 2 | RV Queen mattress | 60 × 40 × 10 |
| `Z2_WaterTank_25gal` | 2 | Fresh water (under bed) | 26 × 20 × 26 |
| `Z2_EcoFlow_10kWh` | 2 | Batteries (under bed) | 26 × 20 × 26 |
| `RoofFan_1` | — | MaxxAir fan 1 | 14 × 14 × 3 |
| `RoofFan_2` | — | MaxxAir fan 2 | 14 × 14 × 3 |
| `Z5_Lagun_Table` | 5 | Table surface | 28 × 20 × 1.5 |
| `Z5_Table_Pedestal` | 5 | Table leg/pedestal | 4 × 4 × 34 |

---

## Tips

- **Hide ghost walls** (right-click → Hide) to see inside clearly
- **Section Analysis** (INSPECT → Section Analysis) cuts through the model for elevation views
- Use **Render** workspace for photorealistic renders
- Export as **STEP** (File → Export → .step) to share with fabricators
- The script uses **Direct Design** mode — all bodies are independent and editable
- Body names match zone numbers from the spec for easy cross-referencing
