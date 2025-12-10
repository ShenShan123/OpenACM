`timescale 1ns / 1ps

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

module Exact_8bit(
    input [7:0] N1,
    input [7:0] N2,
    output [15:0] P_APPROX
    );
    
    wire pp_0;
    wire [1:0] pp_1;
    wire [2:0] pp_2;
    wire [3:0] pp_3;
    wire [3:0] pp_4;
    wire [3:0] pp_5;
    wire [3:0] pp_6;
    wire [3:0] pp_7;
    wire [3:0] pp_8;
    wire [3:0] pp_9;
    wire [3:0] pp_10;
    wire [3:0] pp_11;
    wire [3:0] pp_12;
    wire [1:0] pp_13;
    wire pp_14;
    
    wire [7:0] n1;
    wire [7:0] n2;
    
    assign n1 = {1'b0,N1[6:0]};
    assign n2 = {1'b0,N2[6:0]};
    
    STAGE1 STAGE1
    (
        .A(n1),
        .B(n2),
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
       .pp_14(pp_14) 
    );
    
    wire [15:0] approx;
    
    STAGE2 STAGE2
    (
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
       .approx(approx) 
    );
    
    assign P_APPROX = {N1[7]^N2[7],approx[14:0]};
    
endmodule

module STAGE1(
    input [7:0] A,
    input [7:0] B,
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
    output [1:0] pp_13,
    output pp_14 
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
    
    wire pp_10_s;
    wire pp_10_c1;
    wire pp_10_c2;
    
    wire pp_11_s;
    wire pp_11_c;
    assign pp_0 = A[0] & B[0];
    assign pp_1 = {A[0] & B[1],A[1] & B[0]};
    assign pp_2 = {A[0] & B[2],A[1] & B[1],A[2] & B[0]};
    assign pp_3 = {A[0] & B[3],A[1] & B[2],A[2] & B[1],A[3] & B[0]};
    assign pp_4 = {A[0] & B[4],A[1] & B[3],A[2] & B[2],pp_4_s};
    assign pp_5 = {pp_4_c,A[0] & B[5],A[1] & B[4],pp_5_s};
    assign pp_6 = {pp_5_c1,A[0] & B[6],pp_6_s2,pp_6_s1};
    assign pp_7 = {pp_6_c3,pp_6_c1,pp_7_s2,pp_7_s1};
    assign pp_8 = {pp_7_c3,pp_7_c1,pp_8_s2,pp_8_s1};
    assign pp_9 = {pp_8_c3,pp_8_c1,pp_9_s2,pp_9_s1};
    assign pp_10 = {pp_10_s,A[3] & B[7],pp_9_c1,pp_9_c3};
    assign pp_11 = {pp_11_s,A[5] & B[6],A[4] & B[7],pp_10_c1};
    assign pp_12 = {A[7] & B[5],A[6] & B[6],A[5] & B[7],pp_11_c};
    assign pp_13 = {A[7] & B[6],A[6] & B[7]};
    assign pp_14 = {A[7] & B[7]};
    Half_adder Half_adder_pp_4(
        .a(A[4] & B[0]),
        .b(A[3] & B[1]),
        .S(pp_4_s),
        .C(pp_4_c)
    );
    
    E_4_2 E_4_2_pp_5(
        .a(A[5] & B[0]),
        .b(A[4] & B[1]),
        .c(A[3] & B[2]),
        .d(A[2] & B[3]),
        .CIN(1'b0),
        .S(pp_5_s),
        .C(pp_5_c1),
        .COUT(pp_5_c2)
    );
    
    E_4_2 E_4_2_pp_6(
        .a(A[6] & B[0]),
        .b(A[5] & B[1]),
        .c(A[4] & B[2]),
        .d(A[3] & B[3]),
        .CIN(pp_5_c2),
        .S(pp_6_s1),
        .C(pp_6_c1),
        .COUT(pp_6_c2)
    );
    
    Half_adder Half_adder_pp_6(
        .a(A[2] & B[4]),
        .b(A[1] & B[5]),
        .S(pp_6_s2),
        .C(pp_6_c3)
    );
    
    E_4_2 E_4_2_pp_7_1(
        .a(A[7] & B[0]),
        .b(A[6] & B[1]),
        .c(A[5] & B[2]),
        .d(A[4] & B[3]),
        .CIN(pp_6_c2),
        .S(pp_7_s1),
        .C(pp_7_c1),
        .COUT(pp_7_c2)
    );
    
    E_4_2 E_4_2_pp_7_2(
        .a(A[3] & B[4]),
        .b(A[2] & B[5]),
        .c(A[1] & B[6]),
        .d(A[0] & B[7]),
        .CIN(1'b0),
        .S(pp_7_s2),
        .C(pp_7_c3),
        .COUT(pp_7_c4)
    );
    
    E_4_2 E_4_2_pp_8_1(
        .a(A[7] & B[1]),
        .b(A[6] & B[2]),
        .c(A[5] & B[3]),
        .d(A[4] & B[4]),
        .CIN(pp_7_c2),
        .S(pp_8_s1),
        .C(pp_8_c1),
        .COUT(pp_8_c2)
    );
    
    E_4_2 E_4_2_pp_8_2(
        .a(A[3] & B[5]),
        .b(A[2] & B[6]),
        .c(A[1] & B[7]),
        .d(pp_7_c4),
        .CIN(1'b0),
        .S(pp_8_s2),
        .C(pp_8_c3),
        .COUT(pp_8_c4)
    );
    
    E_4_2 E_4_2_pp_9_1(
        .a(A[7] & B[2]),
        .b(A[6] & B[3]),
        .c(A[5] & B[4]),
        .d(A[4] & B[5]),
        .CIN(pp_8_c2),
        .S(pp_9_s1),
        .C(pp_9_c1),
        .COUT(pp_9_c2)
    );
    
    Full_adder Full_adder_pp_9(
        .a(A[3] & B[6]),
        .b(A[2] & B[7]),
        .CIN(pp_8_c4),
        .S(pp_9_s2),
        .C(pp_9_c3)
    );
    
    E_4_2 E_4_2_pp_10(
        .a(A[7] & B[3]),
        .b(A[6] & B[4]),
        .c(A[5] & B[5]),
        .d(A[4] & B[6]),
        .CIN(pp_9_c2),
        .S(pp_10_s),
        .C(pp_10_c1),
        .COUT(pp_10_c2)
    );
    Full_adder Full_adder_pp_11(
        .a(A[7] & B[4]),
        .b(A[6] & B[5]),
        .CIN(pp_10_c2),
        .S(pp_11_s),
        .C(pp_11_c)
    );
    
    
endmodule

module STAGE2(
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
    input [1:0] pp_13,
    input pp_14,
    output [15:0] approx
    );
    
        wire [14:0] A;
        wire [14:0] B;
        
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
        wire pp_13_c;
        
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
        
        assign A[14] = pp_14;
        assign B[14] = pp_13_c;
  
        CLA16bit Final_add(
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
    
    E_4_2 E_4_2_pp_10(
        .a(pp_10[0]),
        .b(pp_10[1]),
        .c(pp_10[2]),
        .d(pp_10[3]),
        .CIN(pp_9_c2),
        .S(pp_10_s),
        .C(pp_10_c1),
        .COUT(pp_10_c2)
    );
    
    E_4_2 E_4_2_pp_11(
        .a(pp_11[0]),
        .b(pp_11[1]),
        .c(pp_11[2]),
        .d(pp_11[3]),
        .CIN(pp_10_c2),
        .S(pp_11_s),
        .C(pp_11_c1),
        .COUT(pp_11_c2)
    );
    
    E_4_2 E_4_2_pp_12(
        .a(pp_12[0]),
        .b(pp_12[1]),
        .c(pp_12[2]),
        .d(pp_12[3]),
        .CIN(pp_11_c2),
        .S(pp_12_s),
        .C(pp_12_c1),
        .COUT(pp_12_c2)
    );
    
    Full_adder Full_adder_pp_13(
        .a(pp_13[0]),
        .b(pp_13[1]),
        .CIN(pp_12_c2),
        .S(pp_13_s),
        .C(pp_13_c)
       );
    
endmodule

