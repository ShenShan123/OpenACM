`timescale 1ns / 1ps
module V_EFPM #(
    parameter WIDTH = 32,          // 总位宽 8- 32
	parameter EXP_W = 8			//	指数位宽 3-8
)(
    input      	[WIDTH-1:0]   X,
    input      	[WIDTH-1:0]   Y,
    output  	[WIDTH-1:0]   M
);

localparam 	MAN_W = WIDTH - EXP_W - 1	;
localparam 	BIAS = (1 << (EXP_W-1)) - 1		;
localparam 	EXP_MAX = (1<<EXP_W)-1		;

reg               ovf	;  // 上溢
reg               udf  ; // 下溢

wire                					signX 	=	X[WIDTH-1]					;
wire 	[EXP_W-1:0]    	expX  	= X[WIDTH-2 -: EXP_W]	;
wire 	[MAN_W-1:0]    	manX  	= X[MAN_W-1:0]			;

wire                					signY 	= Y[WIDTH-1]					;
wire 	[EXP_W-1:0]    	expY  	= Y[WIDTH-2 -: EXP_W]	;
wire 	[MAN_W-1:0]    	manY  	= Y[MAN_W-1:0]			;

// 输入分类
wire x_zero 	= (expX==0 && manX==0)				;
wire x_inf  	= (expX==EXP_MAX && manX==0)	;
wire x_nan  	= (expX==EXP_MAX && manX!=0)	;

wire y_zero 	= (expY==0 && manY==0)				;
wire y_inf  	= (expY==EXP_MAX && manY==0)	;
wire y_nan  	= (expY==EXP_MAX && manY!=0)	;

wire signR = signX ^ signY;
reg  [EXP_W-1:0]    		expR	;
reg  [MAN_W-1:0]    	manR	;
reg                 				special	;

// 尾数乘法：隐含 1 
wire [MAN_W:0] mx =  {1'b1, manX};
wire [MAN_W:0] my =  {1'b1, manY};
wire [2*MAN_W+1:0] mul_raw = mx * my;   // 2*MAN_W+2 位

// 归一化移位量
wire        shift = mul_raw[2*MAN_W+1];   // 1 表示要右移 1 位
wire [2*MAN_W+1:0] mul_norm = shift ? (mul_raw >> 1) : mul_raw;

// 指数计算
wire signed [EXP_W+1:0] exp_raw =expX+expY-BIAS+shift;   // 右移→指数+1
        
// 舍入：round-to-nearest-even
localparam ROUND_BIT 	= MAN_W			;
localparam GUARD     		= ROUND_BIT-1	;
localparam STICKY    			= ROUND_BIT-2	;

wire round 	= mul_norm[GUARD]			;
wire sticky 	= |mul_norm[STICKY:0]		;
wire lsb 		= mul_norm[ROUND_BIT]	;
wire inc 		= round & (sticky | lsb)		;

wire [MAN_W+1:0] man_round = mul_norm[2*MAN_W+1 -: MAN_W+2] + {{(MAN_W+1){1'b0}}, inc };
wire exp_inc = man_round[MAN_W+1];   // 舍入后尾数溢出
wire [MAN_W+1:0] mul_final = exp_inc ? (man_round >> 1) : man_round;

wire signed [EXP_W+1:0] exp_rounded = exp_raw + { {EXP_W+1{1'b0}}, exp_inc };
wire [EXP_W-1:0] exp_final =
      (exp_rounded >= EXP_MAX) ? EXP_MAX :
      (exp_rounded <= 0) ? 8'd0 : exp_rounded[EXP_W-1:0];
								 
wire expOvf = exp_rounded >= EXP_MAX;
wire expUdf = exp_rounded < 0;
// 默认结果
always @(*) begin
    // 特殊值处理
    if (x_nan | y_nan) 
	begin
        special = 1'b1;
        expR = EXP_MAX;
		manR = {1'b1, {(MAN_W-1){1'b0}}};   
    end
    else if ((x_inf & y_zero) | (y_inf & x_zero))
	begin
        special = 1'b1;
        expR = EXP_MAX;
		manR = {1'b1, {(MAN_W-1){1'b0}}};   
    end
    else if (x_inf | y_inf) begin
        special = 1'b1;
        expR = EXP_MAX;
        manR = 0;
        ovf = 1'b1;
    end
    else if (x_zero | y_zero) begin
        special = 1'b1;
        expR = 0;
        manR = 0;
    end
    else if (expOvf) begin
        special = 1'b1;
        expR = EXP_MAX;
        manR = 0;
        ovf = 1'b1;
    end
    else if (expUdf) begin
        special = 1'b1;
        expR = 0;
        manR = 0;
        udf = 1'b1;
    end
	else begin
		special = 1'b0;
		ovf     = 1'b0;
		udf     = 1'b0;
		expR    = exp_final[EXP_W-1:0];
		manR    = mul_final[MAN_W-1:0];
	end
end

assign M = {signR, expR, manR} ;

endmodule
