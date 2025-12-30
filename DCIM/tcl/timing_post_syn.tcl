#File Name: timing_post_syn.tcl
# 1. Read the Technology Library​
read_liberty ./DCIM/nangate45/lib/NangateOpenCellLibrary_typical.lib
read_liberty ./DCIM/nangate45/lib/SRAM_6T_CORE_16x8_MC_TB.lib

# 2. Read the Design Netlist
read_verilog ./DCIM/results/synth/sram_sim_synth.v

# 3. Set the Top Module
link_design sram_multiplier_system
set_wire_load_mode top
set_wire_load_model -name "5K_hvratio_1_1" -library "NangateOpenCellLibrary"

# 4. Read the SDC Constraints​
read_sdc ./DCIM/tcl/constraint.sdc

# 5. Report Critical Path
report_checks
write_sdf ./DCIM/results/synth/sram_sim.sdf