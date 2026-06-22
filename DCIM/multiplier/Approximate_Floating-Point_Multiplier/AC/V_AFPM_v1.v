`timescale 1ns / 1ps
module V_AFPM_v1#(
    parameter WIDTH 	= 32		,       	// 	总位宽16-32
	parameter EXP_W 	= 8		,			//		指数位宽5-8
	parameter n 			= 4		,			//		截取位宽3-6
	parameter mode	=	0					//		模式选择(0:低精度 、1：中精度、2：高精度)
)(
    input  		wire 	[WIDTH-1:0] x,
    input  		wire 	[WIDTH-1:0] y,
    output 	wire  	[WIDTH-1:0] z
);

localparam TOTAL 		= (mode + 1)*n				;//TOTAL<MAN_W
localparam MAN_W 	= WIDTH - EXP_W - 1		;	//尾数位宽
localparam BIAS 		= (1 << (EXP_W-1)) - 1	;//基数
//============================================================================
// 1. 解析输入
//============================================================================
wire      						sx		, sy		;
wire   	[EXP_W-1:0]  	ex		, ey		;
wire 	[MAN_W-1:0] 	mx	, my		;
wire   	[n-1:0]  			A, B, C, D		;
wire                            zero_in     ;

wire do_AC,do_AD,do_BC	;
wire 				ad_nonzero	;
wire					bc_nonzero	;

wire        					sign				;
wire  [EXP_W-1:0]  	exp_unbias	;

assign sx 	= x[WIDTH-1]		;
assign sy 	= y[WIDTH-1]		;
assign ex 	= x[WIDTH-2 -: EXP_W]	;
assign ey 	= y[WIDTH-2 -: EXP_W]	;
assign mx 	= x[MAN_W-1:0]		;
assign my 	= y[MAN_W-1:0]		;
assign zero_in = (x[WIDTH-2:0] == 0) || (y[WIDTH-2:0] == 0);

assign sign = sx ^ sy;
assign exp_unbias =  ex + ey - BIAS;

assign  A = mx[MAN_W-1 -: n]		;
assign  B = mx[MAN_W-1-n -: n]	;
assign  C = my[MAN_W-1 -: n]		;
assign  D = my[MAN_W-1-n -: n]	;

assign ad_nonzero = (A != 0) && (D != 0);
assign bc_nonzero = (B != 0) && (C != 0);

assign do_AC = (A != 0) && (C != 0);
assign do_AD = ((D[n-1:2] != 0) || (C == 0)) && ((A != 0)&&(D != 0));
assign do_BC = ((B[n-1:2] != 0) || (A == 0)) && ((C != 0)&&(B != 0));
//============================================================================
// 2. 计算部分积，误差补偿项
//============================================================================
wire  [2*n-1:0]  p_AC;
reg  [2*n-1:0]   p_AD, p_BC;
reg [TOTAL+1:0] total_sum;

assign p_AC = do_AC ? A * C : 0;

always @(*)
begin
	if (mode == 0)
		total_sum = mx[MAN_W-1 -: TOTAL] + my[MAN_W-1 -: TOTAL]+(A&C);
    else if (mode == 1)
	begin
		p_AD = do_AD ? A[n-1 -: n-1]  :  (ad_nonzero ? A[n-1] :0);
		p_BC = do_BC ? C[n-1 -: n-1] : (bc_nonzero ? C[n-1] :0);
		total_sum = p_AC+p_AD+p_BC+mx[MAN_W-1 -: TOTAL] + my[MAN_W-1 -: TOTAL];
	end
    else begin
		p_AD = do_AD ? A * D :  (ad_nonzero ? {A, 1'b0} :0);
		p_BC = do_BC ? B * C : (bc_nonzero ? {C, 1'b0} :0);
		total_sum = (p_AC<<n)+p_AD+p_BC+mx[MAN_W-1 -: TOTAL] + my[MAN_W-1 -: TOTAL];
	end
end
//============================================================================
// 3. 结果
//============================================================================
wire sel;

assign sel = total_sum[TOTAL+1] || total_sum[TOTAL]; 

assign z[WIDTH-1] = zero_in ? 1'b0 : sign ;
assign z[WIDTH-2 -: EXP_W] = zero_in ? 0 : (exp_unbias + sel) ;

generate
    if (mode == 0) begin : gen_mode0_mantissa
        reg [TOTAL-1:0] m_pc;
        always @(*) begin
            if (sel)
                m_pc = ((total_sum - (1<<TOTAL)) >> 1);
            else
                m_pc = total_sum[TOTAL-1:0];
        end
        assign z[MAN_W-1:0] = zero_in ? 0 : (m_pc<<(MAN_W-TOTAL));
    end
    else begin : gen_other_mode_mantissa
        assign z[MAN_W-1:0] = zero_in ? 0 : (sel ? {~total_sum[TOTAL],total_sum[TOTAL-1:0]}<<(MAN_W-TOTAL-1) : total_sum[TOTAL-1:0]<<(MAN_W-TOTAL)); 
    end
endgenerate

endmodule
