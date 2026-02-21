#!/usr/bin/env python3
"""
Ford Transit 148" ELWB High Roof – Interactive Layout Editor Generator
=======================================================================
Generates a self-contained HTML layout editor with:
  • Sidebar panel with per-item position/dimension sliders
  • Add / duplicate / delete custom items (overhead cabinets, shelves, etc.)
  • Real-time 3-D Plotly preview that updates on every slider change
  • Parametric Transit shell (superellipse roof + walls)
  • Export layout as JSON  /  Import previously saved layouts
  • "Generate Final Render" exports JSON for the STEP-shell script

Output:
  04-outputs/20260220-layout-editor.html

Usage:
  python generate_layout_editor_v1.py
"""

import os, json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR    = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "04-outputs"))
os.makedirs(OUT_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════
# Default layout items  (all values in inches)
# ═══════════════════════════════════════════════════════════════════════

CL, CW, CH = 172.2, 70.2, 81.5   # cargo interior

DEFAULT_ITEMS = [
    # Zone 1 – Sofa
    {"id":"sofa_base",    "name":"Z1 – Sofa Base",        "zone":"Zone 1 – Sofa Bed",
     "x":11.1, "y":0,  "z":0,  "dx":48, "dy":24, "dz":16,
     "color":"#7D5A14", "opacity":0.90},
    {"id":"sofa_cushion", "name":"Z1 – Seat Cushion",     "zone":"Zone 1 – Sofa Bed",
     "x":12.6, "y":1.5,"z":16, "dx":45, "dy":14.4,"dz":4,
     "color":"#C9A84C", "opacity":0.95},
    {"id":"sofa_back",    "name":"Z1 – Backrest",          "zone":"Zone 1 – Sofa Bed",
     "x":12.1, "y":19, "z":16, "dx":46, "dy":5,  "dz":18,
     "color":"#A07840", "opacity":0.95},

    # Zone 5 – Aisle / Table
    {"id":"lagun_table",  "name":"Z5 – Lagun Table",      "zone":"Zone 5 – Aisle",
     "x":28,  "y":40, "z":34, "dx":28, "dy":20, "dz":1.5,
     "color":"#8E44AD", "opacity":0.85},
    {"id":"table_ped",    "name":"Z5 – Table Pedestal",   "zone":"Zone 5 – Aisle",
     "x":40,  "y":48, "z":0,  "dx":4,  "dy":4,  "dz":34,
     "color":"#6C3483", "opacity":0.80},

    # Zone 3 – Wet Bath (port)
    {"id":"bath_cab",     "name":"Z3 – Bath Cabinet",     "zone":"Zone 3 – Wet Bath",
     "x":0,   "y":70, "z":0,  "dx":26, "dy":44, "dz":36,
     "color":"#1A5276", "opacity":0.65},
    {"id":"bath_counter", "name":"Z3 – Counter",          "zone":"Zone 3 – Wet Bath",
     "x":0,   "y":70, "z":36, "dx":26, "dy":44, "dz":2,
     "color":"#BDC3C7", "opacity":0.90},
    {"id":"toilet",       "name":"Z3 – Toilet",           "zone":"Zone 3 – Wet Bath",
     "x":5,   "y":96, "z":38, "dx":16, "dy":16, "dz":14,
     "color":"#D5D8DC", "opacity":0.90},

    # Zone 4 – Galley (starboard)
    {"id":"galley_cab",   "name":"Z4 – Galley Cabinet",   "zone":"Zone 4 – Galley",
     "x":48.2,"y":70, "z":0,  "dx":22, "dy":44, "dz":36,
     "color":"#6D3A0E", "opacity":0.65},
    {"id":"galley_ctr",   "name":"Z4 – Counter",          "zone":"Zone 4 – Galley",
     "x":48.2,"y":70, "z":36, "dx":22, "dy":44, "dz":2,
     "color":"#BDC3C7", "opacity":0.90},
    {"id":"fridge",       "name":"Z4 – Fridge 90 L",      "zone":"Zone 4 – Galley",
     "x":48.2,"y":70, "z":0,  "dx":24, "dy":20, "dz":23,
     "color":"#2E86C1", "opacity":0.88},
    {"id":"sink",         "name":"Z4 – Sink",             "zone":"Zone 4 – Galley",
     "x":72.2-22+24,"y":70,"z":29, "dx":15,"dy":13,"dz":7,
     "color":"#85C1E9", "opacity":0.85},

    # Zone 2 – Bed
    {"id":"bed_plat",     "name":"Z2 – Bed Platform",     "zone":"Zone 2 – Bed",
     "x":1,   "y":130,"z":0,  "dx":68.2,"dy":42.2,"dz":28,
     "color":"#1E6B3A", "opacity":0.60},
    {"id":"mattress",     "name":"Z2 – Mattress",         "zone":"Zone 2 – Bed",
     "x":5.1, "y":131.1,"z":28,"dx":60,"dy":40,"dz":10,
     "color":"#A9DFBF", "opacity":0.92},
    {"id":"water_tank",   "name":"Z2 – Water Tank 25 gal","zone":"Zone 2 – Bed",
     "x":2,   "y":131,"z":1,  "dx":26, "dy":20, "dz":26,
     "color":"#3498DB", "opacity":0.30},
    {"id":"ecoflow",      "name":"Z2 – EcoFlow 10 kWh",  "zone":"Zone 2 – Bed",
     "x":42.2,"y":131,"z":1,  "dx":26, "dy":20, "dz":26,
     "color":"#F39C12", "opacity":0.30},

    # Overhead cabinets (new – user requested)
    {"id":"upper_bath",   "name":"Z3 – Upper Bath Cabinet","zone":"Zone 3 – Wet Bath",
     "x":0,   "y":70, "z":54, "dx":26, "dy":44, "dz":14,
     "color":"#2E86C1", "opacity":0.35},
    {"id":"upper_galley", "name":"Z4 – Upper Galley Cabinet","zone":"Zone 4 – Galley",
     "x":48.2,"y":70, "z":54, "dx":22, "dy":44, "dz":18,
     "color":"#8B6248", "opacity":0.45},

    # Wheel wells (fixed – not moveable)
    {"id":"ww_port",      "name":"Wheel Well – Port",     "zone":"Structure",
     "x":0,   "y":60, "z":0,  "dx":7.7,"dy":58, "dz":13.5,
     "color":"#7f8c8d", "opacity":0.75, "locked":True},
    {"id":"ww_stbd",      "name":"Wheel Well – Stbd",     "zone":"Structure",
     "x":62.5,"y":60, "z":0,  "dx":7.7,"dy":58, "dz":13.5,
     "color":"#7f8c8d", "opacity":0.75, "locked":True},

    # Roof fans
    {"id":"fan1",         "name":"Roof Fan 1",            "zone":"Roof Fans",
     "x":28.1,"y":42, "z":78.5,"dx":14,"dy":14, "dz":3,
     "color":"#E59866", "opacity":0.85},
    {"id":"fan2",         "name":"Roof Fan 2",            "zone":"Roof Fans",
     "x":28.1,"y":85, "z":78.5,"dx":14,"dy":14, "dz":3,
     "color":"#E59866", "opacity":0.85},
]

# ═══════════════════════════════════════════════════════════════════════
# HTML TEMPLATE
# ═══════════════════════════════════════════════════════════════════════

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ford Transit Van Build – Layout Editor</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background:#0d1117;
         color:#c9d1d9; display:flex; height:100vh; overflow:hidden; }

  /* ── Sidebar ────────────────────────────────────────── */
  #sidebar { width:380px; min-width:340px; background:#161b22;
             border-right:1px solid #30363d; display:flex; flex-direction:column;
             overflow:hidden; }
  #sidebar-header { padding:12px 16px; background:#1c2129; border-bottom:1px solid #30363d; }
  #sidebar-header h2 { font-size:14px; color:#58a6ff; margin-bottom:4px; }
  #sidebar-header p { font-size:11px; color:#8b949e; }

  #toolbar { padding:8px 12px; background:#1c2129; border-bottom:1px solid #30363d;
             display:flex; gap:6px; flex-wrap:wrap; }
  #toolbar button { padding:5px 10px; font-size:11px; border:1px solid #30363d;
                    border-radius:4px; background:#21262d; color:#c9d1d9;
                    cursor:pointer; transition:all 0.15s; }
  #toolbar button:hover { background:#30363d; border-color:#58a6ff; }
  #toolbar button.primary { background:#238636; border-color:#2ea043; color:white; }
  #toolbar button.primary:hover { background:#2ea043; }
  #toolbar button.danger { border-color:#f85149; color:#f85149; }
  #toolbar button.danger:hover { background:#f85149; color:white; }

  #items-panel { flex:1; overflow-y:auto; padding:8px; }
  #items-panel::-webkit-scrollbar { width:6px; }
  #items-panel::-webkit-scrollbar-thumb { background:#30363d; border-radius:3px; }

  .item-card { background:#0d1117; border:1px solid #30363d; border-radius:6px;
               margin-bottom:8px; overflow:hidden; transition:border-color 0.15s; }
  .item-card.selected { border-color:#58a6ff; }
  .item-card.locked { opacity:0.6; }

  .item-header { display:flex; align-items:center; padding:8px 10px;
                 cursor:pointer; gap:8px; }
  .item-header:hover { background:#161b22; }
  .item-swatch { width:14px; height:14px; border-radius:3px; flex-shrink:0; }
  .item-name { font-size:12px; font-weight:500; flex:1; }
  .item-zone { font-size:10px; color:#8b949e; }
  .item-toggle { font-size:10px; color:#484f58; transition:transform 0.2s; }
  .item-toggle.open { transform:rotate(90deg); }

  .item-body { display:none; padding:8px 10px 10px; border-top:1px solid #21262d; }
  .item-body.open { display:block; }

  .prop-row { display:flex; align-items:center; gap:6px; margin-bottom:6px; }
  .prop-label { font-size:10px; color:#8b949e; width:18px; text-align:right;
                flex-shrink:0; font-weight:600; }
  .prop-slider { flex:1; accent-color:#58a6ff; height:16px; }
  .prop-value { font-size:11px; width:48px; background:#0d1117; color:#c9d1d9;
                border:1px solid #30363d; border-radius:3px; padding:2px 4px;
                text-align:center; font-family:monospace; }
  .prop-group-label { font-size:10px; color:#58a6ff; margin:8px 0 4px;
                      text-transform:uppercase; letter-spacing:0.5px; }

  .item-actions { display:flex; gap:4px; margin-top:8px; }
  .item-actions button { flex:1; padding:3px; font-size:10px; border-radius:3px;
                         border:1px solid #30363d; background:#21262d;
                         color:#8b949e; cursor:pointer; }
  .item-actions button:hover { color:#c9d1d9; border-color:#484f58; }
  .item-actions button.del:hover { color:#f85149; border-color:#f85149; }

  /* ── 3D Viewport ────────────────────────────────────── */
  #viewport { flex:1; position:relative; }
  #plotly-3d { width:100%; height:100%; }
  #status-bar { position:absolute; bottom:0; left:0; right:0; padding:6px 14px;
                background:rgba(13,17,23,0.85); border-top:1px solid #30363d;
                font-size:11px; color:#8b949e; display:flex; justify-content:space-between; }

  /* ── Modal ──────────────────────────────────────────── */
  .modal-bg { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6);
              z-index:100; align-items:center; justify-content:center; }
  .modal-bg.active { display:flex; }
  .modal { background:#161b22; border:1px solid #30363d; border-radius:8px;
           padding:20px; width:420px; max-width:90vw; }
  .modal h3 { color:#58a6ff; margin-bottom:12px; font-size:14px; }
  .modal label { display:block; font-size:12px; color:#8b949e; margin:8px 0 3px; }
  .modal input, .modal select { width:100%; padding:6px 8px; font-size:12px;
           background:#0d1117; border:1px solid #30363d; border-radius:4px;
           color:#c9d1d9; }
  .modal-actions { display:flex; gap:8px; margin-top:16px; justify-content:flex-end; }
  .modal-actions button { padding:6px 16px; font-size:12px; border-radius:4px;
                          border:1px solid #30363d; background:#21262d;
                          color:#c9d1d9; cursor:pointer; }
  .modal-actions button.primary { background:#238636; border-color:#2ea043; color:white; }
</style>
</head>
<body>

<!-- ═══ SIDEBAR ═══ -->
<div id="sidebar">
  <div id="sidebar-header">
    <h2>🚐 Ford Transit Layout Editor</h2>
    <p>148" ELWB High Roof – Drag sliders to reposition items</p>
  </div>
  <div id="toolbar">
    <button class="primary" onclick="addItem()">＋ Add Item</button>
    <button onclick="addPreset('overhead_cab')">＋ Overhead Cab</button>
    <button onclick="addPreset('shelf')">＋ Shelf</button>
    <button onclick="exportJSON()">💾 Export</button>
    <button onclick="importJSON()">📂 Import</button>
    <button onclick="resetLayout()">↺ Reset</button>
  </div>
  <div id="items-panel"></div>
</div>

<!-- ═══ VIEWPORT ═══ -->
<div id="viewport">
  <div id="plotly-3d"></div>
  <div id="status-bar">
    <span id="status-text">Ready – click items to edit, drag sliders to move</span>
    <span id="status-dims"></span>
  </div>
</div>

<!-- ═══ ADD ITEM MODAL ═══ -->
<div class="modal-bg" id="add-modal">
  <div class="modal">
    <h3>Add New Item</h3>
    <label>Name</label>
    <input id="new-name" value="Custom Cabinet" />
    <label>Zone / Group</label>
    <select id="new-zone">
      <option>Zone 1 – Sofa Bed</option>
      <option>Zone 2 – Bed</option>
      <option>Zone 3 – Wet Bath</option>
      <option>Zone 4 – Galley</option>
      <option>Zone 5 – Aisle</option>
      <option selected>Overhead Storage</option>
      <option>Custom</option>
    </select>
    <div style="display:flex; gap:8px;">
      <div><label>Width</label><input id="new-dx" type="number" value="24" /></div>
      <div><label>Depth</label><input id="new-dy" type="number" value="18" /></div>
      <div><label>Height</label><input id="new-dz" type="number" value="14" /></div>
    </div>
    <label>Color</label>
    <input id="new-color" type="color" value="#6B8FA3" />
    <div class="modal-actions">
      <button onclick="closeModal()">Cancel</button>
      <button class="primary" onclick="confirmAdd()">Add to Layout</button>
    </div>
  </div>
</div>

<!-- ═══ IMPORT MODAL ═══ -->
<div class="modal-bg" id="import-modal">
  <div class="modal">
    <h3>Import Layout JSON</h3>
    <label>Paste JSON or select file</label>
    <textarea id="import-text" rows="8" style="width:100%;background:#0d1117;color:#c9d1d9;
              border:1px solid #30363d;border-radius:4px;padding:6px;font-family:monospace;
              font-size:11px;resize:vertical;"></textarea>
    <input type="file" id="import-file" accept=".json" style="margin-top:8px;font-size:11px;"
           onchange="loadFile(event)" />
    <div class="modal-actions">
      <button onclick="closeImportModal()">Cancel</button>
      <button class="primary" onclick="confirmImport()">Import</button>
    </div>
  </div>
</div>

<script>
// ═══════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════
const CL=172.2, CW=70.2, CH=81.5;

// ═══════════════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════════════
let items = %%ITEMS_JSON%%;
let nextId = 100;
let selectedId = null;
let updateTimer = null;

// ═══════════════════════════════════════════════════════════════════
// SHELL GEOMETRY (parametric – lightweight for interactive editor)
// ═══════════════════════════════════════════════════════════════════

function makeBox(x,y,z,dx,dy,dz) {
  return {
    x:[x,x+dx,x+dx,x,   x,   x+dx,x+dx,x],
    y:[y,y,   y+dy,y+dy,y,   y,   y+dy,y+dy],
    z:[z,z,   z,   z,   z+dz,z+dz,z+dz,z+dz],
    i:[0,0,4,4,0,0,1,1,0,0,2,2],
    j:[1,2,5,6,1,4,2,5,3,4,3,6],
    k:[2,3,6,7,4,5,5,6,4,7,6,7]
  };
}

function makeRoof() {
  const nL=40, nP=48;
  const halfW=CW/2+4, wallH=58, peakH=CH+6, archH=peakH-wallH, nExp=3.5;
  const xs=[], ys=[], zs=[], ii=[], jj=[], kk=[];
  for(let yi=0;yi<nL;yi++){
    const yy=-5+(CL+10)*yi/(nL-1);
    for(let pi=0;pi<nP;pi++){
      const t=Math.PI-Math.PI*pi/(nP-1);
      const ct=Math.cos(t), st=Math.sin(t);
      const px=halfW*Math.sign(ct)*Math.pow(Math.abs(ct),2/nExp);
      const pz=wallH+archH*Math.pow(Math.abs(st),2/nExp);
      xs.push(CW/2+px); ys.push(yy); zs.push(pz);
    }
  }
  for(let yi=0;yi<nL-1;yi++){
    for(let pi=0;pi<nP-1;pi++){
      const v00=yi*nP+pi, v10=(yi+1)*nP+pi, v01=yi*nP+pi+1, v11=(yi+1)*nP+pi+1;
      ii.push(v00,v01); jj.push(v10,v10); kk.push(v01,v11);
    }
  }
  return {x:xs,y:ys,z:zs,i:ii,j:jj,k:kk};
}

function shellTraces() {
  const roof = makeRoof();
  const traces = [];

  // Floor
  const fl = makeBox(-3,-3,-2,CW+6,CL+6,2);
  traces.push({type:'mesh3d',x:fl.x,y:fl.y,z:fl.z,i:fl.i,j:fl.j,k:fl.k,
    color:'#b8a88a',opacity:0.35,name:'Floor',legendgroup:'Shell',
    showlegend:true,hoverinfo:'skip',flatshading:true});

  // Walls (port, stbd, rear, front partition)
  for(const [nm,bx] of [
    ['Wall–Port',  makeBox(-3,-3,0, 3,CL+6,CH)],
    ['Wall–Stbd',  makeBox(CW,-3,0, 3,CL+6,CH)],
    ['Wall–Rear',  makeBox(-3,CL,0, CW+6,3,CH)],
    ['Partition',   makeBox(-3,-3,0, CW+6,3,CH)],
  ]){
    traces.push({type:'mesh3d',x:bx.x,y:bx.y,z:bx.z,i:bx.i,j:bx.j,k:bx.k,
      color:'#667788',opacity:0.06,name:nm,legendgroup:'Shell',
      showlegend:false,hoverinfo:'skip',flatshading:true});
  }

  // Roof
  traces.push({type:'mesh3d',x:roof.x,y:roof.y,z:roof.z,i:roof.i,j:roof.j,k:roof.k,
    color:'#8899aa',opacity:0.08,name:'Roof',legendgroup:'Shell',
    showlegend:true,hoverinfo:'skip',flatshading:true,
    lighting:{ambient:0.7,diffuse:0.5,specular:0.1,roughness:0.8}});

  // Windows (translucent)
  for(const [wy0,wy1] of [[30,68],[72,112],[133,170]]){
    const wp=makeBox(-1,wy0,36,1,wy1-wy0,22);
    const ws=makeBox(CW,wy0,36,1,wy1-wy0,22);
    traces.push({type:'mesh3d',x:wp.x,y:wp.y,z:wp.z,i:wp.i,j:wp.j,k:wp.k,
      color:'#5DADE2',opacity:0.18,name:'Window',legendgroup:'Shell',
      showlegend:false,hoverinfo:'skip',flatshading:true});
    traces.push({type:'mesh3d',x:ws.x,y:ws.y,z:ws.z,i:ws.i,j:ws.j,k:ws.k,
      color:'#5DADE2',opacity:0.18,name:'Window',legendgroup:'Shell',
      showlegend:false,hoverinfo:'skip',flatshading:true});
  }

  return traces;
}

// ═══════════════════════════════════════════════════════════════════
// ITEM TRACES
// ═══════════════════════════════════════════════════════════════════

function itemTraces() {
  const traces = [];
  for (const it of items) {
    const b = makeBox(it.x, it.y, it.z, it.dx, it.dy, it.dz);
    const sel = (it.id === selectedId);
    traces.push({
      type:'mesh3d', x:b.x, y:b.y, z:b.z, i:b.i, j:b.j, k:b.k,
      color: sel ? '#58a6ff' : it.color,
      opacity: sel ? Math.min(it.opacity+0.15, 1.0) : it.opacity,
      name: it.name,
      legendgroup: it.zone || it.name,
      showlegend: true,
      hovertext: `${it.name}<br>${it.dx.toFixed(1)}W × ${it.dy.toFixed(1)}D × ${it.dz.toFixed(1)}H`,
      hoverinfo:'text',
      flatshading:true,
      lighting:{ambient:0.55,diffuse:0.65,specular:0.25,roughness:0.6,fresnel:0.15},
      lightposition:{x:200,y:-100,z:300},
    });

    // wireframe edges for selected item
    if (sel) {
      const {x:bx,y:by,z:bz} = b;
      const ex=[], ey=[], ez=[];
      const edges=[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],
                   [0,4],[1,5],[2,6],[3,7]];
      for(const [a,c] of edges){
        ex.push(bx[a],bx[c],null); ey.push(by[a],by[c],null); ez.push(bz[a],bz[c],null);
      }
      traces.push({type:'scatter3d',x:ex,y:ey,z:ez,mode:'lines',
        line:{color:'#58a6ff',width:3},showlegend:false,hoverinfo:'skip'});
    }
  }
  return traces;
}

function annotationTraces() {
  const t = [];
  // Front arrow
  t.push({type:'scatter3d',x:[CW/2,CW/2],y:[-5,-20],z:[0,0],
    mode:'lines+text',text:['','◄── FRONT'],textposition:'bottom center',
    textfont:{size:11,color:'#E74C3C',family:'Arial Black'},
    line:{color:'#E74C3C',width:4},showlegend:false,hoverinfo:'skip'});
  // Dimension lines
  for(const [x0,y0,z0,x1,y1,z1,txt] of [
    [0,-8,0,CW,-8,0,'◄─ 70.2" ─►'],
    [-8,0,0,-8,CL,0,'172.2"'],
    [CW+8,0,0,CW+8,0,CH,'81.5"']
  ]){
    t.push({type:'scatter3d',x:[x0,x1],y:[y0,y1],z:[z0,z1],mode:'lines+markers',
      line:{color:'#aaa',width:2,dash:'dot'},marker:{size:3,color:'#aaa',symbol:'diamond'},
      showlegend:false,hoverinfo:'skip'});
    t.push({type:'scatter3d',x:[(x0+x1)/2],y:[(y0+y1)/2],z:[(z0+z1)/2+3],
      mode:'text',text:[txt],textfont:{size:9,color:'#aaa'},
      showlegend:false,hoverinfo:'skip'});
  }
  return t;
}

// ═══════════════════════════════════════════════════════════════════
// PLOTLY RENDER
// ═══════════════════════════════════════════════════════════════════

const LAYOUT = {
  scene:{
    xaxis:{title:'Width (port→stbd) [in]', range:[-30,CW+30],
           backgroundcolor:'#1a1a2e',gridcolor:'#2a2a4a',showbackground:true,color:'#8888aa'},
    yaxis:{title:'Length (front→rear) [in]', range:[-30,CL+20],
           backgroundcolor:'#16213e',gridcolor:'#2a2a4a',showbackground:true,color:'#8888aa'},
    zaxis:{title:'Height [in]', range:[-5,CH+25],
           backgroundcolor:'#0f3460',gridcolor:'#2a2a4a',showbackground:true,color:'#8888aa'},
    aspectmode:'data',
    camera:{eye:{x:1.6,y:-1.4,z:0.9}, up:{x:0,y:0,z:1}},
  },
  paper_bgcolor:'#0d1117', plot_bgcolor:'#0d1117',
  legend:{font:{color:'white',size:10},bgcolor:'rgba(20,20,40,0.7)',
          bordercolor:'#444466',borderwidth:1,itemsizing:'constant',groupclick:'toggleitem'},
  margin:{l:0,r:0,t:10,b:0},
  uirevision:'keep',  // preserve camera on re-render
};

const cachedShell = shellTraces();
const cachedAnnot = annotationTraces();

function render() {
  const traces = [...cachedShell, ...itemTraces(), ...cachedAnnot];
  Plotly.react('plotly-3d', traces, LAYOUT, {displayModeBar:true,
    modeBarButtonsToAdd:['orbitRotation','resetCameraDefault3d']});
  updateStatus();
}

function scheduleRender() {
  if(updateTimer) clearTimeout(updateTimer);
  updateTimer = setTimeout(render, 30);
}

// ═══════════════════════════════════════════════════════════════════
// SIDEBAR  – build item cards
// ═══════════════════════════════════════════════════════════════════

function buildSidebar() {
  const panel = document.getElementById('items-panel');
  panel.innerHTML = '';
  for (const it of items) {
    const locked = it.locked || false;
    const card = document.createElement('div');
    card.className = 'item-card' + (it.id===selectedId?' selected':'') + (locked?' locked':'');
    card.id = 'card-'+it.id;

    // Header
    const hdr = document.createElement('div');
    hdr.className = 'item-header';
    hdr.innerHTML = `
      <span class="item-swatch" style="background:${it.color}"></span>
      <span class="item-name">${it.name}</span>
      <span class="item-zone">${it.zone||''}</span>
      <span class="item-toggle" id="tog-${it.id}">▶</span>`;
    hdr.onclick = () => toggleCard(it.id);
    card.appendChild(hdr);

    // Body
    const body = document.createElement('div');
    body.className = 'item-body';
    body.id = 'body-'+it.id;
    if (!locked) {
      body.innerHTML = `
        <div class="prop-group-label">Position</div>
        ${slider(it,'x','X',  -10, CW+10)}
        ${slider(it,'y','Y',  -10, CL+10)}
        ${slider(it,'z','Z',  -5,  CH+10)}
        <div class="prop-group-label">Dimensions</div>
        ${slider(it,'dx','W', 1, 72)}
        ${slider(it,'dy','D', 1, 100)}
        ${slider(it,'dz','H', 1, CH)}
        <div class="prop-group-label">Appearance</div>
        <div class="prop-row">
          <span class="prop-label">🎨</span>
          <input type="color" value="${it.color}" style="flex:1;height:24px;background:none;border:none;cursor:pointer;"
                 onchange="setProp('${it.id}','color',this.value)" />
          <span class="prop-label" style="width:auto">α</span>
          <input type="range" class="prop-slider" min="0.05" max="1" step="0.05"
                 value="${it.opacity}" style="flex:1"
                 oninput="setProp('${it.id}','opacity',parseFloat(this.value))" />
        </div>
        <div class="item-actions">
          <button onclick="duplicateItem('${it.id}')">⧉ Duplicate</button>
          <button class="del" onclick="deleteItem('${it.id}')">✕ Delete</button>
        </div>`;
    } else {
      body.innerHTML = '<div style="font-size:11px;color:#484f58;padding:4px;">Locked – structural element</div>';
    }
    card.appendChild(body);
    panel.appendChild(card);
  }
}

function slider(it, prop, label, min, max) {
  const v = it[prop];
  const step = (prop==='opacity') ? 0.05 : 0.1;
  return `<div class="prop-row">
    <span class="prop-label">${label}</span>
    <input type="range" class="prop-slider" min="${min}" max="${max}" step="${step}"
           value="${v}" id="sl-${it.id}-${prop}"
           oninput="onSlider('${it.id}','${prop}',this.value)" />
    <input type="text" class="prop-value" value="${v.toFixed(1)}" id="vl-${it.id}-${prop}"
           onchange="onValue('${it.id}','${prop}',this.value)" />
  </div>`;
}

function toggleCard(id) {
  selectedId = (selectedId===id) ? null : id;
  // toggle body open/close
  for(const it of items){
    const b = document.getElementById('body-'+it.id);
    const t = document.getElementById('tog-'+it.id);
    const c = document.getElementById('card-'+it.id);
    if(it.id===selectedId){ b.classList.add('open'); t.classList.add('open'); c.classList.add('selected'); }
    else { b.classList.remove('open'); t.classList.remove('open'); c.classList.remove('selected'); }
  }
  scheduleRender();
}

// ═══════════════════════════════════════════════════════════════════
// PROPERTY EDITING
// ═══════════════════════════════════════════════════════════════════

function findItem(id) { return items.find(i=>i.id===id); }

function onSlider(id, prop, val) {
  const it = findItem(id);
  if(!it) return;
  const v = parseFloat(val);
  it[prop] = v;
  const vEl = document.getElementById('vl-'+id+'-'+prop);
  if(vEl) vEl.value = v.toFixed(1);
  scheduleRender();
}

function onValue(id, prop, val) {
  const it = findItem(id);
  if(!it) return;
  const v = parseFloat(val);
  if(isNaN(v)) return;
  it[prop] = v;
  const sEl = document.getElementById('sl-'+id+'-'+prop);
  if(sEl) sEl.value = v;
  scheduleRender();
}

function setProp(id, prop, val) {
  const it = findItem(id);
  if(!it) return;
  it[prop] = val;
  scheduleRender();
}

// ═══════════════════════════════════════════════════════════════════
// ADD / DUPLICATE / DELETE
// ═══════════════════════════════════════════════════════════════════

function addItem() { document.getElementById('add-modal').classList.add('active'); }
function closeModal() { document.getElementById('add-modal').classList.remove('active'); }

function confirmAdd() {
  const nm = document.getElementById('new-name').value || 'Custom Item';
  const zone = document.getElementById('new-zone').value;
  const dx = parseFloat(document.getElementById('new-dx').value) || 24;
  const dy = parseFloat(document.getElementById('new-dy').value) || 18;
  const dz = parseFloat(document.getElementById('new-dz').value) || 14;
  const color = document.getElementById('new-color').value;
  const id = 'custom_'+(nextId++);

  items.push({id, name:nm, zone, x:CW/2-dx/2, y:CL/2-dy/2, z:CH-dz-5,
              dx, dy, dz, color, opacity:0.7});
  closeModal();
  buildSidebar();
  selectedId = id;
  toggleCard(id);
}

const PRESETS = {
  overhead_cab: {name:'Overhead Cabinet', zone:'Overhead Storage',
                 dx:24, dy:30, dz:12, color:'#6B8FA3', opacity:0.55,
                 z:60, x:0, y:70},
  shelf:        {name:'Open Shelf', zone:'Overhead Storage',
                 dx:28, dy:20, dz:1.5, color:'#8B7355', opacity:0.80,
                 z:55, x:CW/2-14, y:50},
};

function addPreset(key) {
  const p = PRESETS[key];
  const id = key+'_'+(nextId++);
  items.push({...p, id});
  buildSidebar();
  selectedId = id;
  toggleCard(id);
}

function duplicateItem(id) {
  const src = findItem(id);
  if(!src) return;
  const nid = 'dup_'+(nextId++);
  items.push({...src, id:nid, name:src.name+' (copy)', x:src.x+2, y:src.y+2});
  buildSidebar();
  selectedId = nid;
  toggleCard(nid);
}

function deleteItem(id) {
  items = items.filter(i=>i.id!==id);
  if(selectedId===id) selectedId=null;
  buildSidebar();
  scheduleRender();
}

// ═══════════════════════════════════════════════════════════════════
// IMPORT / EXPORT
// ═══════════════════════════════════════════════════════════════════

function exportJSON() {
  const data = {
    version: 1,
    cargo: {length:CL, width:CW, height:CH},
    items: items.map(i => ({...i})),
    exported: new Date().toISOString(),
  };
  const blob = new Blob([JSON.stringify(data,null,2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'van-layout-' + new Date().toISOString().slice(0,10) + '.json';
  a.click();
  document.getElementById('status-text').textContent = '✅ Layout exported!';
}

function importJSON() { document.getElementById('import-modal').classList.add('active'); }
function closeImportModal() { document.getElementById('import-modal').classList.remove('active'); }

function loadFile(e) {
  const f = e.target.files[0];
  if(!f) return;
  const r = new FileReader();
  r.onload = () => { document.getElementById('import-text').value = r.result; };
  r.readAsText(f);
}

function confirmImport() {
  try {
    const data = JSON.parse(document.getElementById('import-text').value);
    if(data.items) { items = data.items; }
    else if(Array.isArray(data)) { items = data; }
    // Recompute nextId from imported items to avoid ID collisions
    let maxId = 100;
    items.forEach(item => {
      const match = item.id.match(/_(\\d+)$/);
      if(match) maxId = Math.max(maxId, parseInt(match[1]));
    });
    nextId = maxId + 1;
    buildSidebar();
    scheduleRender();
    closeImportModal();
    document.getElementById('status-text').textContent = '✅ Layout imported!';
  } catch(e) {
    alert('Invalid JSON: '+e.message);
  }
}

function resetLayout() {
  if(!confirm('Reset to default layout?')) return;
  items = JSON.parse(JSON.stringify(%%ITEMS_JSON%%));
  selectedId = null;
  nextId = 100;  // Reset nextId to initial value
  buildSidebar();
  scheduleRender();
}

// ═══════════════════════════════════════════════════════════════════
// STATUS
// ═══════════════════════════════════════════════════════════════════

function updateStatus() {
  const n = items.length;
  document.getElementById('status-dims').textContent =
    `${n} items · Cargo: ${CL}L × ${CW}W × ${CH}H inches`;
}

// ═══════════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════════

buildSidebar();
render();
</script>
</body>
</html>"""


def main():
    print("=" * 60)
    print(" Ford Transit Van Build – Layout Editor Generator")
    print("=" * 60)

    items_json = json.dumps(DEFAULT_ITEMS)
    html = HTML_TEMPLATE.replace("%%ITEMS_JSON%%", items_json)

    out_path = os.path.join(OUT_DIR, "20260220-layout-editor.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) // 1024
    print(f"\n✅  Layout Editor: {out_path}  ({size_kb} KB)")
    print("\n🖱️  Open in your browser to start editing the layout.")
    print("    • Click an item in the sidebar to select it")
    print("    • Drag sliders to reposition & resize")
    print("    • Use ＋ buttons to add overhead cabinets, shelves, etc.")
    print("    • 💾 Export saves your layout as JSON")
    print("    • 📂 Import loads a previously saved layout")
    print("    • The 3-D view preserves camera angle while editing")


if __name__ == "__main__":
    main()
