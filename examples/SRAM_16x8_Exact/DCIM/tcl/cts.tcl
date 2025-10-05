# ==================== Clock Tree Synthesis Script ====================
# Design Name and Technology Platform​
set DESIGN_NAME "sram_sim"    ;# Design Name
set ACTUAL_TOP_MODULE_NAME "sram_multiplier_system"
set PLATFORM "nangate45" ;# Technology Platform

# --- Path Configuration ---
set PLATFORM_DIR "./DCIM/nangate45"
set RESULTS_DIR "./DCIM/results/cts" ;
set SDC_FILE "./DCIM/results/placement/3_5_place_dp.sdc"
set SCRIPTS_DIR "./DCIM/scripts"
file mkdir $RESULTS_DIR

# === Technical Docs Configuration​ ===
set TECH_LEF "./DCIM/nangate45/lef/NangateOpenCellLibrary.tech.lef"
set SC_LEF "./DCIM/nangate45/lef/NangateOpenCellLibrary.macro.mod.lef"
set LIB_FILES "./DCIM/nangate45/lib/NangateOpenCellLibrary_typical.lib"
set SRAM_LEF "./DCIM/nangate45/lef/SRAM_6T_CORE_16x8_MC_TB.lef"
set SRAM_LIB "./DCIM/nangate45/lib/SRAM_6T_CORE_16x8_MC_TB.lib"

# === Environment Variables Configuration ===
set ::env(DONT_USE_CELLS) "TAPCELL_* FILLER_*"
set ::env(CELL_PAD_IN_SITES_DETAIL_PLACEMENT) 2
set ::env(CTS_CLUSTER_DIAMETER) 100  ;# Maximum Clock Sink Distance (µm)​
set ::env(CTS_BUF_DISTANCE) 50       ;# Buffer Spacing
set ::env(SETUP_SLACK_MARGIN) 0.1    ;# Timing Repair Parameters​
set ::env(HOLD_SLACK_MARGIN) 0.05    ;# Timing Repair Parameters​
set ::env(SCRIPTS_DIR) "./DCIM/scripts"
set ::env(REPORTS_DIR) "./DCIM/reports"

# === Load the Placement Result​ ===
read_lef $TECH_LEF
read_lef $SC_LEF
read_liberty $LIB_FILES
read_liberty $SRAM_LIB
read_lef $SRAM_LEF
read_db "./DCIM/results/placement/3_5_place_dp.odb"
read_sdc $SDC_FILE
# Load the Platform RC Tech File​
source ${PLATFORM_DIR}/setRC.tcl

# === Key Step 1: Repair Clock Inverters ===
puts "\n===== Repair Clock Inverters ====="
repair_clock_inverters

# === Key Step 2: Clock Tree Synthesis ===
puts "\n===== Run Clock Tree Synthesis ====="
clock_tree_synthesis -sink_clustering_enable \
                     -distance_between_buffers $::env(CTS_BUF_DISTANCE) \
                     -balance_levels; # Balance Clock Tree Levels​
# -sink_clustering_max_diameter $::env(CTS_CLUSTER_DIAMETER) 

# === Set Propagated Clocks​ ===
set_propagated_clock [all_clocks]

# === Key Step 3: Repair Clock Network​ ===
puts "\n===== Repair Clock Network ====="
repair_clock_nets

# === Placement Legalization ===
puts "\n===== Run Placement Legalization ====="
set_placement_padding -global \
                      -left $::env(CELL_PAD_IN_SITES_DETAIL_PLACEMENT) \
                      -right $::env(CELL_PAD_IN_SITES_DETAIL_PLACEMENT)
# Phased Detailed Placement​
detailed_placement 

# === Parasitic Estimation​ ===
estimate_parasitics -placement

# === Timing Repair​ ===
puts "\n===== Timing Repair​ ====="
source "$SCRIPTS_DIR/util.tcl"
repair_timing_helper

# === Post-Timing-Repair Detailed Placement​ ===
puts "\n===== Post-Timing-Repair Detailed Placement ====="
detailed_placement

# === ​​Save Results​ ===
write_db $RESULTS_DIR/4_1_cts.odb
write_sdc $RESULTS_DIR/4_cts.sdc
#write_cdl -masters "$SC_LEF $TECH_LEF $SRAM_LEF" $RESULTS_DIR/4_cts.cdl
# === Generate Report​ ===
puts "\n===== Clock Tree Quality Report​ ====="
report_checks -path_delay min_max -fields {slew cap input_pins}  ;# ​​Timing Check​

puts "\n===== Placement Legalization Check ====="
check_placement -verbose

puts "Clock Tree Synthesis for ${DESIGN_NAME} completed!"

report_design_area