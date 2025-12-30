import re

def modify_width(data_width=8, addr_count=16, multiplier_module="Exact", rtl_dir="./DCIM/rtl"):

    addr_width = (addr_count - 1).bit_length()
    mult_width = data_width * 2

    #sram_control

    with open(f"{rtl_dir}/sram_control.v", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'parameter\s+DATA_WIDTH\s*=\s*\d+;', f'parameter DATA_WIDTH = {data_width};'),
        (r'parameter\s+ADDR_COUNT\s*=\s*\d+;', f'parameter ADDR_COUNT = {addr_count};'),
        (r'parameter\s+ADDR_WIDTH\s*=\s*\d+;', f'parameter ADDR_WIDTH = {addr_width};'),
        (r'parameter\s+MULT_WIDTH\s*=\s*\d+;', f'parameter MULT_WIDTH = {mult_width};'),

        (r'(input\s*)\[\d+:\d+\](\s*data_in,)', f'\\1[{data_width - 1}:0]\\2'),
        (r'(output\s+reg\s*)\[\d+:\d+\](\s*data_out\s*,?)', f'\\1[{mult_width - 1}:0]\\2'),

        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB'),
        (r'(\w+)\s+u_multiplier', f'{multiplier_module}_{data_width}bit u_multiplier')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open(f"{rtl_dir}/sram_control.v", 'w', encoding='utf-8') as f:
        f.write(content)

    # yosys

    with open("./DCIM/tcl/sram_yosys.ys", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB'),
        (r'(\w+)_(\d+)bit\.v', f'{multiplier_module}_{data_width}bit.v')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/sram_yosys.ys", 'w', encoding='utf-8') as f:
        f.write(content)

    # timing_post_syn

    with open("./DCIM/tcl/timing_post_syn.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/timing_post_syn.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    # power_post_syn

    with open("./DCIM/tcl/power_post_syn.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/power_post_syn.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #floorplan

    with open("./DCIM/tcl/floorplan.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/floorplan.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #placement

    with open("./DCIM/tcl/placement.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/placement.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #CTS

    with open("./DCIM/tcl/cts.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/cts.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #route

    with open("./DCIM/tcl/route.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/route.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #ext

    with open("./DCIM/tcl/ext_parasitics.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/ext_parasitics.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #timing_post_rout

    with open("./DCIM/tcl/timing_post_rout.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/timing_post_rout.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #power_post_rout

    with open("./DCIM/tcl/power_post_rout.tcl", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/tcl/power_post_rout.tcl", 'w', encoding='utf-8') as f:
        f.write(content)

    #Testbench_Behavioral

    with open("./DCIM/sim_behavioral/Testbench_Behavioral.v", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'parameter\s+DATA_WIDTH\s*=\s*\d+;', f'parameter DATA_WIDTH = {data_width};'),
        (r'parameter\s+ADDR_COUNT\s*=\s*\d+;', f'parameter ADDR_COUNT = {addr_count};'),
        (r'parameter\s+ADDR_WIDTH\s*=\s*\d+;', f'parameter ADDR_WIDTH = {addr_width};'),
        (r'parameter\s+MULT_WIDTH\s*=\s*\d+;', f'parameter MULT_WIDTH = {mult_width};')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/sim_behavioral/Testbench_Behavioral.v", 'w', encoding='utf-8') as f:
        f.write(content)

    with open("./DCIM/sim_behavioral/file_list.f", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'(\w+)_(\d+)bit\.v', f'{multiplier_module}_{data_width}bit.v')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/sim_behavioral/file_list.f", 'w', encoding='utf-8') as f:
        f.write(content)

    #Testbench_Functional

    with open("./DCIM/sim_functional/Testbench_Functional.v", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'parameter\s+DATA_WIDTH\s*=\s*\d+;', f'parameter DATA_WIDTH = {data_width};'),
        (r'parameter\s+ADDR_COUNT\s*=\s*\d+;', f'parameter ADDR_COUNT = {addr_count};'),
        (r'parameter\s+ADDR_WIDTH\s*=\s*\d+;', f'parameter ADDR_WIDTH = {addr_width};'),
        (r'parameter\s+MULT_WIDTH\s*=\s*\d+;', f'parameter MULT_WIDTH = {mult_width};')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/sim_functional/Testbench_Functional.v", 'w', encoding='utf-8') as f:
        f.write(content)

    #Testbench_Timing

    with open("./DCIM/sim_timing/Testbench_Timing.v", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'parameter\s+DATA_WIDTH\s*=\s*\d+;', f'parameter DATA_WIDTH = {data_width};'),
        (r'parameter\s+ADDR_COUNT\s*=\s*\d+;', f'parameter ADDR_COUNT = {addr_count};'),
        (r'parameter\s+ADDR_WIDTH\s*=\s*\d+;', f'parameter ADDR_WIDTH = {addr_width};'),
        (r'parameter\s+MULT_WIDTH\s*=\s*\d+;', f'parameter MULT_WIDTH = {mult_width};')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    with open("./DCIM/sim_timing/Testbench_Timing.v", 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_width", default="8")
    parser.add_argument("--addr_count", default="16")
    parser.add_argument("--multiplier_module", default="Exact")
    parser.add_argument("--rtl_dir", default="./DCIM/rtl")

    args = parser.parse_args()

    modify_width(
        data_width=int(args.data_width),
        addr_count=int(args.addr_count),
        multiplier_module=args.multiplier_module,
        rtl_dir=args.rtl_dir
    )
