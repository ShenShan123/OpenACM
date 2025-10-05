import datetime
import math

class MultiplierGeneratorArbitrary:
    def __init__(self, n_bits=32):
        self.n_bits = n_bits
        self.output_bits = 2 * n_bits
        self.stage_count = self._calculate_stage_count(n_bits)
        self.compression_width = self._get_compression_width(n_bits)
        
    def _calculate_stage_count(self, n_bits):
        if n_bits <= 4:
            return 1
        else:
            return math.ceil(math.log2(n_bits/4)) + 1
    
    def _get_compression_width(self, n_bits):
        if n_bits <= 2:
            return n_bits
        elif n_bits <=4:
            return 2
        else:
            power = math.floor(math.log2(n_bits-1))
            compression_width = 2 ** power
            return max(4, compression_width)
    
    def _calculate_partial_product_count(self, column):
        count = 0
        for j in range(max(0, column - self.n_bits + 1), min(column + 1, self.n_bits)):
            if j < self.n_bits and (column - j) < self.n_bits:
                count += 1
        return count
    
    def _calculate_stage1_widths(self, total_columns):
        widths = []
        compression_width = self.compression_width
        
        pp_counts = [self._calculate_partial_product_count(col) for col in range(total_columns + 1)]
        
        for col in range(total_columns + 1):
            pp_count = pp_counts[col]
            target_width = min(pp_count, compression_width)
            
            if col > 0:
                prev_pp_count = pp_counts[col-1]
                if prev_pp_count >= compression_width:
                    target_width = min(pp_count + 1, compression_width)
            
            widths.append(target_width)
        
        return widths, compression_width
    
    def _calculate_stage_widths(self, stage_num, total_columns):
        if stage_num == 1:
            return self._calculate_stage1_widths(total_columns)
        
        if stage_num == 2:
            target_compression = max(4, self.compression_width // 2)
        elif stage_num == 3:
            target_compression = max(2, self.compression_width // 4)
        elif stage_num == 4:
            target_compression = max(1, self.compression_width // 8)
        else:
            target_compression = 1
        
        widths = []
        
        special_col1 = 2 * self.n_bits - 1 - target_compression  
        special_col2 = 2 * self.n_bits - target_compression      
        
        for col in range(total_columns + 1):
            
            if col == special_col2:
                width = target_compression
            elif col < target_compression:
                width = col + 1
            elif col < total_columns - (target_compression - 1):
                width = target_compression
            else:
                width = max(1, total_columns - col)
                    
            widths.append(width)
        
        return widths, target_compression
    
    def _calculate_compressor_counts(self, total_terms, target_width, is_low_part):
        reduce_count = total_terms - target_width
        
        if reduce_count <= 0:
            return 0, 0
        
        compressor_count = reduce_count // 2
        adder_count = (reduce_count - compressor_count * 2) % 2
        
        return compressor_count, adder_count
    
    def _calculate_high_part_compressor_counts(self, col, total_terms, target_width, n_bits, target_compression=None):
        """计算高半位特定列的压缩器数量"""
        
        if target_compression is None:
            target_compression = target_width
        special_col1 = 2 * n_bits - 1 - target_compression  
        special_col2 = 2 * n_bits - target_compression      
        
        if col == special_col1: 
            
            reduce_count = total_terms - 3  
            if reduce_count < 0:
                compressor_count = 0
                adder_count = 1
            else:
                compressor_count = reduce_count // 2
                adder_count = 1
            return compressor_count, adder_count, "full_special1"
        elif col == special_col2:  
          
            reduce_count = total_terms - target_width + 1
            if reduce_count <= 0:
                return 0, 0, "normal_special2"
            compressor_count = reduce_count // 2
            adder_count = (reduce_count - compressor_count * 2) % 2
            return compressor_count, adder_count, "normal_special2"
        elif col == n_bits:  
            reduce_count = total_terms - target_width
            compressor_count = reduce_count // 2
            adder_count = 1
            return compressor_count, adder_count, "full"
        elif col == n_bits + 1:  
            reduce_count = total_terms - target_width
            compressor_count = reduce_count // 2
            adder_count = 1
            return compressor_count, adder_count, "half"
        else:  
            reduce_count = total_terms - target_width + 1
            if reduce_count <= 0:
                return 0, 0, "normal"
            compressor_count = reduce_count // 2
            adder_count = (reduce_count - compressor_count * 2) % 2
            return compressor_count, adder_count, "normal"
    
    def generate_verilog_code(self):
        total_columns = 2 * self.n_bits - 1
        compression_width = self.compression_width
        
        code = """
`timescale 1ns/1ps

{cla}

{acc1}

{e42}

{basic_adders}


{approx_module}

{stage_modules}
""".format(
    n_bits=self.n_bits,
    output_bits=self.output_bits,
    stage_count=self.stage_count,
    compression_width=compression_width,
    timestamp=datetime.datetime.now(),
    cla=self._generate_cla_modules(),
    acc1=self._generate_acc1_module(),
    e42=self._generate_e_4_2_module(),
    basic_adders=self._generate_basic_adder_modules(),
    approx_module=self._generate_approx_module(total_columns),
    stage_modules=self._generate_all_stage_modules(total_columns)
)
        return code
    
    def _generate_cla_modules(self):
        code = """
module CLA4bit (
    input [3:0] A,
    input [3:0] B,
    input Cin,
    output [3:0] Sum,
    output Cout
);
    wire [3:0] C;
    
    assign Sum[0] = A[0] ^ B[0] ^ Cin;
    assign Sum[1] = A[1] ^ B[1] ^ C[0];
    assign Sum[2] = A[2] ^ B[2] ^ C[1];
    assign Sum[3] = A[3] ^ B[3] ^ C[2];
    assign C[0] = (A[0] & B[0]) | ((A[0] ^ B[0]) & Cin);
    assign C[1] = (A[1] & B[1]) | ((A[1] ^ B[1]) & C[0]);
    assign C[2] = (A[2] & B[2]) | ((A[2] ^ B[2]) & C[1]);
    assign C[3] = (A[3] & B[3]) | ((A[3] ^ B[3]) & C[2]);
    assign Cout = C[3];
endmodule
"""
        bits_needed = [self.output_bits]
        current = self.output_bits
        while current > 4:
            current = current // 2
            if current >= 4:
                bits_needed.append(current)
        
        for bits in sorted(set(bits_needed)):
            if bits > 4:
                code += self._generate_cla_module(bits)
        
        return code
    
    def _generate_cla_module(self, bits):
        if bits == 4:
            return ""
        
        half_bits = bits // 2
        return """
module CLA{bits}bit (
    input [{bits_minus1}:0] A,
    input [{bits_minus1}:0] B,
    input Cin,
    output [{bits_minus1}:0] Sum,
    output Cout
);
    wire c1;
    
    CLA{half_bits}bit cla1(
        .A(A[{half_minus1}:0]),
        .B(B[{half_minus1}:0]),
        .Cin(Cin),
        .Sum(Sum[{half_minus1}:0]),
        .Cout(c1)
    );
    
    CLA{half_bits}bit cla2(
        .A(A[{bits_minus1}:{half_bits}]),
        .B(B[{bits_minus1}:{half_bits}]),
        .Cin(c1),
        .Sum(Sum[{bits_minus1}:{half_bits}]),
        .Cout(Cout)
    );
endmodule
""".format(
    bits=bits,
    bits_minus1=bits-1,
    half_bits=half_bits,
    half_minus1=half_bits-1
)

    def _generate_acc1_module(self):
        return """
module ACCI1(
    input a,
    input b,
    input c,
    input d,
    output S,
    output C
);
    wire part1;
    wire part2;
    wire part3;
    wire part4;
    wire part5;
    wire part6;
    wire part7;
    wire part8;
    assign part1 = a ^ b;
    assign part2 = c ^ d;
    assign part3 = a | b;
    assign part4 = c | d;
    assign part5 = a & b;
    assign part6 = c & d;
    assign part7 = (~part5) | (~c);
    assign part8 = ~((~part2) ^ ~(part3 & ~part5));
    assign S = ~(part7 & part8);
    assign C = ~((~part2 | ~(part1 & ~part5)) & ~part5 & (~c | ~d));
endmodule
"""

    def _generate_e_4_2_module(self):
        return """
module E_4_2(
    input a,
    input b,
    input c,
    input d,
    input CIN,
    output S,
    output C,
    output COUT
);
    wire part;
    assign part = a ^ b ^ c ^ d;
    assign S = part ^ CIN;
    assign COUT = ((a ^ b) & c) | (~(a ^ b) & a);
    assign C = (part & CIN) | (~part & d);
endmodule
"""

    def _generate_basic_adder_modules(self):
        return """
module Full_adder(
    input a,
    input b,
    input CIN,
    output S,
    output C
);
    wire S1, T1, T2, T3;
    
    xor x1 (S1, a, b);
    xor x2 (S, S1, CIN);
    
    and A1 (T3, a, b);
    and A2 (T2, b, CIN);
    and A3 (T1, a, CIN);
    
    or O1 (C, T1, T2, T3);
endmodule

module Half_adder(
    input a,
    input b,
    output S,
    output C
);
    xor x1 (S, a, b);
    and x2 (C, a, b);
endmodule

module LOGIC0_X1 (
    output Z
);
    assign Z = 1'b0;
endmodule
"""

    def _generate_approx_module(self, total_columns):
        pp_definitions = []
        for stage in range(1, self.stage_count + 1):
            widths, _ = self._calculate_stage_widths(stage, total_columns)
            if stage == self.stage_count:
                continue
            
            for i in range(total_columns + 1):
                if stage in [1, 2, 3, 4] and i == total_columns:  
                    continue
                width = widths[i]
                if width == 0:
                    continue
                elif width == 1:
                    pp_definitions.append("    wire pp{}_{};".format(stage, i))
                else:
                    pp_definitions.append("    wire [{}:0] pp{}_{};".format(width-1, stage, i))
        
        pp_definitions.append("    wire [{}:0] A;".format(self.output_bits-2))
        pp_definitions.append("    wire [{}:0] B;".format(self.output_bits-2))
        pp_definitions.append("    wire cin_net;")

        stage_instances = []
        
       
        stage1_inputs = []
        widths, _ = self._calculate_stage_widths(1, total_columns)
        for i in range(total_columns + 1):
            width = widths[i]
            if width == 0:
                continue
            stage1_inputs.append("        .pp1_{}(pp1_{})".format(i, i))
        stage_instances.append("""
    STAGE1_{n_bits} STAGE1(
        .A(N1),
        .B(N2),
        .cin_net(cin_net),
{inputs}
    );""".format(n_bits=self.n_bits, inputs=",\n".join(stage1_inputs)))
        
        
        for stage in range(2, self.stage_count):
            inputs = []
            outputs = []
            prev_widths, _ = self._calculate_stage_widths(stage-1, total_columns)
            curr_widths, _ = self._calculate_stage_widths(stage, total_columns)
            for i in range(total_columns + 1):
                
                if stage in [2, 3] and i == total_columns:
                    continue
                prev_width = prev_widths[i]
                curr_width = curr_widths[i]
                if prev_width == 0 or curr_width == 0:
                    continue
                inputs.append("        .pp{}_{}(pp{}_{})".format(stage-1, i, stage-1, i))
                outputs.append("        .pp{}_{}(pp{}_{})".format(stage, i, stage, i))
            
            stage_instances.append("""
    STAGE{stage_num}_{n_bits} STAGE{stage_num}(
        .cin_net(cin_net),
{inputs},
{outputs}
    );""".format(stage_num=stage, n_bits=self.n_bits, inputs=",\n".join(inputs), outputs=",\n".join(outputs)))
        
        
        final_inputs = []
        prev_widths, _ = self._calculate_stage_widths(self.stage_count-1, total_columns)
        for i in range(total_columns + 1):
           
            if i ==  total_columns :
                continue
            width = prev_widths[i]
            if width == 0:
                continue
            final_inputs.append("        .pp{}_{}(pp{}_{})".format(self.stage_count-1, i, self.stage_count-1, i))
        
        stage_instances.append("""
    STAGE{stage_count}_{n_bits} STAGE{stage_count}(
        .cin_net(cin_net),
{inputs},
        .A(A),
        .B(B)
    );""".format(stage_count=self.stage_count, n_bits=self.n_bits, inputs=",\n".join(final_inputs)))

        return """
module Appro4_2_{n_bits}bit(
    input [{n_bits_minus1}:0] N1,
    input [{n_bits_minus1}:0] N2,
    output [{output_bits_minus1}:0] P_APPROX
);
{pp_definitions}
    LOGIC0_X1 u_gnd (.Z(cin_net));
{stage_instances}

    CLA{output_bits_plus1}bit Final_add(
        .A({{1'b0, A}}),
        .B({{1'b0, B}}),
        .Cin(cin_net),
        .Sum(P_APPROX),
        .Cout()
    );
endmodule
""".format(
    n_bits=self.n_bits,
    n_bits_minus1=self.n_bits-1,
    output_bits=self.output_bits,
    output_bits_minus1=self.output_bits-1,
    output_bits_plus1=self.output_bits,
    pp_definitions="\n".join(pp_definitions),
    stage_instances="\n".join(stage_instances)
)

    def _generate_all_stage_modules(self, total_columns):
        stage_modules = ""
        
        for stage in range(1, self.stage_count + 1):
            if stage == 1:
                stage_modules += self._generate_stage1_module(total_columns)
            elif stage < self.stage_count:
                stage_modules += self._generate_intermediate_stage_module(stage, total_columns)
            else:
                stage_modules += self._generate_final_stage_module(stage, total_columns)
        
        return stage_modules

    def _generate_stage1_module(self, total_columns):
        n_bits = self.n_bits
        
        code = """
    module STAGE1_{n_bits}(
        input [{n_minus1}:0] A,
        input [{n_minus1}:0] B,
        input cin_net,
    """.format(n_bits=n_bits, n_minus1=n_bits-1)
        
        outputs = []
        widths, target_compression = self._calculate_stage_widths(1, total_columns)
        for i in range(total_columns + 1):
            if i == total_columns:  
                continue
            width = widths[i]
            if width == 0:
                continue
            elif width == 1:
                outputs.append("    output pp1_{}".format(i))
            else:
                outputs.append("    output [{}:0] pp1_{}".format(width-1, i))
        
        code += ",\n".join(outputs) + "\n);\n\n"
        
        split_column = n_bits  
        
        assignments = []
        internal_wires = []
        
        
        carry_signals = {}
        cout_signals = {}
        
        
        special_col1 = 2 * n_bits - 1 - target_compression
        special_col2 = 2 * n_bits - target_compression
        column =n_bits
        
        special_col1_carry = None
        
        
        for col in range(total_columns + 1):
            if col == total_columns:
                continue
            
           
            all_pp_terms = []
            for j in range(max(0, col - n_bits + 1), min(col + 1, n_bits)):
                if j < n_bits and (col - j) < n_bits:
                    all_pp_terms.append("A[{}] & B[{}]".format(j, col - j))
            
            target_width = widths[col]
            total_pp_terms = len(all_pp_terms)
            
            is_low_part = col < split_column
            
            if col not in carry_signals:
                carry_signals[col] = []
            if col not in cout_signals:
                cout_signals[col] = []
            
           
            carry_terms_from_prev = []
            if col > 0 and col-1 in carry_signals:
                carry_terms_from_prev = carry_signals[col-1]
            
            
            pp_terms_for_compression = all_pp_terms.copy()
            
            
            if col == special_col1 and not is_low_part:
                
                if len(pp_terms_for_compression) < 2:
                    
                    while len(pp_terms_for_compression) < 2:
                        pp_terms_for_compression.append("cin_net")
                
               
                fa_inputs = pp_terms_for_compression[:2]
                remaining_pp_terms = pp_terms_for_compression[2:]
                
                fa_signal = "pp1_{}_fa_s".format(col)
                fa_carry = "pp1_{}_fa_c".format(col)
                
                internal_wires.append("    wire {};".format(fa_signal))
                internal_wires.append("    wire {};".format(fa_carry))
                
                
                cin_signal = "1'b0"
                if col > 0 and col-1 in cout_signals and cout_signals[col-1]:
                    cin_signal = cout_signals[col-1][0]
                
                assignments.append("    Full_adder Full_adder_pp1_fa_{}(".format(col))
                assignments.append("        .a({}),".format(fa_inputs[0]))
                assignments.append("        .b({}),".format(fa_inputs[1]))
                assignments.append("        .CIN({}),".format(cin_signal))
                assignments.append("        .S({}),".format(fa_signal))
                assignments.append("        .C({})".format(fa_carry))
                assignments.append("    );")
                
                
                special_col1_carry = fa_carry
                
               
                output_terms = [fa_signal] + remaining_pp_terms
                if col > 0 and col-1 in carry_signals:
                    output_terms.extend(carry_signals[col-1])
                
                
                if len(output_terms) > target_width:
                    output_terms = output_terms[:target_width]
                
                if len(output_terms) == 0:
                    assignments.append("    assign pp1_{} = 1'b0;".format(col))
                elif len(output_terms) == 1:
                    assignments.append("    assign pp1_{} = {};".format(col, output_terms[0]))
                else:
                    if len(output_terms) < target_width:
                        output_terms = ["1'b0"] * (target_width - len(output_terms)) + output_terms
                    assignments.append("    assign pp1_{} = {{{}}};".format(col, ", ".join(output_terms)))
            
            
            elif col == special_col2 and not is_low_part:
            
                output_terms = pp_terms_for_compression
                if special_col1_carry is not None:
                    output_terms.append(special_col1_carry)
                
                
                if carry_terms_from_prev and len(output_terms) >= target_width:
                    if len(output_terms) >= 1:
                        a = output_terms[-1]
                        cin = carry_terms_from_prev[0]

                        fa_signal = "pp1_{}_carry_fa_s".format(col)
                        fa_carry = "pp1_{}_carry_fa_c".format(col)
                        
                        internal_wires.append("    wire {};".format(fa_signal))
                        internal_wires.append("    wire {};".format(fa_carry))
                        
                        assignments.append("    Full_adder carry_fa_{}(".format(col))
                        assignments.append("        .a({}),".format(a))
                        assignments.append("        .b(1'b0),")
                        assignments.append("        .CIN({}),".format(cin))
                        assignments.append("        .S({}),".format(fa_signal))
                        assignments.append("        .C({})".format(fa_carry))
                        assignments.append("    );")
                        
                        output_terms = output_terms[:-1] + [fa_signal]
                        
                        if col not in carry_signals:
                            carry_signals[col] = []
                        carry_signals[col].append(fa_carry)
                elif carry_terms_from_prev and len(output_terms) < target_width:
                    output_terms.extend(carry_terms_from_prev)
                
               
                if len(output_terms) > target_width:
                    output_terms = output_terms[:target_width]
                
                if len(output_terms) == 0:
                    assignments.append("    assign pp1_{} = 1'b0;".format(col))
                elif len(output_terms) == 1:
                    assignments.append("    assign pp1_{} = {};".format(col, output_terms[0]))
                else:
                    if len(output_terms) < target_width:
                        output_terms = ["1'b0"] * (target_width - len(output_terms)) + output_terms
                    assignments.append("    assign pp1_{} = {{{}}};".format(col, ", ".join(output_terms)))
            
           
            else:
                if total_pp_terms <= target_width:
                   
                    output_terms = pp_terms_for_compression
                    
                    
                    if is_low_part and col > 0 and col-1 in carry_signals:
                        output_terms.extend(carry_terms_from_prev)
                    
                   
                    if len(output_terms) == 0:
                        assignments.append("    assign pp1_{} = 1'b0;".format(col))
                    elif len(output_terms) == 1:
                        assignments.append("    assign pp1_{} = {};".format(col, output_terms[0]))
                    else:
                        
                        if len(output_terms) < target_width and is_low_part:
                            output_terms = output_terms + ["1'b0"] * (target_width - len(output_terms))
                        assignments.append("    assign pp1_{} = {{{}}};".format(col, ", ".join(output_terms)))
                else:
                    if is_low_part:
                        compressor_count, adder_count = self._calculate_compressor_counts(
                            total_pp_terms, target_width, is_low_part)
                        
                        compressor = "ACCI1"
                        adder = "Half_adder"
                    else:
                        compressor_count, adder_count, adder_type = self._calculate_high_part_compressor_counts(
                            col, total_pp_terms, target_width, n_bits)
                        
                        compressor = "E_4_2"
                        if adder_type == "full":
                            adder = "Full_adder"
                        elif adder_type == "half":
                            adder = "Half_adder"
                        else:
                            adder = "Full_adder"
                    
                    comp_terms = []
                    adder_terms = []
                    
                   
                    for comp_idx in range(compressor_count):
                        if len(pp_terms_for_compression) < 4:
                            break
                            
                        inputs = pp_terms_for_compression[:4]
                        pp_terms_for_compression = pp_terms_for_compression[4:]
                        
                        s_signal = "pp1_{}_comp_{}_s".format(col, comp_idx)
                        c_signal = "pp1_{}_comp_{}_c".format(col, comp_idx)
                        
                        internal_wires.append("    wire {};".format(s_signal))
                        internal_wires.append("    wire {};".format(c_signal))
                        
                        if compressor == "ACCI1":
                            assignments.append("    {} ACCI1_{}_{}(".format(compressor, col, comp_idx))
                            assignments.append("        .a({}),".format(inputs[0]))
                            assignments.append("        .b({}),".format(inputs[1]))
                            assignments.append("        .c({}),".format(inputs[2]))
                            assignments.append("        .d({}),".format(inputs[3]))
                            assignments.append("        .S({}),".format(s_signal))
                            assignments.append("        .C({})".format(c_signal))
                            assignments.append("    );")
                            
                            if col not in carry_signals:
                                carry_signals[col] = []
                            carry_signals[col].append(c_signal)
                        else:
                           
                            cout_signal = "pp1_{}_e42_{}_cout".format(col, comp_idx)
                            internal_wires.append("    wire {};".format(cout_signal))
                            
                           
                            cin_signal = "cin_net"
                            if col > 0 and col-1 in cout_signals and comp_idx < len(cout_signals[col-1]):
                                cin_signal = cout_signals[col-1][comp_idx]
                            
                            assignments.append("    {} e42_{}_{}(".format(compressor, col, comp_idx))
                            assignments.append("        .a({}),".format(inputs[0]))
                            assignments.append("        .b({}),".format(inputs[1]))
                            assignments.append("        .c({}),".format(inputs[2]))
                            assignments.append("        .d({}),".format(inputs[3]))
                            assignments.append("        .CIN({}),".format(cin_signal))
                            assignments.append("        .S({}),".format(s_signal))
                            assignments.append("        .C({}),".format(c_signal))
                            assignments.append("        .COUT({})".format(cout_signal))
                            assignments.append("    );")
                            
                           
                            if col not in cout_signals:
                                cout_signals[col] = []
                            cout_signals[col].append(cout_signal)
                            
                            
                            if col not in carry_signals:
                                carry_signals[col] = []
                            carry_signals[col].append(c_signal)
                        
                        comp_terms.append(s_signal)
                    
                    
                    for add_idx in range(adder_count):
                        if len(pp_terms_for_compression) < 2 and adder != "Half_adder":
                            break
                        if len(pp_terms_for_compression) < 1:
                            break
                            
                        if adder == "Half_adder":
                            ha_signal = "pp1_{}_ha{}_s".format(col, add_idx)
                            ha_carry = "pp1_{}_ha{}_c".format(col, add_idx)
                            
                            internal_wires.append("    wire {};".format(ha_signal))
                            internal_wires.append("    wire {};".format(ha_carry))
                            
                            assignments.append("    Half_adder ha_{}_{}(".format(col, add_idx))
                            assignments.append("        .a({}),".format(pp_terms_for_compression[0]))
                            assignments.append("        .b({}),".format(pp_terms_for_compression[1] if len(pp_terms_for_compression) > 1 else "cin_net"))
                            assignments.append("        .S({}),".format(ha_signal))
                            assignments.append("        .C({})".format(ha_carry))
                            assignments.append("    );")
                            
                            pp_terms_for_compression = pp_terms_for_compression[2:] if len(pp_terms_for_compression) > 1 else []
                            adder_terms.append(ha_signal)
                            if is_low_part:
                                
                                if col not in carry_signals:
                                    carry_signals[col] = []
                                carry_signals[col].append(ha_carry)
                            else:
                                
                                if col not in carry_signals:
                                    carry_signals[col] = []
                                carry_signals[col].append(ha_carry)
                        else:
                            
                            fa_signal = "pp1_{}_fa{}_s".format(col, add_idx)
                            fa_carry = "pp1_{}_fa{}_c".format(col, add_idx)
                            
                            internal_wires.append("    wire {};".format(fa_signal))
                            internal_wires.append("    wire {};".format(fa_carry))
                            
                            
                            cin_signal = "cin_net"
                            remaining_cout_count = 0
                            if col > 0 and col-1 in cout_signals:
                                remaining_cout_count = len(cout_signals[col-1]) - compressor_count
                                if add_idx < remaining_cout_count:
                                    cin_signal = cout_signals[col-1][compressor_count + add_idx]
                            
                            
                            if col == n_bits and adder_type == "full":
                                
                                if len(pp_terms_for_compression) >= 2:
                                    
                                    if len(pp_terms_for_compression) >= 3:
                                        cin_signal = pp_terms_for_compression[2]
                                        pp_terms_for_compression = pp_terms_for_compression[:2]  
                                    else:
                                       
                                        cin_signal = "1'b0"
                            
                            assignments.append("    Full_adder fa_{}_{}(".format(col, add_idx))
                            assignments.append("        .a({}),".format(pp_terms_for_compression[0]))
                            assignments.append("        .b({}),".format(pp_terms_for_compression[1] if len(pp_terms_for_compression) > 1 else "cin_net"))
                            assignments.append("        .CIN({}),".format(cin_signal))
                            assignments.append("        .S({}),".format(fa_signal))
                            assignments.append("        .C({})".format(fa_carry))
                            assignments.append("    );")
                            
                            pp_terms_for_compression = pp_terms_for_compression[3:] if len(pp_terms_for_compression) > 1 else []
                            adder_terms.append(fa_signal)
                           
                            if col not in carry_signals:
                                carry_signals[col] = []
                            carry_signals[col].append(fa_carry)
                    
                  
                    if is_low_part:
                       
                        output_terms = pp_terms_for_compression + comp_terms + adder_terms
                        
                        
                        if col > 0 and col-1 in carry_signals:
                            output_terms.extend(carry_signals[col-1])
                        
                       
                        if len(output_terms) > target_width:
                            output_terms = output_terms[:target_width]
                        
                        
                        if len(output_terms) < target_width:
                            output_terms = output_terms + ["1'b0"] * (target_width - len(output_terms))
                        
                        if len(output_terms) == 0:
                            assignments.append("    assign pp1_{} = 1'b0;".format(col))
                        elif len(output_terms) == 1:
                            assignments.append("    assign pp1_{} = {};".format(col, output_terms[0]))
                        else:
                            assignments.append("    assign pp1_{} = {{{}}};".format(col, ", ".join(output_terms)))
                    else:
                        
                        processed_terms = set()
                        
                        
                        for comp_idx in range(compressor_count):
                            if comp_idx * 4 < len(all_pp_terms):
                                for i in range(min(4, len(all_pp_terms) - comp_idx * 4)):
                                    idx = comp_idx * 4 + i
                                    if idx < len(all_pp_terms):
                                        processed_terms.add(all_pp_terms[idx])
                        
                          
                        for add_idx in range(adder_count):
                            
                            if col == n_bits and adder_type == "full" : 
                                input_count = 3  
                            else:
                                input_count = 2
                            
                            start_idx = compressor_count * 4 + add_idx * input_count
                            for i in range(input_count):
                                idx = start_idx + i
                                if idx < len(all_pp_terms):
                                    processed_terms.add(all_pp_terms[idx])
                        
                       
                        remaining_high_pp_terms = []
                        for term in all_pp_terms:
                            if term not in processed_terms:
                                remaining_high_pp_terms.append(term)
                        
                        
                        output_terms = remaining_high_pp_terms + comp_terms + adder_terms
                        
                       
                        if carry_terms_from_prev and len(output_terms) >= target_width:
                            if len(output_terms) >= 1:
                                a = output_terms[-1]
                                cin = carry_terms_from_prev[0]

                                fa_signal = "pp1_{}_carry_fa_s".format(col)
                                fa_carry = "pp1_{}_carry_fa_c".format(col)
                                
                                internal_wires.append("    wire {};".format(fa_signal))
                                internal_wires.append("    wire {};".format(fa_carry))
                                
                                assignments.append("    Full_adder carry_fa_{}(".format(col))
                                assignments.append("        .a({}),".format(a))
                                assignments.append("        .b(1'b0),")
                                assignments.append("        .CIN({}),".format(cin))
                                assignments.append("        .S({}),".format(fa_signal))
                                assignments.append("        .C({})".format(fa_carry))
                                assignments.append("    );")
                                
                                output_terms = output_terms[:-1] + [fa_signal]
                               
                                if col not in carry_signals:
                                    carry_signals[col] = []
                                carry_signals[col].append(fa_carry)
                        elif carry_terms_from_prev and len(output_terms) < target_width:
                            output_terms.extend(carry_terms_from_prev)
                        
                       
                        if len(output_terms) > target_width:
                            output_terms = output_terms[:target_width]
                        
                        
                        if len(output_terms) == 0:
                            assignments.append("    assign pp1_{} = 1'b0;".format(col))
                        elif len(output_terms) == 1:
                            assignments.append("    assign pp1_{} = {};".format(col, output_terms[0]))
                        else:
                            assignments.append("    assign pp1_{} = {{{}}};".format(col, ", ".join(output_terms)))
        
        code += "\n".join(internal_wires) + "\n\n" + "\n".join(assignments) + "\n"
        code += "endmodule\n"
        
        return code

    def _generate_intermediate_stage_module(self, stage_num, total_columns):
        n_bits = self.n_bits
        prev_stage = stage_num - 1
        
        code = """
module STAGE{stage_num}_{n_bits}(
    input cin_net,
""".format(stage_num=stage_num, n_bits=n_bits)
        
        inputs = []
        prev_widths, _ = self._calculate_stage_widths(prev_stage, total_columns)
        
        for i in range(total_columns + 1):
            if i == total_columns:  
                continue
            width = prev_widths[i]
            if width == 0:
                continue
            elif width == 1:
                inputs.append("    input pp{}_{}".format(prev_stage, i))
            else:
                inputs.append("    input [{}:0] pp{}_{}".format(width-1, prev_stage, i))
        
        outputs = []
        curr_widths, target_compression = self._calculate_stage_widths(stage_num, total_columns)
        
        for i in range(total_columns + 1):
            if i == total_columns:  
                continue
            width = curr_widths[i]
            if width == 0:
                continue
            elif width == 1:
                outputs.append("    output pp{}_{}".format(stage_num, i))
            else:
                outputs.append("    output [{}:0] pp{}_{}".format(width-1, stage_num, i))
        
        code += ",\n".join(inputs) + ",\n"
        code += ",\n".join(outputs) + "\n);\n\n"
        
        code += self._generate_compression_logic(stage_num, total_columns, prev_stage, stage_num, target_compression)
        
        code += "endmodule\n"
        return code

    def _generate_final_stage_module(self, stage_num, total_columns):
        n_bits = self.n_bits
        prev_stage = stage_num - 1
        
        code = """
module STAGE{stage_num}_{n_bits}(
    input cin_net,
""".format(stage_num=stage_num, n_bits=n_bits)
        
        inputs = []
        prev_widths, _ = self._calculate_stage_widths(prev_stage, total_columns)
        
        for i in range(total_columns + 1):
            if i == total_columns:  
                continue
            width = prev_widths[i]
            if width == 0:
                continue
            elif width == 1:
                inputs.append("    input pp{}_{}".format(prev_stage, i))
            else:
                inputs.append("    input [{}:0] pp{}_{}".format(width-1, prev_stage, i))
        
        code += ",\n".join(inputs) + ",\n"
        code += "    output [{}:0] A,\n".format(2*n_bits-2)
        code += "    output [{}:0] B\n".format(2*n_bits-2)
        code += ");\n\n"
        
        code += self._generate_final_compression_logic(total_columns, prev_stage)
        
        code += "endmodule\n"
        return code

    def _generate_compression_logic(self, stage_num, total_columns, input_stage, output_stage, target_compression):
        n_bits = self.n_bits
        assignments = []
        internal_wires = []
        
        split_column = n_bits
        
        carry_signals = {}
        cout_signals = {}
        
        input_widths, _ = self._calculate_stage_widths(input_stage, total_columns)
        output_widths, _ = self._calculate_stage_widths(output_stage, total_columns)
        
        
        special_col1 = 2 * n_bits - 1 - target_compression  
        special_col2 = 2 * n_bits - target_compression      
        
        
        special_col1_carry = None
        
        for col in range(total_columns + 1):
            
            if col == total_columns and output_stage in [2, 3]:
                continue
                
            input_width = input_widths[col]
            output_width = output_widths[col]
            
            if input_width == 0 or output_width == 0:
                continue
            
            pp_terms = []
            if input_width == 1:
                pp_terms.append("pp{}_{}".format(input_stage, col))
            else:
                for k in range(input_width):
                    pp_terms.append("pp{}_{}[{}]".format(input_stage, col, k))
            
            total_pp_terms = len(pp_terms)
            
            is_low_part = col < split_column
            
            if col not in carry_signals:
                carry_signals[col] = []
            if col not in cout_signals:
                cout_signals[col] = []
            
            
            carry_terms_from_prev = []
            if col > 0 and col-1 in carry_signals:
                carry_terms_from_prev = carry_signals[col-1]
            
            
            if col == special_col1 and not is_low_part:
                
                if len(pp_terms) < 2:
                   
                    while len(pp_terms) < 2:
                        pp_terms.append("cin_net")
                
                
                fa_inputs = pp_terms[:2]
                remaining_pp_terms = pp_terms[2:]
                
                fa_signal = "pp{}_{}_fa_s".format(output_stage, col)
                fa_carry = "pp{}_{}_fa_c".format(output_stage, col)
                
                internal_wires.append("    wire {};".format(fa_signal))
                internal_wires.append("    wire {};".format(fa_carry))
                
               
                cin_signal = "cin_net"
                if col > 0 and col-1 in cout_signals and cout_signals[col-1]:
                    cin_signal = cout_signals[col-1][0]
                
                assignments.append("    Full_adder Full_adder_pp{}_{}(".format(output_stage, col))
                assignments.append("        .a({}),".format(fa_inputs[0]))
                assignments.append("        .b({}),".format(fa_inputs[1]))
                assignments.append("        .CIN({}),".format(cin_signal))
                assignments.append("        .S({}),".format(fa_signal))
                assignments.append("        .C({})".format(fa_carry))
                assignments.append("    );")
                
                
                special_col1_carry = fa_carry
                
                
                output_terms = [fa_signal] + remaining_pp_terms
                if col > 0 and col-1 in carry_signals:
                    output_terms.extend(carry_signals[col-1])
                
                
                if len(output_terms) > output_width:
                    output_terms = output_terms[:output_width]
                
                if len(output_terms) == 0:
                    assignments.append("    assign pp{}_{} = 1'b0;".format(output_stage, col))
                elif len(output_terms) == 1:
                    assignments.append("    assign pp{}_{} = {};".format(output_stage, col, output_terms[0]))
                else:
                    if len(output_terms) < output_width:
                        output_terms = ["1'b0"] * (output_width - len(output_terms)) + output_terms
                    assignments.append("    assign pp{}_{} = {{{}}};".format(output_stage, col, ", ".join(output_terms)))
            
          
            elif col == special_col2 and not is_low_part:
               
                
                
                output_terms = pp_terms
                if special_col1_carry is not None:
                    output_terms.append(special_col1_carry)
                
                
                if carry_terms_from_prev and len(output_terms) >= output_width:
                    if len(output_terms) >= 1:
                        a = output_terms[-1]
                        cin = carry_terms_from_prev[0]

                        fa_signal = "pp{}_{}_carry_fa_s".format(output_stage, col)
                        fa_carry = "pp{}_{}_carry_fa_c".format(output_stage, col)
                        
                        internal_wires.append("    wire {};".format(fa_signal))
                        internal_wires.append("    wire {};".format(fa_carry))
                        
                        assignments.append("    Full_adder carry_fa_{}_{}(".format(output_stage, col))
                        assignments.append("        .a({}),".format(a))
                        assignments.append("        .b(1'b0),")
                        assignments.append("        .CIN({}),".format(cin))
                        assignments.append("        .S({}),".format(fa_signal))
                        assignments.append("        .C({})".format(fa_carry))
                        assignments.append("    );")
                        
                        output_terms = output_terms[:-1] + [fa_signal]
                        
                        if col not in carry_signals:
                            carry_signals[col] = []
                        carry_signals[col].append(fa_carry)
                elif carry_terms_from_prev and len(output_terms) < output_width:
                    output_terms.extend(carry_terms_from_prev)
                
                
                if len(output_terms) > output_width :
                    output_terms = output_terms[:output_width]
                
                if len(output_terms) == 0:
                    assignments.append("    assign pp{}_{} = 1'b0;".format(output_stage, col))
                elif len(output_terms) == 1:
                    assignments.append("    assign pp{}_{} = {};".format(output_stage, col, output_terms[0]))
                else:
                    if len(output_terms) < output_width:
                        output_terms = ["1'b0"] * (output_width - len(output_terms)) + output_terms
                    assignments.append("    assign pp{}_{} = {{{}}};".format(output_stage, col, ", ".join(output_terms)))
            
            
            else:
                if total_pp_terms <= output_width:
                    output_terms = pp_terms
                    
                    if is_low_part and col > 0 and col-1 in carry_signals:
                        output_terms.extend(carry_signals[col-1])
                    
                    if len(output_terms) == 0:
                        assignments.append("    assign pp{}_{} = 1'b0;".format(output_stage, col))
                    elif len(output_terms) == 1:
                        assignments.append("    assign pp{}_{} = {};".format(output_stage, col, output_terms[0]))
                    else:
                        if len(output_terms) < output_width:
                            output_terms = ["1'b0"] * (output_width - len(output_terms)) + output_terms
                        assignments.append("    assign pp{}_{} = {{{}}};".format(output_stage, col, ", ".join(output_terms)))
                else:
                    if is_low_part:
                        compressor_count, adder_count = self._calculate_compressor_counts(
                            total_pp_terms, output_width, is_low_part)
                        
                        compressor = "ACCI1"
                        adder = "Half_adder"
                    else:
                        compressor_count, adder_count, adder_type = self._calculate_high_part_compressor_counts(
                            col, total_pp_terms, output_width, n_bits, target_compression)
                        
                        compressor = "E_4_2"
                        if adder_type == "full":
                            adder = "Full_adder"
                        elif adder_type == "half":
                            adder = "Half_adder"
                        elif adder_type == "full_special1":
                            adder = "Full_adder"
                        elif adder_type == "normal_special2":
                            adder = "Full_adder"  
                        else:
                            adder = "Full_adder"
                    
                    comp_terms = []
                    
                    for comp_idx in range(compressor_count):
                        if len(pp_terms) < 4:
                            break
                            
                        inputs_comp = pp_terms[:4]
                        pp_terms = pp_terms[4:]
                        
                        s_signal = "pp{}_{}_comp{}_s".format(output_stage, col, comp_idx)
                        c_signal = "pp{}_{}_comp{}_c".format(output_stage, col, comp_idx)
                        
                        internal_wires.append("    wire {};".format(s_signal))
                        internal_wires.append("    wire {};".format(c_signal))
                        
                        if compressor == "ACCI1":
                            assignments.append("    {} ACCI1_{}_{}_{}(".format(compressor, output_stage, col, comp_idx))
                            assignments.append("        .a({}),".format(inputs_comp[0]))
                            assignments.append("        .b({}),".format(inputs_comp[1]))
                            assignments.append("        .c({}),".format(inputs_comp[2]))
                            assignments.append("        .d({}),".format(inputs_comp[3]))
                            assignments.append("        .S({}),".format(s_signal))
                            assignments.append("        .C({})".format(c_signal))
                            assignments.append("    );")
                            if col not in carry_signals:
                                carry_signals[col] = []
                            carry_signals[col].append(c_signal)
                        else:
                            cout_signal = "pp{}_{}_comp{}_cout".format(output_stage, col, comp_idx)
                            internal_wires.append("    wire {};".format(cout_signal))
                            
                            cin_signal = "cin_net"
                            if col > 0 and col-1 in cout_signals and comp_idx < len(cout_signals[col-1]):
                                cin_signal = cout_signals[col-1][comp_idx]
                            
                            assignments.append("    {} e42_{}_{}_{}(".format(compressor, output_stage, col, comp_idx))
                            assignments.append("        .a({}),".format(inputs_comp[0]))
                            assignments.append("        .b({}),".format(inputs_comp[1]))
                            assignments.append("        .c({}),".format(inputs_comp[2]))
                            assignments.append("        .d({}),".format(inputs_comp[3]))
                            assignments.append("        .CIN({}),".format(cin_signal))
                            assignments.append("        .S({}),".format(s_signal))
                            assignments.append("        .C({}),".format(c_signal))
                            assignments.append("        .COUT({})".format(cout_signal))
                            assignments.append("    );")
                            
                            if col not in cout_signals:
                                cout_signals[col] = []
                            cout_signals[col].append(cout_signal)
                            
                            if col not in carry_signals:
                                carry_signals[col] = []
                            carry_signals[col].append(c_signal)
                        
                        comp_terms.append(s_signal)
                    
                    adder_terms = []
                    for add_idx in range(adder_count):
                        if len(pp_terms) < 2 and adder != "Half_adder":
                            break
                        if len(pp_terms) < 1:
                            break
                            
                        if adder == "Half_adder":
                            ha_signal = "pp{}_{}_ha{}_s".format(output_stage, col, add_idx)
                            ha_carry = "pp{}_{}_ha{}_c".format(output_stage, col, add_idx)
                            
                            internal_wires.append("    wire {};".format(ha_signal))
                            internal_wires.append("    wire {};".format(ha_carry))
                            
                            assignments.append("    Half_adder ha_{}_{}_{}(".format(output_stage, col, add_idx))
                            assignments.append("        .a({}),".format(pp_terms[0]))
                            assignments.append("        .b({}),".format(pp_terms[1] if len(pp_terms) > 1 else "1'b0"))
                            assignments.append("        .S({}),".format(ha_signal))
                            assignments.append("        .C({})".format(ha_carry))
                            assignments.append("    );")
                            
                            pp_terms = pp_terms[2:] if len(pp_terms) > 1 else []
                            adder_terms.append(ha_signal)
                            if is_low_part:
                                if col not in carry_signals:
                                    carry_signals[col] = []
                                carry_signals[col].append(ha_carry)
                            else:
                                if col not in carry_signals:
                                    carry_signals[col] = []
                                carry_signals[col].append(ha_carry)
                        else:
                            fa_signal = "pp{}_{}_fa{}_s".format(output_stage, col, add_idx)
                            fa_carry = "pp{}_{}_fa{}_c".format(output_stage, col, add_idx)
                            
                            internal_wires.append("    wire {};".format(fa_signal))
                            internal_wires.append("    wire {};".format(fa_carry))
                            
                            cin_signal = "cin_net"
                            remaining_cout_count = 0
                            if col > 0 and col-1 in cout_signals:
                                remaining_cout_count = len(cout_signals[col-1]) - compressor_count
                                if add_idx < remaining_cout_count:
                                    cin_signal = cout_signals[col-1][compressor_count + add_idx]
                            
                            
                            if col == n_bits and adder_type == "full":
                                
                                if len(pp_terms) >= 2:
                                   
                                    if len(pp_terms) >= 3:
                                        cin_signal = pp_terms[2]
                                        pp_terms = pp_terms[:2]  
                                    else:
                                       
                                        cin_signal = "cin_net"
                            
                            assignments.append("    Full_adder fa_{}_{}_{}(".format(output_stage, col, add_idx))
                            assignments.append("        .a({}),".format(pp_terms[0]))
                            assignments.append("        .b({}),".format(pp_terms[1] if len(pp_terms) > 1 else "cin_net"))
                            assignments.append("        .CIN({}),".format(cin_signal))
                            assignments.append("        .S({}),".format(fa_signal))
                            assignments.append("        .C({})".format(fa_carry))
                            assignments.append("    );")
                            
                            pp_terms = pp_terms[2:] if len(pp_terms) > 1 else []
                            adder_terms.append(fa_signal)
                            if col not in carry_signals:
                                carry_signals[col] = []
                            carry_signals[col].append(fa_carry)
                    
                    output_terms = pp_terms + comp_terms + adder_terms
                    
                    if not is_low_part and carry_terms_from_prev and len(output_terms) >= output_width:
                        if len(output_terms) >= 1:
                            a = output_terms[-1]
                            cin = carry_terms_from_prev[0]
                            
                            fa_signal = "pp{}_{}_carry_fa_s".format(output_stage, col)
                            fa_carry = "pp{}_{}_carry_fa_c".format(output_stage, col)
                            
                            internal_wires.append("    wire {};".format(fa_signal))
                            internal_wires.append("    wire {};".format(fa_carry))
                            
                            assignments.append("    Full_adder carry_fa_{}_{}(".format(output_stage, col))
                            assignments.append("        .a({}),".format(a))
                            assignments.append("        .b(1'b0),")
                            assignments.append("        .CIN({}),".format(cin))
                            assignments.append("        .S({}),".format(fa_signal))
                            assignments.append("        .C({})".format(fa_carry))
                            assignments.append("    );")
                            
                            output_terms = output_terms[:-1] + [fa_signal]
                            if col not in carry_signals:
                                carry_signals[col] = []
                            carry_signals[col].append(fa_carry)
                    elif not is_low_part and carry_terms_from_prev and len(output_terms) < output_width:
                        output_terms.extend(carry_terms_from_prev)
                    
                    if is_low_part and col > 0 and col-1 in carry_signals:
                        output_terms.extend(carry_signals[col-1])
                    
                    if len(output_terms) > output_width:
                        output_terms = output_terms[:output_width]
                    
                    if len(output_terms) == 0:
                        assignments.append("    assign pp{}_{} = 1'b0;".format(output_stage, col))
                    elif len(output_terms) == 1:
                        assignments.append("    assign pp{}_{} = {};".format(output_stage, col, output_terms[0]))
                    else:
                        if len(output_terms) < output_width:
                            output_terms = ["1'b0"] * (output_width - len(output_terms)) + output_terms
                        assignments.append("    assign pp{}_{} = {{{}}};".format(output_stage, col, ", ".join(output_terms)))
        
        return "\n".join(internal_wires) + "\n\n" + "\n".join(assignments) + "\n"

    def _generate_final_compression_logic(self, total_columns, input_stage):
        n_bits = self.n_bits
        assignments = []
        internal_wires = []
        
        split_column = n_bits
        
        
        a_bits = ['1\'b0'] * (2 * n_bits - 1)
        b_bits = ['1\'b0'] * (2 * n_bits - 1)
        
       
        prev_cout = "cin_net"
        
        input_widths, _ = self._calculate_stage_widths(input_stage, total_columns)
        
        for col in range(total_columns + 1):
            
            if col == total_columns:
                continue
                
            input_width = input_widths[col]
            
            if input_width == 0:
                continue
            
            pp_terms = []
            if input_width == 1:
                pp_terms.append("pp{}_{}".format(input_stage, col))
            else:
                for k in range(input_width):
                    pp_terms.append("pp{}_{}[{}]".format(input_stage, col, k))
            
            is_low_part = col < split_column
            
           
            if is_low_part:
                if col == 0:
                    
                    a_bits[0] = pp_terms[0]
                    b_bits[0] = "1'b0"
                
                elif col == 1:
                    
                    if len(pp_terms) >= 1:
                        a_bits[1] = pp_terms[0]
                    if len(pp_terms) >= 2:
                        b_bits[1] = pp_terms[1]
                
                elif col == 2:
                    
                    if len(pp_terms) >= 2:
                        ha_s = "ha_{}_s".format(col)
                        ha_c = "ha_{}_c".format(col)
                        
                        internal_wires.append("    wire {};".format(ha_s))
                        internal_wires.append("    wire {};".format(ha_c))
                        
                        assignments.append("    Half_adder ha_{}(".format(col))
                        assignments.append("        .a({}),".format(pp_terms[0]))
                        assignments.append("        .b({}),".format(pp_terms[1]))
                        assignments.append("        .S({}),".format(ha_s))
                        assignments.append("        .C({})".format(ha_c))
                        assignments.append("    );")
                        
                        a_bits[2] = ha_s
                        b_bits[2] = pp_terms[2]
                        b_bits[3] = ha_c
                    elif len(pp_terms) == 1:
                        a_bits[2] = pp_terms[0]
                        b_bits[2] = " 1'b0"
                
                else:  
                    
                    if len(pp_terms) >= 4:
                        acci_s = "acci_{}_s".format(col)
                        acci_c = "acci_{}_c".format(col)
                        
                        internal_wires.append("    wire {};".format(acci_s))
                        internal_wires.append("    wire {};".format(acci_c))
                        
                        assignments.append("    ACCI1 ACCI1_{}(".format(col))
                        assignments.append("        .a({}),".format(pp_terms[0]))
                        assignments.append("        .b({}),".format(pp_terms[1]))
                        assignments.append("        .c({}),".format(pp_terms[2]))
                        assignments.append("        .d({}),".format(pp_terms[3]))
                        assignments.append("        .S({}),".format(acci_s))
                        assignments.append("        .C({})".format(acci_c))
                        assignments.append("    );")
                        
                        a_bits[col] = acci_s
                        b_bits[col+1] = acci_c
                    elif len(pp_terms) == 3:
                        
                        acci_s = "acci_{}_s".format(col)
                        acci_c = "acci_{}_c".format(col)
                        
                        internal_wires.append("    wire {};".format(acci_s))
                        internal_wires.append("    wire {};".format(acci_c))
                        
                        assignments.append("    ACCI1 ACCI1_{}(".format(col))
                        assignments.append("        .a({}),".format(pp_terms[0]))
                        assignments.append("        .b({}),".format(pp_terms[1]))
                        assignments.append("        .c({}),".format(pp_terms[2]))
                        assignments.append("        .d(1'b0),")
                        assignments.append("        .S({}),".format(acci_s))
                        assignments.append("        .C({})".format(acci_c))
                        assignments.append("    );")
                        
                        a_bits[col] = acci_s
                        b_bits[col+1] = acci_c
                    elif len(pp_terms) == 2:
                        
                        ha_s = "ha_{}_s".format(col)
                        ha_c = "ha_{}_c".format(col)
                        
                        internal_wires.append("    wire {};".format(ha_s))
                        internal_wires.append("    wire {};".format(ha_c))
                        
                        assignments.append("    Half_adder ha_{}(".format(col))
                        assignments.append("        .a({}),".format(pp_terms[0]))
                        assignments.append("        .b({}),".format(pp_terms[1]))
                        assignments.append("        .S({}),".format(ha_s))
                        assignments.append("        .C({})".format(ha_c))
                        assignments.append("    );")
                        
                        a_bits[col] = ha_s
                        b_bits[col+1] = ha_c
                    elif len(pp_terms) == 1:
                        a_bits[col] = pp_terms[0]
                        b_bits[col+1] = "1'b0"
            
           
            else:
                if col == 2 * n_bits - 2:  
                  
                    a_bits[2*n_bits-2] = pp_terms[0] if len(pp_terms) > 0 else "1'b0"
                
                elif col == 2 * n_bits - 3:  
                    
                    if len(pp_terms) >= 2:
                        fa_s = "fa_{}_s".format(col)
                        fa_c = "fa_{}_c".format(col)
                        
                        internal_wires.append("    wire {};".format(fa_s))
                        internal_wires.append("    wire {};".format(fa_c))
                        
                        assignments.append("    Full_adder fa_{}(".format(col))
                        assignments.append("        .a({}),".format(pp_terms[0]))
                        assignments.append("        .b({}),".format(pp_terms[1]))
                        assignments.append("        .CIN({}),".format(prev_cout))
                        assignments.append("        .S({}),".format(fa_s))
                        assignments.append("        .C({})".format(fa_c))
                        assignments.append("    );")
                        
                        a_bits[col] = fa_s
                        b_bits[col+1] = fa_c
                    elif len(pp_terms) == 1:
                        
                        fa_s = "fa_{}_s".format(col)
                        fa_c = "fa_{}_c".format(col)
                        
                        internal_wires.append("    wire {};".format(fa_s))
                        internal_wires.append("    wire {};".format(fa_c))
                        
                        assignments.append("    Full_adder fa_{}(".format(col))
                        assignments.append("        .a({}),".format(pp_terms[0]))
                        assignments.append("        .b(1'b0),")
                        assignments.append("        .CIN({}),".format(prev_cout))
                        assignments.append("        .S({}),".format(fa_s))
                        assignments.append("        .C({})".format(fa_c))
                        assignments.append("    );")
                        
                        a_bits[col] = fa_s
                        b_bits[col+1] = fa_c
                
                else:  
                    
                    if len(pp_terms) >= 4:
                        e42_s = "e42_{}_s".format(col)
                        e42_c = "e42_{}_c".format(col)
                        e42_cout = "e42_{}_cout".format(col)
                        
                        internal_wires.append("    wire {};".format(e42_s))
                        internal_wires.append("    wire {};".format(e42_c))
                        internal_wires.append("    wire {};".format(e42_cout))
                        
                        assignments.append("    E_4_2 e42_{}(".format(col))
                        assignments.append("        .a({}),".format(pp_terms[0]))
                        assignments.append("        .b({}),".format(pp_terms[1]))
                        assignments.append("        .c({}),".format(pp_terms[2]))
                        assignments.append("        .d({}),".format(pp_terms[3]))
                        assignments.append("        .CIN({}),".format(prev_cout))
                        assignments.append("        .S({}),".format(e42_s))
                        assignments.append("        .C({}),".format(e42_c))
                        assignments.append("        .COUT({})".format(e42_cout))
                        assignments.append("    );")
                        
                        a_bits[col] = e42_s
                        b_bits[col+1] = e42_c
                        prev_cout = e42_cout
                    
                    elif len(pp_terms) == 3:
                        
                        e42_s = "e42_{}_s".format(col)
                        e42_c = "e42_{}_c".format(col)
                        e42_cout = "e42_{}_cout".format(col)
                        
                        internal_wires.append("    wire {};".format(e42_s))
                        internal_wires.append("    wire {};".format(e42_c))
                        internal_wires.append("    wire {};".format(e42_cout))
                        
                        assignments.append("    E_4_2 e42_{}(".format(col))
                        assignments.append("        .a({}),".format(pp_terms[0]))
                        assignments.append("        .b({}),".format(pp_terms[1]))
                        assignments.append("        .c({}),".format(pp_terms[2]))
                        assignments.append("        .d(1'b0),")
                        assignments.append("        .CIN({}),".format(prev_cout))
                        assignments.append("        .S({}),".format(e42_s))
                        assignments.append("        .C({}),".format(e42_c))
                        assignments.append("        .COUT({})".format(e42_cout))
                        assignments.append("    );")
                        
                        a_bits[col] = e42_s
                        b_bits[col+1] = e42_c
                        prev_cout = e42_cout
                    
                    elif len(pp_terms) == 2:
                        
                        fa_s = "fa_{}_s".format(col)
                        fa_c = "fa_{}_c".format(col)
                        
                        internal_wires.append("    wire {};".format(fa_s))
                        internal_wires.append("    wire {};".format(fa_c))
                        
                        assignments.append("    Full_adder fa_{}(".format(col))
                        assignments.append("        .a({}),".format(pp_terms[0]))
                        assignments.append("        .b({}),".format(pp_terms[1]))
                        assignments.append("        .CIN({}),".format(prev_cout))
                        assignments.append("        .S({}),".format(fa_s))
                        assignments.append("        .C({})".format(fa_c))
                        assignments.append("    );")
                        
                        a_bits[col] = fa_s
                        b_bits[col+1] = fa_c
                        
                        prev_cout = "1'b0"

        
        
        a_assign = ", ".join(reversed(a_bits))
        b_assign = ", ".join(reversed(b_bits))
        
        assignments.append("    assign A = {{{}}};".format(a_assign))
        assignments.append("    assign B = {{{}}};".format(b_assign))
        
        return "\n".join(internal_wires) + "\n\n" + "\n".join(assignments) + "\n"

def generate_Appro_4_2(test_bit_widths):

    for bits in test_bit_widths:
        generator = MultiplierGeneratorArbitrary(n_bits=bits)
        verilog_code = generator.generate_verilog_code()

        filename = f"Appro4_2_{bits}bit.v"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(verilog_code)

   
