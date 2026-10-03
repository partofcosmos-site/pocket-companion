// =============================================================================
// Pocket Companion - Snap-Fit Tactile Button Caps
// File: cad/button_caps.scad
// =============================================================================

include <parameters.scad>

// Mode switcher: "print" (array of 3 caps on build plate) or "single"
mode = "print"; // ["print", "single", "assembly"]

module rounded_cylinder(d, h, r) {
    rotate_extrude() {
        hull() {
            square([d/2 - r, h]);
            translate([d/2 - r, r]) circle(r=r);
            translate([d/2 - r, h - r]) circle(r=r);
        }
    }
}

// Single button cap
// In "assembly" orientation: top head points UP (+Z), flange at bottom, plunger facing DOWN (-Z)
// In "print" orientation: inverted so the top head or flange prints flat on the bed with zero supports!
module button_cap(orient = "print") {
    if (orient == "assembly") {
        union() {
            // Lower captive flange (retaining collar inside lid)
            cylinder(d = btn_flange_d, h = btn_flange_t);
            
            // Central sliding shaft
            translate([0, 0, btn_flange_t])
                cylinder(d = btn_head_d, h = btn_shaft_h - btn_flange_t);
            
            // Tactile top head with ergonomic chamfer and dished thumb depression
            translate([0, 0, btn_shaft_h]) {
                difference() {
                    cylinder(d = btn_head_d, h = 1.6);
                    // Ergonomic concave dish
                    translate([0, 0, 1.6 + 6.0])
                        sphere(r = 6.2);
                }
            }
            
            // Underside tactile switch actuator plunger nipple
            translate([0, 0, -btn_plunger_h])
                cylinder(d1 = btn_plunger_d - 0.5, d2 = btn_plunger_d, h = btn_plunger_h);
        }
    } else if (orient == "print") {
        // Optimized for FDM/SLA support-free 3D printing
        // Inverted: Flat top head on the build plate (Z=0), flange in the middle, plunger extending upward
        translate([0, 0, btn_shaft_h + 1.6])
        rotate([180, 0, 0])
        button_cap(orient = "assembly");
    }
}

// Array of 3 button caps spaced for batch printing on 3D printer bed
module button_caps_array(spacing = 14.0) {
    for (i = [0 : 2]) {
        translate([i * spacing, 0, 0])
            button_cap(orient = "print");
    }
}

// Top-level render selection
if (mode == "print") {
    // Print-ready trio of tactile button caps
    translate([-14.0, 0, 0])
        button_caps_array(spacing = 14.0);
} else if (mode == "single") {
    button_cap(orient = "print");
} else if (mode == "assembly") {
    button_cap(orient = "assembly");
}
