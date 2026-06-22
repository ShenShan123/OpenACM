`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
//  EAFPU.v
//  参数化 EAFPU：MODE=0(NC), 1(LPC), 2(HPC)
//--------------------------------------------------------
module EAFPU(
    input  wire [31:0] a,
    input  wire [31:0] b,
    output wire  [31:0] y
);

parameter MODE = 2 ;   // 0,1,2 仅允许这三个值

// ---------- 解码 ----------
wire        sa = a[31];
wire [7:0]  ea = a[30:23];
wire [22:0] mA = a[22:0];

wire        sb = b[31];
wire [7:0]  eb = b[30:23];
wire [22:0] mB = b[22:0];
wire        zero_in = (a[30:0] == 0) || (b[30:0] == 0);

// ---------- 指数 ----------
wire sign = sa ^ sb ;
wire [7:0] rawExp =  ea + eb - 9'd127;

// 固定 16-bit 截断 → 7-bit m*
wire [6:0] ma_star = mA[22:16];
wire [6:0] mb_star = mB[22:16];

// 近似和
wire [12:0] m_sum = {ma_star, 5'd0} + {mb_star, 5'd0};

// ---------- 误差修正项（参数决定） ----------
reg [11:0] corr;
reg [5:0] ah2;
reg [5:0] bh2;
always @(*)
begin
    case (MODE)
    0: corr = 12'd0;
    1: begin           // LPC 3×3
			corr = { ( {3'd0, mA[22:20]} * {3'd0, mB[22:20]} ), 6'd0 };
          end
    2: begin           // HPC 6×6
            corr = mA[22:17] * mB[22:17];
          end
    default: corr = 12'd0;
    endcase
end

// ---------- 总和 ----------
wire [13:0] sum_full ;
wire carry;
assign sum_full = corr+m_sum;

// carry 判定
assign carry = (sum_full[13] || sum_full[12]);

// ---------- 规格化 ----------
reg [13:0] m_pc;
always @(*)
begin
    if (carry)
        if (MODE == 0)
            m_pc = sum_full - 13'd4096;
        else
            m_pc = ((sum_full - 13'd4096) >> 1);
    else
        m_pc = sum_full;
end

// ---------- 输出 ----------
assign y[31] = zero_in ? 1'b0 : sign ;
assign y[30:23] = zero_in ? 0 : (rawExp + carry) ;
assign y[22:0] = zero_in ? 0 : {m_pc[11:0], 11'd0};

endmodule
