`timescale 1ns / 1ps

module Log_our_8bit(
    input [7:0] x,
    input [7:0] y,
    output [15:0] p
    );

	wire [7:0] kx;
	wire zero_x;
	wire [2:0] code_x;    

    LOD8 LODx (
		.data_i(x),
		.zero_o(zero_x),
		.data_o(kx)
	 ); 
	 

	PriorityEncoder_8 PEx (
		.data_i(kx),
		.code_o(code_x)
	 ); 


	wire [7:0] ky;
	wire zero_y;
	wire [2:0] code_y;

	LOD8 LODy (
		.data_i(y),
		.zero_o(zero_y),
		.data_o(ky)
	 ); 

	PriorityEncoder_8 PEy (
			.data_i(ky),
			.code_o(code_y)
		 ); 
    
    wire [6:0] sub_x;
	assign sub_x = x ^ kx;	
	
	wire [6:0] sub_y;
	assign sub_y = y ^ ky;

    wire [6:0] Q1;
    wire [6:0] Q2;
	wire [15:0] compensate;
    wire flag;

    assign flag = (sub_x > sub_y)? 1'b1 : 1'b0;
        
    assign Q1 = (flag)? sub_x : sub_y;
    assign Q2 = (flag)? sub_y : sub_x;

    wire [7:0] NOD_Q1;
    wire [2:0] K;

    NOD8 NOD
    (
        .data_i(Q1),
        .data_o(NOD_Q1)
    );
		
    PriorityEncoder_8 PE
    (
        .data_i(NOD_Q1),
        .code_o(K)
    );
    
    assign compensate = Q2 << K;
    
	wire [3:0] code_sum;
	assign code_sum = code_x + code_y;

	wire [15:0] dec_out;
	Decoder16 dec(code_sum,dec_out);

	wire [15:0] pp_x;
	assign pp_x = sub_x << code_y;

	wire [15:0] pp_y;
	assign pp_y = sub_y << code_x;
	 
	wire [15:0] tmp_pp;
	wire [15:0] pp_abs;
	
	assign tmp_pp = compensate | dec_out;

	assign pp_abs = tmp_pp + pp_x + pp_y;
	
	wire not_zero;
    
    assign not_zero = ~zero_x & ~zero_y;
    
    assign p = not_zero ? pp_abs : 16'b0;
    
endmodule


module LOD8(
    input [7:0] data_i,
    output zero_o,
    output [7:0] data_o
    );
	
    wire [7:0] z;
    wire [1:0] zdet;
    wire [1:0] select;

    assign zdet[1] = |(data_i[7:4]) ;
    assign zdet[0] = |(data_i[3:0]);
    assign zero_o = ~( zdet[1] | zdet[0]);

    LOD4 lod2_1 (
        .data_i(data_i[7:4]), 
        .data_o(z[7:4])
        );
    LOD4 lod2_0 (
        .data_i(data_i[3:0]), 
        .data_o(z[3:0])
        );
  
    LOD2 Middle(
        .data_i(zdet), 
        .data_o(select)       
    );

	wire [7:0] tmp_out;
	

	Muxes2in1Array4 Inst_MUX214_1 (
        .data_i(z[7:4]), 
        .select_i(select[1]), 
        .data_o(tmp_out[7:4])
    );

    Muxes2in1Array4 Inst_MUX214_0 (
        .data_i(z[3:0]), 
        .select_i(select[0]), 
        .data_o(tmp_out[3:0])
    );

    assign data_o = tmp_out;

    
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

module LOD2(
    input [1:0] data_i,
    output [1:0] data_o
    );
	 
    assign data_o[1] = data_i[1];
    assign data_o[0] = ~data_i[1] & data_i[0];

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

module PriorityEncoder_8(
    input [7:0] data_i,
    output [2:0] code_o
    );
    
    wire [3:0] tmp0;
    assign tmp0 = {data_i[7],data_i[5],data_i[3],data_i[1]};
    OR_tree code0(tmp0,code_o[0]);
    
    wire [3:0] tmp1;
    assign tmp1 = {data_i[7],data_i[6],data_i[3],data_i[2]};
    OR_tree code1(tmp1,code_o[1]);
    
    wire [3:0] tmp2;
    assign tmp2 = {data_i[7],data_i[6],data_i[5],data_i[4]};
    OR_tree code2(tmp2,code_o[2]);
    

endmodule

module OR_tree(
    input [3:0] data_i,
    output data_o
    );
    
    wire [1:0] tmp1;
    
    assign tmp1 = data_i[1:0] | data_i[3:2];
    assign data_o = tmp1[0] | tmp1[1];
endmodule

module Decoder16(
    input [3:0] code_i,
    output [15:0] data_o
    );
	 
	assign data_o = (1 << code_i);
endmodule

module NOD8(
    input [6:0] data_i,
    output [7:0] data_o
    );

	assign data_o[7] = data_i[6] & data_i[5];

	NOD_unit_basic nod_basic_unit15(.in0(data_i[6]),.in1(data_i[5]),.in2(data_i[4]),.out0(data_o[6]));

	wire [5:0] t_in;
	assign t_in[5] = 1'b1;
	
	genvar i;
    generate
        for ( i = 2; i < 6; i = i+1 )
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
