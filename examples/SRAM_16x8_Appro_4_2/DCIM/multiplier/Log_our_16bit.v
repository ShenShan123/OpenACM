`timescale 1ns / 1ps

module Log_our_16bit(
    input [15:0] x,
    input [15:0] y,
    output [31:0] p
    );
    
	wire [15:0] kx;
	wire zero_x;
	wire [3:0] code_x;


	LOD16 LODx (
		.data_i(x),
		.zero_o(zero_x),
		.data_o(kx)
	 ); 
	 

	PriorityEncoder_16 PEx (
		.data_i(kx),
		.code_o(code_x)
	 ); 
	 

	wire [15:0] ky;
	wire zero_y;
	wire [3:0] code_y;

	LOD16 LODy (
		.data_i(y),
		.zero_o(zero_y),
		.data_o(ky)
	 ); 

	PriorityEncoder_16 PEy (
			.data_i(ky),
			.code_o(code_y)
		 ); 

	wire [14:0] sub_x;
	assign sub_x = x ^ kx;	
	
 
	wire [14:0] sub_y;
	assign sub_y = y ^ ky;	

 
    wire [14:0] Q1;
    wire [14:0] Q2;
	wire [31:0] compensate;
    wire flag;

    assign flag = (sub_x > sub_y)? 1'b1 : 1'b0;
        
    assign Q1 = (flag)? sub_x : sub_y;
    assign Q2 = (flag)? sub_y : sub_x;

    wire [15:0] NOD_Q1;
    wire [3:0] K;

    NOD16 NOD
    (
        .data_i(Q1),
        .data_o(NOD_Q1)
    );
		
    PriorityEncoder_16 PE
    (
        .data_i(NOD_Q1),
        .code_o(K)
    );

	assign compensate = Q2 << K;

	wire [4:0] code_sum;
	assign code_sum = code_x + code_y;

	wire [31:0] dec_out;
	Decoder32 dec(code_sum,dec_out);

	wire [31:0] pp_x;
	assign pp_x = sub_x << code_y;

	wire [31:0] pp_y;
	assign pp_y = sub_y << code_x;
	 
	wire [31:0] tmp_pp;
	wire [31:0] pp_abs;

	assign tmp_pp = compensate | dec_out;

	assign pp_abs = tmp_pp + pp_x + pp_y;

	(* keep *)wire not_zero;
	
    assign not_zero = ~zero_x & ~zero_y;
    assign p = not_zero ? pp_abs : 32'b0;
	
endmodule



module PriorityEncoder_16(
    input [15:0] data_i,
    output [3:0] code_o
    );
    
    wire [7:0] tmp0;
    assign tmp0 = {data_i[15],data_i[13],data_i[11],data_i[9],data_i[7],data_i[5],data_i[3],data_i[1]};
    OR_tree code0(tmp0,code_o[0]);
    
    wire [7:0] tmp1;
    assign tmp1 = {data_i[15],data_i[14],data_i[11],data_i[10],data_i[7],data_i[6],data_i[3],data_i[2]};
    OR_tree code1(tmp1,code_o[1]);
    
    wire [7:0] tmp2;
    assign tmp2 = {data_i[15],data_i[14],data_i[13],data_i[12],data_i[7],data_i[6],data_i[5],data_i[4]};
    OR_tree code2(tmp2,code_o[2]);
    
    wire [7:0] tmp3;
    assign tmp3 = {data_i[15],data_i[14],data_i[13],data_i[12],data_i[11],data_i[10],data_i[9],data_i[8]};
    OR_tree code3(tmp3,code_o[3]);
endmodule


module OR_tree(
    input [7:0] data_i,
    output data_o
    );
    
    wire [3:0] tmp1;
    wire [1:0] tmp2;
    
    assign tmp1 = data_i[3:0] | data_i[7:4];
    assign tmp2 = tmp1[1:0] | tmp1[3:2];
    assign data_o = tmp2[0] | tmp2[1];
endmodule

module LOD4(
    input [3:0] data_i,
    output [3:0] data_o
    );
	 
	 
	 wire mux0;
	 wire mux1;
	 wire mux2;
	 
	 assign mux2 = (data_i[3]==1) ? 1'b0 : 1'b1;
	 assign mux1 = (data_i[2]==1) ? 1'b0 : mux2;
	 assign mux0 = (data_i[1]==1) ? 1'b0 : mux1;
	 
	 assign data_o[3] = data_i[3];
	 assign data_o[2] =(mux2 & data_i[2]);
	 assign data_o[1] =(mux1 & data_i[1]);
	 assign data_o[0] =(mux0 & data_i[0]);
	 
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

module LOD16(
    input [15:0] data_i,
    output zero_o,
    output [15:0] data_o
    );
	 
	 wire [15:0] z;
	 wire [3:0] select;
	 wire [3:0] zdet;
	 
	 assign zdet[3] = data_i[15] | data_i[14] | data_i[13] | data_i[12];
	 assign zdet[2] = data_i[11] | data_i[10] | data_i[9] | data_i[8];
	 assign zdet[1] = data_i[7] | data_i[6] | data_i[5] | data_i[4];
	 assign zdet[0] = data_i[3] | data_i[2] | data_i[1] | data_i[0];
	 assign zero_o = ~(zdet[3] | zdet[2] | zdet[1] | zdet[0]);
		 
	 LOD4 lod4_3 (
		.data_i(data_i[15:12]), 
		.data_o(z[15:12])
	 );
	 
	 LOD4 lod4_2 (
		.data_i(data_i[11:8]), 
		.data_o(z[11:8])
	 );

	 LOD4 lod4_1 (
		.data_i(data_i[7:4]), 
		.data_o(z[7:4])
	 );
	 
	 LOD4 lod4_0 (
		.data_i(data_i[3:0]), 
		.data_o(z[3:0])
	 );
	 
	 LOD4 lod4_middle (
		.data_i(zdet), 
		.data_o(select)
	 );
	 
	 
	 Muxes2in1Array4 Inst_MUX214_3 (
		.data_i(z[15:12]), 
		.select_i(select[3]), 
		.data_o(data_o[15:12])
    );
	 
	 Muxes2in1Array4 Inst_MUX214_2 (
		.data_i(z[11:8]), 
		.select_i(select[2]), 
		.data_o(data_o[11:8])
    );
	 
	 Muxes2in1Array4 Inst_MUX214_1 (
		.data_i(z[7:4]), 
		.select_i(select[1]), 
		.data_o(data_o[7:4])
    );
	 
	 Muxes2in1Array4 Inst_MUX214_0 (
		.data_i(z[3:0]), 
		.select_i(select[0]), 
		.data_o(data_o[3:0])
    );


endmodule

module Decoder32(
    input [4:0] code_i,
    output [31:0] data_o
    );
	 
	assign data_o = (1 << code_i);
endmodule

module NOD16(
    input [14:0] data_i,
    output [15:0] data_o
    );

	assign data_o[15] = data_i[14] & data_i[13];

	NOD_unit_basic nod_basic_unit15(.in0(data_i[14]),.in1(data_i[13]),.in2(data_i[12]),.out0(data_o[14]));

	wire [13:0] t_in;
	assign t_in[13] = 1'b1;
	genvar i;
    generate
        for ( i = 2; i < 14; i = i+1 )
            begin : nod_cels
            NOD_unit Nod_bits(.data_i(data_i[i+1:i-2]),.t_in(t_in[i]),.data_o(data_o[i]),.t_out(t_in[i-1]));
            end
    endgenerate

	assign t_in[0] =  t_in[1] & ~data_i[2];

	assign data_o[1] = t_in[0] & data_i[1] & ~data_i[0];

	assign data_o[0] = t_in[0] & ~data_i[1] & data_i[0];
endmodule

module NOD_unit_basic(
	input in0,
	input in1,
	input in2,
	output out0
	);

	wire tmp1,tmp2,tmp3;
	assign tmp1 = in0 & ~in1;
	assign tmp2 = in1 & in2 &(~in0);
	assign out0 = tmp1 | tmp2;

endmodule 

module NOD_unit(
	input [3:0] data_i,
	input t_in,
	output data_o,
	output t_out
	);

	wire tmp1,t_wire;
	NOD_unit_basic nod_basic_unit(.in0(data_i[2]),.in1(data_i[1]),.in2(data_i[0]),.out0(tmp1));

	assign t_wire = ~data_i[3] & t_in;
	assign t_out = t_wire;
	assign data_o = t_wire & tmp1;

endmodule 
