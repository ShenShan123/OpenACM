#File Name: floorplan.tcl
# Design Name and Technology Platform​
set DESIGN_NAME "sram_sim"    ;# Design Name
set ACTUAL_TOP_MODULE_NAME "sram_multiplier_system"
set PLATFORM "nangate45" ;# Technology Platform​

# --- Path Configuration ---
set PLATFORM_DIR "./DCIM/nangate45"
set SYNTH_VERILOG_FILE "./DCIM/results/synth/sram_sim_synth.v"
set SDC_FILE "./DCIM/tcl/constraint.sdc"
set RESULTS_DIR "./DCIM/results/floorplan"
file mkdir $RESULTS_DIR

# === Technical Docs Configuration ===
set TECH_LEF "./DCIM/nangate45/lef/NangateOpenCellLibrary.tech.lef"
set SC_LEF "./DCIM/nangate45/lef/NangateOpenCellLibrary.macro.mod.lef"
set SRAM_LEF "./DCIM/nangate45/lef/SRAM_6T_CORE_32x16_MC_TB.lef"
set SRAM_LIB "./DCIM/nangate45/lib/SRAM_6T_CORE_32x16_MC_TB.lib"
set LIB_FILES "./DCIM/nangate45/lib/NangateOpenCellLibrary_typical.lib"
set SITE_NAME   "FreePDK45_38x28_10R_NP_162NW_34O"
set ::env(TAP_CELL_NAME) "TAPCELL_X1"

# === Design Initialization ===
read_lef $TECH_LEF
read_lef $SC_LEF
read_lef $SRAM_LEF
read_liberty $LIB_FILES
read_liberty $SRAM_LIB

# Load the Netlist and Constraints​
read_verilog $SYNTH_VERILOG_FILE
link_design $ACTUAL_TOP_MODULE_NAME
read_sdc $SDC_FILE

# ======================== 2_1_floorplan.tcl =========================
# Floorplan Initialization Phase​
# ​​Dependencies: 1_synth.v, 1_synth.sdc, LEF files, etc.​
# Generate​: 2_1_floorplan.odb, 2_1_floorplan.sdc

# === Floorplan Initialization ===
puts "=== Floorplan Initialization ==="
initialize_floorplan \
  -utilization 50 \
  -aspect_ratio 1.0 \
  -core_space 5.0 \
  -site $SITE_NAME 


# Generate Power Rails​
source $PLATFORM_DIR/make_tracks.tcl
# ​​Export the Phase-Specific Results​
write_db $RESULTS_DIR/2_1_floorplan.odb
write_sdc $RESULTS_DIR/2_1_floorplan.sdc
write_def $RESULTS_DIR/2_1_floorplan.def

# ======================== 2_2_floorplan_macro.tcl ====================

puts "=== Macro Placement Phase​ ==="

place_macro -macro_name sram_inst -location {40 25} -orient N

# ​​Export the Results
write_db $RESULTS_DIR/2_2_floorplan_macro.odb
write_def $RESULTS_DIR/2_2_floorplan_macro.def
# ======================== 2_3_floorplan_tapcell.tcl =================
# Tapcell Insertion Phase
# Insert Tapcells (reading the cell name from an environment variable)​
# insert_tapcell \
#   -tapcell_master $::env(TAP_CELL_NAME) \
#   -distance 20
puts "=== Tapcell Insertion Phase ==="
source ${PLATFORM_DIR}/tapcell.tcl
# ​​Export the Results
write_db $RESULTS_DIR/2_3_floorplan_tapcell.odb
write_def $RESULTS_DIR/2_3_floorplan_tapcell.def

# ======================== 2_4_floorplan_pdn.tcl =====================
# ​PDN Generation Phase
# ​Dependencies：2_3_floorplan_tapcell.odb
# Generate：2_4_floorplan_pdn.odb
puts "=== ​PDN Generation Phase ==="
# === Power Network Configuration​ ===
source ${PLATFORM_DIR}/grid_strategy-M1-M4-M7.tcl
pdngen

# Check all supply nets
set block [ord::get_db_block]
foreach net [$block getNets] {
    set type [$net getSigType]
}

# === ​​Export the Results ===
write_db $RESULTS_DIR/2_4_floorplan_pdn.odb
write_sdc $RESULTS_DIR/2_4_floorplan_pdn.sdc
write_def $RESULTS_DIR/2_4_floorplan_pdn.def

# === Generate Report​ ===
report_design_area
report_design_area_metrics
puts "Floorplan completed for ${DESIGN_NAME}"
