// analog_neuron - external interface only (Silicluster v3, analog project)
//
// Single-input analog ReLU neuron in SKY130A, 1.8 V supply:
//     Y = 2 * max(0, X - Vk),   Vk = 0.326 * VDD  (0.586 V at 1.8 V)
//
// The circuit is analog; this module only declares its ports for integration.
// Layout: top cell "analog_neuron", 180 um x 115 um, origin at the lower-left corner.
//   X   : metal3, right edge, x = 179.4 um, y = 81.27 um
//   Y   : metal3, right edge, x = 179.4 um, y = 82.07 um
//   VDD : metal5 horizontal rail, top    (y = 111.5 - 114.5 um)
//   VSS : metal5 horizontal rail, bottom (y =   0.5 -   3.5 um)
//   Power grid: metal4 vertical straps, metal5 horizontal rails.

`default_nettype none

module analog_neuron (
    inout  wire VDD,   // 1.8 V supply
    inout  wire VSS,   // ground
    input  wire X,     // analog input, 0.3 - 1.2 V; ~300 kOhm to an internal ~0.26 V node
    output wire Y      // analog output, 0 - ~1.2 V; unbuffered ~300 kOhm source (load >= 10 MOhm)
);
endmodule

`default_nettype wire
