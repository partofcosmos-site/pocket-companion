// =============================================================================
// Pocket Companion - Parametric Enclosure Dimensions & Mechanical Parameters
// All dimensions in millimeters (mm)
// =============================================================================

$fn = 64; // High-resolution circle rendering for 3D printing

// -----------------------------------------------------------------------------
// 3D Printing Tolerances & Clearances
// -----------------------------------------------------------------------------
tol = 0.25;               // Standard FDM/SLA clearance tolerance
slide_tol = 0.30;         // Clearance for sliding fit (buttons, switches)
press_tol = 0.15;         // Interference/press fit tolerance

// -----------------------------------------------------------------------------
// PCB Dimensions (from Pocket_Companion_PCB.json)
// -----------------------------------------------------------------------------
pcb_w = 52.0;             // PCB width (X axis)
pcb_h = 38.0;             // PCB depth/height (Y axis)
pcb_t = 1.6;              // PCB thickness (Z axis)
pcb_corner_r = 3.0;       // PCB outline corner radius

// PCB Internal Cavity
cavity_w = pcb_w + 2 * tol; // 52.5 mm
cavity_h = pcb_h + 2 * tol; // 38.5 mm

// -----------------------------------------------------------------------------
// Enclosure Wall & Outer Geometry
// -----------------------------------------------------------------------------
wall_t = 2.0;             // Perimeter shell wall thickness
floor_t = 2.0;            // Base bottom floor thickness
roof_t = 2.2;             // Top lid ceiling thickness

outer_w = cavity_w + 2 * wall_t; // 56.5 mm
outer_h = cavity_h + 2 * wall_t; // 42.5 mm
outer_corner_r = pcb_corner_r + wall_t; // 5.0 mm

// Height breakdown (Z axis)
// - Floor: 2.0mm
// - Lower bay (LiPo 400mAh + wiring + RP2040 underside): 7.5mm
// - PCB shelf / standoff height: 7.5mm from inner floor
// - PCB thickness: 1.6mm
// - Upper bay (OLED, button stems, buzzer): 6.4mm
// - Roof: 2.2mm
// Total height = 2.0 + 7.5 + 1.6 + 6.4 + 2.2 = 19.7 mm
standoff_z = 7.5;         // Height of PCB mounting face above inner floor
base_inner_d = 7.5;       // Depth of base inner cavity
lid_inner_d = 8.0;        // Depth of lid inner cavity (PCB top to ceiling)

base_total_h = floor_t + base_inner_d; // 9.5 mm
lid_total_h = roof_t + lid_inner_d;    // 10.2 mm
total_enclosure_h = base_total_h + lid_total_h; // 19.7 mm

// Mating Lip (Tongue & Groove alignment joint)
lip_h = 1.5;              // Height of interlocking lip
lip_w = wall_t / 2;       // 1.0 mm lip thickness

// -----------------------------------------------------------------------------
// PCB Mounting Standoffs & Corner Bosses
// -----------------------------------------------------------------------------
standoff_inset_x = 3.5;   // X distance from PCB edge to hole center
standoff_inset_y = 3.5;   // Y distance from PCB edge to hole center
standoff_od = 5.6;        // Standoff outer diameter
screw_hole_d = 2.0;       // Pilot hole diameter for M2 self-tapping screws
screw_head_d = 4.2;       // Counterbore diameter for M2 screw head
screw_head_depth = 1.8;   // Counterbore depth

// Standoff center coordinates relative to PCB origin (0, 0)
standoff_pos = [
    [standoff_inset_x, standoff_inset_y],
    [pcb_w - standoff_inset_x, standoff_inset_y],
    [standoff_inset_x, pcb_h - standoff_inset_y],
    [pcb_w - standoff_inset_x, pcb_h - standoff_inset_y]
];

// -----------------------------------------------------------------------------
// Component Layout (Coordinates relative to PCB bottom-left corner)
// -----------------------------------------------------------------------------
// 1. OLED Display (0.96" SSD1306)
// Header at (26.0, 8.0), Display spans ~Y: 9.0 to 25.0
oled_center_x = 26.0;
oled_center_y = 16.5;
oled_window_w = 23.5;     // Visible active OLED display width
oled_window_h = 12.5;     // Visible active OLED display height
oled_window_r = 1.2;      // Window corner radius
oled_bezel_w = 27.5;      // Recessed outer cosmetic bezel width
oled_bezel_h = 16.5;      // Recessed outer cosmetic bezel height
oled_bezel_recess = 0.8;  // Bezel recess depth into top surface

// 2. Tactile Push Buttons (SW1, SW2, SW3)
btn_y = 30.0;
btn_x_left   = 12.0;
btn_x_action = 26.0;
btn_x_right  = 40.0;
btn_positions = [
    [btn_x_left, btn_y],
    [btn_x_action, btn_y],
    [btn_x_right, btn_y]
];

// Button cap dimensions
btn_head_d = 6.0;         // Button cap diameter
btn_hole_d = btn_head_d + 2 * slide_tol; // 6.6 mm guide hole in lid
btn_flange_d = 8.4;       // Captive retaining brim diameter
btn_flange_t = 1.0;       // Retaining brim thickness
btn_shaft_h = 6.8;        // Total shaft height
btn_plunger_d = 3.0;      // Contact nipple diameter for tactile switch
btn_plunger_h = 1.4;      // Contact nipple height
btn_travel = 0.5;         // Tactile switch nominal actuation travel

// 3. Piezo Buzzer Sound Vents (BZ1 at x=44.0, y=14.0)
buzzer_x = 44.0;
buzzer_y = 14.0;
vent_center_d = 2.2;      // Center acoustic hole
vent_ring_d = 1.5;        // Outer ring acoustic hole diameter
vent_ring_r = 3.6;        // Radius of circular vent pattern

// 4. Power Slide Switch (SW_PWR at x=6.0, y=12.0)
pwr_switch_x = 0;         // Opening on left wall
pwr_switch_y = 12.0;      // Y position along the wall
pwr_slot_w = 9.5;         // Slot width along Y axis (travel + knob)
pwr_slot_h = 4.2;         // Slot height along Z axis
pwr_slot_z = floor_t + standoff_z + pcb_t + 0.8; // Aligned with switch toggle

// 5. TP4056 USB-C Charger Port
// Mounted at the bottom or rear wall
usbc_wall_y = 0;          // Cutout on bottom wall (Y=0)
usbc_center_x = 26.0;     // Centered along X axis
usbc_w = 10.2;            // USB-C connector cutout width
usbc_h = 4.6;             // USB-C connector cutout height
usbc_r = 1.5;             // USB-C rounded pill corners
usbc_z = floor_t + 1.2;   // Height from bottom floor

// 6. 400mAh LiPo Battery Bay (on Base shell floor)
lipo_bay_w = 38.0;        // Bay width for 400mAh pouch
lipo_bay_h = 26.0;        // Bay depth
lipo_bay_d = 4.5;         // Recess / side retention pocket depth
lipo_center_x = 26.0;
lipo_center_y = 20.0;
