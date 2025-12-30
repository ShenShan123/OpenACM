import re

def sram_specify(data_width, addr_width):
    code = "    reg notifier;\n"
    code += "    specify\n"
    for i in range(data_width):
        code += f"        (posedge clk => rd_out[{i}]) = (0.000, 0.000);\n"
    code += f"        $setuphold(posedge clk, we_in, 0.000, 0.000, notifier);\n"
    code += f"        $setuphold(posedge clk, ce_in, 0.000, 0.000, notifier);\n"
    for i in range(addr_width):
        code += f"        $setuphold(posedge clk, addr_in[{i}], 0.000, 0.000, notifier);\n"
    for i in range(data_width):
        code += f"        $setuphold(posedge clk, wd_in[{i}], 0.000, 0.000, notifier);\n"
    code += "        $width(posedge clk, 0, 0, notifier);\n"
    code += "        $width(negedge clk, 0, 0, notifier);\n"
    code += "        $period(posedge clk, 0, notifier);\n"
    code += "    endspecify"
    return code

def modify_sram(data_width=8, addr_count=16, rtl_dir="./DCIM/rtl", result_dir="./DCIM/results"):

    addr_width = (addr_count - 1).bit_length()
    mult_width = data_width * 2

    #sram

    with open(f"{rtl_dir}/sram.v", 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        (r'parameter\s+DATA_WIDTH\s*=\s*\d+;', f'parameter DATA_WIDTH = {data_width};'),
        (r'parameter\s+ADDR_COUNT\s*=\s*\d+;', f'parameter ADDR_COUNT = {addr_count};'),
        (r'parameter\s+ADDR_WIDTH\s*=\s*\d+;', f'parameter ADDR_WIDTH = {addr_width};'),
        (r'parameter\s+MULT_WIDTH\s*=\s*\d+;', f'parameter MULT_WIDTH = {mult_width};'),

        (r'(input\s*)\[\d+:\d+\](\s*addr_in,)', f'\\1[{addr_width - 1}:0]\\2'),
        (r'(input\s*)\[\d+:\d+\](\s*wd_in,)', f'\\1[{data_width - 1}:0]\\2'),
        (r'(output\s+reg\s*)\[\d+:\d+\](\s*rd_out\s*,?)', f'\\1[{data_width - 1}:0]\\2'),
        (r'(reg\s*)\[\d+:\d+\](\s*mem\s*)\[\d+:\d+\]', f'\\1[{data_width - 1}:0]\\2[0:{addr_count - 1}]'),

        (r'SRAM_6T_CORE_(\d+)x(\d+)_MC_TB', f'SRAM_6T_CORE_{addr_count}x{data_width}_MC_TB')
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    specify_pattern = re.compile(
        r'\s*reg\s+notifier;\s*\n'
        r'\s*specify.*?endspecify',
        re.DOTALL
    )

    content = specify_pattern.sub('', content)

    with open(f"{result_dir}/synth/sram_syn.v", 'w', encoding='utf-8') as f:
        f.write(content)

    endmodule_pos = content.find('endmodule')
    specify_code = sram_specify(data_width, addr_width)
    content = content[:endmodule_pos] + specify_code + "\n" + content[endmodule_pos:]

    with open(f"{rtl_dir}/sram.v", 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_width", default="8")
    parser.add_argument("--addr_count", default="16")
    parser.add_argument("--rtl_dir", default="./DCIM/rtl")
    parser.add_argument("--result_dir", default="./DCIM/results")

    args = parser.parse_args()

    modify_sram(
        data_width=int(args.data_width),
        addr_count=int(args.addr_count),
        rtl_dir=args.rtl_dir,
        result_dir=args.result_dir
    )