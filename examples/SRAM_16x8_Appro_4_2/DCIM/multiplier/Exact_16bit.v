`timescale 1ns / 1ps

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
    assign COUT = ((a ^ b) & c) |  (~(a ^ b) & a);
    assign C = (part & CIN) | (~part & d);
endmodule

module Full_adder(
  input a,
  input b,
  input CIN,
  output S,
  output C
    );
    wire S1 , T1, T2, T3;
    
    xor x1 (S1,a,b);
    xor x2 (S,S1,CIN);
    
    and A1 (T3,a,b);
    and A2 (T2,b,CIN);
    and A3 (T1,a,CIN);
    
    or O1 (C,T1,T2,T3);
endmodule

module Half_adder(
  input a,
  input b,
  output S,
  output C
    );
    

    xor x1 (S,a,b);
    and x2 (C,a,b);
endmodule

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
    assign C[0] = (A[0] & B[0]) || ((A[0] ^ B[0]) & Cin);
    assign C[1] = (A[1] & B[1]) || ((A[1] ^ B[1]) & C[0]);
    assign C[2] = (A[2] & B[2]) || ((A[2] ^ B[2]) & C[1]);
    assign C[3] = (A[3] & B[3]) || ((A[3] ^ B[3]) & C[2]);
    assign Cout = C[3];

endmodule

module CLA16bit (
    input [15:0] A, 
    input [15:0] B, 
    input Cin, 
    output [15:0] Sum, 
    output Cout 
);

wire c1, c2, c3;

CLA4bit cla1
(
    .A(A[3:0]),
    .B(B[3:0]),
    .Cin(Cin),
    .Sum(Sum[3:0]),
    .Cout(c1)
);

CLA4bit cla2
(
    .A(A[7:4]),
    .B(B[7:4]),
    .Cin(c1),
    .Sum(Sum[7:4]),
    .Cout(c2)
);

CLA4bit cla3
(
    .A(A[11:8]),
    .B(B[11:8]),
    .Cin(c2),
    .Sum(Sum[11:8]),
    .Cout(c3)
);

CLA4bit cla4
(
    .A(A[15:12]),
    .B(B[15:12]),
    .Cin(c3),
    .Sum(Sum[15:12]),
    .Cout(Cout)
);


endmodule

module CLA32bit (
    input [31:0] A, 
    input [31:0] B, 
    input Cin, 
    output [31:0] Sum, 
    output Cout 
);

wire c1;

CLA16bit cla1
(
    .A(A[15:0]),
    .B(B[15:0]),
    .Cin(Cin),
    .Sum(Sum[15:0]),
    .Cout(c1)
);

CLA16bit cla2
(
    .A(A[31:16]),
    .B(B[31:16]),
    .Cin(c1),
    .Sum(Sum[31:16]),
    .Cout(Cout)
);

endmodule

module Exact_16bit(
    input [15:0] N1,
    input [15:0] N2,
    output [31:0] P_APPROX
    );

    wire pp_0;
    wire [1:0] pp_1;
    wire [2:0] pp_2;
    wire [3:0] pp_3; 
    wire [4:0] pp_4;
    wire [5:0] pp_5;
    wire [6:0] pp_6;
    wire [7:0] pp_7;    
    wire [7:0] pp_8;
    wire [7:0] pp_9;
    wire [7:0] pp_10;
    wire [7:0] pp_11;
    wire [7:0] pp_12;
    wire [7:0] pp_13;
    wire [7:0] pp_14;
    wire [7:0] pp_15;
    wire [7:0] pp_16;   
    wire [7:0] pp_17;
    wire [7:0] pp_18;
    wire [7:0] pp_19;
    wire [7:0] pp_20;
    wire [7:0] pp_21;
    wire [7:0] pp_22;
    wire [7:0] pp_23;
    wire [7:0] pp_24;
    wire [5:0] pp_25;
    wire [4:0] pp_26;
    wire [3:0] pp_27;
    wire [2:0] pp_28;
    wire [1:0] pp_29;
    wire pp_30;
    
    wire s_0;
    wire [1:0] s_1;
    wire [2:0] s_2;
    wire [3:0] s_3; 
    wire [3:0] s_4;
    wire [3:0] s_5;
    wire [3:0] s_6;
    wire [3:0] s_7;   
    wire [3:0] s_8;
    wire [3:0] s_9;
    wire [3:0] s_10;
    wire [3:0] s_11;
    wire [3:0] s_12;
    wire [3:0] s_13;
    wire [3:0] s_14;
    wire [3:0] s_15;
    wire [3:0] s_16;   
    wire [3:0] s_17;
    wire [3:0] s_18;
    wire [3:0] s_19;
    wire [3:0] s_20;
    wire [3:0] s_21;
    wire [3:0] s_22;
    wire [3:0] s_23;
    wire [3:0] s_24;
    wire [3:0] s_25;
    wire [3:0] s_26;
    wire [3:0] s_27;
    wire [3:0] s_28;
    wire [1:0] s_29;
    wire s_30;
    
    
    
    STAGE1 STAGE1
    (
        .A(N1),
        .B(N2),
       .pp_0(pp_0),
       .pp_1(pp_1),
       .pp_2(pp_2),
       .pp_3(pp_3), 
       .pp_4(pp_4),
       .pp_5(pp_5),
       .pp_6(pp_6),
       .pp_7(pp_7),
       .pp_8(pp_8),
       .pp_9(pp_9),
       .pp_10(pp_10),
       .pp_11(pp_11),
       .pp_12(pp_12),
       .pp_13(pp_13),
       .pp_14(pp_14),    
       .pp_15(pp_15),
       .pp_16(pp_16),
       .pp_17(pp_17),
       .pp_18(pp_18), 
       .pp_19(pp_19),
       .pp_20(pp_20),
       .pp_21(pp_21),
       .pp_22(pp_22),
       .pp_23(pp_23),
       .pp_24(pp_24),
       .pp_25(pp_25),
       .pp_26(pp_26),
       .pp_27(pp_27),
       .pp_28(pp_28),
       .pp_29(pp_29),
       .pp_30(pp_30)       
    );
    
    STAGE2 STAGE2
    (
       .s_0(pp_0),
       .s_1(pp_1),
       .s_2(pp_2),
       .s_3(pp_3), 
       .s_4(pp_4),
       .s_5(pp_5),
       .s_6(pp_6),
       .s_7(pp_7),
       .s_8(pp_8),
       .s_9(pp_9),
       .s_10(pp_10),
       .s_11(pp_11),
       .s_12(pp_12),
       .s_13(pp_13),
       .s_14(pp_14),    
       .s_15(pp_15),
       .s_16(pp_16),
       .s_17(pp_17),
       .s_18(pp_18), 
       .s_19(pp_19),
       .s_20(pp_20),
       .s_21(pp_21),
       .s_22(pp_22),
       .s_23(pp_23),
       .s_24(pp_24),
       .s_25(pp_25),
       .s_26(pp_26),
       .s_27(pp_27),
       .s_28(pp_28),
       .s_29(pp_29),
       .s_30(pp_30),       
       .pp_0(s_0),
       .pp_1(s_1),
       .pp_2(s_2),
       .pp_3(s_3), 
       .pp_4(s_4),
       .pp_5(s_5),
       .pp_6(s_6),
       .pp_7(s_7),
       .pp_8(s_8),
       .pp_9(s_9),
       .pp_10(s_10),
       .pp_11(s_11),
       .pp_12(s_12),
       .pp_13(s_13),
       .pp_14(s_14),    
       .pp_15(s_15),
       .pp_16(s_16),
       .pp_17(s_17),
       .pp_18(s_18), 
       .pp_19(s_19),
       .pp_20(s_20),
       .pp_21(s_21),
       .pp_22(s_22),
       .pp_23(s_23),
       .pp_24(s_24),
       .pp_25(s_25),
       .pp_26(s_26),
       .pp_27(s_27),
       .pp_28(s_28),
       .pp_29(s_29),
       .pp_30(s_30)       
    );
    
    STAGE3 STAGE3(
       .pp_0(s_0),
       .pp_1(s_1),
       .pp_2(s_2),
       .pp_3(s_3), 
       .pp_4(s_4),
       .pp_5(s_5),
       .pp_6(s_6),
       .pp_7(s_7),
       .pp_8(s_8),
       .pp_9(s_9),
       .pp_10(s_10),
       .pp_11(s_11),
       .pp_12(s_12),
       .pp_13(s_13),
       .pp_14(s_14),    
       .pp_15(s_15),
       .pp_16(s_16),
       .pp_17(s_17),
       .pp_18(s_18), 
       .pp_19(s_19),
       .pp_20(s_20),
       .pp_21(s_21),
       .pp_22(s_22),
       .pp_23(s_23),
       .pp_24(s_24),
       .pp_25(s_25),
       .pp_26(s_26),
       .pp_27(s_27),
       .pp_28(s_28),
       .pp_29(s_29),
       .pp_30(s_30),
       .approx(P_APPROX)        
    );
endmodule

module STAGE1(
    input [15:0] A,
    input [15:0] B,
    output pp_0,
    output [1:0] pp_1,
    output [2:0] pp_2,
    output [3:0] pp_3, 
    output [4:0] pp_4,
    output [5:0] pp_5,
    output [6:0] pp_6,
    output [7:0] pp_7,
    
    output [7:0] pp_8,
    output [7:0] pp_9,
    output [7:0] pp_10,
    output [7:0] pp_11,
    output [7:0] pp_12,
    output [7:0] pp_13,
    output [7:0] pp_14,
    output [7:0] pp_15,
    output [7:0] pp_16,   
    output [7:0] pp_17,
    output [7:0] pp_18,
    output [7:0] pp_19,
    output [7:0] pp_20,
    output [7:0] pp_21,
    output [7:0] pp_22,
    output [7:0] pp_23,
    output [7:0] pp_24,
    output [5:0] pp_25,
    output [4:0] pp_26,
    output [3:0] pp_27,
    output [2:0] pp_28,
    output [1:0] pp_29,
    output pp_30          
    );
    wire pp_8_s;
    wire pp_8_c;
    wire pp_9_s;
    wire pp_9_c1;
    wire pp_9_c2;
    wire pp_10_s1;
    wire pp_10_c1;
    wire pp_10_c2;
    wire pp_10_s2;
    wire pp_10_c3;
    wire pp_11_s1;
    wire pp_11_c1;
    wire pp_11_c2;
    wire pp_11_s2;
    wire pp_11_c3;
    wire pp_11_c4;
    wire pp_12_s1;
    wire pp_12_c1;
    wire pp_12_c2;
    wire pp_12_s2;
    wire pp_12_c3;
    wire pp_12_c4;
    wire pp_12_s3;
    wire pp_12_c5;
    wire pp_13_s1;
    wire pp_13_c1;
    wire pp_13_c2;
    wire pp_13_s2;
    wire pp_13_c3;
    wire pp_13_c4;
    wire pp_13_s3;
    wire pp_13_c5;
    wire pp_13_c6;
    
    wire pp_14_s1;
    wire pp_14_c1;
    wire pp_14_c2;
    wire pp_14_s2;
    wire pp_14_c3;
    wire pp_14_c4;
    wire pp_14_s3;
    wire pp_14_c5;
    wire pp_14_c6;
    wire pp_14_s4;
    wire pp_14_c7;
    
    wire pp_15_s1;
    wire pp_15_c1;
    wire pp_15_c2;
    wire pp_15_s2;
    wire pp_15_c3;
    wire pp_15_c4;
    wire pp_15_s3;
    wire pp_15_c5;
    wire pp_15_c6;
    wire pp_15_s4;
    wire pp_15_c7;
    wire pp_15_c8;
    
    wire pp_16_s1;
    wire pp_16_c1;
    wire pp_16_c2;
    wire pp_16_s2;
    wire pp_16_c3;
    wire pp_16_c4;
    wire pp_16_s3;
    wire pp_16_c5;
    wire pp_16_c6;
    wire pp_16_s4;
    wire pp_16_c7;
    wire pp_16_c8;
    
    wire pp_17_s1;
    wire pp_17_c1;
    wire pp_17_c2;
    wire pp_17_s2;
    wire pp_17_c3;
    wire pp_17_c4;
    wire pp_17_s3;
    wire pp_17_c5;
    wire pp_17_c6;
    wire pp_17_s4;
    wire pp_17_c7;
    
    wire pp_18_s1;
    wire pp_18_c1;
    wire pp_18_c2;
    wire pp_18_s2;
    wire pp_18_c3;
    wire pp_18_c4;
    wire pp_18_s3;
    wire pp_18_c5;
    wire pp_18_c6;
    
    wire pp_19_s1;
    wire pp_19_c1;
    wire pp_19_c2;
    wire pp_19_s2;
    wire pp_19_c3;
    wire pp_19_c4;
    wire pp_19_s3;
    wire pp_19_c5;
    
    wire pp_20_s1;
    wire pp_20_c1;
    wire pp_20_c2;
    wire pp_20_s2;
    wire pp_20_c3;
    wire pp_20_c4;
    
    wire pp_21_s1;
    wire pp_21_c1;
    wire pp_21_c2;
    wire pp_21_s2;
    wire pp_21_c3;
    
    wire pp_22_s1;
    wire pp_22_c1;
    wire pp_22_c2;
    
    wire pp_23_s;
    wire pp_23_c;
 
   
    assign pp_0 = A[0] & B[0];
    assign pp_1 = {A[1] & B[0],A[0] & B[1]};
    assign pp_2 = {A[2] & B[0],A[1] & B[1],A[0] & B[2]};
    assign pp_3 = {A[3] & B[0],A[2] & B[1],A[1] & B[2],A[0] & B[3]};
    assign pp_4 = {A[4] & B[0],A[3] & B[1],A[2] & B[2],A[1] & B[3],A[0] & B[4]};
    assign pp_5 = {A[5] & B[0],A[4] & B[1],A[3] & B[2],A[2] & B[3],A[1] & B[4],A[0] & B[5]};
    assign pp_6 = {A[6] & B[0],A[5] & B[1],A[4] & B[2],A[3] & B[3],A[2] & B[4],A[1] & B[5],A[0] & B[6]};
    assign pp_7 = {A[7] & B[0],A[6] & B[1],A[5] & B[2],A[4] & B[3],A[3] & B[4],A[2] & B[5],A[1] & B[6],A[0] & B[7]};
    assign pp_8 = {A[8] & B[0],A[7] & B[1],A[6] & B[2],A[5] & B[3],A[4] & B[4],A[3] & B[5],A[2] & B[6],pp_8_s};
    assign pp_9 = {A[9] & B[0],A[8] & B[1],A[7] & B[2],A[6] & B[3],A[5] & B[4],A[4] & B[5],pp_8_c,pp_9_s};
    assign pp_10 = {A[10] & B[0],A[9] & B[1],A[8] & B[2],A[7] & B[3],A[6] & B[4],pp_9_c1,pp_10_s1,pp_10_s2};
    assign pp_11 = {A[11] & B[0],A[10] & B[1],A[9] & B[2],A[8] & B[3],pp_10_c3,pp_10_c1,pp_11_s1,pp_11_s2};
    assign pp_12 = {A[12] & B[0],A[11] & B[1],A[10] & B[2],pp_11_c1,pp_11_c3,pp_12_s1,pp_12_s2,pp_12_s3};
    assign pp_13 = {A[13] & B[0],A[12] & B[1],pp_12_c1,pp_12_c3,pp_12_c5,pp_13_s1,pp_13_s2,pp_13_s3};
    assign pp_14 = {A[14] & B[0],pp_13_c1,pp_13_c3,pp_13_c5,pp_14_s1,pp_14_s2,pp_14_s3,pp_14_s4};
    assign pp_15 = {pp_14_c1,pp_14_c3,pp_14_c5,pp_14_c7,pp_15_s1,pp_15_s2,pp_15_s3,pp_15_s4};
    assign pp_16 = {pp_15_c1,pp_15_c3,pp_15_c5,pp_15_c7,pp_16_s1,pp_16_s2,pp_16_s3,pp_16_s4};
    assign pp_17 = {pp_16_c1,pp_16_c3,pp_16_c5,pp_16_c7,pp_17_s1,pp_17_s2,pp_17_s3,pp_17_s4};
    assign pp_18 = {A[15] & B[3],pp_17_c1,pp_17_c3,pp_17_c5,pp_17_c7,pp_18_s1,pp_18_s2,pp_18_s3};
    assign pp_19 = {A[15] & B[4],pp_18_c1,pp_18_c3,pp_18_c5,pp_18_c6,pp_19_s1,pp_19_s2,pp_19_s3};
    assign pp_20 = {A[15] & B[5],A[14] & B[6],A[13] & B[7],pp_19_c1,pp_19_c3,pp_19_c5,pp_20_s1,pp_20_s2};
    assign pp_21 = {A[15] & B[6],A[14] & B[7],A[13] & B[8],pp_20_c1,pp_20_c3,pp_20_c4,pp_21_s1,pp_21_s2};
    assign pp_22 = {A[15] & B[7],A[14] & B[8],A[13] & B[9],A[12] & B[10],A[11] & B[11],pp_21_c1,pp_21_c3,pp_22_s1};
    assign pp_23 = {A[15] & B[8],A[14] & B[9],A[13] & B[10],A[12] & B[11],A[11] & B[12],pp_22_c1,pp_22_c2,pp_23_s};
    assign pp_24 = {A[15] & B[9],A[14] & B[10],A[13] & B[11],A[12] & B[12],A[11] & B[13],A[10] & B[14],A[9] & B[15],pp_23_c};
    assign pp_25 = {A[15] & B[10],A[14] & B[11],A[13] & B[12],A[12] & B[13],A[11] & B[14],A[10] & B[15]};
    assign pp_26 = {A[15] & B[11],A[14] & B[12],A[13] & B[13],A[12] & B[14],A[11] & B[15]};
    assign pp_27 = {A[15] & B[12],A[14] & B[13],A[13] & B[14],A[12] & B[15]};
    assign pp_28 = {A[15] & B[13],A[14] & B[14],A[13] & B[15]};
    assign pp_29 = {A[15] & B[14],A[14] & B[15]};
    assign pp_30 = {A[15] & B[15]};
    Half_adder Half_adder_pp_8(
        .a(A[0] & B[8]),
        .b(A[1] & B[7]),
        .S(pp_8_s),
        .C(pp_8_c)
    );
    
    E_4_2 E_4_2_pp_9(
        .a(A[0] & B[9]),
        .b(A[1] & B[8]),
        .c(A[2] & B[7]),
        .d(A[3] & B[6]),
        .CIN(1'b0),
        .S(pp_9_s),
        .C(pp_9_c1),
        .COUT(pp_9_c2)
    );
    
    E_4_2 E_4_2_pp_10(
        .a(A[0] & B[10]),
        .b(A[1] & B[9]),
        .c(A[2] & B[8]),
        .d(A[3] & B[7]),
        .CIN(pp_9_c2),
        .S(pp_10_s1),
        .C(pp_10_c1),
        .COUT(pp_10_c2)
    );
    
    Half_adder Half_adder_pp_10(
        .a(A[4] & B[6]),
        .b(A[5] & B[5]),
        .S(pp_10_s2),
        .C(pp_10_c3)
    );
    
    E_4_2 E_4_2_pp_11_1(
        .a(A[0] & B[11]),
        .b(A[1] & B[10]),
        .c(A[2] & B[9]),
        .d(A[3] & B[8]),
        .CIN(pp_10_c2),
        .S(pp_11_s1),
        .C(pp_11_c1),
        .COUT(pp_11_c2)
    );
    
    E_4_2 E_4_2_pp_11_2(
        .a(A[4] & B[7]),
        .b(A[5] & B[6]),
        .c(A[6] & B[5]),
        .d(A[7] & B[4]),
        .CIN(1'b0),
        .S(pp_11_s2),
        .C(pp_11_c3),
        .COUT(pp_11_c4)
    );
    
    E_4_2 E_4_2_pp_12_1(
        .a(A[0] & B[12]),
        .b(A[1] & B[11]),
        .c(A[2] & B[10]),
        .d(A[3] & B[9]),
        .CIN(pp_11_c2),
        .S(pp_12_s1),
        .C(pp_12_c1),
        .COUT(pp_12_c2)
    );
    
    E_4_2 E_4_2_pp_12_2(
        .a(A[4] & B[8]),
        .b(A[5] & B[7]),
        .c(A[6] & B[6]),
        .d(A[7] & B[5]),
        .CIN(pp_11_c4),
        .S(pp_12_s2),
        .C(pp_12_c3),
        .COUT(pp_12_c4)
    );
    
    Half_adder Half_adder_pp_12(
        .a(A[8] & B[4]),
        .b(A[9] & B[3]),
        .S(pp_12_s3),
        .C(pp_12_c5)
    );
    
    E_4_2 E_4_2_pp_13_1(
        .a(A[0] & B[13]),
        .b(A[1] & B[12]),
        .c(A[2] & B[11]),
        .d(A[3] & B[10]),
        .CIN(pp_12_c2),
        .S(pp_13_s1),
        .C(pp_13_c1),
        .COUT(pp_13_c2)
    );
    
    E_4_2 E_4_2_pp_13_2(
        .a(A[4] & B[9]),
        .b(A[5] & B[8]),
        .c(A[6] & B[7]),
        .d(A[7] & B[6]),
        .CIN(pp_12_c4),
        .S(pp_13_s2),
        .C(pp_13_c3),
        .COUT(pp_13_c4)
    );
    
    E_4_2 E_4_2_pp_13_3(
        .a(A[8] & B[5]),
        .b(A[9] & B[4]),
        .c(A[10] & B[3]),
        .d(A[11] & B[2]),
        .CIN(1'b0),
        .S(pp_13_s3),
        .C(pp_13_c5),
        .COUT(pp_13_c6)
    );
    
    E_4_2 E_4_2_pp_14_1(
        .a(A[0] & B[14]),
        .b(A[1] & B[13]),
        .c(A[2] & B[12]),
        .d(A[3] & B[11]),
        .CIN(pp_13_c2),
        .S(pp_14_s1),
        .C(pp_14_c1),
        .COUT(pp_14_c2)
    );
    
    E_4_2 E_4_2_pp_14_2(
        .a(A[4] & B[10]),
        .b(A[5] & B[9]),
        .c(A[6] & B[8]),
        .d(A[7] & B[7]),
        .CIN(pp_13_c4),
        .S(pp_14_s2),
        .C(pp_14_c3),
        .COUT(pp_14_c4)
    );
    
    E_4_2 E_4_2_pp_14_3(
        .a(A[8] & B[6]),
        .b(A[9] & B[5]),
        .c(A[10] & B[4]),
        .d(A[11] & B[3]),
        .CIN(pp_13_c6),
        .S(pp_14_s3),
        .C(pp_14_c5),
        .COUT(pp_14_c6)
    );
    
    Half_adder Half_adder_pp_14(
        .a(A[12] & B[2]),
        .b(A[13] & B[1]),
        .S(pp_14_s4),
        .C(pp_14_c7)
    );
    
    E_4_2 E_4_2_pp_15_1(
        .a(A[0] & B[15]),
        .b(A[1] & B[14]),
        .c(A[2] & B[13]),
        .d(A[3] & B[12]),
        .CIN(pp_14_c2),
        .S(pp_15_s1),
        .C(pp_15_c1),
        .COUT(pp_15_c2)
    );
    
    E_4_2 E_4_2_pp_15_2(
        .a(A[4] & B[11]),
        .b(A[5] & B[10]),
        .c(A[6] & B[9]),
        .d(A[7] & B[8]),
        .CIN(pp_14_c4),
        .S(pp_15_s2),
        .C(pp_15_c3),
        .COUT(pp_15_c4)
    );
    
    E_4_2 E_4_2_pp_15_3(
        .a(A[8] & B[7]),
        .b(A[9] & B[6]),
        .c(A[10] & B[5]),
        .d(A[11] & B[4]),
        .CIN(pp_14_c6),
        .S(pp_15_s3),
        .C(pp_15_c5),
        .COUT(pp_15_c6)
    );
    
    E_4_2 E_4_2_pp_15_4(
        .a(A[12] & B[3]),
        .b(A[13] & B[2]),
        .c(A[14] & B[1]),
        .d(A[15] & B[0]),
        .CIN(1'b0),
        .S(pp_15_s4),
        .C(pp_15_c7),
        .COUT(pp_15_c8)
    );
    
    E_4_2 E_4_2_pp_16_1(
        .a(A[1] & B[15]),
        .b(A[2] & B[14]),
        .c(A[3] & B[13]),
        .d(A[4] & B[12]),
        .CIN(pp_15_c2),
        .S(pp_16_s1),
        .C(pp_16_c1),
        .COUT(pp_16_c2)
    );
    
    E_4_2 E_4_2_pp_16_2(
        .a(A[5] & B[11]),
        .b(A[6] & B[10]),
        .c(A[7] & B[9]),
        .d(A[8] & B[8]),
        .CIN(pp_15_c4),
        .S(pp_16_s2),
        .C(pp_16_c3),
        .COUT(pp_16_c4)
    );
    
    E_4_2 E_4_2_pp_16_3(
        .a(A[9] & B[7]),
        .b(A[10] & B[6]),
        .c(A[11] & B[5]),
        .d(A[12] & B[4]),
        .CIN(pp_15_c6),
        .S(pp_16_s3),
        .C(pp_16_c5),
        .COUT(pp_16_c6)
    );
    
    E_4_2 E_4_2_pp_16_4(
        .a(A[13] & B[3]),
        .b(A[14] & B[2]),
        .c(A[15] & B[1]),
        .d(pp_15_c8),
        .CIN(1'b0),
        .S(pp_16_s4),
        .C(pp_16_c7),
        .COUT(pp_16_c8)
    );
    
    E_4_2 E_4_2_pp_17_1(
        .a(A[2] & B[15]),
        .b(A[3] & B[14]),
        .c(A[4] & B[13]),
        .d(A[5] & B[12]),
        .CIN(pp_16_c2),
        .S(pp_17_s1),
        .C(pp_17_c1),
        .COUT(pp_17_c2)
    );
    
    E_4_2 E_4_2_pp_17_2(
        .a(A[6] & B[11]),
        .b(A[7] & B[10]),
        .c(A[8] & B[9]),
        .d(A[9] & B[8]),
        .CIN(pp_16_c4),
        .S(pp_17_s2),
        .C(pp_17_c3),
        .COUT(pp_17_c4)
    );
    
    E_4_2 E_4_2_pp_17_3(
        .a(A[10] & B[7]),
        .b(A[11] & B[6]),
        .c(A[12] & B[5]),
        .d(A[13] & B[4]),
        .CIN(pp_16_c6),
        .S(pp_17_s3),
        .C(pp_17_c5),
        .COUT(pp_17_c6)
    );
    
    Full_adder Full_adder_pp_17(
        .a(A[14] & B[3]),
        .b(A[15] & B[2]),
        .CIN(pp_16_c8),
        .S(pp_17_s4),
        .C(pp_17_c7)
    );
    
    E_4_2 E_4_2_pp_18_1(
        .a(A[3] & B[15]),
        .b(A[4] & B[14]),
        .c(A[5] & B[13]),
        .d(A[6] & B[12]),
        .CIN(pp_17_c2),
        .S(pp_18_s1),
        .C(pp_18_c1),
        .COUT(pp_18_c2)
    );
    
    E_4_2 E_4_2_pp_18_2(
        .a(A[7] & B[11]),
        .b(A[8] & B[10]),
        .c(A[9] & B[9]),
        .d(A[10] & B[8]),
        .CIN(pp_17_c4),
        .S(pp_18_s2),
        .C(pp_18_c3),
        .COUT(pp_18_c4)
    );
    
    E_4_2 E_4_2_pp_18_3(
        .a(A[11] & B[7]),
        .b(A[12] & B[6]),
        .c(A[13] & B[5]),
        .d(A[14] & B[4]),
        .CIN(pp_17_c6),
        .S(pp_18_s3),
        .C(pp_18_c5),
        .COUT(pp_18_c6)
    );
    
    E_4_2 E_4_2_pp_19_1(
        .a(A[4] & B[15]),
        .b(A[5] & B[14]),
        .c(A[6] & B[13]),
        .d(A[7] & B[12]),
        .CIN(pp_18_c2),
        .S(pp_19_s1),
        .C(pp_19_c1),
        .COUT(pp_19_c2)
    );
    
    E_4_2 E_4_2_pp_19_2(
        .a(A[8] & B[11]),
        .b(A[9] & B[10]),
        .c(A[10] & B[9]),
        .d(A[11] & B[8]),
        .CIN(pp_18_c4),
        .S(pp_19_s2),
        .C(pp_19_c3),
        .COUT(pp_19_c4)
    );
    
    Full_adder Full_adder_pp_19(
        .a(A[12] & B[7]),
        .b(A[13] & B[6]),
        .CIN(A[14] & B[5]),
        .S(pp_19_s3),
        .C(pp_19_c5)
    );
    
    E_4_2 E_4_2_pp_20_1(
        .a(A[5] & B[15]),
        .b(A[6] & B[14]),
        .c(A[7] & B[13]),
        .d(A[8] & B[12]),
        .CIN(pp_19_c2),
        .S(pp_20_s1),
        .C(pp_20_c1),
        .COUT(pp_20_c2)
    );
    
    E_4_2 E_4_2_pp_20_2(
        .a(A[9] & B[11]),
        .b(A[10] & B[10]),
        .c(A[11] & B[9]),
        .d(A[12] & B[8]),
        .CIN(pp_19_c4),
        .S(pp_20_s2),
        .C(pp_20_c3),
        .COUT(pp_20_c4)
    );
    
    E_4_2 E_4_2_pp_21_1(
        .a(A[6] & B[15]),
        .b(A[7] & B[14]),
        .c(A[8] & B[13]),
        .d(A[9] & B[12]),
        .CIN(pp_20_c2),
        .S(pp_21_s1),
        .C(pp_21_c1),
        .COUT(pp_21_c2)
    );
    
    Full_adder Full_adder_pp_21(
        .a(A[10] & B[11]),
        .b(A[11] & B[10]),
        .CIN(A[12] & B[9]),
        .S(pp_21_s2),
        .C(pp_21_c3)
    );
    
    E_4_2 E_4_2_pp_22(
        .a(A[7] & B[15]),
        .b(A[8] & B[14]),
        .c(A[9] & B[13]),
        .d(A[10] & B[12]),
        .CIN(pp_21_c2),
        .S(pp_22_s1),
        .C(pp_22_c1),
        .COUT(pp_22_c2)
    );
    
    Full_adder Full_adder_pp_23(
        .a(A[8] & B[15]),
        .b(A[9] & B[14]),
        .CIN(A[10] & B[13]),
        .S(pp_23_s),
        .C(pp_23_c)
    );
    
endmodule

module STAGE2(
    input s_0,
    input [1:0] s_1,
    input [2:0] s_2,
    input [3:0] s_3, 
    input [4:0] s_4,
    input [5:0] s_5,
    input [6:0] s_6,
    input [7:0] s_7,              
    input [7:0] s_8,
    input [7:0] s_9,
    input [7:0] s_10,
    input [7:0] s_11,
    input [7:0] s_12,
    input [7:0] s_13,
    input [7:0] s_14,
    input [7:0] s_15,
    input [7:0] s_16,   
    input [7:0] s_17,
    input [7:0] s_18,
    input [7:0] s_19,
    input [7:0] s_20,
    input [7:0] s_21,
    input [7:0] s_22,
    input [7:0] s_23,
    input [7:0] s_24,
    input [5:0] s_25,
    input [4:0] s_26,
    input [3:0] s_27,
    input [2:0] s_28,
    input [1:0] s_29,
    input s_30,
    output pp_0,
    output [1:0] pp_1,
    output [2:0] pp_2,
    output [3:0] pp_3, 
    output [3:0] pp_4,
    output [3:0] pp_5,
    output [3:0] pp_6,
    output [3:0] pp_7,
    
    output [3:0] pp_8,
    output [3:0] pp_9,
    output [3:0] pp_10,
    output [3:0] pp_11,
    output [3:0] pp_12,
    output [3:0] pp_13,
    output [3:0] pp_14,
    output [3:0] pp_15,
    output [3:0] pp_16,   
    output [3:0] pp_17,
    output [3:0] pp_18,
    output [3:0] pp_19,
    output [3:0] pp_20,
    output [3:0] pp_21,
    output [3:0] pp_22,
    output [3:0] pp_23,
    output [3:0] pp_24,
    output [3:0] pp_25,
    output [3:0] pp_26,
    output [3:0] pp_27,
    output [3:0] pp_28,
    output [1:0] pp_29,
    output pp_30
    );
    
    wire pp_4_s;
    wire pp_4_c;
    wire pp_5_s;
    wire pp_5_c1;
    wire pp_5_c2;
    wire pp_6_s1;
    wire pp_6_c1;
    wire pp_6_c2;
    wire pp_6_s2;
    wire pp_6_c3;
    wire pp_7_s1;
    wire pp_7_c1;
    wire pp_7_c2;
    wire pp_7_s2;
    wire pp_7_c3;
    wire pp_7_c4;
    
    wire pp_8_s1;
    wire pp_8_c1;
    wire pp_8_c2;
    wire pp_8_s2;
    wire pp_8_c3;
    wire pp_8_c4;
    
    wire pp_9_s1;
    wire pp_9_c1;
    wire pp_9_c2;
    wire pp_9_s2;
    wire pp_9_c3;
    wire pp_9_c4;
    
    wire pp_10_s1;
    wire pp_10_c1;
    wire pp_10_c2;
    wire pp_10_s2;
    wire pp_10_c3;
    wire pp_10_c4;
    
    wire pp_11_s1;
    wire pp_11_c1;
    wire pp_11_c2;
    wire pp_11_s2;
    wire pp_11_c3;
    wire pp_11_c4;
    
    wire pp_12_s1;
    wire pp_12_c1;
    wire pp_12_c2;
    wire pp_12_s2;
    wire pp_12_c3;
    wire pp_12_c4;
    
    wire pp_13_s1;
    wire pp_13_c1;
    wire pp_13_c2;
    wire pp_13_s2;
    wire pp_13_c3;
    wire pp_13_c4;
    
    wire pp_14_s1;
    wire pp_14_c1;
    wire pp_14_c2;
    wire pp_14_s2;
    wire pp_14_c3;
    wire pp_14_c4;
    
    wire pp_15_s1;
    wire pp_15_c1;
    wire pp_15_c2;
    wire pp_15_s2;
    wire pp_15_c3;
    wire pp_15_c4;
      
    wire pp_16_s1;
    wire pp_16_c1;
    wire pp_16_c2;
    wire pp_16_s2;
    wire pp_16_c3;
    wire pp_16_c4;
    
    wire pp_17_s1;
    wire pp_17_c1;
    wire pp_17_c2;
    wire pp_17_s2;
    wire pp_17_c3;
    wire pp_17_c4;
    
    wire pp_18_s1;
    wire pp_18_c1;
    wire pp_18_c2;
    wire pp_18_s2;
    wire pp_18_c3;
    wire pp_18_c4;
    
    wire pp_19_s1;
    wire pp_19_c1;
    wire pp_19_c2;
    wire pp_19_s2;
    wire pp_19_c3;
    wire pp_19_c4;
    
    
    wire pp_20_s1;
    wire pp_20_c1;
    wire pp_20_c2;
    wire pp_20_s2;
    wire pp_20_c3;
    wire pp_20_c4;  
  
    wire pp_21_s1;
    wire pp_21_c1;
    wire pp_21_c2;
    wire pp_21_s2;
    wire pp_21_c3;
    wire pp_21_c4;  
  
    wire pp_22_s1;
    wire pp_22_c1;
    wire pp_22_c2;
    wire pp_22_s2;
    wire pp_22_c3;
    wire pp_22_c4;
    
    wire pp_23_s1;
    wire pp_23_c1;
    wire pp_23_c2;
    wire pp_23_s2;
    wire pp_23_c3;
    wire pp_23_c4;
    
    wire pp_24_s1;
    wire pp_24_c1;
    wire pp_24_c2;
    wire pp_24_s2;
    wire pp_24_c3;
    wire pp_24_c4;
    
    wire pp_25_s1;
    wire pp_25_c1;
    wire pp_25_c2;
    wire pp_25_s2;
    wire pp_25_c3;
    
    wire pp_26_s;
    wire pp_26_c1;
    wire pp_26_c2;
    
    wire pp_27_s;
    wire pp_27_c;
    
    
    
    assign pp_0 = s_0;
    assign pp_1 = s_1;
    assign pp_2 = s_2;
    assign pp_3 = s_3;
    assign pp_4 = {s_4[4:2],pp_4_s};
    assign pp_5 = {s_5[5:4],pp_4_c,pp_5_s};
    assign pp_6 = {s_6[6],pp_5_c1,pp_6_s1,pp_6_s2};
    assign pp_7 = {pp_7_s1,pp_7_s2,pp_6_c1,pp_6_c3};
    assign pp_8 = {pp_8_s1,pp_8_s2,pp_7_c1,pp_7_c3};
    assign pp_9 = {pp_9_s1,pp_9_s2,pp_8_c1,pp_8_c3};
    assign pp_10 = {pp_10_s1,pp_10_s2,pp_9_c1,pp_9_c3};
    assign pp_11 = {pp_11_s1,pp_11_s2,pp_10_c1,pp_10_c3};
    assign pp_12 = {pp_12_s1,pp_12_s2,pp_11_c1,pp_11_c3};
    assign pp_13 = {pp_13_s1,pp_13_s2,pp_12_c1,pp_12_c3};
    assign pp_14 = {pp_14_s1,pp_14_s2,pp_13_c1,pp_13_c3};
    assign pp_15 = {pp_15_s1,pp_15_s2,pp_14_c1,pp_14_c3};
    assign pp_16 = {pp_16_s1,pp_16_s2,pp_15_c1,pp_15_c3};
    assign pp_17 = {pp_17_s1,pp_17_s2,pp_16_c1,pp_16_c3};
    assign pp_18 = {pp_18_s1,pp_18_s2,pp_17_c1,pp_17_c3};
    assign pp_19 = {pp_19_s1,pp_19_s2,pp_18_c1,pp_18_c3};
    assign pp_20 = {pp_20_s1,pp_20_s2,pp_19_c1,pp_19_c3};
    assign pp_21 = {pp_21_s1,pp_21_s2,pp_20_c1,pp_20_c3};
    assign pp_22 = {pp_22_s1,pp_22_s2,pp_21_c1,pp_21_c3};
    assign pp_23 = {pp_23_s1,pp_23_s2,pp_22_c1,pp_22_c3};
    assign pp_24 = {pp_24_s1,pp_24_s2,pp_23_c1,pp_23_c3};
    assign pp_25 = {pp_25_s1,pp_25_s2,pp_24_c1,pp_24_c3};
    assign pp_26 = {s_26[4],pp_26_s,pp_25_c1,pp_25_c3};
    assign pp_27 = {s_27[3],pp_27_s,pp_26_c1,pp_26_c2};
    assign pp_28 = {s_28,pp_27_c};
    assign pp_29 = s_29;
    assign pp_30 = s_30;
    
    Half_adder Half_adder_pp_4(
        .a(s_4[0]),
        .b(s_4[1]),
        .S(pp_4_s),
        .C(pp_4_c)
    );
    
    E_4_2 E_4_2_pp_5(
        .a(s_5[0]),
        .b(s_5[1]),
        .c(s_5[2]),
        .d(s_5[3]),
        .CIN(1'b0),
        .S(pp_5_s),
        .C(pp_5_c1),
        .COUT(pp_5_c2)
    );
    
    E_4_2 E_4_2_pp_6(
        .a(s_6[0]),
        .b(s_6[1]),
        .c(s_6[2]),
        .d(s_6[3]),
        .CIN(pp_5_c2),
        .S(pp_6_s1),
        .C(pp_6_c1),
        .COUT(pp_6_c2)
    );
    
    Half_adder Half_adder_pp_6(
        .a(s_6[4]),
        .b(s_6[5]),
        .S(pp_6_s2),
        .C(pp_6_c3)
    );
    
    E_4_2 E_4_2_pp_7_1(
        .a(s_7[0]),
        .b(s_7[1]),
        .c(s_7[2]),
        .d(s_7[3]),
        .CIN(pp_6_c2),
        .S(pp_7_s1),
        .C(pp_7_c1),
        .COUT(pp_7_c2)
    );
    
    E_4_2 E_4_2_pp_7_2(
        .a(s_7[4]),
        .b(s_7[5]),
        .c(s_7[6]),
        .d(s_7[7]),
        .CIN(1'b0),
        .S(pp_7_s2),
        .C(pp_7_c3),
        .COUT(pp_7_c4)
    );
    
    E_4_2 E_4_2_pp_8_1(
        .a(s_8[0]),
        .b(s_8[1]),
        .c(s_8[2]),
        .d(s_8[3]),
        .CIN(pp_7_c2),
        .S(pp_8_s1),
        .C(pp_8_c1),
        .COUT(pp_8_c2)
    );
    
    E_4_2 E_4_2_pp_8_2(
        .a(s_8[4]),
        .b(s_8[5]),
        .c(s_8[6]),
        .d(s_8[7]),
        .CIN(pp_7_c4),
        .S(pp_8_s2),
        .C(pp_8_c3),
        .COUT(pp_8_c4)
    );
    
    E_4_2 E_4_2_pp_9_1(
        .a(s_9[0]),
        .b(s_9[1]),
        .c(s_9[2]),
        .d(s_9[3]),
        .CIN(pp_8_c2),
        .S(pp_9_s1),
        .C(pp_9_c1),
        .COUT(pp_9_c2)
    );
    
    E_4_2 E_4_2_pp_9_2(
        .a(s_9[4]),
        .b(s_9[5]),
        .c(s_9[6]),
        .d(s_9[7]),
        .CIN(pp_8_c4),
        .S(pp_9_s2),
        .C(pp_9_c3),
        .COUT(pp_9_c4)
    );
    
    E_4_2 E_4_2_pp_10_1(
        .a(s_10[0]),
        .b(s_10[1]),
        .c(s_10[2]),
        .d(s_10[3]),
        .CIN(pp_9_c2),
        .S(pp_10_s1),
        .C(pp_10_c1),
        .COUT(pp_10_c2)
    );
    
    E_4_2 E_4_2_pp_10_2(
        .a(s_10[4]),
        .b(s_10[5]),
        .c(s_10[6]),
        .d(s_10[7]),
        .CIN(pp_9_c4),
        .S(pp_10_s2),
        .C(pp_10_c3),
        .COUT(pp_10_c4)
    );
    
    E_4_2 E_4_2_pp_11_1(
        .a(s_11[0]),
        .b(s_11[1]),
        .c(s_11[2]),
        .d(s_11[3]),
        .CIN(pp_10_c2),
        .S(pp_11_s1),
        .C(pp_11_c1),
        .COUT(pp_11_c2)
    );
    
    E_4_2 E_4_2_pp_11_2(
        .a(s_11[4]),
        .b(s_11[5]),
        .c(s_11[6]),
        .d(s_11[7]),
        .CIN(pp_10_c4),
        .S(pp_11_s2),
        .C(pp_11_c3),
        .COUT(pp_11_c4)
    );
    
    E_4_2 E_4_2_pp_12_1(
        .a(s_12[0]),
        .b(s_12[1]),
        .c(s_12[2]),
        .d(s_12[3]),
        .CIN(pp_11_c2),
        .S(pp_12_s1),
        .C(pp_12_c1),
        .COUT(pp_12_c2)
    );
    
    E_4_2 E_4_2_pp_12_2(
        .a(s_12[4]),
        .b(s_12[5]),
        .c(s_12[6]),
        .d(s_12[7]),
        .CIN(pp_11_c4),
        .S(pp_12_s2),
        .C(pp_12_c3),
        .COUT(pp_12_c4)
    );
    
    E_4_2 E_4_2_pp_13_1(
        .a(s_13[0]),
        .b(s_13[1]),
        .c(s_13[2]),
        .d(s_13[3]),
        .CIN(pp_12_c2),
        .S(pp_13_s1),
        .C(pp_13_c1),
        .COUT(pp_13_c2)
    );
    
    E_4_2 E_4_2_pp_13_2(
        .a(s_13[4]),
        .b(s_13[5]),
        .c(s_13[6]),
        .d(s_13[7]),
        .CIN(pp_12_c4),
        .S(pp_13_s2),
        .C(pp_13_c3),
        .COUT(pp_13_c4)
    );
    E_4_2 E_4_2_pp_14_1(
        .a(s_14[0]),
        .b(s_14[1]),
        .c(s_14[2]),
        .d(s_14[3]),
        .CIN(pp_13_c2),
        .S(pp_14_s1),
        .C(pp_14_c1),
        .COUT(pp_14_c2)
    );
    
    E_4_2 E_4_2_pp_14_2(
        .a(s_14[4]),
        .b(s_14[5]),
        .c(s_14[6]),
        .d(s_14[7]),
        .CIN(pp_13_c4),
        .S(pp_14_s2),
        .C(pp_14_c3),
        .COUT(pp_14_c4)
    );
    
    E_4_2 E_4_2_pp_15_1(
        .a(s_15[0]),
        .b(s_15[1]),
        .c(s_15[2]),
        .d(s_15[3]),
        .CIN(pp_14_c2),
        .S(pp_15_s1),
        .C(pp_15_c1),
        .COUT(pp_15_c2)
    );
    
    E_4_2 E_4_2_pp_15_2(
        .a(s_15[4]),
        .b(s_15[5]),
        .c(s_15[6]),
        .d(s_15[7]),
        .CIN(pp_14_c4),
        .S(pp_15_s2),
        .C(pp_15_c3),
        .COUT(pp_15_c4)
    );
    
    E_4_2 E_4_2_pp_16_1(
        .a(s_16[0]),
        .b(s_16[1]),
        .c(s_16[2]),
        .d(s_16[3]),
        .CIN(pp_15_c2),
        .S(pp_16_s1),
        .C(pp_16_c1),
        .COUT(pp_16_c2)
    );
    
    E_4_2 E_4_2_pp_16_2(
        .a(s_16[4]),
        .b(s_16[5]),
        .c(s_16[6]),
        .d(s_16[7]),
        .CIN(pp_15_c4),
        .S(pp_16_s2),
        .C(pp_16_c3),
        .COUT(pp_16_c4)
    );
    
    E_4_2 E_4_2_pp_17_1(
        .a(s_17[0]),
        .b(s_17[1]),
        .c(s_17[2]),
        .d(s_17[3]),
        .CIN(pp_16_c2),
        .S(pp_17_s1),
        .C(pp_17_c1),
        .COUT(pp_17_c2)
    );
    
    E_4_2 E_4_2_pp_17_2(
        .a(s_17[4]),
        .b(s_17[5]),
        .c(s_17[6]),
        .d(s_17[7]),
        .CIN(pp_16_c4),
        .S(pp_17_s2),
        .C(pp_17_c3),
        .COUT(pp_17_c4)
    );
    
    E_4_2 E_4_2_pp_18_1(
        .a(s_18[0]),
        .b(s_18[1]),
        .c(s_18[2]),
        .d(s_18[3]),
        .CIN(pp_17_c2),
        .S(pp_18_s1),
        .C(pp_18_c1),
        .COUT(pp_18_c2)
    );
    
    E_4_2 E_4_2_pp_18_2(
        .a(s_18[4]),
        .b(s_18[5]),
        .c(s_18[6]),
        .d(s_18[7]),
        .CIN(pp_17_c4),
        .S(pp_18_s2),
        .C(pp_18_c3),
        .COUT(pp_18_c4)
    );
    
    E_4_2 E_4_2_pp_19_1(
        .a(s_19[0]),
        .b(s_19[1]),
        .c(s_19[2]),
        .d(s_19[3]),
        .CIN(pp_18_c2),
        .S(pp_19_s1),
        .C(pp_19_c1),
        .COUT(pp_19_c2)
    );
    
    E_4_2 E_4_2_pp_19_2(
        .a(s_19[4]),
        .b(s_19[5]),
        .c(s_19[6]),
        .d(s_19[7]),
        .CIN(pp_18_c4),
        .S(pp_19_s2),
        .C(pp_19_c3),
        .COUT(pp_19_c4)
    );
    E_4_2 E_4_2_pp_20_1(
        .a(s_20[0]),
        .b(s_20[1]),
        .c(s_20[2]),
        .d(s_20[3]),
        .CIN(pp_19_c2),
        .S(pp_20_s1),
        .C(pp_20_c1),
        .COUT(pp_20_c2)
    );
    
    E_4_2 E_4_2_pp_20_2(
        .a(s_20[4]),
        .b(s_20[5]),
        .c(s_20[6]),
        .d(s_20[7]),
        .CIN(pp_19_c4),
        .S(pp_20_s2),
        .C(pp_20_c3),
        .COUT(pp_20_c4)
    );
    
    E_4_2 E_4_2_pp_21_1(
        .a(s_21[0]),
        .b(s_21[1]),
        .c(s_21[2]),
        .d(s_21[3]),
        .CIN(pp_20_c2),
        .S(pp_21_s1),
        .C(pp_21_c1),
        .COUT(pp_21_c2)
    );
    
    E_4_2 E_4_2_pp_21_2(
        .a(s_21[4]),
        .b(s_21[5]),
        .c(s_21[6]),
        .d(s_21[7]),
        .CIN(pp_20_c4),
        .S(pp_21_s2),
        .C(pp_21_c3),
        .COUT(pp_21_c4)
    );
    
    
    E_4_2 E_4_2_pp_22_1(
        .a(s_22[0]),
        .b(s_22[1]),
        .c(s_22[2]),
        .d(s_22[3]),
        .CIN(pp_21_c2),
        .S(pp_22_s1),
        .C(pp_22_c1),
        .COUT(pp_22_c2)
    );
    
    E_4_2 E_4_2_pp_22_2(
        .a(s_22[4]),
        .b(s_22[5]),
        .c(s_22[6]),
        .d(s_22[7]),
        .CIN(pp_21_c4),
        .S(pp_22_s2),
        .C(pp_22_c3),
        .COUT(pp_22_c4)
    );
    
    E_4_2 E_4_2_pp_23_1(
        .a(s_23[0]),
        .b(s_23[1]),
        .c(s_23[2]),
        .d(s_23[3]),
        .CIN(pp_22_c2),
        .S(pp_23_s1),
        .C(pp_23_c1),
        .COUT(pp_23_c2)
    );
    
    E_4_2 E_4_2_pp_23_2(
        .a(s_23[4]),
        .b(s_23[5]),
        .c(s_23[6]),
        .d(s_23[7]),
        .CIN(pp_22_c4),
        .S(pp_23_s2),
        .C(pp_23_c3),
        .COUT(pp_23_c4)
    );
    
    E_4_2 E_4_2_pp_24_1(
        .a(s_24[0]),
        .b(s_24[1]),
        .c(s_24[2]),
        .d(s_24[3]),
        .CIN(pp_23_c2),
        .S(pp_24_s1),
        .C(pp_24_c1),
        .COUT(pp_24_c2)
    );
    
    E_4_2 E_4_2_pp_24_2(
        .a(s_24[4]),
        .b(s_24[5]),
        .c(s_24[6]),
        .d(s_24[7]),
        .CIN(pp_23_c4),
        .S(pp_24_s2),
        .C(pp_24_c3),
        .COUT(pp_24_c4)
    );
    
    E_4_2 E_4_2_pp_25_1(
        .a(s_25[0]),
        .b(s_25[1]),
        .c(s_25[2]),
        .d(s_25[3]),
        .CIN(pp_24_c2),
        .S(pp_25_s1),
        .C(pp_25_c1),
        .COUT(pp_25_c2)
    );
    
    Full_adder Full_adder_pp_25(
        .a(s_25[4]),
        .b(s_25[5]),
        .CIN(pp_24_c4),
        .S(pp_25_s2),
        .C(pp_25_c3)
    );
    E_4_2 E_4_2_pp_26_1(
        .a(s_26[0]),
        .b(s_26[1]),
        .c(s_26[2]),
        .d(s_26[3]),
        .CIN(pp_25_c2),
        .S(pp_26_s),
        .C(pp_26_c1),
        .COUT(pp_26_c2)
    );
    
    Full_adder Full_adder_pp_27(
        .a(s_27[0]),
        .b(s_27[1]),
        .CIN(s_27[2]),
        .S(pp_27_s),
        .C(pp_27_c)
    );
    
    
endmodule

module STAGE3(
    input pp_0,
    input [1:0] pp_1,
    input [2:0] pp_2,
    input [3:0] pp_3, 
    input [3:0] pp_4,
    input [3:0] pp_5,
    input [3:0] pp_6,
    input [3:0] pp_7,   
    input [3:0] pp_8,
    input [3:0] pp_9,
    input [3:0] pp_10,
    input [3:0] pp_11,
    input [3:0] pp_12,
    input [3:0] pp_13,
    input [3:0] pp_14,
    input [3:0] pp_15,
    input [3:0] pp_16,   
    input [3:0] pp_17,
    input [3:0] pp_18,
    input [3:0] pp_19,
    input [3:0] pp_20,
    input [3:0] pp_21,
    input [3:0] pp_22,
    input [3:0] pp_23,
    input [3:0] pp_24,
    input [3:0] pp_25,
    input [3:0] pp_26,
    input [3:0] pp_27,
    input [3:0] pp_28,
    input [1:0] pp_29,
    input pp_30,
    output [31:0] approx
    );
    
    wire [30:0] A;
    wire [30:0] B;
    
    wire pp_2_s;
    wire pp_2_c;
    wire pp_3_s;
    wire pp_3_c1;
    wire pp_3_c2;
    wire pp_4_s;
    wire pp_4_c1;
    wire pp_4_c2;
    wire pp_5_s;
    wire pp_5_c1;
    wire pp_5_c2;
    wire pp_6_s;
    wire pp_6_c1;
    wire pp_6_c2;
    wire pp_7_s;
    wire pp_7_c1;
    wire pp_7_c2;

    
    wire pp_8_s;
    wire pp_8_c1;
    wire pp_8_c2;

    
    wire pp_9_s;
    wire pp_9_c1;
    wire pp_9_c2;
 
    
    wire pp_10_s;
    wire pp_10_c1;
    wire pp_10_c2;

    
    wire pp_11_s;
    wire pp_11_c1;
    wire pp_11_c2;
 
    
    wire pp_12_s;
    wire pp_12_c1;
    wire pp_12_c2;

    
    wire pp_13_s;
    wire pp_13_c1;
    wire pp_13_c2;

    wire pp_14_s;
    wire pp_14_c1;
    wire pp_14_c2;

    
    wire pp_15_s;
    wire pp_15_c1;
    wire pp_15_c2;

      
    wire pp_16_s;
    wire pp_16_c1;
    wire pp_16_c2;

    
    wire pp_17_s;
    wire pp_17_c1;
    wire pp_17_c2;

    
    wire pp_18_s;
    wire pp_18_c1;
    wire pp_18_c2;

    
    wire pp_19_s;
    wire pp_19_c1;
    wire pp_19_c2;

    
    
    wire pp_20_s;
    wire pp_20_c1;
    wire pp_20_c2;

  
    wire pp_21_s;
    wire pp_21_c1;
    wire pp_21_c2;
 
  
    wire pp_22_s;
    wire pp_22_c1;
    wire pp_22_c2;

    
    wire pp_23_s;
    wire pp_23_c1;
    wire pp_23_c2;

    
    wire pp_24_s;
    wire pp_24_c1;
    wire pp_24_c2;
 
    
    wire pp_25_s;
    wire pp_25_c1;
    wire pp_25_c2;

    
    wire pp_26_s;
    wire pp_26_c1;
    wire pp_26_c2;
    
    wire pp_27_s;
    wire pp_27_c1;
    wire pp_27_c2;
    
    wire pp_28_s;
    wire pp_28_c1;
    wire pp_28_c2;
    
    wire pp_29_s;
    wire pp_29_c;
    
    assign A[0] = pp_0;
    assign B[0] = 1'b0;
    assign A[1] = pp_1[1];
    assign B[1] = pp_1[0];
    assign A[2] = pp_2_s;
    assign B[2] = pp_2[2];
    assign A[3] = pp_3_s;
    assign B[3] = pp_2_c;
    assign A[4] = pp_4_s;
    assign B[4] = pp_3_c1;
    assign A[5] = pp_5_s;
    assign B[5] = pp_4_c1;
    assign A[6] = pp_6_s;
    assign B[6] = pp_5_c1;
    assign A[7] = pp_7_s;
    assign B[7] = pp_6_c1;
    assign A[8] = pp_8_s;
    assign B[8] = pp_7_c1;
    assign A[9] = pp_9_s;
    assign B[9] = pp_8_c1;
    assign A[10] = pp_10_s;
    assign B[10] = pp_9_c1;
    assign A[11] = pp_11_s;
    assign B[11] = pp_10_c1;
    assign A[12] = pp_12_s;
    assign B[12] = pp_11_c1;
    assign A[13] = pp_13_s;
    assign B[13] = pp_12_c1;
    assign A[14] = pp_14_s;
    assign B[14] = pp_13_c1;
    assign A[15] = pp_15_s;
    assign B[15] = pp_14_c1;
    assign A[16] = pp_16_s;
    assign B[16] = pp_15_c1;
    assign A[17] = pp_17_s;
    assign B[17] = pp_16_c1;
    assign A[18] = pp_18_s;
    assign B[18] = pp_17_c1;
    assign A[19] = pp_19_s;
    assign B[19] = pp_18_c1;
    assign A[20] = pp_20_s;
    assign B[20] = pp_19_c1;
    assign A[21] = pp_21_s;
    assign B[21] = pp_20_c1;
    assign A[22] = pp_22_s;
    assign B[22] = pp_21_c1;
    assign A[23] = pp_23_s;
    assign B[23] = pp_22_c1;
    assign A[24] = pp_24_s;
    assign B[24] = pp_23_c1;
    assign A[25] = pp_25_s;
    assign B[25] = pp_24_c1;
    assign A[26] = pp_26_s;
    assign B[26] = pp_25_c1;
    assign A[27] = pp_27_s;
    assign B[27] = pp_26_c1;
    assign A[28] = pp_28_s;
    assign B[28] = pp_27_c1;
    assign A[29] = pp_29_s;
    assign B[29] = pp_28_c1;
    assign A[30] = pp_30;
    assign B[30] = pp_29_c;
    
CLA32bit Final_add
    (
     .A({1'b0,A}),
     .B({1'b0,B}),
     .Sum(approx),
     .Cin(1'b0),
     .Cout()
    );

    Half_adder Half_adder_pp_2(
        .a(pp_2[0]),
        .b(pp_2[1]),
        .S(pp_2_s),
        .C(pp_2_c)
    );
    
    E_4_2 E_4_2_pp_3(
        .a(pp_3[0]),
        .b(pp_3[1]),
        .c(pp_3[2]),
        .d(pp_3[3]),
        .CIN(1'b0),
        .S(pp_3_s),
        .C(pp_3_c1),
        .COUT(pp_3_c2)
    );
    
    E_4_2 E_4_2_pp_4(
        .a(pp_4[0]),
        .b(pp_4[1]),
        .c(pp_4[2]),
        .d(pp_4[3]),
        .CIN(pp_3_c2),
        .S(pp_4_s),
        .C(pp_4_c1),
        .COUT(pp_4_c2)
    );
    
    
    E_4_2 E_4_2_pp_5(
        .a(pp_5[0]),
        .b(pp_5[1]),
        .c(pp_5[2]),
        .d(pp_5[3]),
        .CIN(pp_4_c2),
        .S(pp_5_s),
        .C(pp_5_c1),
        .COUT(pp_5_c2)
    );
    
    E_4_2 E_4_2_pp_6(
        .a(pp_6[0]),
        .b(pp_6[1]),
        .c(pp_6[2]),
        .d(pp_6[3]),
        .CIN(pp_5_c2),
        .S(pp_6_s),
        .C(pp_6_c1),
        .COUT(pp_6_c2)
    );
    
    E_4_2 E_4_2_pp_7(
        .a(pp_7[0]),
        .b(pp_7[1]),
        .c(pp_7[2]),
        .d(pp_7[3]),
        .CIN(pp_6_c2),
        .S(pp_7_s),
        .C(pp_7_c1),
        .COUT(pp_7_c2)
    );
    
    E_4_2 E_4_2_pp_8(
        .a(pp_8[0]),
        .b(pp_8[1]),
        .c(pp_8[2]),
        .d(pp_8[3]),
        .CIN(pp_7_c2),
        .S(pp_8_s),
        .C(pp_8_c1),
        .COUT(pp_8_c2)
    );
    
    E_4_2 E_4_2_pp_9(
        .a(pp_9[0]),
        .b(pp_9[1]),
        .c(pp_9[2]),
        .d(pp_9[3]),
        .CIN(pp_8_c2),
        .S(pp_9_s),
        .C(pp_9_c1),
        .COUT(pp_9_c2)
    );
    

    
    E_4_2 E_4_2_pp_10_1(
        .a(pp_10[0]),
        .b(pp_10[1]),
        .c(pp_10[2]),
        .d(pp_10[3]),
        .CIN(pp_9_c2),
        .S(pp_10_s),
        .C(pp_10_c1),
        .COUT(pp_10_c2)
    );
    
 
    
    E_4_2 E_4_2_pp_11_1(
        .a(pp_11[0]),
        .b(pp_11[1]),
        .c(pp_11[2]),
        .d(pp_11[3]),
        .CIN(pp_10_c2),
        .S(pp_11_s),
        .C(pp_11_c1),
        .COUT(pp_11_c2)
    );
    

    
    E_4_2 E_4_2_pp_12_1(
        .a(pp_12[0]),
        .b(pp_12[1]),
        .c(pp_12[2]),
        .d(pp_12[3]),
        .CIN(pp_11_c2),
        .S(pp_12_s),
        .C(pp_12_c1),
        .COUT(pp_12_c2)
    );
    
 
    
    E_4_2 E_4_2_pp_13_1(
        .a(pp_13[0]),
        .b(pp_13[1]),
        .c(pp_13[2]),
        .d(pp_13[3]),
        .CIN(pp_12_c2),
        .S(pp_13_s),
        .C(pp_13_c1),
        .COUT(pp_13_c2)
    );
    

    E_4_2 E_4_2_pp_14_1(
        .a(pp_14[0]),
        .b(pp_14[1]),
        .c(pp_14[2]),
        .d(pp_14[3]),
        .CIN(pp_13_c2),
        .S(pp_14_s),
        .C(pp_14_c1),
        .COUT(pp_14_c2)
    );
    

    
    E_4_2 E_4_2_pp_15_1(
        .a(pp_15[0]),
        .b(pp_15[1]),
        .c(pp_15[2]),
        .d(pp_15[3]),
        .CIN(pp_14_c2),
        .S(pp_15_s),
        .C(pp_15_c1),
        .COUT(pp_15_c2)
    );
    

    
    E_4_2 E_4_2_pp_16_1(
        .a(pp_16[0]),
        .b(pp_16[1]),
        .c(pp_16[2]),
        .d(pp_16[3]),
        .CIN(pp_15_c2),
        .S(pp_16_s),
        .C(pp_16_c1),
        .COUT(pp_16_c2)
    );
    

    
    E_4_2 E_4_2_pp_17_1(
        .a(pp_17[0]),
        .b(pp_17[1]),
        .c(pp_17[2]),
        .d(pp_17[3]),
        .CIN(pp_16_c2),
        .S(pp_17_s),
        .C(pp_17_c1),
        .COUT(pp_17_c2)
    );
    

    
    E_4_2 E_4_2_pp_18_1(
        .a(pp_18[0]),
        .b(pp_18[1]),
        .c(pp_18[2]),
        .d(pp_18[3]),
        .CIN(pp_17_c2),
        .S(pp_18_s),
        .C(pp_18_c1),
        .COUT(pp_18_c2)
    );
    

    
    E_4_2 E_4_2_pp_19_1(
        .a(pp_19[0]),
        .b(pp_19[1]),
        .c(pp_19[2]),
        .d(pp_19[3]),
        .CIN(pp_18_c2),
        .S(pp_19_s),
        .C(pp_19_c1),
        .COUT(pp_19_c2)
    );
    

    E_4_2 E_4_2_pp_20_1(
        .a(pp_20[0]),
        .b(pp_20[1]),
        .c(pp_20[2]),
        .d(pp_20[3]),
        .CIN(pp_19_c2),
        .S(pp_20_s),
        .C(pp_20_c1),
        .COUT(pp_20_c2)
    );
    

    
    E_4_2 E_4_2_pp_21_1(
        .a(pp_21[0]),
        .b(pp_21[1]),
        .c(pp_21[2]),
        .d(pp_21[3]),
        .CIN(pp_20_c2),
        .S(pp_21_s),
        .C(pp_21_c1),
        .COUT(pp_21_c2)
    );
    

    
    
    E_4_2 E_4_2_pp_22_1(
        .a(pp_22[0]),
        .b(pp_22[1]),
        .c(pp_22[2]),
        .d(pp_22[3]),
        .CIN(pp_21_c2),
        .S(pp_22_s),
        .C(pp_22_c1),
        .COUT(pp_22_c2)
    );

    
    E_4_2 E_4_2_pp_23_1(
        .a(pp_23[0]),
        .b(pp_23[1]),
        .c(pp_23[2]),
        .d(pp_23[3]),
        .CIN(pp_22_c2),
        .S(pp_23_s),
        .C(pp_23_c1),
        .COUT(pp_23_c2)
    );
    

    
    E_4_2 E_4_2_pp_24_1(
        .a(pp_24[0]),
        .b(pp_24[1]),
        .c(pp_24[2]),
        .d(pp_24[3]),
        .CIN(pp_23_c2),
        .S(pp_24_s),
        .C(pp_24_c1),
        .COUT(pp_24_c2)
    );
    

    
    E_4_2 E_4_2_pp_25_1(
        .a(pp_25[0]),
        .b(pp_25[1]),
        .c(pp_25[2]),
        .d(pp_25[3]),
        .CIN(pp_24_c2),
        .S(pp_25_s),
        .C(pp_25_c1),
        .COUT(pp_25_c2)
    );
    

    E_4_2 E_4_2_pp_26_1(
        .a(pp_26[0]),
        .b(pp_26[1]),
        .c(pp_26[2]),
        .d(pp_26[3]),
        .CIN(pp_25_c2),
        .S(pp_26_s),
        .C(pp_26_c1),
        .COUT(pp_26_c2)
    );
    
E_4_2 E_4_2_pp_27_1(
        .a(pp_27[0]),
        .b(pp_27[1]),
        .c(pp_27[2]),
        .d(pp_27[3]),
        .CIN(pp_26_c2),
        .S(pp_27_s),
        .C(pp_27_c1),
        .COUT(pp_27_c2)
    );
    
    E_4_2 E_4_2_pp_28_1(
        .a(pp_28[0]),
        .b(pp_28[1]),
        .c(pp_28[2]),
        .d(pp_28[3]),
        .CIN(pp_27_c2),
        .S(pp_28_s),
        .C(pp_28_c1),
        .COUT(pp_28_c2)
    );
    
    Full_adder Full_adder_pp_29(
        .a(pp_29[0]),
        .b(pp_29[1]),
        .CIN(pp_28_c2),
        .S(pp_29_s),
        .C(pp_29_c)
    );
    
 
endmodule
