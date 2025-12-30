# ----------------------------------------
# Set current design
# ----------------------------------------
current_design sram_multiplier_system

# ----------------------------------------
# Clock Definition
# ----------------------------------------
set clk_name core_clock
set clk_port_name clk
set clk_period 10.0     ;# Clock period: 10ns = 100MHz
set clk_io_pct 0.2      ;

set clk_port [get_ports $clk_port_name]
create_clock -name $clk_name -period $clk_period $clk_port
set_clock_uncertainty 0.1 [get_clocks $clk_name]

# ----------------------------------------
# Reset signal constraint
# ----------------------------------------
set reset_port [get_ports rst_n]

# ----------------------------------------
# Input delay constraints
# ----------------------------------------
set_input_delay 2.0 -clock $clk_name [get_ports data_in]
set_input_delay 2.0 -clock $clk_name [get_ports init_enable]
set_input_delay 2.0 -clock $clk_name [get_ports pe_ce]

# ----------------------------------------
# Output delay constraints
# ----------------------------------------
set_output_delay 2.0 -clock $clk_name [get_ports data_out]
set_output_delay 2.0 -clock $clk_name [get_ports valid_out]
set_output_delay 2.0 -clock $clk_name [get_ports init_done]

set_drive 1.0 [get_ports data_in]
set_load 0.5 [get_ports data_out]
set_load 0.5 [get_ports valid_out]
set_load 0.5 [get_ports init_done]
