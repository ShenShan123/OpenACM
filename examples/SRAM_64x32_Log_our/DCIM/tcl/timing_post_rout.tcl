# 1. Read the Technology Library​
read_liberty ./DCIM/nangate45/lib/NangateOpenCellLibrary_typical.lib
read_liberty ./DCIM/nangate45/lib/SRAM_6T_CORE_64x32_MC_TB.lib

# 2. Read the Design Netlist
read_verilog ./DCIM/results/net_normalization/netlist_cleaned.v

# 3. Set the Top Module

link_design sram_multiplier_system

# 4. Read the SDC Constraints​
read_sdc ./DCIM/tcl/constraint.sdc
read_spef ./DCIM/results/net_normalization/spef_cleaned.spef

# 5. Report Critical Path
report_checks
write_sdf ./DCIM/results/routing/timing_rout.sdf