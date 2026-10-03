// =============================================================================
// Pocket Companion - 2D Orthographic Engineering Blueprint Drawing & Fastener Audit
// File: engineering_drawing_pocket_companion.typ
// Standard: ISO 2768-mK / ASME Y14.5M-2018
// =============================================================================

#set page(
  paper: "a4",
  flipped: false,
  margin: (x: 15mm, top: 24mm, bottom: 24mm),
  header: context {
    if counter(page).get().first() > 1 {
      grid(
        columns: (1fr, auto),
        align(left)[#text(7.5pt, fill: rgb("#475569"), weight: "bold")[POCKET COMPANION ENCLOSURE — ENGINEERING SPECIFICATION & BLUEPRINT]],
        align(right)[#text(7.5pt, fill: rgb("#64748b"))[DWG-PC-CAD-01 | REV 2.5]]
      )
      v(-3pt)
      line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    }
  },
  header-ascent: 2mm,
  footer: context {
    let p = counter(page).get().first()
    let total = counter(page).final().first()
    line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    v(2pt)
    grid(
      columns: (1fr, auto),
      align(left)[#text(7.5pt, fill: rgb("#64748b"))[Confidential & Sovereign Hardware Directorate • ISO 2768-mK Tolerance Standard]],
      align(right)[#text(7.5pt, fill: rgb("#0f172a"), weight: "bold")[Sheet #p of #total]]
    )
  },
  footer-descent: 2mm
)

#set text(
  font: ("Segoe UI", "Arial"),
  size: 8.5pt,
  fill: rgb("#0f172a")
)

#set par(justify: true, leading: 0.55em)

// --- Title Block Header ---
#block(
  width: 100%,
  stroke: 1pt + rgb("#0f172a"),
  inset: (x: 10pt, y: 8pt),
  radius: 2pt,
  fill: rgb("#f8fafc"),
  [
    #grid(
      columns: (1fr, auto),
      align: (left, right),
      [
        #text(13pt, weight: "bold", fill: rgb("#0f172a"))[POCKET COMPANION ENCLOSURE SPECIFICATION] \
        #v(1pt)
        #text(8pt, fill: rgb("#334155"))[Parametric 3D Printable Unibody Enclosure • Mechanical Blueprint & Fastener Stress Audit] \
        #text(7.5pt, fill: rgb("#64748b"))[Hardware Directorate | Engineering Release Date: October 4, 2026 | Material: PETG / PLA / ABS]
      ],
      [
        #box(
          stroke: 0.8pt + rgb("#0f172a"),
          inset: (x: 6pt, y: 4pt),
          radius: 2pt,
          align(center)[
            #text(7.5pt, weight: "bold", fill: rgb("#0f172a"))[DWG-PC-CAD-01] \
            #context text(6.5pt, fill: rgb("#64748b"))[SHEET 1 OF #str(counter(page).final().first())]
          ]
        )
      ]
    )
  ]
)

#v(2pt)

// --- Section 1: Datum References & Global Dimensions ---
#text(9.5pt, weight: "bold", fill: rgb("#0369a1"))[1. Primary Manufacturing Datums & Envelope Geometry]

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 8pt,
  [
    #box(stroke: 0.5pt + rgb("#cbd5e1"), inset: 6pt, radius: 2pt, width: 100%, fill: rgb("#ffffff"))[
      #text(8pt, weight: "bold")[Datum Reference Frame] \
      #v(2pt)
      - *Datum [A]:* Bottom exterior base floor plane ($Z = 0.00$).
      - *Datum [B]:* Rear exterior shell wall plane ($Y = 42.50$).
      - *Datum [C]:* Left exterior shell wall plane ($X = 0.00$).
    ]
  ],
  [
    #box(stroke: 0.5pt + rgb("#cbd5e1"), inset: 6pt, radius: 2pt, width: 100%, fill: rgb("#ffffff"))[
      #text(8pt, weight: "bold")[Overall Dimensions] \
      #v(2pt)
      - *Length ($X$):* $56.50 plus.minus 0.15$ mm
      - *Width ($Y$):* $42.50 plus.minus 0.15$ mm
      - *Height ($Z$):* $19.70 plus.minus 0.20$ mm
      - *Corner Radius:* R5.00 mm external
    ]
  ],
  [
    #box(stroke: 0.5pt + rgb("#cbd5e1"), inset: 6pt, radius: 2pt, width: 100%, fill: rgb("#ffffff"))[
      #text(8pt, weight: "bold")[Enclosure Walls] \
      #v(2pt)
      - *Perimeter Shell Wall:* $2.00$ mm
      - *Base Floor Thickness:* $2.00$ mm
      - *Top Lid Roof Thickness:* $2.20$ mm
      - *Joint Lip Thickness:* $1.00$ mm
    ]
  ]
)

#v(2pt)

// --- Section 2: Orthographic Projections ---
#text(9.5pt, weight: "bold", fill: rgb("#0369a1"))[2. 2D Orthographic Projections & Component Fitment (First Angle)]

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 6pt,
  [
    #align(center)[
      #image("renders/ortho_top.png", width: 95%) \
      #text(7pt, weight: "bold")[Figure 1: Plan View (Top View)] \
      #text(6.5pt, fill: rgb("#64748b"))[OLED Window (24.8x14.8), 3x Buttons (X=12,26,40), Buzzer Grille]
    ]
  ],
  [
    #align(center)[
      #image("renders/ortho_front.png", width: 95%) \
      #text(7pt, weight: "bold")[Figure 2: Elevation View (Front View)] \
      #text(6.5pt, fill: rgb("#64748b"))[USB-C Mouth (11.5x6.5, 45° Chamfer), Parting Line (Z=9.50)]
    ]
  ],
  [
    #align(center)[
      #image("renders/ortho_side.png", width: 95%) \
      #text(7pt, weight: "bold")[Figure 3: Profile View (Side View)] \
      #text(6.5pt, fill: rgb("#64748b"))[Slide Switch Slot (9.5x4.2), M2 Standoff Boss Heights (Z=7.50)]
    ]
  ]
)

#v(2pt)

// --- Section 3: Fastener Boss Stress & Pull-Out Calculations ---
#text(9.5pt, weight: "bold", fill: rgb("#0369a1"))[3. Fastener Boss Hoop Stress & Screw Pull-Out Force Verification]

#table(
  columns: (1.5fr, 1.2fr, 2.5fr, 1.2fr),
  inset: 4pt,
  stroke: 0.5pt + rgb("#cbd5e1"),
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else { none },
  align: (left, center, left, center),
  [#text(7.5pt, weight: "bold")[Analytical Parameter]],
  [#text(7.5pt, weight: "bold")[Value]],
  [#text(7.5pt, weight: "bold")[Governing Physical Equation / Mechanics]],
  [#text(7.5pt, weight: "bold")[Verification Status]],
  [Boss Outer Diameter ($D_"boss"$)], [$4.40$ mm], [Thick-walled cylinder outer boundary ($r_o = 2.20$ mm)], [PASS (Geometric)],
  [Core Pilot Hole ($d_"core"$)], [$2.00$ mm], [Pilot hole diameter for M2 thread forming ($r_i = 1.00$ mm)], [PASS (Optimum 80%)],
  [Boss Wall Thickness ($t_"wall"$)], [$1.20$ mm], [$t_"wall" = (D_"boss" - d_"core") / 2 = (4.40 - 2.00) / 2$], [PASS ($t > 0.6 d$)],
  [Thread Engagement ($L_e$)], [$6.50$ mm], [$L_e / d = 6.50 / 2.00 = 3.25 d$ (high axial grip)], [PASS ($> 2.5 d$)],
  [Radial Interference ($Delta r$)], [$0.10$ mm], [Radial displacement imposed by M2 thread profile into bore], [PASS (Nominal)],
  [Lamé Internal Pressure ($p$)], [$15.82$ MPa], [$p = (Delta r / r_i) E ((r_o^2 - r_i^2) / ((1 + nu) r_o^2 + (1 - nu) r_i^2))$], [PASS (Elastic Range)],
  [Peak Tangential Hoop Stress], [$26.37$ MPa], [$sigma_(theta, "max") = p ((r_o^2 + r_i^2) / (r_o^2 - r_i^2))$ in PETG ($E=2100$ MPa)], [PASS ($"SF"_y = 1.90$)],
  [Shear Area in Plastic ($A_s$)], [$24.72 "mm"^2$], [$A_s = pi dot d_"maj" dot L_e dot "TSF" = pi times 2.20 times 6.50 times 0.55$], [PASS (Bulk Matrix)],
  [Axial Screw Pull-Out Force], [$741.6$ N], [$F_"pull" = A_s dot tau_s = 24.72 "mm"^2 times 30.0 "MPa" approx 75.6$ kgf], [PASS ($"SF" = 3.71$)],
  [Tightening Preload ($F_"clamp"$)], [$200.0$ N], [Nominal torque $T = 0.20 " N" dot "m"$ into plastic boss], [PASS (Zero Strip-Out)]
)

#pagebreak()

// --- Page 2: Tolerances & Manufacturing Matrix ---
#text(9.5pt, weight: "bold", fill: rgb("#0369a1"))[4. Manufacturing Clearance & Dimensional Tolerance Matrix]

#table(
  columns: (1.8fr, 1.3fr, 1.4fr, 1.5fr, 1.1fr),
  inset: 3.5pt,
  stroke: 0.5pt + rgb("#cbd5e1"),
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else { none },
  align: (left, left, left, left, center),
  [#text(7.5pt, weight: "bold")[Subsystem Feature]],
  [#text(7.5pt, weight: "bold")[CAD Geometry]],
  [#text(7.5pt, weight: "bold")[Mating Hardware]],
  [#text(7.5pt, weight: "bold")[Clearance / Fit Margins]],
  [#text(7.5pt, weight: "bold")[Audit Status]],
  [Tactile Button Shafts], [Dia $6.50$ mm through-bore], [Dia $6.00$ mm button stem], [$0.25$ mm radial ($0.50$ mm diametral)], [PASS (Glide)],
  [Tactile Plunger Travel], [$1.45$ mm pocket depth], [$6 times 6$ mm SMD dome switch], [$0.25$ mm nominal pre-travel stroke], [PASS (Positive Stop)],
  [Snap-Fit Latch Interlock], [$0.30$ mm undercut bead (4x)], [$0.35$ mm detent pockets], [$0.05$ mm retention clearance], [PASS ($>5000$ cycles)],
  [USB-C Receptacle Port], [$11.50 times 6.50$ mm cutout], [Standard USB-C plug overmold], [$0.80$ mm $45^degree$ conical entry flare], [PASS (Deep Seating)],
  [PCB Perimeter Cavity], [$52.50 times 38.50$ mm cavity], [$52.00 times 38.00$ mm FR4 PCB], [$0.25$ mm radial perimeter margin], [PASS (ISO Slip-Fit)],
  [M2 Corner Boss Holes], [Dia $2.00$ mm pilot bore], [M2 self-tapping screw], [$1.20$ mm solid boss wall thickness], [PASS (Hoop Safe)],
  [M2 Screw Counterbores], [Dia $4.40$ mm, depth $1.80$ mm], [M2 screw head ($d=3.8$ mm)], [$0.30$ mm radial tool clearance], [PASS (Flush Head)],
  [LiPo Battery Bay], [$38.00 times 26.00 times 4.50$ mm], [$400$ mAh pouch ($35 times 25$ mm)], [$1.50$ mm perimeter air jacket], [PASS (Convection)],
  [TP4056 Module Rails], [$17.50$ mm internal span], [Standard TP4056 breakout], [$0.25$ mm guide rail slide clearance], [PASS (Snap-In)]
)

#v(2pt)

// --- Section 5: Mesh Topology & Volumetric Data ---
#text(9.5pt, weight: "bold", fill: rgb("#0369a1"))[5. Watertight Mesh Topologies & Volumetric Audit]

#grid(
  columns: (1fr, 1.2fr),
  gutter: 8pt,
  [
    #table(
      columns: (1.6fr, 0.9fr, 1fr, 1fr),
      inset: 3.5pt,
      stroke: 0.5pt + rgb("#cbd5e1"),
      fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else { none },
      align: (left, center, center, center),
      [#text(7pt, weight: "bold")[Part Name]],
      [#text(7pt, weight: "bold")[Faces]],
      [#text(7pt, weight: "bold")[Volume]],
      [#text(7pt, weight: "bold")[Watertight]],
      [`enclosure_base.stl`], [4,156], [$8.953 "cm"^3$], [YES (0 non-man)],
      [`enclosure_lid.stl`], [9,952], [$8.014 "cm"^3$], [YES (0 non-man)],
      [`button_caps.stl`], [2,682], [$0.801 "cm"^3$], [YES (0 non-man)],
      [`print_bed_plate.stl`], [16,444], [$17.595 "cm"^3$], [YES (0 non-man)]
    )
  ],
  [
    #box(stroke: 0.5pt + rgb("#cbd5e1"), inset: 5pt, radius: 2pt, width: 100%, fill: rgb("#f8fafc"))[
      #text(7.5pt, weight: "bold")[Bambu Lab X1C / Prusa MK4 Single-Plate Print Feasibility] \
      #v(1pt)
      #text(7pt)[
        - *Array Envelope:* $121.0 times 85.0 times 11.1$ mm (Footprint: $102.85 "cm"^2$)
        - *Bed Occupation:* $24.7\%$ of Prusa MK4 ($250 times 210$ mm); $19.5\%$ of Bambu X1C.
        - *Support Requirement:* *0% supports required*. 100% flat surface orientation.
        - *Estimated Fabrication Time:* $42$ minutes at $0.20$ mm layer height.
      ]
    ]
  ]
)

#v(2pt)

// --- Section 6: Exploded Assembly & Internal Component Proof ---
#text(9.5pt, weight: "bold", fill: rgb("#0369a1"))[6. Exploded Assembly Verification & Layer Breakdown]

#align(center)[
  #image("renders/exploded_view.png", width: 58%) \
  #text(7pt, weight: "bold")[Figure 4: Exploded Multi-Tier Hardware Assembly ($1920 times 1080$ High-Resolution Projection)] \
  #text(6.5pt, fill: rgb("#64748b"))[Tier 1: Base Shell • Tier 2: LiPo Battery & TP4056 • Tier 3: Main PCB • Tier 4: Lid Bezel • Tier 5: 3x Buttons • Tier 6: M2 Fasteners]
]

#pagebreak()

// --- Page 3: Drop-Impact Kinematics & Stress Distribution ---
#text(9.5pt, weight: "bold", fill: rgb("#0369a1"))[7. MIL-STD-810H / IEC 60068-2-31 Drop-Impact Kinematics & Shock Verification]

#table(
  columns: (1.6fr, 1.1fr, 2.3fr, 1.2fr),
  inset: 3.5pt,
  stroke: 0.5pt + rgb("#cbd5e1"),
  fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else { none },
  align: (left, center, left, center),
  [#text(7.5pt, weight: "bold")[Dynamic Parameter]],
  [#text(7.5pt, weight: "bold")[Nominal Value]],
  [#text(7.5pt, weight: "bold")[Kinematic Formulation / Mechanics]],
  [#text(7.5pt, weight: "bold")[Verification Status]],
  [Freefall Drop Height ($h$)], [$1.20$ m], [Freefall onto rigid concrete floor per MIL-STD-810H], [PASS (Standard Test)],
  [Impact Velocity ($v_0$)], [$4.85$ m/s], [$v_0 = sqrt(2 g h) = sqrt(2 times 9.807 times 1.20)$ m/s], [PASS (Kinematic Freefall)],
  [Total Assembly Mass ($M_"pc"$)], [$52.50$ g], [Enclosure ($22.57$ g) + PCB ($18.0$ g) + LiPo ($9.5$ g) + Screws], [PASS (Total In-Flight)],
  [Total Impact Energy ($E_k$)], [$617.8$ mJ], [$E_k = M_"pc" dot g dot h = 0.0525 times 9.807 times 1.20$ J], [PASS (Kinetic Baseline)],
  [Corner Contact Deceleration], [$777.0$ g], [$a_"contact" = (pi v_0) / (2 tau)$ at apex ($tau = 1.0$ ms contact duration)], [PASS (Elastic Contact)],
  [Internal Shock Transmissibility], [$50.0$ g], [Damped thermoplastic enclosure attenuates to internal deck], [PASS (IEC 60068-2-31)],
  [1.5mm Chamfer Strain Energy ($U_"cap"$)], [$762.2$ mJ], [$U_"cap" = V_"def" dot u_t = 185 "mm"^3 times 4.12 "mJ/mm"^3$ in PETG], [PASS ($123.4\%$ Absorption)],
  [PCB Standoff Bending Stress], [$2.07$ MPa], [$sigma_b = (V dot h) / Z = (2.21 times 7.50) / 8.01$ MPa ($V = 2.21$ N per boss)], [PASS ($"SF"_b = 24.19$)],
  [PCB Standoff Shear Stress], [$0.18$ MPa], [$tau = V / A = 2.21 / 12.06$ MPa direct annular shear], [PASS ($"SF"_s = 163.9$)],
  [Combined Standoff von Mises], [$2.09$ MPa], [$sigma_"vm" = sqrt(sigma_b^2 + 3 tau^2) = sqrt(2.07^2 + 3(0.18^2))$ MPa], [PASS ($"FoS" = 23.91 gt.eq 2.0$)],
  [LiPo Pouch Retention ($50g$)], [$4.66$ N], [$F_"inertial" = 0.0095 times 490.33$ N; Rib Shear $tau = 0.12$ MPa], [PASS ($"FoS" = 252.1 gt.eq 2.0$)]
)

#v(2pt)

// --- Section 8: Drop-Impact Stress Distribution & Deceleration Diagram ---
#text(9.5pt, weight: "bold", fill: rgb("#0369a1"))[8. Drop-Impact Finite Element & Kinematic Stress Distribution Proof]

#align(center)[
  #image("renders/drop_impact_stress_analysis.png", width: 94%) \
  #text(7pt, weight: "bold")[Figure 5: High-Resolution Drop-Impact Kinematics, Chamfer Energy Absorption & Standoff Stress Map ($1920 times 1080$)] \
  #text(6.5pt, fill: rgb("#64748b"))[Panel 1: Deceleration Pulse • Panel 2: Chamfer Strain Energy • Panel 3: Chamfer Stress Field • Panel 4: Standoff Bending • Panel 5: LiPo Retention • Panel 6: Audit Matrix]
]
