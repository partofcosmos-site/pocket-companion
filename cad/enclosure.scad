// =============================================================================
// Pocket Companion - Parametric 3D Printable Enclosure Suite
// File: cad/enclosure.scad
// =============================================================================

include <parameters.scad>
use <button_caps.scad>

// Part selection for rendering / compilation
// Options: "assembly", "exploded", "base", "lid", "buttons", "cutaway"
part = "assembly"; // ["assembly", "exploded", "base", "lid", "buttons", "cutaway"]

// -----------------------------------------------------------------------------
// Geometric Primitives & 2D Profiles
// -----------------------------------------------------------------------------
module rounded_rect_2d(w, h, r) {
    hull() {
        translate([r, r]) circle(r = r);
        translate([w - r, r]) circle(r = r);
        translate([r, h - r]) circle(r = r);
        translate([w - r, h - r]) circle(r = r);
    }
}

module rounded_box(w, h, z, r) {
    linear_extrude(height = z)
        rounded_rect_2d(w, h, r);
}

// -----------------------------------------------------------------------------
// Base Shell (Houses LiPo pouch, TP4056 USB-C, Power Switch, PCB Standoffs)
// -----------------------------------------------------------------------------
module enclosure_base() {
    difference() {
        union() {
            // 1. Hollow outer perimeter shell
            difference() {
                union() {
                    // Solid outer block
                    rounded_box(outer_w, outer_h, base_total_h, outer_corner_r);
                    
                    // Stepped interlocking alignment tongue on top rim
                    translate([wall_t - lip_w/2, wall_t - lip_w/2, base_total_h])
                        difference() {
                            rounded_box(cavity_w + lip_w, cavity_h + lip_w, lip_h, outer_corner_r - wall_t/2);
                            translate([lip_w + tol, lip_w + tol, -0.1])
                                rounded_box(cavity_w - lip_w - 2*tol, cavity_h - lip_w - 2*tol, lip_h + 0.2, pcb_corner_r);
                        }
                }
                
                // Interior hollow cavity
                translate([wall_t, wall_t, floor_t])
                    rounded_box(cavity_w, cavity_h, base_total_h + lip_h + 2.0, pcb_corner_r);
            }
            
            // 2. Corner Standoff Bosses for PCB (52x38mm)
            for (pos = standoff_pos) {
                translate([wall_t + tol + pos[0], wall_t + tol + pos[1], floor_t])
                    cylinder(d = standoff_od, h = standoff_z);
            }
            
            // 3. Continuous PCB perimeter resting shelf (1.2mm ledge around inner wall)
            translate([wall_t, wall_t, floor_t + standoff_z - 1.2])
                difference() {
                    rounded_box(cavity_w, cavity_h, 1.2, pcb_corner_r);
                    translate([1.2, 1.2, -0.1])
                        rounded_box(cavity_w - 2.4, cavity_h - 2.4, 1.4, pcb_corner_r);
                }
            
            // 4. 400mAh LiPo Battery Pouch Retention Bay (38mm x 26mm cradle)
            translate([wall_t + tol + lipo_center_x - lipo_bay_w/2, wall_t + tol + lipo_center_y - lipo_bay_h/2, floor_t]) {
                // Side retention ribs
                cube([1.4, lipo_bay_h, 3.2]);
                translate([lipo_bay_w - 1.4, 0, 0])
                    cube([1.4, lipo_bay_h, 3.2]);
                // End stop tabs
                cube([lipo_bay_w, 1.4, 2.5]);
                translate([0, lipo_bay_h - 1.4, 0])
                    cube([lipo_bay_w, 1.4, 2.5]);
            }
            
            // 5. TP4056 USB-C Charger Module Bay Guide Rails
            translate([wall_t + tol + usbc_center_x - 17.5/2 - 1.4, wall_t, floor_t]) {
                cube([1.4, 18.0, 3.0]);
                translate([17.5 + 1.4, 0, 0])
                    cube([1.4, 18.0, 3.0]);
            }
        }
        
        // --- Cutouts & Subtractions ---
        
        // 1. M2 Screw pilot holes in the 4 corner standoffs
        for (pos = standoff_pos) {
            translate([wall_t + tol + pos[0], wall_t + tol + pos[1], floor_t + standoff_z - 6.5])
                cylinder(d = screw_hole_d, h = 8.0);
        }
        
        // 2. TP4056 USB-C cutout on bottom wall (Y = 0)
        translate([wall_t + tol + usbc_center_x - usbc_w/2, -1.0, usbc_z])
            hull() {
                translate([usbc_r, 0, usbc_r])
                    rotate([-90, 0, 0]) cylinder(r = usbc_r, h = wall_t + 2.0);
                translate([usbc_w - usbc_r, 0, usbc_r])
                    rotate([-90, 0, 0]) cylinder(r = usbc_r, h = wall_t + 2.0);
                translate([usbc_r, 0, usbc_h - usbc_r])
                    rotate([-90, 0, 0]) cylinder(r = usbc_r, h = wall_t + 2.0);
                translate([usbc_w - usbc_r, 0, usbc_h - usbc_r])
                    rotate([-90, 0, 0]) cylinder(r = usbc_r, h = wall_t + 2.0);
            }
        
        // 3. Power Slide Switch Notch on left wall (X = 0) at parting line
        translate([-1.0, wall_t + tol + pwr_switch_y - pwr_slot_w/2, base_total_h - 2.5])
            cube([wall_t + 2.0, pwr_slot_w, 3.0 + lip_h + 0.5]);
        
        // 4. Bottom perimeter chamfer for ergonomic handheld comfort
        difference() {
            translate([-1, -1, -0.1])
                cube([outer_w + 2, outer_h + 2, 0.8]);
            translate([0, 0, -0.2])
                rounded_box(outer_w, outer_h, 1.0, outer_corner_r);
        }
    }
}

// -----------------------------------------------------------------------------
// Top Lid (OLED Bezel Window, 3x Button Guide Shafts, Piezo Sound Vents)
// -----------------------------------------------------------------------------
module enclosure_lid() {
    difference() {
        union() {
            // 1. Hollow outer lid body
            difference() {
                // Solid outer shell
                rounded_box(outer_w, outer_h, lid_total_h, outer_corner_r);
                
                // Interior hollow cavity
                translate([wall_t, wall_t, -0.1])
                    rounded_box(cavity_w, cavity_h, lid_inner_d + 0.1, pcb_corner_r);
                
                // Interlocking groove to receive base tongue
                translate([wall_t - lip_w/2 - tol, wall_t - lip_w/2 - tol, -0.1])
                    difference() {
                        rounded_box(cavity_w + lip_w + 2*tol, cavity_h + lip_w + 2*tol, lip_h + 0.2, outer_corner_r - wall_t/2 + tol);
                        translate([lip_w - tol, lip_w - tol, -0.2])
                            rounded_box(cavity_w - lip_w + 2*tol, cavity_h - lip_w + 2*tol, lip_h + 0.6, pcb_corner_r);
                    }
            }
            
            // 2. Three Cylindrical Button Guide Shaft Sleeves on lid underside
            for (bpos = btn_positions) {
                translate([wall_t + tol + bpos[0], wall_t + tol + bpos[1], 0])
                    cylinder(d = btn_flange_d + 1.8, h = lid_inner_d);
            }
            
            // 3. Underside OLED Display Locator Frame
            translate([wall_t + tol + oled_center_x - (oled_bezel_w + 1.2)/2,
                       wall_t + tol + oled_center_y - (oled_bezel_h + 1.2)/2,
                       lid_inner_d - 2.5]) {
                difference() {
                    rounded_box(oled_bezel_w + 1.2, oled_bezel_h + 1.2, 2.5, 1.5);
                    translate([1.2, 1.2, -0.1])
                        rounded_box(oled_bezel_w - 1.2, oled_bezel_h - 1.2, 2.7, 1.2);
                }
            }
            
            // 4. Corner screw boss reinforcement tubes inside lid
            for (pos = standoff_pos) {
                translate([wall_t + tol + pos[0], wall_t + tol + pos[1], 0])
                    cylinder(d = standoff_od, h = lid_inner_d);
            }
        }
        
        // --- Cutouts & Functional Apertures ---
        
        // 1. OLED Display: Active Screen Aperture & Recessed Outer Bezel
        // Active view window through ceiling
        translate([wall_t + tol + oled_center_x - oled_window_w/2,
                   wall_t + tol + oled_center_y - oled_window_h/2,
                   lid_inner_d - 0.5])
            rounded_box(oled_window_w, oled_window_h, roof_t + 1.0, oled_window_r);
        
        // Recessed cosmetic framing bezel on top face
        translate([wall_t + tol + oled_center_x - oled_bezel_w/2,
                   wall_t + tol + oled_center_y - oled_bezel_h/2,
                   lid_total_h - oled_bezel_recess])
            rounded_box(oled_bezel_w, oled_bezel_h, oled_bezel_recess + 0.2, oled_window_r + 0.8);
        
        // 2. Three Tactile Button Guide Shafts
        for (bpos = btn_positions) {
            // Button sliding guide hole through lid
            translate([wall_t + tol + bpos[0], wall_t + tol + bpos[1], -0.2])
                cylinder(d = btn_hole_d, h = lid_total_h + 0.4);
            
            // Captive retaining flange counterbore pocket inside sleeve
            translate([wall_t + tol + bpos[0], wall_t + tol + bpos[1], -0.1])
                cylinder(d = btn_flange_d + 2*tol, h = btn_flange_t + 1.2);
        }
        
        // 3. Piezo Buzzer Acoustic Resonance Grille
        // Central acoustic vent hole
        translate([wall_t + tol + buzzer_x, wall_t + tol + buzzer_y, lid_inner_d - 0.5])
            cylinder(d = vent_center_d, h = roof_t + 1.0);
        
        // Concentric acoustic ring of 6 holes
        for (a = [0 : 60 : 300]) {
            translate([wall_t + tol + buzzer_x + vent_ring_r * cos(a),
                       wall_t + tol + buzzer_y + vent_ring_r * sin(a),
                       lid_inner_d - 0.5])
                cylinder(d = vent_ring_d, h = roof_t + 1.0);
        }
        
        // 4. Power Switch Upper Slot Clearance (Left wall, X = 0)
        translate([-1.0, wall_t + tol + pwr_switch_y - pwr_slot_w/2, -0.1])
            cube([wall_t + 2.0, pwr_slot_w, pwr_slot_h - 1.0]);
        
        // 5. Corner M2 Screw Fastener Counterbored Holes
        for (pos = standoff_pos) {
            // Screw thread clearance hole
            translate([wall_t + tol + pos[0], wall_t + tol + pos[1], -0.5])
                cylinder(d = screw_hole_d + 0.4, h = lid_total_h + 1.0);
            
            // Flush screw head counterbore on top surface
            translate([wall_t + tol + pos[0], wall_t + tol + pos[1], lid_total_h - screw_head_depth])
                cylinder(d = screw_head_d, h = screw_head_depth + 0.2);
        }
    }
}

// -----------------------------------------------------------------------------
// PCB Model Representation (for assembly verification & visual proof)
// -----------------------------------------------------------------------------
module pcb_model() {
    color([0.15, 0.45, 0.25, 0.9]) // FR4 Green / Purple Soldermask
    difference() {
        rounded_box(pcb_w, pcb_h, pcb_t, pcb_corner_r);
        // Standoff corner screw holes
        for (pos = standoff_pos) {
            translate([pos[0], pos[1], -0.5])
                cylinder(d = screw_hole_d + 0.2, h = pcb_t + 1.0);
        }
    }
    
    // 0.96" OLED Module PCB & Glass
    color([0.1, 0.1, 0.15, 0.95])
    translate([oled_center_x - 13.5, oled_center_y - 13.5, pcb_t]) {
        cube([27.0, 27.0, 1.4]);
        // OLED Glass active display
        color([0.05, 0.2, 0.4, 0.95])
        translate([1.75, 7.5, 1.4])
            cube([23.5, 12.0, 1.2]);
    }
    
    // 3x Tactile Switch Bodies (6x6x5mm)
    for (bpos = btn_positions) {
        color([0.2, 0.2, 0.25])
        translate([bpos[0] - 3.0, bpos[1] - 3.0, pcb_t]) {
            cube([6.0, 6.0, 3.5]);
            // Button metal actuator stem
            color([0.8, 0.8, 0.85])
            translate([3.0, 3.0, 3.5])
                cylinder(d = 3.2, h = 1.5);
        }
    }
    
    // Piezo Buzzer (dia 9.0mm, h 4.2mm)
    color([0.15, 0.15, 0.18])
    translate([buzzer_x, buzzer_y, pcb_t])
        cylinder(d = 9.0, h = 4.2);
    
    // Waveshare RP2040-Zero (Bottom side, x=26, y=18)
    color([0.1, 0.35, 0.55])
    translate([26.0 - 9.0, 18.0 - 11.75, -2.5])
        cube([18.0, 23.5, 2.5]);
    
    // SPDT Power Slide Switch
    color([0.7, 0.7, 0.75])
    translate([pwr_switch_x + 1.0, pwr_switch_y - 4.0, pcb_t]) {
        cube([4.0, 8.5, 3.5]);
        // Toggle knob extending through wall
        color([0.2, 0.2, 0.2])
        translate([-3.5, 3.0, 0.8])
            cube([3.5, 2.5, 2.0]);
    }
}

// -----------------------------------------------------------------------------
// Assembly & Exploded Visualizer
// -----------------------------------------------------------------------------
module enclosure_assembly(lid_z_offset = 0) {
    // Base Shell
    color([0.20, 0.22, 0.25]) // Sleek Matte Cyber Slate
        enclosure_base();
    
    // 400mAh LiPo Battery Model in Base
    color([0.75, 0.75, 0.78, 0.85])
    translate([wall_t + tol + lipo_center_x - 35.0/2, wall_t + tol + lipo_center_y - 25.0/2, floor_t + 0.4])
        cube([35.0, 25.0, 5.5]);
    
    // Internal PCB Assembly
    translate([wall_t + tol, wall_t + tol, floor_t + standoff_z + (lid_z_offset > 0 ? lid_z_offset * 0.35 : 0)])
        pcb_model();
    
    // 3x Tactile Button Caps
    for (bpos = btn_positions) {
        color([0.92, 0.30, 0.24]) // Racing Red tactile caps
        translate([wall_t + tol + bpos[0], wall_t + tol + bpos[1], floor_t + standoff_z + pcb_t + 4.8 + (lid_z_offset > 0 ? lid_z_offset * 1.15 : 0)])
            button_cap(orient = "assembly");
    }
    
    // Top Lid
    color([0.30, 0.34, 0.38, 0.92]) // Semi-transparent smoked slate
    translate([0, 0, base_total_h + lid_z_offset])
        enclosure_lid();
}

// -----------------------------------------------------------------------------
// Top-Level Execution Selector
// -----------------------------------------------------------------------------
if (part == "base") {
    // Base shell oriented flat on build plate for printing
    enclosure_base();
} else if (part == "lid") {
    // Lid oriented flat on build plate (roof down or inner cavity up)
    enclosure_lid();
} else if (part == "buttons") {
    // 3x button caps array
    translate([0, 0, 0])
        button_caps_array();
} else if (part == "assembly") {
    // Fully mated, closed assembly
    enclosure_assembly(lid_z_offset = 0);
} else if (part == "exploded") {
    // Exploded presentation view showing all internal hardware layers
    enclosure_assembly(lid_z_offset = 28.0);
} else if (part == "cutaway") {
    // Longitudinal cross-section view for internal fit verification
    difference() {
        enclosure_assembly(lid_z_offset = 0);
        translate([outer_w/2, -5, -5])
            cube([outer_w + 10, outer_h + 10, total_enclosure_h + 10]);
    }
}
