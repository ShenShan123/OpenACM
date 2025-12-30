import math
import sys

class MultiplierGenerator:
    def __init__(self, N=8):
        self.N = N
        self.k_bits = self.calculate_k_bits(N)
        self.output_width = 2 * N
    
    def calculate_k_bits(self, N):
        """Calculate priority encoder output bit width"""
        if N <= 1:
            return 1
        return math.ceil(math.log2(N))
    
    def generate_verilog(self):
        """Generate complete Verilog code"""
        code = f"""// Auto-generated {self.N}-bit Approximate Logarithmic Multiplier
// Bit Width: {self.N}, Priority Encoder Bits: {self.k_bits}, Output Width: {self.output_width}

"""
        # Generate modules in dependency order
        code += self.generate_base_modules()
        code += self.generate_or_trees()
        code += self.generate_lod_modules()
        code += self.generate_priority_encoder()
        code += self.generate_nod_module()
        code += self.generate_decoder()
        code += self.generate_pim_multiplier()
        
        return code
    
    def generate_base_modules(self):
        """Generate base modules"""
        return """
module LOD2(
    input [1:0] data_i,
    output [1:0] data_o
);
    assign data_o[1] = data_i[1];
    assign data_o[0] = ~data_i[1] & data_i[0];
endmodule

module LOD4(
    input [3:0] data_i,
    output [3:0] data_o
);
    wire mux0, mux1, mux2;
    
    assign mux2 = (data_i[3]==1) ? 1'b0 : 1'b1;
    assign mux1 = (data_i[2]==1) ? 1'b0 : mux2;
    assign mux0 = (data_i[1]==1) ? 1'b0 : mux1;
    
    assign data_o[3] = data_i[3];
    assign data_o[2] = (mux2 & data_i[2]);
    assign data_o[1] = (mux1 & data_i[1]);
    assign data_o[0] = (mux0 & data_i[0]);
endmodule

module Muxes2in1Array4(
    input [3:0] data_i,
    input select_i,
    output [3:0] data_o
);
    assign data_o[3] = select_i ? data_i[3] : 1'b0;
    assign data_o[2] = select_i ? data_i[2] : 1'b0;
    assign data_o[1] = select_i ? data_i[1] : 1'b0;
    assign data_o[0] = select_i ? data_i[0] : 1'b0;

endmodule

module NOD_unit_basic(
    input in0,
    input in1,
    input in2,
    output out0
);
    wire tmp1, tmp2;
    assign tmp1 = in0 & ~in1;
    assign tmp2 = in1 & in2 & (~in0);
    assign out0 = tmp1 | tmp2;
endmodule

module NOD_unit(
    input [3:0] data_i,
    input t_in,
    output data_o,
    output t_out
);
    wire tmp1, t_wire;
    NOD_unit_basic nod_basic_unit(
        .in0(data_i[2]),
        .in1(data_i[1]), 
        .in2(data_i[0]),
        .out0(tmp1)
    );
    assign t_wire = ~data_i[3] & t_in;
    assign t_out = t_wire;
    assign data_o = t_wire & tmp1;
endmodule
"""
    
    def generate_or_tree_recursive(self, size, level=0):
        """Recursively generate OR_tree module for any power-of-2 bit width"""
        if size == 1:
            return "    assign data_o = data_i[0];\n"
        elif size == 2:
            return "    assign data_o = data_i[0] | data_i[1];\n"
        else:
            half_size = size // 2
            
            # Generate recursive code
            code = f"    wire [1:0] tmp{level};\n"
            code += f"    assign tmp{level}[0] = |data_i[{half_size-1}:0];\n"
            code += f"    assign tmp{level}[1] = |data_i[{size-1}:{half_size}];\n"
            code += f"    assign data_o = tmp{level}[0] | tmp{level}[1];\n"
            
            return code
    
    def generate_or_tree_module(self, size):
        """Generate complete OR_tree module"""
        if size == 1:
            return f"""
module OR_tree_{size}(
    input [0:0] data_i,
    output data_o
);
    assign data_o = data_i[0];
endmodule
"""
        elif size == 2:
            return f"""
module OR_tree_{size}(
    input [1:0] data_i,
    output data_o
);
    assign data_o = data_i[0] | data_i[1];
endmodule
"""
        else:
            # Check if it's a power of 2
            if (size & (size - 1)) == 0:
                # It's a power of 2, use recursive generation
                inner_code = self.generate_or_tree_recursive(size)
                
                return f"""
module OR_tree_{size}(
    input [{size-1}:0] data_i,
    output data_o
);
{inner_code}
endmodule
"""
            else:
                # If not a power of 2, use simplified implementation
                return f"""
module OR_tree_{size}(
    input [{size-1}:0] data_i,
    output data_o
);
    assign data_o = |data_i;
endmodule
"""
    
    def generate_or_trees(self):
        """Generate all required OR_tree modules"""
        # Determine which OR_tree sizes are needed
        sizes_needed = set()
        
        # OR_tree sizes needed for priority encoder
        # Fix: When N is a power of 2, each OR_tree size is N/2
        for i in range(self.k_bits):
            count = 0
            for j in range(self.N):
                if (j >> i) & 1:  # Check if the i-th bit of index j is 1
                    count += 1
            if count > 0:
                # If N is a power of 2, prioritize using N/2 size
                if (self.N & (self.N - 1)) == 0 and count == self.N // 2:
                    sizes_needed.add(self.N // 2)
                else:
                    sizes_needed.add(count)
        
        # Ensure basic sizes exist
        sizes_needed.add(2)
        sizes_needed.add(4)
        if self.N >= 8:
            # Fix: When N>=8, ensure N/2 size exists (if N is a power of 2)
            if (self.N & (self.N - 1)) == 0 and self.N >= 8:
                sizes_needed.add(self.N // 2)
            else:
                sizes_needed.add(8)
        if self.N >= 16:
            if (self.N & (self.N - 1)) == 0 and self.N >= 16:
                sizes_needed.add(self.N // 2)
            else:
                sizes_needed.add(16)
        if self.N >= 32:
            if (self.N & (self.N - 1)) == 0 and self.N >= 32:
                sizes_needed.add(self.N // 2)
            else:
                sizes_needed.add(32)
        
        # Generate all required OR_tree modules
        code = ""
        generated_sizes = set()
        
        for size in sorted(sizes_needed):
            if size not in generated_sizes:
                code += self.generate_or_tree_module(size)
                generated_sizes.add(size)
        
        return code
    
    def generate_lod_module(self, size):
        """Recursively generate LOD module for any bit width"""
        if size <= 4:
            # Base case: use existing LOD2 or LOD4
            if size == 2:
                return ""
            elif size == 4:
                return ""
            else:
                # For other small sizes, use simplified LOD implementation
                return f"""
    module LOD{size}(
        input [{size-1}:0] data_i,
        output zero_o,
        output [{size-1}:0] data_o
    );
        // Simplified LOD for small sizes
        assign zero_o = ~(|data_i);
    endmodule
    """
        
        # Recursively decompose into smaller LOD modules
        # Prioritize 4-bit grouping (consistent with example)
        if size % 4 == 0:
            num_groups = size // 4
            code = f"""
    module LOD{size}(
        input [{size-1}:0] data_i,
        output zero_o,
        output [{size-1}:0] data_o
    );
        wire [{size-1}:0] z;
        wire [{num_groups-1}:0] select;
        wire [{num_groups-1}:0] zdet;
        """
            
            # Generate zero detection signals
            for i in range(num_groups):
                start = i * 4
                end = start + 3
                code += f"""
        assign zdet[{i}] = data_i[{end}] | data_i[{end-1}] | data_i[{end-2}] | data_i[{start}];"""
            
            code += f"""
        assign zero_o = ~(|zdet);
        
        // Sub-LODs"""
            
            # Generate sub-LOD instances
            for i in range(num_groups):
                start = i * 4
                end = start + 3
                code += f"""
        LOD4 lod4_{i}(
            .data_i(data_i[{end}:{start}]), 
            .data_o(z[{end}:{start}])
        );"""
            
            code += f"""
        
        // Select signal generation"""
            
            # Generate select signal generator
            if num_groups == 4:
                code += """
        LOD4 lod4_middle(
            .data_i(zdet), 
            .data_o(select)
        );"""
            elif num_groups == 3:
                code += """
        // For 3 groups, use custom selection logic
        wire [2:0] select;
        assign select[2] = zdet[2];
        assign select[1] = ~zdet[2] & zdet[1];
        assign select[0] = ~zdet[2] & ~zdet[1] & zdet[0];"""
            elif num_groups == 2:
                code += """
        LOD2 select_gen(
            .data_i(zdet), 
            .data_o(select)
        );"""
            else:
                # For more than 4 groups, recursively generate selector
                code += f"""
        LOD{num_groups} select_gen(
            .data_i(zdet), 
            .data_o(select)
        );"""
            
            code += """
        
        // Multiplexers"""
            
            # Generate multiplexer instances
            for i in range(num_groups):
                start = i * 4
                end = start + 3
                code += f"""
        Muxes2in1Array4 Inst_MUX214_{i}(
            .data_i(z[{end}:{start}]), 
            .select_i(select[{i}]), 
            .data_o(data_o[{end}:{start}])
        );"""
            
            code += """
    endmodule
    """
            return code
        else:
            # For sizes not divisible by 4, use binary recursion
            half_size = size // 2
            return f"""
module LOD{size}(
    input [{size-1}:0] data_i,
    output zero_o,
    output [{size-1}:0] data_o
);
    wire [{half_size-1}:0] high_data, low_data;
    wire high_zero, low_zero;
    wire [1:0] zdet;
    wire [1:0] select;
    
    LOD{half_size} lod_high(.data_i(data_i[{size-1}:{half_size}]), .zero_o(high_zero), .data_o(high_data));
    LOD{half_size} lod_low(.data_i(data_i[{half_size-1}:0]), .zero_o(low_zero), .data_o(low_data));
    
    assign zdet[1] = ~high_zero;
    assign zdet[0] = ~low_zero;
    assign zero_o = high_zero & low_zero;
    
    LOD2 select_gen(.data_i(zdet), .data_o(select));
    
    assign data_o = select[1] ? {{high_data, {{{half_size}{{1'b0}}}}}} : 
                                 {{{{half_size}}{{1'b0}}}}, low_data}};
endmodule
"""

    def generate_lod_modules(self):
        """Generate LOD modules"""
        code = ""
        
        # Generate LOD modules required for current bit width
        current_size = self.N
        generated_sizes = set()
        
        # First generate smaller dependency modules
        sizes_to_generate = []
        temp_size = current_size
        while temp_size > 4:
            sizes_to_generate.append(temp_size)
            if temp_size % 4 == 0:
                temp_size = temp_size // 4
            else:
                temp_size = temp_size // 2
        
        # Generate in ascending order (ensuring dependencies)
        for size in reversed(sizes_to_generate):
            if size not in generated_sizes:
                code += self.generate_lod_module(size)
                generated_sizes.add(size)
        
        return code
        
    
    def generate_priority_encoder(self):
        """Generate priority encoder"""
        signal_assignments = ""
        or_tree_calls = ""
        
        for i in range(self.k_bits):
            # Collect all input indices where the i-th bit is 1
            selected_indices = []
            for j in range(self.N):
                if (j >> i) & 1:  # Check if the i-th bit of index j is 1
                    selected_indices.append(j)
            
            if selected_indices:
                # Sort in descending order to ensure high bits come first
                selected_indices.sort(reverse=True)
                signals = ", ".join([f"data_i[{idx}]" for idx in selected_indices])
                signal_assignments += f"    wire [{len(selected_indices)-1}:0] tmp{i};\n"
                signal_assignments += f"    assign tmp{i} = {{{signals}}};\n"
                
                # Generate OR tree call
                or_tree_calls += f"    OR_tree_{len(selected_indices)} pe_{i}(.data_i(tmp{i}), .data_o(code_o[{i}]));\n"
            else:
                or_tree_calls += f"    assign code_o[{i}] = 1'b0;\n"
        
        return f"""
module PriorityEncoder_{self.N}(
    input [{self.N-1}:0] data_i,
    output [{self.k_bits-1}:0] code_o
);
{signal_assignments}
{or_tree_calls}
endmodule
"""
    
    def generate_nod_module(self):
        """Generate NOD module"""
        if self.N < 3:
            return ""
        
        return f"""
module NOD{self.N}(
    input [{self.N-2}:0] data_i,  // Input bit width is N-1
    output [{self.N-1}:0] data_o
);
    // Highest bit processing
    assign data_o[{self.N-1}] = data_i[{self.N-2}] & data_i[{self.N-3}];
    
    NOD_unit_basic nod_basic_unit_top(
        .in0(data_i[{self.N-2}]), 
        .in1(data_i[{self.N-3}]), 
        .in2(data_i[{self.N-4}]), 
        .out0(data_o[{self.N-2}])
    );
    
    // Middle bit processing
    wire [{self.N-3}:0] t_in;
    assign t_in[{self.N-3}] = 1'b1;
    
    genvar i;
    generate
        for (i = 2; i < {self.N-2}; i = i + 1) begin : nod_cells
            NOD_unit Nod_bits(
                .data_i(data_i[i+1:i-2]),
                .t_in(t_in[i]),
                .data_o(data_o[i]),
                .t_out(t_in[i-1])
            );
        end
    endgenerate
    
    // Lowest bit processing
    assign t_in[0] = t_in[1] & ~data_i[2];
    assign data_o[1] = t_in[0] & data_i[1] & ~data_i[0];
    assign data_o[0] = t_in[0] & ~data_i[1] & data_i[0];
endmodule
"""
    
    def generate_decoder(self):
        """Generate decoder"""
        return f"""
module Decoder_{self.N*2}(
    input [{self.k_bits}:0] code_i,
    output [{self.output_width-1}:0] data_o
);
    assign data_o = (1'b1 << code_i);
endmodule
"""
    
    
    def generate_pim_multiplier(self):
        """Generate PIM multiplier"""
        return f"""
module Log_our_{self.N}bit(
    input [{self.N-1}:0] x,
    input [{self.N-1}:0] y,
    output [{self.output_width-1}:0] p
);
    // LOD for x
    wire [{self.N-1}:0] kx;
    wire zero_x;
    wire [{self.k_bits-1}:0] code_x;

    LOD{self.N} LOD_x(
        .data_i(x),
        .zero_o(zero_x),
        .data_o(kx)
    );

    PriorityEncoder_{self.N} PE_x(
        .data_i(kx),
        .code_o(code_x)
    );

    // LOD for y
    wire [{self.N-1}:0] ky;
    wire zero_y;
    wire [{self.k_bits-1}:0] code_y;

    LOD{self.N} LOD_y(
        .data_i(y),
        .zero_o(zero_y),
        .data_o(ky)
    );

    PriorityEncoder_{self.N} PE_y(
        .data_i(ky),
        .code_o(code_y)
    );

    // N-2K computation (using N-1 bits)
    wire [{self.N-2}:0] sub_x, sub_y;
    assign sub_x = (x ^ kx);
    assign sub_y = (y ^ ky);

    // Compensation logic
    wire [{self.N-2}:0] Q1, Q2;
    wire [{self.output_width-1}:0] compensate;
    wire flag;

    assign flag = (sub_x > sub_y) ? 1'b1 : 1'b0;

    assign Q1 = (flag) ? sub_x : sub_y;
    assign Q2 = (flag) ? sub_y : sub_x;

    // NOD processing
    wire [{self.N-1}:0] NOD_Q1;
    wire [{self.k_bits-1}:0] K;

    NOD{self.N} NOD_inst(
        .data_i(Q1),
        .data_o(NOD_Q1)
    );

    PriorityEncoder_{self.N} PE_comp(
        .data_i(NOD_Q1),
        .code_o(K)
    );

    // Compensation term
    assign compensate = Q2 << K;

    // Decoder for k_x + k_y
    wire [{self.k_bits}:0] code_sum;
    wire [{self.output_width-1}:0] dec_out;

    assign code_sum = code_x + code_y;
    Decoder_{self.N*2} decoder(
        .code_i(code_sum),
        .data_o(dec_out)
    );

    // Partial product generation
    wire [{self.output_width-1}:0] pp_x, pp_y;
    assign pp_x = sub_x << code_y;
    assign pp_y = sub_y << code_x;

    // Final product computation
    wire [{self.output_width-1}:0] tmp_pp, pp_abs;
    assign tmp_pp = compensate | dec_out;
    assign pp_abs = tmp_pp + pp_x + pp_y;

    // Zero detection and output
    wire not_zero;
    assign not_zero = ~zero_x & ~zero_y;
    assign p = not_zero ? pp_abs : {self.output_width}'b0;

endmodule
"""

def generate_Log(test_bit_widths):
    
    for bits in test_bit_widths:
        generator = MultiplierGenerator(N=bits)
        verilog_code = generator.generate_verilog()
        
        filename = "Log_our_{}bit.v".format(bits)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(verilog_code)

