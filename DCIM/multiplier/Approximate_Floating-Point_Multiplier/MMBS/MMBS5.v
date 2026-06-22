`timescale 1ns / 1ps
module MMBS5 (
    input  wire [31:0] a,
    input  wire [31:0] b,
    output wire  [31:0] y
);

// ---------- 解码 ----------
wire        sa = a[31];
wire [7:0]  ea = a[30:23];
wire [22:0] ma = a[22:0];
wire        sb = b[31];
wire [7:0]  eb = b[30:23];
wire [22:0] mb = b[22:0];
wire        zero_in = (a[30:0] == 0) || (b[30:0] == 0);

wire [23:0] mx = {1'b1, ma};   // 24-bit 隐含位尾数
wire [23:0] my = {1'b1, mb};

// ---------- 指数 ----------
wire        sign = sa ^ sb ;
wire [7:0] rawExp = ea + eb - 9'd127;

// ---------- 尾数分段 ----------
wire [4:0] A = mx[23:19];
wire [18:0] C = mx[18:0];
wire [4:0] B = my[23:19];
wire [18:0] D = my[18:0];

// ---------- 精确高 5×5 ----------
wire [9:0] P_AB = A * B;

// ---------- ASA 近似交叉项 ----------
reg [4:0] lz_ad;
reg [3:0] n_ad, m_ad;
reg [4:0] sum_ad;
reg [9:0] approx_ad;
reg [4:0] shift_ad;

always @(*) begin
    if (D == 19'd0) begin
        approx_ad = 10'd0;
        lz_ad = 5'd0;
    end 
	else begin
        if      (D[18]) lz_ad = 5'd18;
        else if (D[17]) lz_ad = 5'd17;
        else if (D[16]) lz_ad = 5'd16;
        else if (D[15]) lz_ad = 5'd15;
        else if (D[14]) lz_ad = 5'd14;
        else if (D[13]) lz_ad = 5'd13;
        else if (D[12]) lz_ad = 5'd12;
        else if (D[11]) lz_ad = 5'd11;
        else if (D[10]) lz_ad = 5'd10;
        else if (D[9])  lz_ad = 5'd9;
        else if (D[8])  lz_ad = 5'd8;
        else if (D[7])  lz_ad = 5'd7;
        else if (D[6])  lz_ad = 5'd6;
        else if (D[5])  lz_ad = 5'd5;
        else if (D[4])  lz_ad = 5'd4;
        else if (D[3])  lz_ad = 5'd3;
        else if (D[2])  lz_ad = 5'd2;
        else if (D[1])  lz_ad = 5'd1;
        else if (D[0])  lz_ad = 5'd0;
        else            lz_ad = 5'd0; 
        shift_ad = (lz_ad >= 5'd4) ? (lz_ad - 5'd4) : 5'd0;
        n_ad = (D >> shift_ad) & 4'hF;
        m_ad = A[3:0]; 
        sum_ad = m_ad + n_ad;
        approx_ad = (10'h10 | sum_ad[3:0]) << (sum_ad[4] ? 5 : 4);
    end
end

// ----------------------------------------------------------
//  always 2 : 算 P_BC
// ----------------------------------------------------------
reg [4:0] lz_bc;
reg [3:0] n_bc, m_bc;
reg [4:0] sum_bc;
reg [9:0] approx_bc;
reg [4:0] shift_bc;
	
always @(*) begin
    if (C == 19'd0) begin
        approx_bc = 10'd0;
        lz_bc = 5'd0; 
    end 
	else begin
        if      (C[18]) lz_bc = 5'd18;
        else if (C[17]) lz_bc = 5'd17;
        else if (C[16]) lz_bc = 5'd16;
        else if (C[15]) lz_bc = 5'd15;
        else if (C[14]) lz_bc = 5'd14;
        else if (C[13]) lz_bc = 5'd13;
        else if (C[12]) lz_bc = 5'd12;
        else if (C[11]) lz_bc = 5'd11;
        else if (C[10]) lz_bc = 5'd10;
        else if (C[9])  lz_bc = 5'd9;
        else if (C[8])  lz_bc = 5'd8;
        else if (C[7])  lz_bc = 5'd7;
        else if (C[6])  lz_bc = 5'd6;
        else if (C[5])  lz_bc = 5'd5;
        else if (C[4])  lz_bc = 5'd4;
        else if (C[3])  lz_bc = 5'd3;
        else if (C[2])  lz_bc = 5'd2;
        else if (C[1])  lz_bc = 5'd1;
        else if (C[0])  lz_bc = 5'd0;
        else            lz_bc = 5'd0; 
        shift_bc = (lz_bc >= 5'd4) ? (lz_bc - 5'd4) : 5'd0;      
        n_bc = (C >> shift_bc) & 4'hF;
        m_bc = B[3:0]; 
        sum_bc = m_bc + n_bc;
        approx_bc = (10'h10 | sum_bc[3:0]) << (sum_bc[4] ? 5 : 4);
    end
end

// ---------- 累加 ----------
wire [47:0] total_sum =  (approx_ad << (shift_ad + 19) )+ (approx_bc << (shift_bc + 19))+(P_AB << 38);

wire        carry = total_sum[47];

// ---------- 输出 ----------
assign y[31] = zero_in ? 1'b0 : sign ;
assign y[30:23] = zero_in ? 0 : (rawExp + carry) ;
assign y[22:0] = zero_in ? 0 : (carry ? total_sum[46:24] : total_sum[45:23]); 

endmodule
