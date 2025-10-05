script -c "
    make -f ./DCIM/sim_behavioral/Makefile com
    make -f ./DCIM/sim_behavioral/Makefile sim
    make -f ./DCIM/sim_behavioral/Makefile clean
" ./DCIM/results/log/Behavioral_Simulation.log

script -c "yosys ./DCIM/tcl/sram_yosys.ys" ./DCIM/results/log/yosys.log

script -c "opensta -exit ./DCIM/tcl/timing_post_syn.tcl" ./DCIM/results/log/timing_post_syn.log

script -c "
    make -f ./DCIM/sim_functional/Makefile com
    make -f ./DCIM/sim_functional/Makefile sim
    make -f ./DCIM/sim_functional/Makefile clean
" ./DCIM/results/log/Functional_Simulation.log

script -c "opensta -exit ./DCIM/tcl/power_post_syn.tcl" ./DCIM/results/log/power_post_syn.log


script -c "openroad -exit ./DCIM/tcl/floorplan.tcl" ./DCIM/results/log/floorplan.log
script -c "openroad -exit ./DCIM/tcl/placement.tcl" ./DCIM/results/log/placement.log
script -c "openroad -exit ./DCIM/tcl/cts.tcl" ./DCIM/results/log/cts.log
script -c "openroad -exit ./DCIM/tcl/route.tcl" ./DCIM/results/log/route.log

script -c "
    openroad -exit ./DCIM/tcl/ext_parasitics.tcl
    python ./DCIM/tcl/net_normalization.py
" ./DCIM/results/log/ext.log

script -c "opensta -exit ./DCIM/tcl/timing_post_rout.tcl" ./DCIM/results/log/timing_post_rout.log

script -c "
    make -f ./DCIM/sim_timing/Makefile com
    make -f ./DCIM/sim_timing/Makefile sim
    make -f ./DCIM/sim_timing/Makefile clean
" ./DCIM/results/log/Timing_Simulation.log

script -c "opensta -exit ./DCIM/tcl/power_post_rout.tcl" ./DCIM/results/log/power_post_rout.log