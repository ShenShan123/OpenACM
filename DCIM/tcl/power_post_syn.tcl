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
read_vcd -scope testbench/dut ./DCIM/results/synth/power_syn.vcd
report_activity_annotation

# 5. Report Power
report_power
