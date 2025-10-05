import re

def legalize_u_multiplier_signal(line):

    line = line.replace('\\', '')

    def repl(m):
        s = m.group()
        s = s.replace('.', '_')
        s = re.sub(r'\[(\d+)\]', r'_\1_', s)
        s = re.sub(r'__+', '_', s)
        if s.endswith('_'):
            s = s[:-1]
        return s

    pattern = r'u_multiplier_NOD_nod_cels\[\d+\]\.Nod_bits[^\s,)]*'
    return re.sub(pattern, repl, line)

def clean_verilog_netlist(input_v, output_v):
    with open(input_v, 'r') as fin, open(output_v, 'w') as fout:
        for line in fin:
            line = line.replace('\\', '')    
            line = line.replace('/', '_')    
            line = legalize_u_multiplier_signal(line)  
            fout.write(line)
    print(f"[INFO] Successfully processed Verilog netlist. Output: {output_v}")

def clean_spef_file(input_spef, output_spef):
    with open(input_spef, 'r') as fin, open(output_spef, 'w') as fout:
        for line in fin:
            if line.startswith('*DIVIDER /'):
                fout.write(line)
            else:
                line = line.replace('\\', '')
                line = line.replace('/', '_')
                line = legalize_u_multiplier_signal(line)
                fout.write(line)
    print(f"[INFO] Successfully processed SPEF file. Output: {output_spef}")

if __name__ == '__main__':
    verilog_in = './DCIM/results/routing/5_3_fillcell.v'     
    verilog_out = './DCIM/results/net_normalization/netlist_cleaned.v'   
    spef_in = './DCIM/results/routing/5_3_parasitic.spef'         
    spef_out = './DCIM/results/net_normalization/spef_cleaned.spef'   

    clean_verilog_netlist(verilog_in, verilog_out)
    clean_spef_file(spef_in, spef_out)