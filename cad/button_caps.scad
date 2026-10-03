// =============================================================================
// Pocket Companion - Snap-Fit Tactile Button Caps
// File: cad/button_caps.scad
// =============================================================================

include <parameters.scad>

// Mode switcher: "print" (array of 3 caps on build plate) or "single"
mode = "print"; // ["print", "single", "assembly"]

// Total button cap height in assembly orientation
btn_total_h = btn_shaft_h + 1.6; // 8.4 mm
dish_depth = 0.5;                // Depth of ergonomic concave thumb dish

// 2D half cross-section profile for seamless 100% watertight 2-manifold revolution
module button_cap_2d_profile() {
    polygon(points = [
        [0, -btn_plunger_h],                                  // Plunger center bottom
        [btn_plunger_d / 2 - 0.2, -btn_plunger_h],            // Plunger bottom taper
        [btn_plunger_d / 2, -0.01],                           // Plunger top
        [btn_flange_d / 2, -0.01],                            // Flange bottom corner
        [btn_flange_d / 2, btn_flange_t],                     // Flange outer rim
        [btn_head_d / 2, btn_flange_t],                       // Flange shoulder to shaft
        [btn_head_d / 2, btn_total_h - 0.6],                  // Shaft upper wall
        [btn_head_d / 2 - 0.6, btn_total_h],                  // Top perimeter chamfer
        [0, btn_total_h - dish_depth]                         // Center of concave thumb dish
    ]);
}

// Single button cap
module button_cap(orient = "print") {
    if (orient == "assembly") {
        rotate_extrude($fn = 64)
            button_cap_2d_profile();
    } else if (orient == "print") {
        // Inverted for 100% support-free bed adhesion
        // Flat/chamfered top face sits on the build plate (Z=0)
        translate([0, 0, btn_total_h])
            rotate([180, 0, 0])
                button_cap(orient = "assembly");
    }
}

// Array of 3 button caps spaced for batch printing on 3D printer bed
module button_caps_array(spacing = 14.0) {
    for (i = [-1 : 1]) {
        translate([i * spacing, 0, 0])
            button_cap(orient = "print");
    }
}

// Top-level render selection
if (mode == "print") {
    // Print-ready trio of tactile button caps
    button_caps_array(spacing = 14.0);
} else if (mode == "single") {
    button_cap(orient = "print");
} else if (mode == "assembly") {
    button_cap(orient = "assembly");
}
