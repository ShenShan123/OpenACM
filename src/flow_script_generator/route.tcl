#File Name: route.tcl
# ==================== Routing Script ====================
# Design Name and Technology Platform
set DESIGN_NAME "sram_sim"    ;# Design Name
set ACTUAL_TOP_MODULE_NAME "sram_multiplier_system"
set PLATFORM "nangate45" ;# Technology Platform

# --- Path Configuration ---
set PLATFORM_DIR "./DCIM/nangate45"
set RESULTS_DIR "./DCIM/results/routing" ;
set SDC_FILE "./DCIM/results/cts/4_cts.sdc"
file mkdir $RESULTS_DIR

# === Technical Docs Configuration ===
set TECH_LEF "./DCIM/nangate45/lef/NangateOpenCellLibrary.tech.lef"
set SC_LEF "./DCIM/nangate45/lef/NangateOpenCellLibrary.macro.mod.lef"
set LIB_FILES "./DCIM/nangate45/lib/NangateOpenCellLibrary_typical.lib"
set SRAM_LEF "./DCIM/nangate45/lef/SRAM_6T_CORE_16x8_MC_TB.lef"
set SRAM_LIB "./DCIM/nangate45/lib/SRAM_6T_CORE_16x8_MC_TB.lib"
# === Environment Variables Configuration ===
set ::env(CELL_PAD_IN_SITES_DETAIL_PLACEMENT) 2 ;# ​​Increase the detailed placement cell spacing
set ::env(DONT_USE_CELLS) "TAPCELL_* FILLER_*"  ;# Forbidden Cell Type
set ::env(SCRIPTS_DIR) "./DCIM/scripts"
set ::env(REPORTS_DIR) "./DCIM/reports"
set ::env(LIB_FILES) $LIB_FILES
set ::env(RESULTS_DIR) $RESULTS_DIR             ;# Results Directory​
# === Key Environmental Variables​ ===
set ::env(MIN_ROUTING_LAYER) metal2             ;# Minimum Routing Layer (Metal2)​
set ::env(MAX_ROUTING_LAYER) metal10            ;# Maximum Routing Layer (Metal10)​
set ::env(FILL_CELLS) "FILLCELL_X1 FILLCELL_X2 FILLCELL_X4 FILLCELL_X8 FILLCELL_X16 FILLCELL_X32"
set ::global_route_congestion_report "$::env(REPORTS_DIR)/congestion.rpt"
set ::env(ROUTING_LAYER_ADJUSTMENT) 0.4         ;# parameter for the fast_route function​

# ==== Read the Design ====
read_lef $TECH_LEF
read_lef $SC_LEF
read_liberty $LIB_FILES
read_db "./DCIM/results/cts/4_1_cts.odb"
read_sdc $SDC_FILE
read_liberty $SRAM_LIB
read_lef $SRAM_LEF

# Load the Platform RC Tech File
source ${PLATFORM_DIR}/setRC.tcl
# Import util.tcl​
source $::env(SCRIPTS_DIR)/util.tcl

# ==== Global Routing ====
puts "=== Start Global Routing ==="

fast_route

# Run Pin Access
pin_access -bottom_routing_layer $::env(MIN_ROUTING_LAYER) \
           -top_routing_layer $::env(MAX_ROUTING_LAYER)

# Run Global Routing
puts "Run Global Routing..."
global_route -congestion_report_file $::global_route_congestion_report

set_placement_padding -global \
                      -left $::env(CELL_PAD_IN_SITES_DETAIL_PLACEMENT) \
                      -right $::env(CELL_PAD_IN_SITES_DETAIL_PLACEMENT)

# Configure Propagated Clocks​
set_propagated_clock [all_clocks]
estimate_parasitics -global_routing

set_dont_use $::env(DONT_USE_CELLS)

# Repair design using global route parasitics
repair_design_helper ;

# Running DPL to fix overlapped instances
# Run to get modified net by DPL
global_route -start_incremental
detailed_placement
# Route only the modified net by DPL
global_route -end_incremental \
             -congestion_report_file $::env(REPORTS_DIR)/congestion_post_repair_design.rpt

# Repair timing using global route parasitics
puts "Repair setup and hold violations..."
estimate_parasitics -global_routing
repair_timing_helper ;

# Running DPL to fix overlapped instances
# Run to get modified net by DPL
global_route -start_incremental
detailed_placement
# Route only the modified net by DPL
global_route -end_incremental \
             -congestion_report_file $::env(REPORTS_DIR)/congestion_post_repair_timing.rpt

# Export Global Routing Results
# write_guides $RESULTS_DIR/route.guide
write_def $RESULTS_DIR/5_1_grt.def
write_db $RESULTS_DIR/5_1_grt.odb

# ==== Detailed Routing ====
puts "=== Start Detailed Routing === "
set detailed_route_args "-output_drc $::env(REPORTS_DIR)/route_drc.rpt"
detailed_route {*}$detailed_route_args

# # Run antenna check and repair
# repair_antennas
# detailed_route {*}$detailed_route_args

# Export Detailed Routing Results
write_def $RESULTS_DIR/5_2_route.def
write_db $RESULTS_DIR/5_2_route.odb
write_verilog $RESULTS_DIR/5_2_route.v

# # ==== Filler Cell Insertion​ ====
puts "=== Start Filler Cell Insertion​ === "
filler_placement $::env(FILL_CELLS)
write_def $RESULTS_DIR/5_3_fillcell.def
write_db $RESULTS_DIR/5_3_fillcell.odb
write_verilog $RESULTS_DIR/5_3_fillcell.v

puts "Routing Phase Completed!"

report_design_area