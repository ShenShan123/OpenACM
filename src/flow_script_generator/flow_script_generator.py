import re

def modify_tcl(design_name="sram_sim", top_model_name="sram_multiplier_system",
               platform="nangate45", platform_dir="./DCIM/nangate45",
               lib="./DCIM/nangate45/lib/NangateOpenCellLibrary.lib",
               lib_typical="./DCIM/nangate45/lib/NangateOpenCellLibrary_typical.lib",
               v="./DCIM/nangate45/NangateOpenCellLibrary.v",
               tech_lef="./DCIM/nangate45/lef/NangateOpenCellLibrary.tech.lef", sc_lef="./DCIM/nangate45/lef/NangateOpenCellLibrary.macro.mod.lef",
               sram_lef="./DCIM/nangate45/lef/SRAM_6T_CORE_16x8_MC_TB.lef", sram_lib="./DCIM/nangate45/lib/SRAM_6T_CORE_16x8_MC_TB.lib",
               rcx_rules="./DCIM/nangate45/rcx_patterns.rules",
               rtl_dir="./DCIM/rtl", multiplier_dir="./DCIM/multiplier",
               sdc_file="./DCIM/tcl/constraint.sdc", result_dir="./DCIM/results",
               scripts_dir="./DCIM/scripts", reports_dir="./DCIM/reports",
               location_x=30, location_y=15):

    # yosys

    with open("./DCIM/tcl/sram_yosys.ys", 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    lib_positions = []

    for i, line in enumerate(lines):
        if re.match(r'^\s*read_liberty\s+', line):
            lib_positions.append(i)  
        elif re.match(r'^\s*read_verilog\s+', line):
            lib_positions.append(i)
        else:
            new_lines.append(line)

    new_lines.insert(lib_positions[0], f'read_liberty -lib {lib}\n')
    new_lines.insert(lib_positions[1], f'read_liberty -lib {sram_lib}\n')
    new_lines.insert(lib_positions[2], f'read_verilog {result_dir}/synth/sram_syn.v\n')
    new_lines.insert(lib_positions[3], f'read_verilog {rtl_dir}/sram_control.v\n')
    new_lines.insert(lib_positions[4], f'read_verilog {multiplier_dir}/Exact_8bit.v\n')

    with open("./DCIM/tcl/sram_yosys.ys", 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    with open("./DCIM/tcl/sram_yosys.ys", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(hierarchy\s+-top\s+)\w+', f'\\1{top_model_name}'),
        (r'(synth\s+-top\s+)\w+', f'\\1{top_model_name}'),
        (r'(write_verilog\s+-noattr\s+-selected\s+).*', f'\\1{result_dir}/synth/{design_name}_synth.v'),

        (r'(dfflibmap\s+-liberty\s+).*', f'\\1{lib_typical}'),
        (r'(abc\s+-liberty\s+).*', f'\\1{lib_typical}'),
        (r'(stat\s+-liberty\s+).*', f'\\1{lib_typical}')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/sram_yosys.ys", 'w', encoding='utf-8') as f:
        f.write(content)

    # timing_post_syn

    with open("./DCIM/tcl/timing_post_syn.tcl", 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    lib_positions = []

    for i, line in enumerate(lines):
        if re.match(r'^\s*read_liberty\s+', line):
            lib_positions.append(i)  
        else:
            new_lines.append(line)

    new_lines.insert(lib_positions[0], f'read_liberty {lib_typical}\n')
    new_lines.insert(lib_positions[1], f'read_liberty {sram_lib}\n')

    with open("./DCIM/tcl/timing_post_syn.tcl", 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    with open("./DCIM/tcl/timing_post_syn.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(read_verilog\s+).*', f'read_verilog {result_dir}/synth/{design_name}_synth.v'),
        (r'link_design\s+\w+', f'link_design {top_model_name}'),
        (r'(read_sdc\s+).*', f'read_sdc {sdc_file}'),
        (r'(write_sdf\s+).*', f'write_sdf {result_dir}/synth/sram_sim.sdf')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/timing_post_syn.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    # power_post_syn

    with open("./DCIM/tcl/power_post_syn.tcl", 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    lib_positions = []

    for i, line in enumerate(lines):
        if re.match(r'^\s*read_liberty\s+', line):
            lib_positions.append(i)  
        else:
            new_lines.append(line)

    new_lines.insert(lib_positions[0], f'read_liberty {lib_typical}\n')
    new_lines.insert(lib_positions[1], f'read_liberty {sram_lib}\n')

    with open("./DCIM/tcl/power_post_syn.tcl", 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    with open("./DCIM/tcl/power_post_syn.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(read_verilog\s+).*', f'read_verilog {result_dir}/synth/{design_name}_synth.v'),
        (r'link_design\s+\w+', f'link_design {top_model_name}'),
        (r'(read_sdc\s+).*', f'read_sdc {sdc_file}'),

        (r'(read_vcd\s+-scope\s+testbench/dut\s+).*?\.vcd', f'\\1{result_dir}/synth/power_syn.vcd')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/power_post_syn.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #floorplan

    with open("./DCIM/tcl/floorplan.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'set\s+DESIGN_NAME\s+".*"', f'set DESIGN_NAME "{design_name}"'),
        (r'set\s+ACTUAL_TOP_MODULE_NAME\s+".*"', f'set ACTUAL_TOP_MODULE_NAME "{top_model_name}"'),
        (r'set\s+PLATFORM\s+".*"', f'set PLATFORM "{platform}"'),

        (r'set\s+PLATFORM_DIR\s+".*"', f'set PLATFORM_DIR "{platform_dir}"'),
        (r'set\s+SYNTH_VERILOG_FILE\s+".*"', f'set SYNTH_VERILOG_FILE "{result_dir}/synth/{design_name}_synth.v"'),
        (r'set\s+SDC_FILE\s+".*"', f'set SDC_FILE "{sdc_file}"'),
        (r'set\s+RESULTS_DIR\s+".*"', f'set RESULTS_DIR "{result_dir}/floorplan"'),

        (r'set\s+TECH_LEF\s+".*"', f'set TECH_LEF "{tech_lef}"'),
        (r'set\s+SC_LEF\s+".*"', f'set SC_LEF "{sc_lef}"'),
        (r'set\s+LIB_FILES\s+".*"', f'set LIB_FILES "{lib_typical}"'),
        (r'set\s+SRAM_LEF\s+".*"', f'set SRAM_LEF "{sram_lef}"'),
        (r'set\s+SRAM_LIB\s+".*"', f'set SRAM_LIB "{sram_lib}"'),

        (r'place_macro -macro_name (\w+) -location {(\d+) (\d+)} -orient (\w+)', f'place_macro -macro_name \\1 -location {{{location_x} {location_y}}} -orient \\4')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/floorplan.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #placement

    with open("./DCIM/tcl/placement.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'set\s+DESIGN_NAME\s+".*"', f'set DESIGN_NAME "{design_name}"'),
        (r'set\s+ACTUAL_TOP_MODULE_NAME\s+".*"', f'set ACTUAL_TOP_MODULE_NAME "{top_model_name}"'),
        (r'set\s+PLATFORM\s+".*"', f'set PLATFORM "{platform}"'),

        (r'set\s+PLATFORM_DIR\s+".*"', f'set PLATFORM_DIR "{platform_dir}"'),
        (r'set\s+SDC_FILE\s+".*"', f'set SDC_FILE "{result_dir}/floorplan/2_4_floorplan_pdn.sdc"'),
        (r'set\s+RESULTS_DIR\s+".*"', f'set RESULTS_DIR "{result_dir}/placement"'),

        (r'set\s+::env\(SCRIPTS_DIR\)\s+".*"', f'set ::env(SCRIPTS_DIR) "{scripts_dir}"'),
        (r'set\s+::env\(REPORTS_DIR\)\s+".*"', f'set ::env(REPORTS_DIR) "{reports_dir}"'),

        (r'read_db\s+".*"', f'read_db "{result_dir}/floorplan/2_4_floorplan_pdn.odb"'),

        (r'set\s+TECH_LEF\s+".*"', f'set TECH_LEF "{tech_lef}"'),
        (r'set\s+SC_LEF\s+".*"', f'set SC_LEF "{sc_lef}"'),
        (r'set\s+LIB_FILES\s+".*"', f'set LIB_FILES "{lib_typical}"'),
        (r'set\s+SRAM_LEF\s+".*"', f'set SRAM_LEF "{sram_lef}"'),
        (r'set\s+SRAM_LIB\s+".*"', f'set SRAM_LIB "{sram_lib}"')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/placement.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #CTS

    with open("./DCIM/tcl/cts.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'set\s+DESIGN_NAME\s+".*"', f'set DESIGN_NAME "{design_name}"'),
        (r'set\s+ACTUAL_TOP_MODULE_NAME\s+".*"', f'set ACTUAL_TOP_MODULE_NAME "{top_model_name}"'),
        (r'set\s+PLATFORM\s+".*"', f'set PLATFORM "{platform}"'),

        (r'set\s+PLATFORM_DIR\s+".*"', f'set PLATFORM_DIR "{platform_dir}"'),
        (r'set\s+SDC_FILE\s+".*"', f'set SDC_FILE "{result_dir}/placement/3_5_place_dp.sdc"'),
        (r'set\s+RESULTS_DIR\s+".*"', f'set RESULTS_DIR "{result_dir}/cts"'),
        (r'set\s+SCRIPTS_DIR\s+".*"', f'set SCRIPTS_DIR "{scripts_dir}"'),

        (r'set\s+::env\(SCRIPTS_DIR\)\s+".*"', f'set ::env(SCRIPTS_DIR) "{scripts_dir}"'),
        (r'set\s+::env\(REPORTS_DIR\)\s+".*"', f'set ::env(REPORTS_DIR) "{reports_dir}"'),

        (r'read_db\s+".*"', f'read_db "{result_dir}/placement/3_5_place_dp.odb"'),

        (r'set\s+TECH_LEF\s+".*"', f'set TECH_LEF "{tech_lef}"'),
        (r'set\s+SC_LEF\s+".*"', f'set SC_LEF "{sc_lef}"'),
        (r'set\s+LIB_FILES\s+".*"', f'set LIB_FILES "{lib_typical}"'),
        (r'set\s+SRAM_LEF\s+".*"', f'set SRAM_LEF "{sram_lef}"'),
        (r'set\s+SRAM_LIB\s+".*"', f'set SRAM_LIB "{sram_lib}"')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/cts.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #route

    with open("./DCIM/tcl/route.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'set\s+DESIGN_NAME\s+".*"', f'set DESIGN_NAME "{design_name}"'),
        (r'set\s+ACTUAL_TOP_MODULE_NAME\s+".*"', f'set ACTUAL_TOP_MODULE_NAME "{top_model_name}"'),
        (r'set\s+PLATFORM\s+".*"', f'set PLATFORM "{platform}"'),

        (r'set\s+PLATFORM_DIR\s+".*"', f'set PLATFORM_DIR "{platform_dir}"'),
        (r'set\s+SDC_FILE\s+".*"', f'set SDC_FILE "{result_dir}/cts/4_cts.sdc"'),
        (r'set\s+RESULTS_DIR\s+".*"', f'set RESULTS_DIR "{result_dir}/routing"'),

        (r'set\s+::env\(SCRIPTS_DIR\)\s+".*"', f'set ::env(SCRIPTS_DIR) "{scripts_dir}"'),
        (r'set\s+::env\(REPORTS_DIR\)\s+".*"', f'set ::env(REPORTS_DIR) "{reports_dir}"'),

        (r'read_db\s+".*"', f'read_db "{result_dir}/cts/4_1_cts.odb"'),

        (r'set\s+TECH_LEF\s+".*"', f'set TECH_LEF "{tech_lef}"'),
        (r'set\s+SC_LEF\s+".*"', f'set SC_LEF "{sc_lef}"'),
        (r'set\s+LIB_FILES\s+".*"', f'set LIB_FILES "{lib_typical}"'),
        (r'set\s+SRAM_LEF\s+".*"', f'set SRAM_LEF "{sram_lef}"'),
        (r'set\s+SRAM_LIB\s+".*"', f'set SRAM_LIB "{sram_lib}"')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/route.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #ext

    with open("./DCIM/tcl/ext_parasitics.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'set\s+DESIGN_NAME\s+".*"', f'set DESIGN_NAME "{design_name}"'),
        (r'set\s+PLATFORM\s+".*"', f'set PLATFORM "{platform}"'),
        (r'set\s+PLATFORM_DIR\s+".*"', f'set PLATFORM_DIR "{platform_dir}"'),

        (r'set\s+DEF_FILE\s+".*"', f'set DEF_FILE "{result_dir}/routing/5_3_fillcell.def"'),
        (r'set\s+OUTPUT_SPEF\s+".*"', f'set OUTPUT_SPEF "{result_dir}/routing/5_3_parasitic.spef"'),

        (r'set\s+MACRO_LEF\s+".*"', f'set MACRO_LEF "{sram_lef}"'),
        (r'set\s+LIB_FILE\s+".*"', f'set LIB_FILE "{lib_typical}"'),
        (r'set\s+RCX_RULES\s+".*"', f'set RCX_RULES "{rcx_rules}"')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/ext_parasitics.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #net_normalization

    with open("./DCIM/tcl/net_normalization.py", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'verilog_in\s*=\s*\'.*?\'', f"verilog_in = '{result_dir}/routing/5_3_fillcell.v'"),
        (r'verilog_out\s*=\s*\'.*?\'', f"verilog_out = '{result_dir}/net_normalization/netlist_cleaned.v'"),
        (r'spef_in\s*=\s*\'.*?\'', f"spef_in = '{result_dir}/routing/5_3_parasitic.spef'"),
        (r'spef_out\s*=\s*\'.*?\'', f"spef_out = '{result_dir}/net_normalization/spef_cleaned.spef'")
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/net_normalization.py", 'w', encoding='utf-8') as f:
        f.write(content)

    #timing_post_rout

    with open("./DCIM/tcl/timing_post_rout.tcl", 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    lib_positions = []

    for i, line in enumerate(lines):
        if re.match(r'^\s*read_liberty\s+', line):
            lib_positions.append(i)  
        else:
            new_lines.append(line)

    new_lines.insert(lib_positions[0], f'read_liberty {lib_typical}\n')
    new_lines.insert(lib_positions[1], f'read_liberty {sram_lib}\n')

    with open("./DCIM/tcl/timing_post_rout.tcl", 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    with open("./DCIM/tcl/timing_post_rout.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(read_verilog\s+).*', f'read_verilog {result_dir}/net_normalization/netlist_cleaned.v'),
        (r'link_design\s+\w+', f'link_design {top_model_name}'),
        (r'(read_sdc\s+).*', f'read_sdc {sdc_file}'),
        (r'(read_spef\s+).*', f'read_spef {result_dir}/net_normalization/spef_cleaned.spef'),
        (r'(write_sdf\s+).*', f'write_sdf {result_dir}/routing/timing_rout.sdf')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/timing_post_rout.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #power_post_rout

    with open("./DCIM/tcl/power_post_rout.tcl", 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    lib_positions = []

    for i, line in enumerate(lines):
        if re.match(r'^\s*read_liberty\s+', line):
            lib_positions.append(i)  
        else:
            new_lines.append(line)

    new_lines.insert(lib_positions[0], f'read_liberty {lib_typical}\n')
    new_lines.insert(lib_positions[1], f'read_liberty {sram_lib}\n')

    with open("./DCIM/tcl/power_post_rout.tcl", 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    with open("./DCIM/tcl/power_post_rout.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(read_verilog\s+).*', f'read_verilog {result_dir}/net_normalization/netlist_cleaned.v'),
        (r'link_design\s+\w+', f'link_design {top_model_name}'),
        (r'(read_sdc\s+).*', f'read_sdc {sdc_file}'),
        (r'(read_spef\s+).*', f'read_spef {result_dir}/net_normalization/spef_cleaned.spef'),

        (r'(read_vcd\s+-scope\s+testbench/dut\s+).*?\.vcd', f'\\1{result_dir}/routing/power_rout.vcd')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/power_post_rout.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #Testbench_Behavioral

    with open("./DCIM/sim_behavioral/Testbench_Behavioral.v", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'\$dumpfile\(".*"\)', f'$dumpfile("{result_dir}/synth/power_rout.vcd")')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/sim_behavioral/Testbench_Behavioral.v", 'w', encoding='utf-8') as f:
        f.write(content)

    new_contents = [
        "-timescale=1ns/1ps",
        "./DCIM/sim_behavioral/pthread_yield_fix.o",
        f"{rtl_dir}/sram.v",
        f"{rtl_dir}/sram_control.v",
        f"{multiplier_dir}/Exact_8bit.v",
        "./DCIM/sim_behavioral/Testbench_Behavioral.v"
    ]

    with open("./DCIM/sim_behavioral/file_list.f", 'w') as f:
        for line in new_contents:
            f.write(line + '\n')

    with open("./DCIM/sim_behavioral/Makefile", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(LIB_FILE\s*=\s*).*', f'LIB_FILE = {v}')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/sim_behavioral/Makefile", 'w', encoding='utf-8') as f:
        f.write(content)

    #Testbench_Functional

    with open("./DCIM/sim_functional/Testbench_Functional.v", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(\$sdf_annotate\(")[^"]+(",\s*dut,,,\s*"MAXIMUM",\s*"1:1:1",\s*"FROM_MTM"\))', f'\\1{result_dir}/synth/sram_sim.sdf\\2'),
        (r'\$dumpfile\(".*"\)', f'$dumpfile("{result_dir}/synth/power_syn.vcd")')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/sim_functional/Testbench_Functional.v", 'w', encoding='utf-8') as f:
        f.write(content)

    new_contents = [
        "-timescale=1ns/1ps",
        "./DCIM/sim_functional/pthread_yield_fix.o",
        f"{result_dir}/synth/{design_name}_synth.v",
        f"{rtl_dir}/sram.v",
        f"{rtl_dir}/cell.v",
        "./DCIM/sim_functional/Testbench_Functional.v"
    ]

    with open("./DCIM/sim_functional/file_list.f", 'w') as f:
        for line in new_contents:
            f.write(line + '\n')

    with open("./DCIM/sim_functional/Makefile", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(LIB_FILE\s*=\s*).*', f'LIB_FILE = {v}')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/sim_functional/Makefile", 'w', encoding='utf-8') as f:
        f.write(content)

    #Testbench_Timing

    with open("./DCIM/sim_timing/Testbench_Timing.v", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(\$sdf_annotate\(")[^"]+(",\s*dut,,,\s*"MAXIMUM",\s*"1:1:1",\s*"FROM_MTM"\))', f'\\1{result_dir}/routing/timing_rout.sdf\\2'),
        (r'\$dumpfile\(".*"\)', f'$dumpfile("{result_dir}/routing/power_rout.vcd")')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/sim_timing/Testbench_Timing.v", 'w', encoding='utf-8') as f:
        f.write(content)

    new_contents = [
        "-timescale=1ns/1ps",
        "./DCIM/sim_timing/pthread_yield_fix.o",
        f"{result_dir}/net_normalization/netlist_cleaned.v",
        f"{rtl_dir}/sram.v",
        f"{rtl_dir}/cell.v",
        "./DCIM/sim_timing/Testbench_Timing.v"
    ]

    with open("./DCIM/sim_timing/file_list.f", 'w') as f:
        for line in new_contents:
            f.write(line + '\n')
    
    with open("./DCIM/sim_timing/Makefile", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(LIB_FILE\s*=\s*).*', f'LIB_FILE = {v}')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/sim_timing/Makefile", 'w', encoding='utf-8') as f:
        f.write(content)

    #eda.sh

    with open(f"./DCIM/tcl/eda.sh", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(script -c\s+"[^"]+"\s+)(.*?)(/log\b)', f'\\1{result_dir}\\3')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open(f"./DCIM/tcl/eda.sh", 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--design_name", default="sram_sim")
    parser.add_argument("--top_model", default="sram_multiplier_system")
    parser.add_argument("--platform", default="nangate45")
    parser.add_argument("--platform_dir", default="./DCIM/nangate45")
    parser.add_argument("--lib", default="./DCIM/nangate45/lib/NangateOpenCellLibrary.lib")
    parser.add_argument("--lib_typical", default="./DCIM/nangate45/lib/NangateOpenCellLibrary_typical.lib")
    parser.add_argument("--v", default="./DCIM/nangate45/NangateOpenCellLibrary.v")
    parser.add_argument("--tech_lef", default="./DCIM/nangate45/lef/NangateOpenCellLibrary.tech.lef")
    parser.add_argument("--sc_lef", default="./DCIM/nangate45/lef/NangateOpenCellLibrary.macro.mod.lef")
    parser.add_argument("--sram_lef", default="./DCIM/nangate45/lef/SRAM_6T_CORE_16x8_MC_TB.lef")
    parser.add_argument("--sram_lib", default="./DCIM/nangate45/lib/SRAM_6T_CORE_16x8_MC_TB.lib")
    parser.add_argument("--rcx_rules", default="./DCIM/nangate45/rcx_patterns.rules")
    parser.add_argument("--rtl_dir", default="./DCIM/rtl")
    parser.add_argument("--multiplier_dir", default="./DCIM/multiplier")
    parser.add_argument("--sdc_file", default="./DCIM/tcl/constraint.sdc")
    parser.add_argument("--result_dir", default="./DCIM/results")
    parser.add_argument("--scripts_dir", default="./DCIM/scripts")
    parser.add_argument("--reports_dir", default="./DCIM/reports")
    parser.add_argument("--location_x", default="30")
    parser.add_argument("--location_y", default="15")

    args = parser.parse_args()

    modify_tcl(
        design_name=args.design_name,
        top_model_name=args.top_model,
        platform=args.platform,
        platform_dir=args.platform_dir,
        lib=args.lib,
        lib_typical=args.lib_typical,
        v=args.v,
        tech_lef=args.tech_lef,
        sc_lef=args.sc_lef,
        sram_lef=args.sram_lef,
        sram_lib=args.sram_lib,
        rcx_rules=args.rcx_rules,
        rtl_dir=args.rtl_dir,
        multiplier_dir=args.multiplier_dir,
        sdc_file=args.sdc_file,
        result_dir=args.result_dir,
        scripts_dir=args.scripts_dir,
        reports_dir=args.reports_dir,
        location_x=int(args.location_x),
        location_y=int(args.location_y)
    )