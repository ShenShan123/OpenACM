###############################################################################
# Created by write_sdc
# Wed Oct  1 12:10:14 2025
###############################################################################
current_design sram_multiplier_system
###############################################################################
# Timing Constraints
###############################################################################
create_clock -name core_clock -period 10.0000 [get_ports {clk}]
set_clock_uncertainty 0.1000 core_clock
set_propagated_clock [get_clocks {core_clock}]
set_input_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_in[0]}]
set_input_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_in[1]}]
set_input_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_in[2]}]
set_input_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_in[3]}]
set_input_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_in[4]}]
set_input_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_in[5]}]
set_input_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_in[6]}]
set_input_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_in[7]}]
set_input_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {init_enable}]
set_input_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {pe_ce}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[0]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[10]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[11]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[12]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[13]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[14]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[15]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[1]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[2]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[3]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[4]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[5]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[6]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[7]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[8]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {data_out[9]}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {init_done}]
set_output_delay 2.0000 -clock [get_clocks {core_clock}] -add_delay [get_ports {valid_out}]
###############################################################################
# Environment
###############################################################################
set_load -pin_load 0.5000 [get_ports {init_done}]
set_load -pin_load 0.5000 [get_ports {valid_out}]
set_load -pin_load 0.5000 [get_ports {data_out[15]}]
set_load -pin_load 0.5000 [get_ports {data_out[14]}]
set_load -pin_load 0.5000 [get_ports {data_out[13]}]
set_load -pin_load 0.5000 [get_ports {data_out[12]}]
set_load -pin_load 0.5000 [get_ports {data_out[11]}]
set_load -pin_load 0.5000 [get_ports {data_out[10]}]
set_load -pin_load 0.5000 [get_ports {data_out[9]}]
set_load -pin_load 0.5000 [get_ports {data_out[8]}]
set_load -pin_load 0.5000 [get_ports {data_out[7]}]
set_load -pin_load 0.5000 [get_ports {data_out[6]}]
set_load -pin_load 0.5000 [get_ports {data_out[5]}]
set_load -pin_load 0.5000 [get_ports {data_out[4]}]
set_load -pin_load 0.5000 [get_ports {data_out[3]}]
set_load -pin_load 0.5000 [get_ports {data_out[2]}]
set_load -pin_load 0.5000 [get_ports {data_out[1]}]
set_load -pin_load 0.5000 [get_ports {data_out[0]}]
set_drive -rise 1.0000 [get_ports {data_in[7]}]
set_drive -fall 1.0000 [get_ports {data_in[7]}]
set_drive -rise 1.0000 [get_ports {data_in[6]}]
set_drive -fall 1.0000 [get_ports {data_in[6]}]
set_drive -rise 1.0000 [get_ports {data_in[5]}]
set_drive -fall 1.0000 [get_ports {data_in[5]}]
set_drive -rise 1.0000 [get_ports {data_in[4]}]
set_drive -fall 1.0000 [get_ports {data_in[4]}]
set_drive -rise 1.0000 [get_ports {data_in[3]}]
set_drive -fall 1.0000 [get_ports {data_in[3]}]
set_drive -rise 1.0000 [get_ports {data_in[2]}]
set_drive -fall 1.0000 [get_ports {data_in[2]}]
set_drive -rise 1.0000 [get_ports {data_in[1]}]
set_drive -fall 1.0000 [get_ports {data_in[1]}]
set_drive -rise 1.0000 [get_ports {data_in[0]}]
set_drive -fall 1.0000 [get_ports {data_in[0]}]
###############################################################################
# Design Rules
###############################################################################
