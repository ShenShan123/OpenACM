#File Name: placement.tcl
# Design Name and Technology Platform​
set DESIGN_NAME "sram_sim"    ;# Design Name
set ACTUAL_TOP_MODULE_NAME "sram_multiplier_system"
set PLATFORM "nangate45" ;# Technology Platform

# --- Path Configuration ---
set PLATFORM_DIR "./DCIM/nangate45"
set RESULTS_DIR "./DCIM/results/placement" ;
set SDC_FILE "./DCIM/results/floorplan/2_4_floorplan_pdn.sdc"

file mkdir $RESULTS_DIR

# === Technical Docs Configuration ===
set TECH_LEF "./DCIM/nangate45/lef/NangateOpenCellLibrary.tech.lef"
set SC_LEF "./DCIM/nangate45/lef/NangateOpenCellLibrary.macro.mod.lef"
set LIB_FILES "./DCIM/nangate45/lib/NangateOpenCellLibrary_typical.lib"
set SRAM_LEF "./DCIM/nangate45/lef/SRAM_6T_CORE_64x32_MC_TB.lef"
set SRAM_LIB "./DCIM/nangate45/lib/SRAM_6T_CORE_64x32_MC_TB.lib"

# === Environment Variables Configuration ===
set ::env(CELL_PAD_IN_SITES_GLOBAL_PLACEMENT) 1 ;# ​​Increase the global placement cell spacing
set ::env(CELL_PAD_IN_SITES_DETAIL_PLACEMENT) 1 ;# ​​Increase the detailed placement cell spacing
set ::env(DONT_USE_CELLS) "TAPCELL_*"  ;# Forbidden Cell Type
set ::env(SCRIPTS_DIR) "./DCIM/scripts"
set ::env(REPORTS_DIR) "./DCIM/reports"
set ::env(LIB_FILES) $LIB_FILES
set ::env(RESULTS_DIR) $RESULTS_DIR             ;# Results Directory​
# === Environment Variables Required by resize.tcl ===
set ::env(TIELO_CELL_AND_PORT) "LOGIC0_X1 Z"    ;# Tie-low cells and ports (for Nangate45)​
set ::env(TIEHI_CELL_AND_PORT) "LOGIC1_X1 Z"    ;# Tie-high cells and ports (for Nangate45)​
# ​​Optional Environment Variables​
set ::env(DONT_BUFFER_PORTS) 0                  ;# 0=buffered I/O port, 1=unbuffered​
set ::env(TIE_SEPARATION) 5                     ;# Tie Cell Pitch (in grid units)​

# === Load the Floorplan Results​ ===
read_lef $TECH_LEF
read_lef $SC_LEF
read_liberty $LIB_FILES
read_db "./DCIM/results/floorplan/2_4_floorplan_pdn.odb" ;# Input the Final Floorplan Results​
read_sdc $SDC_FILE
read_liberty $SRAM_LIB
read_lef $SRAM_LEF

#=== Insert tie cells ===
puts "\n===== Insert Tie Cells ====="
insert_tiecells -prefix TIE LOGIC0_X1/Z
insert_tiecells -prefix TIE LOGIC1_X1/Z

# === Global Placement with I/O Exclusion​ ===
puts "\n===== Run Global Placement​ ====="
global_placement -skip_io -density 0.6 \
                 -pad_left $::env(CELL_PAD_IN_SITES_GLOBAL_PLACEMENT) \
                 -pad_right $::env(CELL_PAD_IN_SITES_GLOBAL_PLACEMENT)

write_db $RESULTS_DIR/3_1_place_gp_skip_io.odb
write_def $RESULTS_DIR/3_1_place_gp_skip_io.def

# === I/O Cell Placement ===
puts "\n===== ​​Place I/O Cells ====="
place_pins -hor_layers "metal5" -ver_layers "metal6"  -random -corner_avoidance 2 -min_distance 1
write_db $RESULTS_DIR/3_2_place_iop.odb
write_def $RESULTS_DIR/3_2_place_iop.def

# Load the Platform RC Tech File​
source ${PLATFORM_DIR}/setRC.tcl

# === Global Placement with I/Os ===
puts "\n===== Global Placement with I/Os ====="
global_placement -density 0.5 -timing_driven \
                 -pad_left $::env(CELL_PAD_IN_SITES_GLOBAL_PLACEMENT) \
                 -pad_right $::env(CELL_PAD_IN_SITES_GLOBAL_PLACEMENT) 
                
write_db $RESULTS_DIR/3_3_place_gp.odb
write_def $RESULTS_DIR/3_3_place_gp.def
# Repair Buffer Driving Capability
# repair_design -verbose

# === Timing Optimization with resize.tcl​ ===
puts "\n===== Timing Optimization with resize.tcl​ ====="
# Create the 2_floorplan.sdc file for resize.tcl​
write_sdc $RESULTS_DIR/2_floorplan.sdc
# ​​Run resize.tcl to repair std cell driving capability​
# WARNING: Comment out line 4 in the official resize.tcl script to avoid ODB reload errors!​
source $::env(SCRIPTS_DIR)/resize.tcl

# === ​​Additional Timing Repair ===
puts "\n===== Run ​​Additional Timing Repair ====="
estimate_parasitics -placement
repair_timing -setup_margin 0.3 

# === Detailed Placement Optimization​ ===
puts "\n===== Run Detailed Placement ====="
set_placement_padding -global \
                      -left $::env(CELL_PAD_IN_SITES_DETAIL_PLACEMENT) \
                      -right $::env(CELL_PAD_IN_SITES_DETAIL_PLACEMENT)
detailed_placement
optimize_mirroring

# === ​​Export the Results ===
write_db $RESULTS_DIR/3_5_place_dp.odb  ;# ​​Detailed Placement Results
write_sdc $RESULTS_DIR/3_5_place_dp.sdc
write_def $RESULTS_DIR/3_5_place_dp.def

# === Generate Report ===
report_units        ;# Report Unit Settings​
report_design_area  ;# Report Design Area​

# === Placement Legalization Check ===
puts "\n===== Placement Legalization Check ====="
check_placement -verbose

# === Report Timing Metrics​ ===
puts "\n===== Critical Path Timing Report​ ====="
report_checks -path_delay min_max -fields {slew cap input_pins} -format full_clock_expanded

puts "Placement for ${DESIGN_NAME} completed!"