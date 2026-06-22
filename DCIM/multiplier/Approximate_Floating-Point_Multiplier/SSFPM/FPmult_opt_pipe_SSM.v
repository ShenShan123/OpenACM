`timescale 1ns / 1ps
module FPmult_opt_pipe_SSM(X,Y,M);
//Single Precision: 32bit, with 1 bit->sign,  8 bits->exponent, 23 bits->mantissa
//X=(-1)^signX * 2^esX * (1+mX)


parameter N=32;//bit-width of the digital string in Single Precision format
parameter Ne=8;//exponent bit-width
parameter Nm=23;//mantissa bit-width

parameter offset_param = 2**(Ne-1)-1;
//input clk, nrst;
input  wire [N-1:0] X,Y;
output wire [N-1:0] M;
wire zero_in;


wire signX, signY;
wire [Ne-1:0] esX, esY;

assign signX=X[N-1];//sign
assign signY=Y[N-1];

assign esX=X[N-2:(N-2)-Ne+1];//exponent
assign esY=Y[N-2:(N-2)-Ne+1];

wire [Nm-1:0] mX_tmp, mY_tmp;
assign mX_tmp=X[(N-2)-Ne:0];//mantissa
assign mY_tmp=Y[(N-2)-Ne:0];
assign zero_in = (X[N-2:0] == 0) || (Y[N-2:0] == 0);

// ************************************
// ****  FLOATING POINT MULTIPLIER ****

// ****  MANTISSA COMPUTATION ****
parameter Nm_tmp=Nm+1;
//wire [2*Nm_tmp-1:0] mM_tmp;
wire [(Nm+3)-1:0] mM_tmp;

wire sel;

wire [(Nm+2)-1:0]mM_tmp2;
wire [(Nm+2)-1:0] mM_FF;
//reg sel_FF;

MMssm_n23_m12 Mult (.a(mX_tmp), .b(mY_tmp), .ris(mM_tmp));// **** CHANGE THE MODULE NAME FOR SIMULATING OTHER MAA UNITS ****


assign mM_FF={~mM_tmp[(Nm+3)-2],mM_tmp[(Nm+3)-3:0]};
assign sel = mM_tmp[(Nm+3)-1] || mM_tmp[(Nm+3)-2]; 

/* always@(posedge clk or negedge nrst)begin
    if(nrst==1'b0)
        mM_FF<={(Nm+2){1'b0}};
    else
        mM_FF<={~mM_tmp[(Nm+3)-2],mM_tmp[(Nm+3)-3:0]};
end */



/* always@(posedge clk or negedge nrst)begin
    if(nrst==1'b0)
        sel_FF<=1'b0;
    else
        sel_FF<=sel;
end */

//normalization
assign mM_tmp2 = mM_FF + {sel,~sel};
assign M[Nm-1:0] = zero_in ? 0 : ((sel==1'b1)? mM_tmp2[(Nm+2)-1:2] : mM_tmp2[(Nm+2)-2:1]); 


// **** EXPONENT COMPUTATION ****
wire [Ne-1:0] esM_tmp;
wire [Ne-1:0] exp_offset;
//reg [Ne-1:0] esM_FF;
assign exp_offset = offset_param;
assign esM_tmp = esX + esY - exp_offset;

/* always@(posedge clk or negedge nrst)begin
    if(nrst==1'b0)
        esM_FF<={Ne{1'b0}};
    else
        esM_FF<=esM_tmp;
end */

assign M[N-2:Nm] = zero_in ? 0 : (esM_tmp + sel);



// **** SIGN COMPUTATION ****
wire s_tmp;
//reg s_FF;
assign s_tmp=signX ^ signY;

/* always@(posedge clk or negedge nrst)begin
    if(nrst==1'b0)
        s_FF<=1'b0;
    else
        s_FF<=s_tmp;
end */

assign M[N-1] = zero_in ? 1'b0 : s_tmp;


endmodule
