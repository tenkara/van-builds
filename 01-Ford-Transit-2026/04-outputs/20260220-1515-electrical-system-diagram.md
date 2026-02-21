# Ford Transit 148" ELWB - Electrical System Diagram v3.0
## EcoFlow Power Kit Gen 2 - 10kWh Configuration

**Date:** February 20, 2026
**System:** EcoFlow Power Kit Gen 2 with 800W Solar, 6000W Alternator Charging
**Battery Capacity:** 10kWh (2× 5kWh LFP modules) - Expandable to 15kWh
**Inverter:** 5kVA (5000W continuous / 10,000W surge peak)

---

## SYSTEM ARCHITECTURE OVERVIEW

```
                    POWER INPUTS
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐    ┌─────▼──────┐   ┌────▼─────┐
   │ SOLAR   │    │ ALTERNATOR │   │  SHORE   │
   │ 800W    │    │   6000W    │   │  POWER   │
   │ (Roof)  │    │  (Engine)  │   │  30A/50A │
   └────┬────┘    └─────┬──────┘   └────┬─────┘
        │                │                │
        │         ┌──────▼────────────────▼──────┐
        └────────→│  ECOFLOW POWER HUB (5kVA)   │
                  │  - Dual MPPT Solar (4800W)   │
                  │  - Alternator Input (6000W)  │
                  │  - Shore Power (4000-6000W)  │
                  │  - Smart BMS & Monitoring    │
                  └──────────┬──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  LFP BATTERIES  │
                    │  2× 5kWh = 10kWh│
                    │  (Expandable)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │ 12V DC  │         │ 120V AC │         │MONITORING│
   │ LOADS   │         │ LOADS   │         │& CONTROL │
   │ (50A)   │         │(5000W)  │         │ (WiFi)   │
   └─────────┘         └─────────┘         └──────────┘
```

---

## ECOFLOW POWER KIT GEN 2 - COMPONENT SPECIFICATIONS

### Power Hub (Brain of the System)
- **Model:** EcoFlow Power Hub Gen 2
- **Inverter Output:** 5000W continuous / 10,000W surge (2-second peak)
- **Voltage:** 48V DC battery input → 120V AC output + 12V DC output
- **Efficiency:** 90% (inverter), 98% (MPPT solar)
- **Dimensions:** 14"W × 10"D × 6"H
- **Weight:** 22 lbs
- **Cooling:** Active fan-cooled
- **Location:** Under bed platform, starboard side access panel

**Integrated Features:**
- Dual MPPT solar charge controllers (4800W max combined)
- Alternator charging controller (6000W / 800A max)
- Shore power charging with power factor correction
- Smart battery management system (BMS)
- WiFi monitoring and control via EcoFlow app
- Automatic transfer switch (shore → battery seamless)
- Overload, short circuit, thermal protection

### LFP Battery Modules (2× 5kWh = 10kWh Total)
- **Model:** EcoFlow Power Kit LFP Battery (5kWh per unit)
- **Chemistry:** LiFePO4 (Lithium Iron Phosphate)
- **Voltage:** 48V nominal (51.2V actual)
- **Capacity per unit:** 5120Wh (100Ah @ 51.2V)
- **Total capacity:** 10,240Wh (10.24kWh)
- **Cycle life:** 3000+ cycles to 80% capacity
- **Operating temp:** -4°F to 113°F (-20°C to 45°C)
- **Dimensions per unit:** 20"W × 10"D × 12"H
- **Weight per unit:** 110 lbs
- **Total weight:** 220 lbs (both batteries)
- **Location:** Under bed platform, port side access panel
- **Expandability:** Can add 1× additional 5kWh module for 15kWh total

**BMS Features:**
- Cell balancing (automatic)
- Over/under voltage protection
- Over-current protection (200A continuous, 300A peak)
- Temperature monitoring per cell
- State of Charge (SOC) accuracy ±3%

### Smart Distribution Panel
- **Model:** EcoFlow Smart Distribution Panel
- **Integrated into Power Hub**
- **12V DC Outputs:** 6× circuits (50A total capacity)
- **120V AC Outputs:** Via standard household breaker panel (separate)
- **Fusing:** Automatic blade fuses (ATO/ATC style)
- **Monitoring:** Real-time per-circuit current monitoring
- **Location:** Mounted adjacent to Power Hub under bed

---

## SOLAR CHARGING SYSTEM

### Solar Panel Array (800W Total)

```
ROOF PLAN - SOLAR LAYOUT:

         FRONT OF VAN ↑
    ┌─────────────────────────────────┐
    │                                 │
    │   ╔═══════════════════════╗     │  PANEL 1
    │   ║  SOLAR PANEL 1        ║     │  400W Monocrystalline
    │   ║  400W / 24V           ║     │  41"×79" (Tilted 10°)
    │   ║  22A Vmp: 48V         ║     │
    │   ╚═══════════════════════╝     │
    │                                 │
    │         [VENT SPACE]            │  Future AC unit location
    │      (for future AC)            │
    │                                 │
    │   ╔═══════════════════════╗     │  PANEL 2
    │   ║  SOLAR PANEL 2        ║     │  400W Monocrystalline
    │   ║  400W / 24V           ║     │  41"×79" (Tilted 10°)
    │   ║  22A Vmp: 48V         ║     │
    │   ╚═══════════════════════╝     │
    │                                 │
    └─────────────────────────────────┘
          REAR OF VAN ↓
```

**Solar Panel Specifications (Each):**
- **Model:** Renogy 400W Monocrystalline or equivalent
- **Rated Power:** 400W (800W total)
- **Voltage at Max Power (Vmp):** 48V
- **Current at Max Power (Imp):** 8.3A
- **Open Circuit Voltage (Voc):** 58V
- **Short Circuit Current (Isc):** 9.2A
- **Efficiency:** 22.5%
- **Dimensions:** 41"W × 79"L × 1.5"H (each panel)
- **Weight:** 45 lbs each (90 lbs total)
- **Frame:** Aluminum alloy (walkable with proper support)
- **Warranty:** 25-year power output, 10-year materials

**Roof Rack System:**
- Aluminum walkable roof rack (heavy-duty)
- Panels mounted on tilt brackets (5-15° adjustable)
- Rack doubles as roof deck platform for access
- Load capacity: 600 lbs (includes person + panels)
- Brands: Aluminess, RB Components custom

**Solar Charge Controller:**
- Integrated dual MPPT in EcoFlow Power Hub
- MPPT 1: 400W (Panel 1)
- MPPT 2: 400W (Panel 2)
- Combined max input: 4800W (future expansion capable)
- Voltage range: 16-150V DC input
- Automatic CV/CC charging profile

**Solar Wiring:**
- **Cable:** 10 AWG marine-grade tinned copper (UV-resistant)
- **Conduit:** Liquid-tight flexible conduit through roof entry
- **Entry gland:** Waterproof cable entry (Scanstrut or similar)
- **Fusing:** 15A inline fuse per panel (at panel junction box)
- **Combiner box:** Roof-mounted weatherproof box
- **Run length:** ~25 feet from roof to under-bed Power Hub

**Daily Solar Production (Estimate):**
- **Peak conditions (summer):** 800W × 5 hours = 4kWh/day
- **Average conditions (spring/fall):** 800W × 4 hours = 3.2kWh/day
- **Poor conditions (winter/cloudy):** 800W × 2 hours = 1.6kWh/day

---

## ALTERNATOR CHARGING SYSTEM

### Alternator Charger (Engine-Based Charging)

```
UNDER HOOD CONNECTION:

    ┌─────────────────────────────────┐
    │   FORD TRANSIT ENGINE BAY       │
    │                                 │
    │  ┌──────────────┐               │
    │  │ ALTERNATOR   │               │  Stock Ford alternator
    │  │  (Stock)     │───┐           │  220-250A output
    │  │  220-250A    │   │           │
    │  └──────────────┘   │           │
    │                     │           │
    │                     ▼           │
    │             ┌───────────────┐   │
    │             │ BATTERY       │   │  Ford starter battery
    │             │ (Starter)     │   │  (stock, untouched)
    │             │ 12V AGM       │   │
    │             └───────┬───────┘   │
    │                     │           │
    │                     │ ←─── TAP POINT (professional install)
    │                     │           │
    │                     ▼           │
    │         ┌──────────────────────┐│
    │         │  ECOFLOW ALTERNATOR  ││  6000W / 800A max input
    │         │  CHARGING CABLE      ││  Voltage: 12-15V input
    │         │  (Heavy gauge)       ││  → 48V battery output
    │         └──────────┬───────────┘│
    │                    │            │
    │                    │ ←─── Through firewall grommet
    │                    │            │
    └────────────────────┼────────────┘
                         │
                         ▼
              TO CARGO AREA (under bed)
              ECOFLOW POWER HUB
```

**Alternator Charger Specifications:**
- **Model:** EcoFlow Alternator Charger Cable (Gen 2)
- **Max Input:** 6000W / 800A from 12V system
- **Input Voltage Range:** 12-15V DC (alternator output)
- **Output to Batteries:** 48V DC (charges LFP batteries)
- **Efficiency:** 95%
- **Cable Gauge:** 2/0 AWG (ultra-heavy duty)
- **Cable Length:** 15 feet (under-hood to cargo area)
- **Fusing:** 300A ANL fuse at tap point (starter battery)
- **Installation:** PROFESSIONAL REQUIRED (tap into starter battery + terminal)

**Charging Rate While Driving:**
- **At idle (800 RPM):** ~1000W (~20A @ 48V) = 1kWh/hour
- **At cruise (1500-2500 RPM):** ~4000-6000W (~80-125A @ 48V) = 4-6kWh/hour
- **Full 10kWh recharge:** 2-3 hours of highway driving

**Smart Charging Logic:**
- Monitors starter battery voltage (prevents draining starter)
- Disconnects if starter battery < 12.8V (engine off)
- Reduces charge rate if alternator overheats
- Prioritizes starter battery, then house batteries

**Installation Notes:**
- Tap point: Positive terminal of starter battery (with 300A fuse)
- Negative: Chassis ground near battery
- Route through existing firewall grommet or create new sealed entry
- Secure cable away from hot exhaust components
- Use split loom or conduit for protection

---

## SHORE POWER SYSTEM

### Shore Power Inlet & Charging

```
EXTERIOR PORT SIDE (Mid-Galley Location):

    VAN EXTERIOR WALL
    ═════════════════════════
         │
         │  ┌───────────────┐
         └──┤ SHORE POWER   │  Marinco 30A inlet
            │ INLET         │  (weatherproof)
            │ 30A / 120V    │
            └───────┬───────┘
                    │
    ═════════════════════════
         │          │
    VAN INTERIOR   │
         │          │
         │  ┌───────▼───────────────┐
         │  │ SHORE POWER CABLE     │  25-50 ft detachable cable
         │  │ (25-50 ft)            │  30A RV-style
         │  └───────┬───────────────┘
         │          │
         │  ┌───────▼───────────────┐
         └──┤ ECOFLOW POWER HUB     │  Integrated shore charger
            │ AC Input (4000W max)  │  Charges batteries + pass-thru
            └───────────────────────┘
```

**Shore Power Inlet:**
- **Model:** Marinco 30A Power Inlet (stainless steel)
- **Voltage:** 120V AC
- **Amperage:** 30A (4000W max)
- **Plug Type:** NEMA TT-30R (RV standard)
- **Location:** Port side exterior, mid-galley (4 feet from rear)
- **Mounting:** Recessed inlet with weatherproof cover
- **Wiring:** 10 AWG 3-conductor (hot, neutral, ground)

**Optional 50A Upgrade:**
- **Inlet:** Marinco 50A Power Inlet
- **Amperage:** 50A (6000W max)
- **Plug Type:** NEMA 14-50R
- **Benefit:** Faster shore charging + higher AC load capacity
- **Required:** Heavier 6 AWG wiring

**Shore Power Cable:**
- **Length:** 25-50 feet (detachable, stored in under-bed garage)
- **Gauge:** 10 AWG (for 30A) or 6 AWG (for 50A)
- **Type:** RV-grade outdoor rated cable
- **Connectors:** Weatherproof twist-lock

**Shore Charging Performance:**
- **30A Shore Power:** 4000W max → ~3500W to batteries (after losses)
  - Charging rate: ~70A @ 48V
  - 0-100% charge time: ~3.5 hours (10kWh battery)
- **50A Shore Power:** 6000W max → ~5500W to batteries
  - Charging rate: ~110A @ 48V
  - 0-100% charge time: ~2.2 hours (10kWh battery)

**Automatic Transfer Switch (Built-In):**
- EcoFlow Power Hub automatically switches between shore power and battery
- Seamless transition (no interruption to AC loads)
- Prioritizes shore power when available (batteries stay full)
- Pass-through mode: Shore power directly feeds AC loads + charges batteries

---

## DC ELECTRICAL DISTRIBUTION (12V System)

### 12V DC Loads & Wiring

```
ECOFLOW POWER HUB (48V → 12V DC Converter)
         │
         │  50A max 12V output (600W)
         │
         ▼
┌────────────────────────────────────────────┐
│   SMART DISTRIBUTION PANEL (12V DC SIDE)   │
│                                            │
│  Circuit 1: LED Lighting (10A fuse)        │──→ All LED strips, puck lights
│  Circuit 2: Water Pump (10A fuse)          │──→ Shurflo pump, accumulator
│  Circuit 3: Fans (15A fuse)                │──→ MaxxAir fans (2×)
│  Circuit 4: Refrigerator (15A fuse)        │──→ 90L compressor fridge
│  Circuit 5: USB/12V Outlets (10A fuse)     │──→ USB-C PD, USB-A, 12V sockets
│  Circuit 6: Accessories (10A fuse)         │──→ Diesel heater, misc devices
│                                            │
└────────────────────────────────────────────┘
```

**12V DC Load Summary:**

| Load | Current (A) | Power (W) | Run Time (Hours) | Daily Use (Wh) |
|------|-------------|-----------|------------------|----------------|
| LED Lighting (all) | 3A | 36W | 4 hours | 144 Wh |
| Water Pump | 8A | 96W | 0.5 hours | 48 Wh |
| MaxxAir Fans (2×) | 6A | 72W | 6 hours | 432 Wh |
| Refrigerator (90L) | 5A | 60W | 24 hours (50% duty) | 720 Wh |
| USB Charging (4 devices) | 4A | 48W | 3 hours | 144 Wh |
| Diesel Heater | 1-3A | 12-36W | 4 hours | 100 Wh |
| **TOTAL DAILY 12V DC** | | | | **~1,588 Wh/day** |

**12V Wiring Specifications:**
- **Main 12V Bus:** 6 AWG from Power Hub to distribution panel
- **Circuit wiring:** 14 AWG (10A), 12 AWG (15A), 10 AWG (20A+)
- **Wire type:** Marine-grade tinned copper (corrosion-resistant)
- **Fusing:** Blade fuses (ATO/ATC) at distribution panel + inline fuses at devices
- **Polarity:** Red (positive), black (negative), yellow (switched positive)
- **Labeling:** All circuits labeled at panel and endpoints

---

## AC ELECTRICAL DISTRIBUTION (120V System)

### 120V AC Loads & Wiring

```
ECOFLOW POWER HUB (Inverter 5000W / 10,000W surge)
         │
         │  120V AC Output (5000W continuous)
         │
         ▼
┌────────────────────────────────────────────┐
│   BREAKER PANEL (120V AC SIDE)             │
│   (Standard household panel)               │
│                                            │
│  Main Breaker: 40A (Shore or Inverter)     │
│                                            │
│  Circuit 1: Kitchen Outlets (20A GFCI)     │──→ 3× outlets (induction, etc)
│  Circuit 2: Galley Appliances (15A)        │──→ Microwave/oven, countertop
│  Circuit 3: Wet Bath (15A GFCI)            │──→ Hot water heater, outlet
│  Circuit 4: Living Area (15A)              │──→ 2× outlets, misc devices
│  Circuit 5: SPARE (15A)                    │──→ Future AC unit or expansion
│                                            │
└────────────────────────────────────────────┘
```

**120V AC Load Summary:**

| Load | Power (W) | Surge (W) | Usage | Daily Use (Wh) |
|------|-----------|-----------|-------|----------------|
| Induction Cooktop | 1800W | 1800W | 1 hour | 1,800 Wh |
| Microwave/Oven Combo | 1500W | 1800W | 0.5 hours | 750 Wh |
| Hot Water Heater (electric element) | 750W | 900W | 2 hours | 1,500 Wh |
| Laptop Charging (2×) | 120W | 150W | 4 hours | 480 Wh |
| Misc Devices (phone, camera, etc) | 100W | 150W | 3 hours | 300 Wh |
| **TOTAL DAILY 120V AC** | | | | **~4,830 Wh/day** |

**Notes:**
- Induction and microwave NOT used simultaneously (exceed 5000W if both on high)
- Hot water heater runs on timer or manual control (primarily free heat from engine while driving)
- EcoFlow inverter handles 10,000W surge for 2 seconds (microwave startup, induction boost)

**120V AC Wiring Specifications:**
- **Main feed:** 6 AWG from Power Hub to breaker panel (40A capacity)
- **Circuit wiring:** 12 AWG (15A circuits), 10 AWG (20A circuits)
- **Wire type:** Romex NM-B or MC cable (building code compliant)
- **GFCI protection:** Required for kitchen and wet bath outlets
- **Outlet spacing:** Maximum 6 feet between outlets in galley
- **Breaker panel location:** Under bed access panel or in galley base cabinet

---

## MONITORING & CONTROL SYSTEM

### EcoFlow Smart Monitoring (App-Based)

```
    ┌─────────────────────────────────────┐
    │   ECOFLOW APP (iOS/Android)         │
    │                                     │
    │  ┌───────────────────────────────┐  │
    │  │ BATTERY STATUS                │  │
    │  │ - SOC: 87%                    │  │  Real-time monitoring
    │  │ - Voltage: 50.4V              │  │  from anywhere with
    │  │ - Current: -45A (discharging) │  │  WiFi or cellular
    │  │ - Time remaining: 4.2 hours   │  │
    │  └───────────────────────────────┘  │
    │                                     │
    │  ┌───────────────────────────────┐  │
    │  │ POWER FLOW                    │  │
    │  │ Solar: 350W                   │  │  Live power flow
    │  │ Alternator: 0W (engine off)   │  │  visualization
    │  │ Shore: 0W (unplugged)         │  │
    │  │ Loads: 2,150W                 │  │
    │  └───────────────────────────────┘  │
    │                                     │
    │  ┌───────────────────────────────┐  │
    │  │ CIRCUIT STATUS (12V DC)       │  │
    │  │ - Lighting: 2.8A              │  │  Per-circuit
    │  │ - Pump: 0A (off)              │  │  monitoring
    │  │ - Fans: 5.2A                  │  │
    │  │ - Fridge: 4.8A                │  │
    │  │ - USB: 1.2A                   │  │
    │  └───────────────────────────────┘  │
    │                                     │
    │  ┌───────────────────────────────┐  │
    │  │ ALERTS & NOTIFICATIONS        │  │
    │  │ - Low battery: 20%            │  │  Configurable
    │  │ - Overload warning            │  │  alerts
    │  │ - High temperature            │  │
    │  └───────────────────────────────┘  │
    └─────────────────────────────────────┘
```

**Monitoring Features:**
- Real-time state of charge (SOC) with ±3% accuracy
- Battery voltage, current, temperature per cell
- Solar production (live and historical)
- Alternator charging status
- Shore power status and input current
- AC inverter load and efficiency
- DC circuit-level monitoring (per circuit current draw)
- Time-to-empty / time-to-full estimates
- Historical data (daily, weekly, monthly energy usage)
- Remote on/off control for AC inverter

**Display Options:**
- **EcoFlow App:** iOS/Android smartphone app (primary interface)
- **Web Interface:** Browser-based dashboard (WiFi connection)
- **Optional Panel Mount Display:** 7" touchscreen (available separately)

**Connectivity:**
- WiFi (2.4GHz) for app connection and monitoring
- Bluetooth for local pairing and setup
- Optional cellular gateway for remote monitoring (off-grid)

---

## WIRING DIAGRAMS

### Main Power Flow Diagram

```
                         ┌─────────────────┐
                         │  SOLAR ARRAY    │
                         │  800W (2×400W)  │
                         └────────┬────────┘
                                  │ 10 AWG MC4 cables
                                  │ Positive + Negative
                                  ▼
                         ┌─────────────────┐
                         │ ROOF COMBINER   │
                         │ BOX (with 15A   │
                         │ fuses per panel)│
                         └────────┬────────┘
                                  │ 10 AWG to Power Hub
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        │ ALTERNATOR              │              SHORE      │
        │ 2/0 AWG                 │              10 AWG     │
        │ (from starter batt)     │              (from      │
        │                         │               inlet)    │
        │                         ▼                         │
        │              ┌──────────────────────┐             │
        │              │ ECOFLOW POWER HUB    │             │
        └─────────────→│                      │←────────────┘
                       │ - Solar MPPT (dual)  │
                       │ - Alt Charger Input  │
                       │ - Shore Charger      │
                       │ - Inverter (5kVA)    │
                       │ - 12V DC Converter   │
                       └──────────┬───────────┘
                                  │
                       ┌──────────┴───────────┐
                       │                      │
                  ┌────▼─────┐          ┌────▼─────┐
                  │ BATTERY  │          │ BATTERY  │
                  │ MODULE 1 │          │ MODULE 2 │
                  │ 5kWh LFP │          │ 5kWh LFP │
                  │ 48V/100Ah│          │ 48V/100Ah│
                  └──────────┘          └──────────┘
                       │                      │
                  Total: 10kWh (expandable to 15kWh)
                       │
        ┌──────────────┴──────────────┐
        │                             │
   ┌────▼─────┐                  ┌────▼─────┐
   │ 12V DC   │                  │ 120V AC  │
   │ DISTRIB. │                  │ BREAKER  │
   │ PANEL    │                  │ PANEL    │
   └────┬─────┘                  └────┬─────┘
        │                             │
   ┌────┴─────────────┐         ┌────┴──────────────┐
   │ - Lights         │         │ - Kitchen outlets │
   │ - Fans           │         │ - Microwave       │
   │ - Water pump     │         │ - Induction       │
   │ - Fridge         │         │ - Hot water       │
   │ - USB outlets    │         │ - Living outlets  │
   └──────────────────┘         └───────────────────┘
```

### Under-Bed Component Layout

```
UNDER-BED PLATFORM (looking from above, bed removed):

┌─────────────────────────────────────────────────────────┐
│                                                         │
│  PORT SIDE ACCESS                 STARBOARD SIDE ACCESS │
│                                                         │
│  ┌──────────────────┐         ┌──────────────────────┐ │
│  │  BATTERY MODULE  │         │  ECOFLOW POWER HUB   │ │
│  │  #1 (5kWh)       │         │  (Brain)             │ │
│  │  20×10×12"       │         │  14×10×6"            │ │
│  │  110 lbs         │         │  22 lbs              │ │
│  └──────────────────┘         │                      │ │
│                               │  - Inverter          │ │
│  ┌──────────────────┐         │  - Solar MPPTs       │ │
│  │  BATTERY MODULE  │         │  - Alt Charger       │ │
│  │  #2 (5kWh)       │         │  - BMS               │ │
│  │  20×10×12"       │         └──────────────────────┘ │
│  │  110 lbs         │                                  │
│  └──────────────────┘         ┌──────────────────────┐ │
│                               │ 12V DISTRIBUTION     │ │
│  ┌──────────────────┐         │ PANEL                │ │
│  │ FRESH WATER TANK │         │ (6 circuits)         │ │
│  │ 25 gallons       │         └──────────────────────┘ │
│  │ 20×36×12"        │                                  │
│  └──────────────────┘         ┌──────────────────────┐ │
│                               │ 120V BREAKER PANEL   │ │
│                               │ (5 circuits)         │ │
│  ┌──────────────────┐         └──────────────────────┘ │
│  │ GEAR STORAGE     │                                  │
│  │ (outdoor equip)  │         ┌──────────────────────┐ │
│  │                  │         │ HOT WATER HEATER     │ │
│  │ Bins, tools,     │         │ Isotemp 6-gallon     │ │
│  │ camping gear     │         │ Heat exchanger       │ │
│  └──────────────────┘         └──────────────────────┘ │
│                                                         │
│  REMOVABLE ACCESS PANELS (3× sections, 24×30" each)    │
└─────────────────────────────────────────────────────────┘

CABLE ROUTING:
- Solar cables: Roof → rear wall conduit → under bed
- Alternator cable: Firewall → under bed (port side routing)
- Shore power: Exterior inlet → under bed (through floor)
- 12V DC wiring: Distribution panel → wall channels → loads
- 120V AC wiring: Breaker panel → wall channels → outlets
```

---

## WIRE SIZING & SPECIFICATIONS

### DC Wiring (12V System)

| Circuit | Load (A) | Wire Gauge | Max Length (ft) | Voltage Drop |
|---------|----------|------------|-----------------|--------------|
| Main 12V Bus | 50A | 6 AWG | 15 ft | <0.5V |
| Lighting | 10A | 14 AWG | 30 ft | <0.3V |
| Water Pump | 10A | 12 AWG | 25 ft | <0.3V |
| Fans (2×) | 15A | 12 AWG | 20 ft | <0.3V |
| Refrigerator | 15A | 10 AWG | 20 ft | <0.3V |
| USB Outlets | 10A | 14 AWG | 25 ft | <0.3V |

**DC Wire Type:**
- Marine-grade tinned copper (all circuits)
- Stranded (flexible, vibration-resistant)
- Multi-color insulation (red, black, yellow for polarity/switching)
- Temperature rating: 105°C (221°F)

**Fusing:**
- Blade fuses (ATO/ATC) at distribution panel
- Inline ANL fuses for high-current (alternator: 300A)
- Fuse rating: 125% of circuit max current

### AC Wiring (120V System)

| Circuit | Load (A) | Wire Gauge | Breaker (A) |
|---------|----------|------------|-------------|
| Main Feed | 40A | 6 AWG | 40A |
| Kitchen Outlets (GFCI) | 20A | 10 AWG | 20A |
| Galley Appliances | 15A | 12 AWG | 15A |
| Wet Bath (GFCI) | 15A | 12 AWG | 15A |
| Living Area | 15A | 12 AWG | 15A |

**AC Wire Type:**
- Romex NM-B or MC cable (building code compliant)
- Copper (solid or stranded)
- Color code: Black (hot), white (neutral), green/bare (ground)
- Temperature rating: 90°C (194°F)

**GFCI Protection:**
- Required: Kitchen, wet bath, exterior outlets
- Trip current: 5mA (Class A)
- Test monthly for safety

### Solar Wiring

| Run | Voltage (V) | Current (A) | Wire Gauge | Length (ft) |
|-----|-------------|-------------|------------|-------------|
| Panel 1 to Combiner | 48V | 8.3A | 10 AWG | 6 ft |
| Panel 2 to Combiner | 48V | 8.3A | 10 AWG | 6 ft |
| Combiner to Power Hub | 48V | 16.6A | 10 AWG | 25 ft |

**Solar Cable Type:**
- MC4 connectors (weatherproof, UV-resistant)
- Photovoltaic (PV) rated wire
- Black (positive), white or red (negative stripe)
- Temperature rating: 90°C, sunlight resistant

### Alternator Wiring

| Run | Voltage (V) | Current (A) | Wire Gauge | Length (ft) |
|-----|-------------|-------------|------------|-------------|
| Starter Battery to Hub | 12-15V | 500A peak | 2/0 AWG | 15 ft |

**Alternator Cable Type:**
- Ultra-flexible welding cable (2/0 AWG)
- Tinned copper (marine-grade)
- Red (positive), black (negative)
- 300A ANL fuse at battery tap point

---

## SAFETY & PROTECTION

### Overcurrent Protection
- **Main breaker:** 40A at 120V AC panel (shore/inverter)
- **Solar fusing:** 15A per panel (roof combiner box)
- **Alternator fusing:** 300A ANL fuse (at battery tap)
- **12V circuits:** Blade fuses (5A to 20A per circuit)
- **Inverter overload:** Automatic shutdown at 5500W continuous

### GFCI & Arc Fault Protection
- **GFCI outlets:** Kitchen (20A), wet bath (15A)
- **AFCI breakers:** Not required (van application), but recommended for sleeping area outlets

### Battery Protection (Built-In BMS)
- Over-voltage cutoff: 58V (per 48V battery)
- Under-voltage cutoff: 40V (protects cells from damage)
- Over-current cutoff: 300A (prevents cable/connector damage)
- Over-temperature cutoff: 140°F (prevents thermal runaway)
- Cell balancing: Automatic (equalizes cells during charge)

### Grounding & Bonding
- **Chassis ground:** Negative battery terminal bonded to van chassis
- **AC ground:** 120V AC system grounded to chassis (via shore power or inverter)
- **Isolated neutral-ground:** EcoFlow inverter provides isolated neutral (safer)
- **Bonding:** All metal enclosures, appliances, panels bonded to chassis ground

---

## DAILY ENERGY BUDGET & USAGE SCENARIOS

### Scenario 1: Typical Daily Use (Off-Grid)

| Time | Activity | Power Draw | Energy Used |
|------|----------|------------|-------------|
| 6:00 AM | Wake up, lights, coffee (Instant Pot) | 1200W (AC) | 200 Wh |
| 7:00 AM | Shower (hot water pump, lights) | 150W (DC) | 50 Wh |
| 8:00 AM - 12:00 PM | Fridge, fans, laptop | 150W (mix) | 600 Wh |
| 12:00 PM | Lunch (induction cooking, 30 min) | 1800W (AC) | 900 Wh |
| 1:00 PM - 6:00 PM | Fridge, fans, USB charging | 120W (mix) | 600 Wh |
| 6:00 PM | Dinner (microwave, induction) | 2000W (AC) | 1000 Wh |
| 7:00 PM - 10:00 PM | Lights, laptop, fans, fridge | 180W (mix) | 540 Wh |
| 10:00 PM - 6:00 AM | Fridge, diesel heater, fans (low) | 80W (mix) | 640 Wh |
| **TOTAL DAILY USE** | | | **~4,530 Wh** |

**Energy Balance:**
- **Consumption:** 4,530 Wh/day (~45% of 10kWh battery)
- **Solar production (avg):** 3,200 Wh/day (4 hours × 800W)
- **Net battery drain:** 1,330 Wh/day (13% battery per day)
- **Days off-grid (no driving):** 7-8 days before recharge needed

### Scenario 2: Heavy Use Day (Cooking, Working, Heating)

| Load | Power | Duration | Energy Used |
|------|-------|----------|-------------|
| Morning cooking (induction) | 1800W | 1 hour | 1,800 Wh |
| Microwave/oven | 1500W | 0.5 hour | 750 Wh |
| Hot water heater (electric) | 750W | 2 hours | 1,500 Wh |
| Laptop + monitor | 150W | 8 hours | 1,200 Wh |
| Fridge (continuous) | 60W | 24 hours | 720 Wh |
| Fans | 72W | 10 hours | 720 Wh |
| Lighting | 36W | 6 hours | 216 Wh |
| Diesel heater | 30W | 8 hours | 240 Wh |
| **TOTAL HEAVY DAY** | | | **~7,146 Wh** |

**Energy Balance:**
- **Consumption:** 7,146 Wh/day (~71% of 10kWh battery)
- **Solar production (good day):** 4,000 Wh/day (5 hours × 800W)
- **Net battery drain:** 3,146 Wh/day (31% battery per day)
- **Days off-grid:** 3 days before recharge needed

### Scenario 3: Travel Day (Alternator Charging)

| Activity | Energy Used/Gained |
|----------|-------------------|
| Morning routine (before driving) | -500 Wh |
| Drive 4 hours @ highway speed | **+16,000 Wh** (4000W avg × 4 hrs) |
| Stop for lunch (cooking) | -1,000 Wh |
| Drive 3 hours | **+12,000 Wh** (4000W avg × 3 hrs) |
| Evening camp (cooking, lights) | -1,500 Wh |
| **NET DAILY BALANCE** | **+25,000 Wh** (battery fully charged, excess wasted) |

**Result:** Battery fully recharged in 2-3 hours of driving, stays at 100% all day

---

## SYSTEM INSTALLATION CHECKLIST

### Professional Installation Required
- [ ] Alternator charger tap into starter battery (300A fuse)
- [ ] Alternator cable routing through firewall (sealed entry)
- [ ] Shore power inlet installation (exterior wall penetration)
- [ ] Solar panel roof rack installation (roof structural integrity)
- [ ] Solar cable roof entry gland (waterproof seal)
- [ ] Grey water tank under-chassis installation
- [ ] Hot water heat exchanger engine coolant tap (under hood)
- [ ] Sofa bed seat belt anchorage installation (FMVSS certified)
- [ ] Final electrical inspection (if required by jurisdiction)

### DIY Installation (with electrical experience)
- [ ] EcoFlow Power Hub mounting (under bed platform)
- [ ] Battery module installation (secure mounting, ventilation)
- [ ] 12V DC distribution panel wiring
- [ ] 120V AC breaker panel wiring
- [ ] Solar combiner box and panel wiring (MC4 connections)
- [ ] LED lighting installation (strips, puck lights)
- [ ] Outlet and switch installation (12V and 120V)
- [ ] Appliance wiring (fridge, microwave, water pump)
- [ ] Wire routing and securing (prevent chafing)
- [ ] Labeling all circuits and breakers

### Testing & Commissioning
- [ ] Continuity testing (all circuits)
- [ ] Polarity testing (DC and AC)
- [ ] GFCI testing (trip test)
- [ ] Solar panel output testing (voltage, current)
- [ ] Alternator charging testing (while driving)
- [ ] Shore power testing (inlet to batteries)
- [ ] Inverter load testing (microwave, induction)
- [ ] Battery balancing verification (EcoFlow app)
- [ ] Monitoring system setup (WiFi pairing, app configuration)
- [ ] Safety equipment testing (smoke, CO detectors)

---

## FUTURE EXPANSION POSSIBILITIES

### Battery Expansion (10kWh → 15kWh)
- Add 1× additional 5kWh LFP battery module
- No other changes needed (Power Hub supports up to 45kWh)
- Installation: 1-2 hours (plug-and-play)
- Cost: ~$2,000

### Solar Expansion (800W → 1200W)
- Add 1× 400W panel (if roof space available after AC install)
- EcoFlow Power Hub supports up to 4800W solar input
- Installation: 2-3 hours (add to combiner box)
- Cost: ~$400 (panel) + $100 (wiring)

### Rooftop Air Conditioner
- EcoFlow Gen 2 can power 2× 13,500 BTU AC units (without soft starter)
- Recommended: Dometic RTX 2000 or Airxcel Penguin II (low profile)
- Roof space reserved (see floor plan roof layout)
- Installation: Professional required (roof cut, sealed mounting)
- Power requirement: 1,500W running, 3,000W starting (within 10kW surge)
- Cost: ~$1,500 (AC unit) + $500 (install)

### Diesel Heater Upgrade
- Current plan: Basic Chinese diesel heater (2-5kW)
- Upgrade option: Espar or Webasto (quieter, more reliable)
- Power requirement: 12V DC, 1-3A (same as current)
- Cost difference: +$1,000-1,500

### Smart Home Integration
- EcoFlow app already provides WiFi monitoring
- Add: Home Assistant integration (open-source smart home)
- Control lights, fans, heater via voice (Alexa, Google Home)
- Automation: Auto-dim lights at sunset, turn on heat at bedtime
- Cost: ~$100 (Raspberry Pi + integrations)

---

## COST ESTIMATE - ELECTRICAL SYSTEM ONLY

| Component | Model/Description | Qty | Unit Price | Total |
|-----------|-------------------|-----|------------|-------|
| **ECOFLOW POWER KIT GEN 2** | | | | |
| Power Hub (5kVA inverter) | EcoFlow Gen 2 Hub | 1 | $2,500 | $2,500 |
| LFP Battery Module (5kWh) | EcoFlow 5kWh LFP | 2 | $2,000 | $4,000 |
| Smart Distribution Panel | Included with Hub | 1 | Included | $0 |
| Alternator Charger Cable | EcoFlow Alt Cable | 1 | $800 | $800 |
| **ECOFLOW SUBTOTAL** | | | | **$7,300** |
| | | | | |
| **SOLAR SYSTEM** | | | | |
| Solar Panel (400W mono) | Renogy or equivalent | 2 | $350 | $700 |
| Roof Rack (walkable) | Aluminess custom | 1 | $1,200 | $1,200 |
| Solar Combiner Box | Weatherproof box + fuses | 1 | $80 | $80 |
| MC4 Solar Cables (10 AWG) | 50 ft total | 1 | $100 | $100 |
| Roof Entry Gland | Scanstrut cable seal | 1 | $40 | $40 |
| **SOLAR SUBTOTAL** | | | | **$2,120** |
| | | | | |
| **SHORE POWER** | | | | |
| Shore Power Inlet (30A) | Marinco stainless | 1 | $80 | $80 |
| Shore Power Cable (50 ft) | 30A RV cable | 1 | $120 | $120 |
| **SHORE POWER SUBTOTAL** | | | | **$200** |
| | | | | |
| **WIRING & DISTRIBUTION** | | | | |
| 120V AC Breaker Panel | 6-circuit panel | 1 | $60 | $60 |
| GFCI Outlets (20A) | Kitchen, wet bath | 3 | $25 | $75 |
| Standard AC Outlets (15A) | Living area | 4 | $8 | $32 |
| USB-C PD Outlets (dual) | Fast charging | 4 | $30 | $120 |
| 12V Cigarette Outlets | Accessories | 2 | $12 | $24 |
| Wire (DC 6-14 AWG mix) | 200 ft total | 1 | $150 | $150 |
| Wire (AC 6-12 AWG mix) | 150 ft total | 1 | $120 | $120 |
| Fuses & Breakers | Assorted | 1 | $80 | $80 |
| Wire Loom & Conduit | Protection | 1 | $60 | $60 |
| Connectors & Terminals | Assorted | 1 | $100 | $100 |
| **WIRING SUBTOTAL** | | | | **$821** |
| | | | | |
| **MONITORING & CONTROL** | | | | |
| EcoFlow App | Included with Hub | 1 | Included | $0 |
| Optional Touchscreen Display | 7" panel mount | 0 | $300 | $0 |
| **MONITORING SUBTOTAL** | | | | **$0** |
| | | | | |
| **PROFESSIONAL INSTALLATION** | | | | |
| Alternator tap + cable routing | Labor | 4 hrs | $100/hr | $400 |
| Solar panel roof rack install | Labor | 6 hrs | $100/hr | $600 |
| Shore power inlet install | Labor | 2 hrs | $100/hr | $200 |
| System commissioning & testing | Labor | 3 hrs | $100/hr | $300 |
| **LABOR SUBTOTAL** | | | | **$1,500** |
| | | | | |
| **TOTAL ELECTRICAL SYSTEM** | | | | **$11,941** |
| **Contingency (15%)** | | | | **$1,791** |
| **GRAND TOTAL** | | | | **$13,732** |

**Notes:**
- Prices current as of February 2026 (estimates, verify with suppliers)
- Does not include hot water system (see plumbing diagram)
- Does not include lighting (see BOM in separate document)
- Professional labor at $100/hr (varies by region: $75-150/hr)
- DIY installation can save ~$1,500 in labor (if experienced)

---

## MAINTENANCE & TROUBLESHOOTING

### Regular Maintenance Schedule

**Monthly:**
- [ ] Test GFCI outlets (press test button)
- [ ] Inspect solar panel surfaces (clean if dusty)
- [ ] Check battery SOC and balancing (via app)
- [ ] Inspect wire connections for corrosion (under bed access)
- [ ] Test smoke and CO detectors

**Quarterly:**
- [ ] Inspect solar panel mounting and roof rack (tighten bolts)
- [ ] Check alternator cable connections (under hood and cargo area)
- [ ] Inspect shore power inlet for damage or corrosion
- [ ] Clean solar combiner box (check for moisture or insects)
- [ ] Review EcoFlow app history for anomalies

**Annually:**
- [ ] Full electrical system inspection (professional recommended)
- [ ] Battery capacity test (full discharge/recharge cycle)
- [ ] Torque check all high-current connections (alternator, batteries)
- [ ] Replace sacrificial anode (if using for bonding)
- [ ] Update EcoFlow firmware (if available)

### Common Troubleshooting

**Issue: Batteries not charging from solar**
- Check solar panel surface (shading, dirt, snow)
- Verify solar cable connections (MC4 connectors tight)
- Check fuses in combiner box (15A per panel)
- Monitor solar input in EcoFlow app (should show voltage/current)
- Test panel voltage with multimeter (should be ~48V Voc per panel)

**Issue: Inverter shuts down under load**
- Verify load is under 5000W continuous (check app)
- Ensure battery SOC > 20% (inverter protects from over-discharge)
- Check battery temperature (may reduce output if hot > 113°F)
- Reduce simultaneous AC loads (don't run induction + microwave together)

**Issue: Alternator not charging**
- Verify engine is running (alternator only charges when driving)
- Check 300A fuse at battery tap point (may have blown)
- Inspect alternator cable for damage (look for melted insulation)
- Monitor alternator input in EcoFlow app (should show 1000-6000W while driving)

**Issue: Shore power not working**
- Check campground breaker (may have tripped)
- Inspect shore power cable for damage
- Verify shore power inlet connection (twist-lock fully engaged)
- Check AC breaker panel main breaker (40A)
- Test with multimeter (should show 120V AC at inlet)

**Issue: 12V DC loads not working**
- Check circuit fuses at distribution panel (may have blown)
- Verify Power Hub is on (check app or LED status)
- Test with multimeter (should show 12-13V DC at outlets)
- Inspect wire connections for loose terminals

---

## COMPLIANCE & STANDARDS

**Electrical Standards:**
- RVIA (Recreational Vehicle Industry Association) guidelines
- NFPA 1192 (National Fire Protection Association RV standard)
- NEC Article 551 (National Electrical Code for RVs)
- ABYC (American Boat & Yacht Council) for marine-grade wiring

**Safety Certifications:**
- EcoFlow Power Kit: UL 2849, UL 9540 (battery safety)
- Solar panels: IEC 61215, IEC 61730 (PV module safety)
- GFCI outlets: UL 943 (ground fault protection)

**Professional Certifications Recommended:**
- Alternator installation: ASE certified mechanic or RV technician
- Solar panel installation: NABCEP certified (North American Board of Certified Energy Practitioners)
- Final inspection: Licensed electrician (if required by jurisdiction)

---

**Document Version:** v3.0 Electrical System Diagram
**Created:** February 20, 2026 15:15
**Status:** Final - Ready for professional installation quotes
**Next Update:** Plumbing system diagram
