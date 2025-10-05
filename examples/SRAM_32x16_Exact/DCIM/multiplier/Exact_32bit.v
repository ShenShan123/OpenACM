
// 32位精确乘法器Verilog代码
// 生成时间: 2025-09-07 23:44:58.214118
// 位宽: 32位输入, 64位输出
`timescale 1ns/1ps

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
    assign C[0] = (A[0] & B[0]) | ((A[0] ^ B[0]) & Cin);
    assign C[1] = (A[1] & B[1]) | ((A[1] ^ B[1]) & C[0]);
    assign C[2] = (A[2] & B[2]) | ((A[2] ^ B[2]) & C[1]);
    assign C[3] = (A[3] & B[3]) | ((A[3] ^ B[3]) & C[2]);
    assign Cout = C[3];
endmodule

module CLA8bit (
    input [7:0] A,
    input [7:0] B,
    input Cin,
    output [7:0] Sum,
    output Cout
);
    wire c1;
    
    CLA4bit cla1(
        .A(A[3:0]),
        .B(B[3:0]),
        .Cin(Cin),
        .Sum(Sum[3:0]),
        .Cout(c1)
    );
    
    CLA4bit cla2(
        .A(A[7:4]),
        .B(B[7:4]),
        .Cin(c1),
        .Sum(Sum[7:4]),
        .Cout(Cout)
    );
endmodule

module CLA16bit (
    input [15:0] A,
    input [15:0] B,
    input Cin,
    output [15:0] Sum,
    output Cout
);
    wire c1;
    
    CLA8bit cla1(
        .A(A[7:0]),
        .B(B[7:0]),
        .Cin(Cin),
        .Sum(Sum[7:0]),
        .Cout(c1)
    );
    
    CLA8bit cla2(
        .A(A[15:8]),
        .B(B[15:8]),
        .Cin(c1),
        .Sum(Sum[15:8]),
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
    
    CLA16bit cla1(
        .A(A[15:0]),
        .B(B[15:0]),
        .Cin(Cin),
        .Sum(Sum[15:0]),
        .Cout(c1)
    );
    
    CLA16bit cla2(
        .A(A[31:16]),
        .B(B[31:16]),
        .Cin(c1),
        .Sum(Sum[31:16]),
        .Cout(Cout)
    );
endmodule

module CLA64bit (
    input [63:0] A,
    input [63:0] B,
    input Cin,
    output [63:0] Sum,
    output Cout
);
    wire c1;
    
    CLA32bit cla1(
        .A(A[31:0]),
        .B(B[31:0]),
        .Cin(Cin),
        .Sum(Sum[31:0]),
        .Cout(c1)
    );
    
    CLA32bit cla2(
        .A(A[63:32]),
        .B(B[63:32]),
        .Cin(c1),
        .Sum(Sum[63:32]),
        .Cout(Cout)
    );
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
    assign COUT = ((a ^ b) & c) | (~(a ^ b) & a);
    assign C = (part & CIN) | (~part & d);
endmodule



module Full_adder(
    input a,
    input b,
    input CIN,
    output S,
    output C
);
    wire S1, T1, T2, T3;
    
    xor x1 (S1, a, b);
    xor x2 (S, S1, CIN);
    
    and A1 (T3, a, b);
    and A2 (T2, b, CIN);
    and A3 (T1, a, CIN);
    
    or O1 (C, T1, T2, T3);
endmodule

module Half_adder(
    input a,
    input b,
    output S,
    output C
);
    xor x1 (S, a, b);
    and x2 (C, a, b);
endmodule


// module sram_multiplier_system(
//     input clk,
//     input [31:0] x,
//     input [31:0] y,
//     input rst_n,
//     output reg [63:0] p_out
// );
//     wire [63:0] P_vec;
//     reg [31:0] X_vec;
//     reg [31:0] Y_vec;
    
//     APPROX32 mult(
//         .N1(X_vec),
//         .N2(Y_vec),
//         .P_APPROX(P_vec)
//     );
    
//     always @(posedge clk) begin
//         if(!rst_n)
//         begin
//             p_out <=0;
//             X_vec <=0;
//             Y_vec <=0;
//         end
//         else begin
//         p_out <= P_vec;
//         X_vec <= x;
//         Y_vec <= y;
//         end
//     end
// endmodule

// module mult32_top(
//     input clk,
//     input [31:0] x,
//     input [31:0] y,
//     output reg [63:0] p_out
// );
//     wire [63:0] P_vec;
//     reg [31:0] X_vec;
//     reg [31:0] Y_vec;
    
//     APPROX32 mult(
//         .N1(X_vec),
//         .N2(Y_vec),
//         .P_APPROX(P_vec)
//     );
    
//     always @(posedge clk) begin
//         p_out <= P_vec;
//         X_vec <= x;
//         Y_vec <= y;
//     end
// endmodule



module Exact_32bit(
    input [31:0] N1,
    input [31:0] N2,
    output [63:0] P_APPROX
);

wire cin_net;
LOGIC0_X1 u_gnd (.Z(cin_net));

// STAGE1输出信号
    wire pp1_0;
    wire [1:0] pp1_1;
    wire [2:0] pp1_2;
    wire [3:0] pp1_3;
    wire [4:0] pp1_4;
    wire [5:0] pp1_5;
    wire [6:0] pp1_6;
    wire [7:0] pp1_7;
    wire [8:0] pp1_8;
    wire [9:0] pp1_9;
    wire [10:0] pp1_10;
    wire [11:0] pp1_11;
    wire [12:0] pp1_12;
    wire [13:0] pp1_13;
    wire [14:0] pp1_14;
    wire [15:0] pp1_15;
    wire [15:0] pp1_16;
    wire [15:0] pp1_17;
    wire [15:0] pp1_18;
    wire [15:0] pp1_19;
    wire [15:0] pp1_20;
    wire [15:0] pp1_21;
    wire [15:0] pp1_22;
    wire [15:0] pp1_23;
    wire [15:0] pp1_24;
    wire [15:0] pp1_25;
    wire [15:0] pp1_26;
    wire [15:0] pp1_27;
    wire [15:0] pp1_28;
    wire [15:0] pp1_29;
    wire [15:0] pp1_30;
    wire [15:0] pp1_31;
    wire [15:0] pp1_32;
    wire [15:0] pp1_33;
    wire [15:0] pp1_34;
    wire [15:0] pp1_35;
    wire [15:0] pp1_36;
    wire [15:0] pp1_37;
    wire [15:0] pp1_38;
    wire [15:0] pp1_39;
    wire [15:0] pp1_40;
    wire [15:0] pp1_41;
    wire [15:0] pp1_42;
    wire [15:0] pp1_43;
    wire [15:0] pp1_44;
    wire [15:0] pp1_45;
    wire [15:0] pp1_46;
    wire [15:0] pp1_47;
    wire [15:0] pp1_48;
    wire [13:0] pp1_49;
    wire [12:0] pp1_50;
    wire [11:0] pp1_51;
    wire [10:0] pp1_52;
    wire [9:0] pp1_53;
    wire [8:0] pp1_54;
    wire [7:0] pp1_55;
    wire [6:0] pp1_56;
    wire [5:0] pp1_57;
    wire [4:0] pp1_58;
    wire [3:0] pp1_59;
    wire [2:0] pp1_60;
    wire [1:0] pp1_61;
    wire pp1_62;
    wire pp1_63;

// STAGE2输出信号
    wire pp2_0;
    wire [1:0] pp2_1;
    wire [2:0] pp2_2;
    wire [3:0] pp2_3;
    wire [4:0] pp2_4;
    wire [5:0] pp2_5;
    wire [6:0] pp2_6;
    wire [7:0] pp2_7;
    wire [7:0] pp2_8;
    wire [7:0] pp2_9;
    wire [7:0] pp2_10;
    wire [7:0] pp2_11;
    wire [7:0] pp2_12;
    wire [7:0] pp2_13;
    wire [7:0] pp2_14;
    wire [7:0] pp2_15;
    wire [7:0] pp2_16;
    wire [7:0] pp2_17;
    wire [7:0] pp2_18;
    wire [7:0] pp2_19;
    wire [7:0] pp2_20;
    wire [7:0] pp2_21;
    wire [7:0] pp2_22;
    wire [7:0] pp2_23;
    wire [7:0] pp2_24;
    wire [7:0] pp2_25;
    wire [7:0] pp2_26;
    wire [7:0] pp2_27;
    wire [7:0] pp2_28;
    wire [7:0] pp2_29;
    wire [7:0] pp2_30;
    wire [7:0] pp2_31;
    wire [7:0] pp2_32;
    wire [7:0] pp2_33;
    wire [7:0] pp2_34;
    wire [7:0] pp2_35;
    wire [7:0] pp2_36;
    wire [7:0] pp2_37;
    wire [7:0] pp2_38;
    wire [7:0] pp2_39;
    wire [7:0] pp2_40;
    wire [7:0] pp2_41;
    wire [7:0] pp2_42;
    wire [7:0] pp2_43;
    wire [7:0] pp2_44;
    wire [7:0] pp2_45;
    wire [7:0] pp2_46;
    wire [7:0] pp2_47;
    wire [7:0] pp2_48;
    wire [7:0] pp2_49;
    wire [7:0] pp2_50;
    wire [7:0] pp2_51;
    wire [7:0] pp2_52;
    wire [7:0] pp2_53;
    wire [7:0] pp2_54;
    wire [7:0] pp2_55;
    wire [7:0] pp2_56;
    wire [5:0] pp2_57;
    wire [4:0] pp2_58;
    wire [3:0] pp2_59;
    wire [2:0] pp2_60;
    wire [1:0] pp2_61;
    wire pp2_62;
    wire pp2_63;

// STAGE3输出信号
    wire pp3_0;
    wire [1:0] pp3_1;
    wire [2:0] pp3_2;
    wire [3:0] pp3_3;
    wire [3:0] pp3_4;
    wire [3:0] pp3_5;
    wire [3:0] pp3_6;
    wire [3:0] pp3_7;
    wire [3:0] pp3_8;
    wire [3:0] pp3_9;
    wire [3:0] pp3_10;
    wire [3:0] pp3_11;
    wire [3:0] pp3_12;
    wire [3:0] pp3_13;
    wire [3:0] pp3_14;
    wire [3:0] pp3_15;
    wire [3:0] pp3_16;
    wire [3:0] pp3_17;
    wire [3:0] pp3_18;
    wire [3:0] pp3_19;
    wire [3:0] pp3_20;
    wire [3:0] pp3_21;
    wire [3:0] pp3_22;
    wire [3:0] pp3_23;
    wire [3:0] pp3_24;
    wire [3:0] pp3_25;
    wire [3:0] pp3_26;
    wire [3:0] pp3_27;
    wire [3:0] pp3_28;
    wire [3:0] pp3_29;
    wire [3:0] pp3_30;
    wire [3:0] pp3_31;
    wire [3:0] pp3_32;
    wire [3:0] pp3_33;
    wire [3:0] pp3_34;
    wire [3:0] pp3_35;
    wire [3:0] pp3_36;
    wire [3:0] pp3_37;
    wire [3:0] pp3_38;
    wire [3:0] pp3_39;
    wire [3:0] pp3_40;
    wire [3:0] pp3_41;
    wire [3:0] pp3_42;
    wire [3:0] pp3_43;
    wire [3:0] pp3_44;
    wire [3:0] pp3_45;
    wire [3:0] pp3_46;
    wire [3:0] pp3_47;
    wire [3:0] pp3_48;
    wire [3:0] pp3_49;
    wire [3:0] pp3_50;
    wire [3:0] pp3_51;
    wire [3:0] pp3_52;
    wire [3:0] pp3_53;
    wire [3:0] pp3_54;
    wire [3:0] pp3_55;
    wire [3:0] pp3_56;
    wire [3:0] pp3_57;
    wire [3:0] pp3_58;
    wire [3:0] pp3_59;
    wire [3:0] pp3_60;
    wire [1:0] pp3_61;
    wire pp3_62;
    wire pp3_63;

// STAGE4输出信号
    wire [63:0] A;
    wire [63:0] B;

    STAGE1_32 STAGE1(
        .A(N1),
        .B(N2),
        .pp1_0(pp1_0),
        .pp1_1(pp1_1),
        .pp1_2(pp1_2),
        .pp1_3(pp1_3),
        .pp1_4(pp1_4),
        .pp1_5(pp1_5),
        .pp1_6(pp1_6),
        .pp1_7(pp1_7),
        .pp1_8(pp1_8),
        .pp1_9(pp1_9),
        .pp1_10(pp1_10),
        .pp1_11(pp1_11),
        .pp1_12(pp1_12),
        .pp1_13(pp1_13),
        .pp1_14(pp1_14),
        .pp1_15(pp1_15),
        .pp1_16(pp1_16),
        .pp1_17(pp1_17),
        .pp1_18(pp1_18),
        .pp1_19(pp1_19),
        .pp1_20(pp1_20),
        .pp1_21(pp1_21),
        .pp1_22(pp1_22),
        .pp1_23(pp1_23),
        .pp1_24(pp1_24),
        .pp1_25(pp1_25),
        .pp1_26(pp1_26),
        .pp1_27(pp1_27),
        .pp1_28(pp1_28),
        .pp1_29(pp1_29),
        .pp1_30(pp1_30),
        .pp1_31(pp1_31),
        .pp1_32(pp1_32),
        .pp1_33(pp1_33),
        .pp1_34(pp1_34),
        .pp1_35(pp1_35),
        .pp1_36(pp1_36),
        .pp1_37(pp1_37),
        .pp1_38(pp1_38),
        .pp1_39(pp1_39),
        .pp1_40(pp1_40),
        .pp1_41(pp1_41),
        .pp1_42(pp1_42),
        .pp1_43(pp1_43),
        .pp1_44(pp1_44),
        .pp1_45(pp1_45),
        .pp1_46(pp1_46),
        .pp1_47(pp1_47),
        .pp1_48(pp1_48),
        .pp1_49(pp1_49),
        .pp1_50(pp1_50),
        .pp1_51(pp1_51),
        .pp1_52(pp1_52),
        .pp1_53(pp1_53),
        .pp1_54(pp1_54),
        .pp1_55(pp1_55),
        .pp1_56(pp1_56),
        .pp1_57(pp1_57),
        .pp1_58(pp1_58),
        .pp1_59(pp1_59),
        .pp1_60(pp1_60),
        .pp1_61(pp1_61),
        .pp1_62(pp1_62),
        .pp1_63(pp1_63)
    );

    STAGE2_32 STAGE2(
        .pp1_0(pp1_0),
        .pp1_1(pp1_1),
        .pp1_2(pp1_2),
        .pp1_3(pp1_3),
        .pp1_4(pp1_4),
        .pp1_5(pp1_5),
        .pp1_6(pp1_6),
        .pp1_7(pp1_7),
        .pp1_8(pp1_8),
        .pp1_9(pp1_9),
        .pp1_10(pp1_10),
        .pp1_11(pp1_11),
        .pp1_12(pp1_12),
        .pp1_13(pp1_13),
        .pp1_14(pp1_14),
        .pp1_15(pp1_15),
        .pp1_16(pp1_16),
        .pp1_17(pp1_17),
        .pp1_18(pp1_18),
        .pp1_19(pp1_19),
        .pp1_20(pp1_20),
        .pp1_21(pp1_21),
        .pp1_22(pp1_22),
        .pp1_23(pp1_23),
        .pp1_24(pp1_24),
        .pp1_25(pp1_25),
        .pp1_26(pp1_26),
        .pp1_27(pp1_27),
        .pp1_28(pp1_28),
        .pp1_29(pp1_29),
        .pp1_30(pp1_30),
        .pp1_31(pp1_31),
        .pp1_32(pp1_32),
        .pp1_33(pp1_33),
        .pp1_34(pp1_34),
        .pp1_35(pp1_35),
        .pp1_36(pp1_36),
        .pp1_37(pp1_37),
        .pp1_38(pp1_38),
        .pp1_39(pp1_39),
        .pp1_40(pp1_40),
        .pp1_41(pp1_41),
        .pp1_42(pp1_42),
        .pp1_43(pp1_43),
        .pp1_44(pp1_44),
        .pp1_45(pp1_45),
        .pp1_46(pp1_46),
        .pp1_47(pp1_47),
        .pp1_48(pp1_48),
        .pp1_49(pp1_49),
        .pp1_50(pp1_50),
        .pp1_51(pp1_51),
        .pp1_52(pp1_52),
        .pp1_53(pp1_53),
        .pp1_54(pp1_54),
        .pp1_55(pp1_55),
        .pp1_56(pp1_56),
        .pp1_57(pp1_57),
        .pp1_58(pp1_58),
        .pp1_59(pp1_59),
        .pp1_60(pp1_60),
        .pp1_61(pp1_61),
        .pp1_62(pp1_62),
        .pp1_63(pp1_63),
        .pp2_0(pp2_0),
        .pp2_1(pp2_1),
        .pp2_2(pp2_2),
        .pp2_3(pp2_3),
        .pp2_4(pp2_4),
        .pp2_5(pp2_5),
        .pp2_6(pp2_6),
        .pp2_7(pp2_7),
        .pp2_8(pp2_8),
        .pp2_9(pp2_9),
        .pp2_10(pp2_10),
        .pp2_11(pp2_11),
        .pp2_12(pp2_12),
        .pp2_13(pp2_13),
        .pp2_14(pp2_14),
        .pp2_15(pp2_15),
        .pp2_16(pp2_16),
        .pp2_17(pp2_17),
        .pp2_18(pp2_18),
        .pp2_19(pp2_19),
        .pp2_20(pp2_20),
        .pp2_21(pp2_21),
        .pp2_22(pp2_22),
        .pp2_23(pp2_23),
        .pp2_24(pp2_24),
        .pp2_25(pp2_25),
        .pp2_26(pp2_26),
        .pp2_27(pp2_27),
        .pp2_28(pp2_28),
        .pp2_29(pp2_29),
        .pp2_30(pp2_30),
        .pp2_31(pp2_31),
        .pp2_32(pp2_32),
        .pp2_33(pp2_33),
        .pp2_34(pp2_34),
        .pp2_35(pp2_35),
        .pp2_36(pp2_36),
        .pp2_37(pp2_37),
        .pp2_38(pp2_38),
        .pp2_39(pp2_39),
        .pp2_40(pp2_40),
        .pp2_41(pp2_41),
        .pp2_42(pp2_42),
        .pp2_43(pp2_43),
        .pp2_44(pp2_44),
        .pp2_45(pp2_45),
        .pp2_46(pp2_46),
        .pp2_47(pp2_47),
        .pp2_48(pp2_48),
        .pp2_49(pp2_49),
        .pp2_50(pp2_50),
        .pp2_51(pp2_51),
        .pp2_52(pp2_52),
        .pp2_53(pp2_53),
        .pp2_54(pp2_54),
        .pp2_55(pp2_55),
        .pp2_56(pp2_56),
        .pp2_57(pp2_57),
        .pp2_58(pp2_58),
        .pp2_59(pp2_59),
        .pp2_60(pp2_60),
        .pp2_61(pp2_61),
        .pp2_62(pp2_62),
        .pp2_63(pp2_63)
    );

    STAGE3_32 STAGE3(
        .pp2_0(pp2_0),
        .pp2_1(pp2_1),
        .pp2_2(pp2_2),
        .pp2_3(pp2_3),
        .pp2_4(pp2_4),
        .pp2_5(pp2_5),
        .pp2_6(pp2_6),
        .pp2_7(pp2_7),
        .pp2_8(pp2_8),
        .pp2_9(pp2_9),
        .pp2_10(pp2_10),
        .pp2_11(pp2_11),
        .pp2_12(pp2_12),
        .pp2_13(pp2_13),
        .pp2_14(pp2_14),
        .pp2_15(pp2_15),
        .pp2_16(pp2_16),
        .pp2_17(pp2_17),
        .pp2_18(pp2_18),
        .pp2_19(pp2_19),
        .pp2_20(pp2_20),
        .pp2_21(pp2_21),
        .pp2_22(pp2_22),
        .pp2_23(pp2_23),
        .pp2_24(pp2_24),
        .pp2_25(pp2_25),
        .pp2_26(pp2_26),
        .pp2_27(pp2_27),
        .pp2_28(pp2_28),
        .pp2_29(pp2_29),
        .pp2_30(pp2_30),
        .pp2_31(pp2_31),
        .pp2_32(pp2_32),
        .pp2_33(pp2_33),
        .pp2_34(pp2_34),
        .pp2_35(pp2_35),
        .pp2_36(pp2_36),
        .pp2_37(pp2_37),
        .pp2_38(pp2_38),
        .pp2_39(pp2_39),
        .pp2_40(pp2_40),
        .pp2_41(pp2_41),
        .pp2_42(pp2_42),
        .pp2_43(pp2_43),
        .pp2_44(pp2_44),
        .pp2_45(pp2_45),
        .pp2_46(pp2_46),
        .pp2_47(pp2_47),
        .pp2_48(pp2_48),
        .pp2_49(pp2_49),
        .pp2_50(pp2_50),
        .pp2_51(pp2_51),
        .pp2_52(pp2_52),
        .pp2_53(pp2_53),
        .pp2_54(pp2_54),
        .pp2_55(pp2_55),
        .pp2_56(pp2_56),
        .pp2_57(pp2_57),
        .pp2_58(pp2_58),
        .pp2_59(pp2_59),
        .pp2_60(pp2_60),
        .pp2_61(pp2_61),
        .pp2_62(pp2_62),
        .pp2_63(pp2_63),
        .pp3_0(pp3_0),
        .pp3_1(pp3_1),
        .pp3_2(pp3_2),
        .pp3_3(pp3_3),
        .pp3_4(pp3_4),
        .pp3_5(pp3_5),
        .pp3_6(pp3_6),
        .pp3_7(pp3_7),
        .pp3_8(pp3_8),
        .pp3_9(pp3_9),
        .pp3_10(pp3_10),
        .pp3_11(pp3_11),
        .pp3_12(pp3_12),
        .pp3_13(pp3_13),
        .pp3_14(pp3_14),
        .pp3_15(pp3_15),
        .pp3_16(pp3_16),
        .pp3_17(pp3_17),
        .pp3_18(pp3_18),
        .pp3_19(pp3_19),
        .pp3_20(pp3_20),
        .pp3_21(pp3_21),
        .pp3_22(pp3_22),
        .pp3_23(pp3_23),
        .pp3_24(pp3_24),
        .pp3_25(pp3_25),
        .pp3_26(pp3_26),
        .pp3_27(pp3_27),
        .pp3_28(pp3_28),
        .pp3_29(pp3_29),
        .pp3_30(pp3_30),
        .pp3_31(pp3_31),
        .pp3_32(pp3_32),
        .pp3_33(pp3_33),
        .pp3_34(pp3_34),
        .pp3_35(pp3_35),
        .pp3_36(pp3_36),
        .pp3_37(pp3_37),
        .pp3_38(pp3_38),
        .pp3_39(pp3_39),
        .pp3_40(pp3_40),
        .pp3_41(pp3_41),
        .pp3_42(pp3_42),
        .pp3_43(pp3_43),
        .pp3_44(pp3_44),
        .pp3_45(pp3_45),
        .pp3_46(pp3_46),
        .pp3_47(pp3_47),
        .pp3_48(pp3_48),
        .pp3_49(pp3_49),
        .pp3_50(pp3_50),
        .pp3_51(pp3_51),
        .pp3_52(pp3_52),
        .pp3_53(pp3_53),
        .pp3_54(pp3_54),
        .pp3_55(pp3_55),
        .pp3_56(pp3_56),
        .pp3_57(pp3_57),
        .pp3_58(pp3_58),
        .pp3_59(pp3_59),
        .pp3_60(pp3_60),
        .pp3_61(pp3_61),
        .pp3_62(pp3_62),
        .pp3_63(pp3_63)
    );

    STAGE4_32 STAGE4(
        .pp3_0(pp3_0),
        .pp3_1(pp3_1),
        .pp3_2(pp3_2),
        .pp3_3(pp3_3),
        .pp3_4(pp3_4),
        .pp3_5(pp3_5),
        .pp3_6(pp3_6),
        .pp3_7(pp3_7),
        .pp3_8(pp3_8),
        .pp3_9(pp3_9),
        .pp3_10(pp3_10),
        .pp3_11(pp3_11),
        .pp3_12(pp3_12),
        .pp3_13(pp3_13),
        .pp3_14(pp3_14),
        .pp3_15(pp3_15),
        .pp3_16(pp3_16),
        .pp3_17(pp3_17),
        .pp3_18(pp3_18),
        .pp3_19(pp3_19),
        .pp3_20(pp3_20),
        .pp3_21(pp3_21),
        .pp3_22(pp3_22),
        .pp3_23(pp3_23),
        .pp3_24(pp3_24),
        .pp3_25(pp3_25),
        .pp3_26(pp3_26),
        .pp3_27(pp3_27),
        .pp3_28(pp3_28),
        .pp3_29(pp3_29),
        .pp3_30(pp3_30),
        .pp3_31(pp3_31),
        .pp3_32(pp3_32),
        .pp3_33(pp3_33),
        .pp3_34(pp3_34),
        .pp3_35(pp3_35),
        .pp3_36(pp3_36),
        .pp3_37(pp3_37),
        .pp3_38(pp3_38),
        .pp3_39(pp3_39),
        .pp3_40(pp3_40),
        .pp3_41(pp3_41),
        .pp3_42(pp3_42),
        .pp3_43(pp3_43),
        .pp3_44(pp3_44),
        .pp3_45(pp3_45),
        .pp3_46(pp3_46),
        .pp3_47(pp3_47),
        .pp3_48(pp3_48),
        .pp3_49(pp3_49),
        .pp3_50(pp3_50),
        .pp3_51(pp3_51),
        .pp3_52(pp3_52),
        .pp3_53(pp3_53),
        .pp3_54(pp3_54),
        .pp3_55(pp3_55),
        .pp3_56(pp3_56),
        .pp3_57(pp3_57),
        .pp3_58(pp3_58),
        .pp3_59(pp3_59),
        .pp3_60(pp3_60),
        .pp3_61(pp3_61),
        .pp3_62(pp3_62),
        .pp3_63(pp3_63),
        .A(A),
        .B(B)
    );


    // 使用CLA加法器计算最终结果
    CLA64bit Final_add(
        .A(A),  // 已经是64位
        .B(B),  // 已经是64位
        .Cin(cin_net),
        .Sum(P_APPROX),
        .Cout()
    );
endmodule



module STAGE1_32(
    input [31:0] A,
    input [31:0] B,
    output pp1_0,
    output [1:0] pp1_1,
    output [2:0] pp1_2,
    output [3:0] pp1_3,
    output [4:0] pp1_4,
    output [5:0] pp1_5,
    output [6:0] pp1_6,
    output [7:0] pp1_7,
    output [8:0] pp1_8,
    output [9:0] pp1_9,
    output [10:0] pp1_10,
    output [11:0] pp1_11,
    output [12:0] pp1_12,
    output [13:0] pp1_13,
    output [14:0] pp1_14,
    output [15:0] pp1_15,
    output [15:0] pp1_16,
    output [15:0] pp1_17,
    output [15:0] pp1_18,
    output [15:0] pp1_19,
    output [15:0] pp1_20,
    output [15:0] pp1_21,
    output [15:0] pp1_22,
    output [15:0] pp1_23,
    output [15:0] pp1_24,
    output [15:0] pp1_25,
    output [15:0] pp1_26,
    output [15:0] pp1_27,
    output [15:0] pp1_28,
    output [15:0] pp1_29,
    output [15:0] pp1_30,
    output [15:0] pp1_31,
    output [15:0] pp1_32,
    output [15:0] pp1_33,
    output [15:0] pp1_34,
    output [15:0] pp1_35,
    output [15:0] pp1_36,
    output [15:0] pp1_37,
    output [15:0] pp1_38,
    output [15:0] pp1_39,
    output [15:0] pp1_40,
    output [15:0] pp1_41,
    output [15:0] pp1_42,
    output [15:0] pp1_43,
    output [15:0] pp1_44,
    output [15:0] pp1_45,
    output [15:0] pp1_46,
    output [15:0] pp1_47,
    output [15:0] pp1_48,
    output [13:0] pp1_49,
    output [12:0] pp1_50,
    output [11:0] pp1_51,
    output [10:0] pp1_52,
    output [9:0] pp1_53,
    output [8:0] pp1_54,
    output [7:0] pp1_55,
    output [6:0] pp1_56,
    output [5:0] pp1_57,
    output [4:0] pp1_58,
    output [3:0] pp1_59,
    output [2:0] pp1_60,
    output [1:0] pp1_61,
    output pp1_62,
    output pp1_63
);
wire cin_net;
LOGIC0_X1 u_gnd (.Z(cin_net));
    wire pp1_16_ha_1_s;
    wire pp1_16_ha_1_c;
    wire pp1_17_e42_1_s;
    wire pp1_17_e42_1_c;
    wire pp1_17_e42_1_cout;
    wire pp1_18_e42_1_s;
    wire pp1_18_e42_1_c;
    wire pp1_18_e42_1_cout;
    wire pp1_18_ha_1_s;
    wire pp1_18_ha_1_c;
    wire pp1_19_e42_1_s;
    wire pp1_19_e42_1_c;
    wire pp1_19_e42_1_cout;
    wire pp1_19_e42_2_s;
    wire pp1_19_e42_2_c;
    wire pp1_19_e42_2_cout;
    wire pp1_20_e42_1_s;
    wire pp1_20_e42_1_c;
    wire pp1_20_e42_1_cout;
    wire pp1_20_e42_2_s;
    wire pp1_20_e42_2_c;
    wire pp1_20_e42_2_cout;
    wire pp1_20_ha_1_s;
    wire pp1_20_ha_1_c;
    wire pp1_21_e42_1_s;
    wire pp1_21_e42_1_c;
    wire pp1_21_e42_1_cout;
    wire pp1_21_e42_2_s;
    wire pp1_21_e42_2_c;
    wire pp1_21_e42_2_cout;
    wire pp1_21_e42_3_s;
    wire pp1_21_e42_3_c;
    wire pp1_21_e42_3_cout;
    wire pp1_22_e42_1_s;
    wire pp1_22_e42_1_c;
    wire pp1_22_e42_1_cout;
    wire pp1_22_e42_2_s;
    wire pp1_22_e42_2_c;
    wire pp1_22_e42_2_cout;
    wire pp1_22_e42_3_s;
    wire pp1_22_e42_3_c;
    wire pp1_22_e42_3_cout;
    wire pp1_22_ha_1_s;
    wire pp1_22_ha_1_c;
    wire pp1_23_e42_1_s;
    wire pp1_23_e42_1_c;
    wire pp1_23_e42_1_cout;
    wire pp1_23_e42_2_s;
    wire pp1_23_e42_2_c;
    wire pp1_23_e42_2_cout;
    wire pp1_23_e42_3_s;
    wire pp1_23_e42_3_c;
    wire pp1_23_e42_3_cout;
    wire pp1_23_e42_4_s;
    wire pp1_23_e42_4_c;
    wire pp1_23_e42_4_cout;
    wire pp1_24_e42_1_s;
    wire pp1_24_e42_1_c;
    wire pp1_24_e42_1_cout;
    wire pp1_24_e42_2_s;
    wire pp1_24_e42_2_c;
    wire pp1_24_e42_2_cout;
    wire pp1_24_e42_3_s;
    wire pp1_24_e42_3_c;
    wire pp1_24_e42_3_cout;
    wire pp1_24_e42_4_s;
    wire pp1_24_e42_4_c;
    wire pp1_24_e42_4_cout;
    wire pp1_24_ha_1_s;
    wire pp1_24_ha_1_c;
    wire pp1_25_e42_1_s;
    wire pp1_25_e42_1_c;
    wire pp1_25_e42_1_cout;
    wire pp1_25_e42_2_s;
    wire pp1_25_e42_2_c;
    wire pp1_25_e42_2_cout;
    wire pp1_25_e42_3_s;
    wire pp1_25_e42_3_c;
    wire pp1_25_e42_3_cout;
    wire pp1_25_e42_4_s;
    wire pp1_25_e42_4_c;
    wire pp1_25_e42_4_cout;
    wire pp1_25_e42_5_s;
    wire pp1_25_e42_5_c;
    wire pp1_25_e42_5_cout;
    wire pp1_26_e42_1_s;
    wire pp1_26_e42_1_c;
    wire pp1_26_e42_1_cout;
    wire pp1_26_e42_2_s;
    wire pp1_26_e42_2_c;
    wire pp1_26_e42_2_cout;
    wire pp1_26_e42_3_s;
    wire pp1_26_e42_3_c;
    wire pp1_26_e42_3_cout;
    wire pp1_26_e42_4_s;
    wire pp1_26_e42_4_c;
    wire pp1_26_e42_4_cout;
    wire pp1_26_e42_5_s;
    wire pp1_26_e42_5_c;
    wire pp1_26_e42_5_cout;
    wire pp1_26_ha_1_s;
    wire pp1_26_ha_1_c;
    wire pp1_27_e42_1_s;
    wire pp1_27_e42_1_c;
    wire pp1_27_e42_1_cout;
    wire pp1_27_e42_2_s;
    wire pp1_27_e42_2_c;
    wire pp1_27_e42_2_cout;
    wire pp1_27_e42_3_s;
    wire pp1_27_e42_3_c;
    wire pp1_27_e42_3_cout;
    wire pp1_27_e42_4_s;
    wire pp1_27_e42_4_c;
    wire pp1_27_e42_4_cout;
    wire pp1_27_e42_5_s;
    wire pp1_27_e42_5_c;
    wire pp1_27_e42_5_cout;
    wire pp1_27_e42_6_s;
    wire pp1_27_e42_6_c;
    wire pp1_27_e42_6_cout;
    wire pp1_28_e42_1_s;
    wire pp1_28_e42_1_c;
    wire pp1_28_e42_1_cout;
    wire pp1_28_e42_2_s;
    wire pp1_28_e42_2_c;
    wire pp1_28_e42_2_cout;
    wire pp1_28_e42_3_s;
    wire pp1_28_e42_3_c;
    wire pp1_28_e42_3_cout;
    wire pp1_28_e42_4_s;
    wire pp1_28_e42_4_c;
    wire pp1_28_e42_4_cout;
    wire pp1_28_e42_5_s;
    wire pp1_28_e42_5_c;
    wire pp1_28_e42_5_cout;
    wire pp1_28_e42_6_s;
    wire pp1_28_e42_6_c;
    wire pp1_28_e42_6_cout;
    wire pp1_28_ha_1_s;
    wire pp1_28_ha_1_c;
    wire pp1_29_e42_1_s;
    wire pp1_29_e42_1_c;
    wire pp1_29_e42_1_cout;
    wire pp1_29_e42_2_s;
    wire pp1_29_e42_2_c;
    wire pp1_29_e42_2_cout;
    wire pp1_29_e42_3_s;
    wire pp1_29_e42_3_c;
    wire pp1_29_e42_3_cout;
    wire pp1_29_e42_4_s;
    wire pp1_29_e42_4_c;
    wire pp1_29_e42_4_cout;
    wire pp1_29_e42_5_s;
    wire pp1_29_e42_5_c;
    wire pp1_29_e42_5_cout;
    wire pp1_29_e42_6_s;
    wire pp1_29_e42_6_c;
    wire pp1_29_e42_6_cout;
    wire pp1_29_e42_7_s;
    wire pp1_29_e42_7_c;
    wire pp1_29_e42_7_cout;
    wire pp1_30_e42_1_s;
    wire pp1_30_e42_1_c;
    wire pp1_30_e42_1_cout;
    wire pp1_30_e42_2_s;
    wire pp1_30_e42_2_c;
    wire pp1_30_e42_2_cout;
    wire pp1_30_e42_3_s;
    wire pp1_30_e42_3_c;
    wire pp1_30_e42_3_cout;
    wire pp1_30_e42_4_s;
    wire pp1_30_e42_4_c;
    wire pp1_30_e42_4_cout;
    wire pp1_30_e42_5_s;
    wire pp1_30_e42_5_c;
    wire pp1_30_e42_5_cout;
    wire pp1_30_e42_6_s;
    wire pp1_30_e42_6_c;
    wire pp1_30_e42_6_cout;
    wire pp1_30_e42_7_s;
    wire pp1_30_e42_7_c;
    wire pp1_30_e42_7_cout;
    wire pp1_30_ha_1_s;
    wire pp1_30_ha_1_c;
    wire pp1_31_e42_1_s;
    wire pp1_31_e42_1_c;
    wire pp1_31_e42_1_cout;
    wire pp1_31_e42_2_s;
    wire pp1_31_e42_2_c;
    wire pp1_31_e42_2_cout;
    wire pp1_31_e42_3_s;
    wire pp1_31_e42_3_c;
    wire pp1_31_e42_3_cout;
    wire pp1_31_e42_4_s;
    wire pp1_31_e42_4_c;
    wire pp1_31_e42_4_cout;
    wire pp1_31_e42_5_s;
    wire pp1_31_e42_5_c;
    wire pp1_31_e42_5_cout;
    wire pp1_31_e42_6_s;
    wire pp1_31_e42_6_c;
    wire pp1_31_e42_6_cout;
    wire pp1_31_e42_7_s;
    wire pp1_31_e42_7_c;
    wire pp1_31_e42_7_cout;
    wire pp1_31_e42_8_s;
    wire pp1_31_e42_8_c;
    wire pp1_31_e42_8_cout;
    wire pp1_32_e42_1_s;
    wire pp1_32_e42_1_c;
    wire pp1_32_e42_1_cout;
    wire pp1_32_e42_2_s;
    wire pp1_32_e42_2_c;
    wire pp1_32_e42_2_cout;
    wire pp1_32_e42_3_s;
    wire pp1_32_e42_3_c;
    wire pp1_32_e42_3_cout;
    wire pp1_32_e42_4_s;
    wire pp1_32_e42_4_c;
    wire pp1_32_e42_4_cout;
    wire pp1_32_e42_5_s;
    wire pp1_32_e42_5_c;
    wire pp1_32_e42_5_cout;
    wire pp1_32_e42_6_s;
    wire pp1_32_e42_6_c;
    wire pp1_32_e42_6_cout;
    wire pp1_32_e42_7_s;
    wire pp1_32_e42_7_c;
    wire pp1_32_e42_7_cout;
    wire pp1_32_e42_8_s;
    wire pp1_32_e42_8_c;
    wire pp1_32_e42_8_cout;
    wire pp1_33_e42_1_s;
    wire pp1_33_e42_1_c;
    wire pp1_33_e42_1_cout;
    wire pp1_33_e42_2_s;
    wire pp1_33_e42_2_c;
    wire pp1_33_e42_2_cout;
    wire pp1_33_e42_3_s;
    wire pp1_33_e42_3_c;
    wire pp1_33_e42_3_cout;
    wire pp1_33_e42_4_s;
    wire pp1_33_e42_4_c;
    wire pp1_33_e42_4_cout;
    wire pp1_33_e42_5_s;
    wire pp1_33_e42_5_c;
    wire pp1_33_e42_5_cout;
    wire pp1_33_e42_6_s;
    wire pp1_33_e42_6_c;
    wire pp1_33_e42_6_cout;
    wire pp1_33_e42_7_s;
    wire pp1_33_e42_7_c;
    wire pp1_33_e42_7_cout;
    wire pp1_33_fa_1_s;
    wire pp1_33_fa_1_c;
    wire pp1_34_e42_1_s;
    wire pp1_34_e42_1_c;
    wire pp1_34_e42_1_cout;
    wire pp1_34_e42_2_s;
    wire pp1_34_e42_2_c;
    wire pp1_34_e42_2_cout;
    wire pp1_34_e42_3_s;
    wire pp1_34_e42_3_c;
    wire pp1_34_e42_3_cout;
    wire pp1_34_e42_4_s;
    wire pp1_34_e42_4_c;
    wire pp1_34_e42_4_cout;
    wire pp1_34_e42_5_s;
    wire pp1_34_e42_5_c;
    wire pp1_34_e42_5_cout;
    wire pp1_34_e42_6_s;
    wire pp1_34_e42_6_c;
    wire pp1_34_e42_6_cout;
    wire pp1_34_e42_7_s;
    wire pp1_34_e42_7_c;
    wire pp1_34_e42_7_cout;
    wire pp1_35_e42_1_s;
    wire pp1_35_e42_1_c;
    wire pp1_35_e42_1_cout;
    wire pp1_35_e42_2_s;
    wire pp1_35_e42_2_c;
    wire pp1_35_e42_2_cout;
    wire pp1_35_e42_3_s;
    wire pp1_35_e42_3_c;
    wire pp1_35_e42_3_cout;
    wire pp1_35_e42_4_s;
    wire pp1_35_e42_4_c;
    wire pp1_35_e42_4_cout;
    wire pp1_35_e42_5_s;
    wire pp1_35_e42_5_c;
    wire pp1_35_e42_5_cout;
    wire pp1_35_e42_6_s;
    wire pp1_35_e42_6_c;
    wire pp1_35_e42_6_cout;
    wire pp1_35_fa_1_s;
    wire pp1_35_fa_1_c;
    wire pp1_36_e42_1_s;
    wire pp1_36_e42_1_c;
    wire pp1_36_e42_1_cout;
    wire pp1_36_e42_2_s;
    wire pp1_36_e42_2_c;
    wire pp1_36_e42_2_cout;
    wire pp1_36_e42_3_s;
    wire pp1_36_e42_3_c;
    wire pp1_36_e42_3_cout;
    wire pp1_36_e42_4_s;
    wire pp1_36_e42_4_c;
    wire pp1_36_e42_4_cout;
    wire pp1_36_e42_5_s;
    wire pp1_36_e42_5_c;
    wire pp1_36_e42_5_cout;
    wire pp1_36_e42_6_s;
    wire pp1_36_e42_6_c;
    wire pp1_36_e42_6_cout;
    wire pp1_37_e42_1_s;
    wire pp1_37_e42_1_c;
    wire pp1_37_e42_1_cout;
    wire pp1_37_e42_2_s;
    wire pp1_37_e42_2_c;
    wire pp1_37_e42_2_cout;
    wire pp1_37_e42_3_s;
    wire pp1_37_e42_3_c;
    wire pp1_37_e42_3_cout;
    wire pp1_37_e42_4_s;
    wire pp1_37_e42_4_c;
    wire pp1_37_e42_4_cout;
    wire pp1_37_e42_5_s;
    wire pp1_37_e42_5_c;
    wire pp1_37_e42_5_cout;
    wire pp1_37_fa_1_s;
    wire pp1_37_fa_1_c;
    wire pp1_38_e42_1_s;
    wire pp1_38_e42_1_c;
    wire pp1_38_e42_1_cout;
    wire pp1_38_e42_2_s;
    wire pp1_38_e42_2_c;
    wire pp1_38_e42_2_cout;
    wire pp1_38_e42_3_s;
    wire pp1_38_e42_3_c;
    wire pp1_38_e42_3_cout;
    wire pp1_38_e42_4_s;
    wire pp1_38_e42_4_c;
    wire pp1_38_e42_4_cout;
    wire pp1_38_e42_5_s;
    wire pp1_38_e42_5_c;
    wire pp1_38_e42_5_cout;
    wire pp1_39_e42_1_s;
    wire pp1_39_e42_1_c;
    wire pp1_39_e42_1_cout;
    wire pp1_39_e42_2_s;
    wire pp1_39_e42_2_c;
    wire pp1_39_e42_2_cout;
    wire pp1_39_e42_3_s;
    wire pp1_39_e42_3_c;
    wire pp1_39_e42_3_cout;
    wire pp1_39_e42_4_s;
    wire pp1_39_e42_4_c;
    wire pp1_39_e42_4_cout;
    wire pp1_39_fa_1_s;
    wire pp1_39_fa_1_c;
    wire pp1_40_e42_1_s;
    wire pp1_40_e42_1_c;
    wire pp1_40_e42_1_cout;
    wire pp1_40_e42_2_s;
    wire pp1_40_e42_2_c;
    wire pp1_40_e42_2_cout;
    wire pp1_40_e42_3_s;
    wire pp1_40_e42_3_c;
    wire pp1_40_e42_3_cout;
    wire pp1_40_e42_4_s;
    wire pp1_40_e42_4_c;
    wire pp1_40_e42_4_cout;
    wire pp1_41_e42_1_s;
    wire pp1_41_e42_1_c;
    wire pp1_41_e42_1_cout;
    wire pp1_41_e42_2_s;
    wire pp1_41_e42_2_c;
    wire pp1_41_e42_2_cout;
    wire pp1_41_e42_3_s;
    wire pp1_41_e42_3_c;
    wire pp1_41_e42_3_cout;
    wire pp1_41_fa_1_s;
    wire pp1_41_fa_1_c;
    wire pp1_42_e42_1_s;
    wire pp1_42_e42_1_c;
    wire pp1_42_e42_1_cout;
    wire pp1_42_e42_2_s;
    wire pp1_42_e42_2_c;
    wire pp1_42_e42_2_cout;
    wire pp1_42_e42_3_s;
    wire pp1_42_e42_3_c;
    wire pp1_42_e42_3_cout;
    wire pp1_43_e42_1_s;
    wire pp1_43_e42_1_c;
    wire pp1_43_e42_1_cout;
    wire pp1_43_e42_2_s;
    wire pp1_43_e42_2_c;
    wire pp1_43_e42_2_cout;
    wire pp1_43_fa_1_s;
    wire pp1_43_fa_1_c;
    wire pp1_44_e42_1_s;
    wire pp1_44_e42_1_c;
    wire pp1_44_e42_1_cout;
    wire pp1_44_e42_2_s;
    wire pp1_44_e42_2_c;
    wire pp1_44_e42_2_cout;
    wire pp1_45_e42_1_s;
    wire pp1_45_e42_1_c;
    wire pp1_45_e42_1_cout;
    wire pp1_45_fa_1_s;
    wire pp1_45_fa_1_c;
    wire pp1_46_e42_1_s;
    wire pp1_46_e42_1_c;
    wire pp1_46_e42_1_cout;

// 压缩器模块实例化
    assign pp1_0 = A[0] & B[0];
    assign pp1_1 = {A[0] & B[1], A[1] & B[0]};
    assign pp1_2 = {A[0] & B[2], A[1] & B[1], A[2] & B[0]};
    assign pp1_3 = {A[0] & B[3], A[1] & B[2], A[2] & B[1], A[3] & B[0]};
    assign pp1_4 = {A[0] & B[4], A[1] & B[3], A[2] & B[2], A[3] & B[1], A[4] & B[0]};
    assign pp1_5 = {A[0] & B[5], A[1] & B[4], A[2] & B[3], A[3] & B[2], A[4] & B[1], A[5] & B[0]};
    assign pp1_6 = {A[0] & B[6], A[1] & B[5], A[2] & B[4], A[3] & B[3], A[4] & B[2], A[5] & B[1], A[6] & B[0]};
    assign pp1_7 = {A[0] & B[7], A[1] & B[6], A[2] & B[5], A[3] & B[4], A[4] & B[3], A[5] & B[2], A[6] & B[1], A[7] & B[0]};
    assign pp1_8 = {A[0] & B[8], A[1] & B[7], A[2] & B[6], A[3] & B[5], A[4] & B[4], A[5] & B[3], A[6] & B[2], A[7] & B[1], A[8] & B[0]};
    assign pp1_9 = {A[0] & B[9], A[1] & B[8], A[2] & B[7], A[3] & B[6], A[4] & B[5], A[5] & B[4], A[6] & B[3], A[7] & B[2], A[8] & B[1], A[9] & B[0]};
    assign pp1_10 = {A[0] & B[10], A[1] & B[9], A[2] & B[8], A[3] & B[7], A[4] & B[6], A[5] & B[5], A[6] & B[4], A[7] & B[3], A[8] & B[2], A[9] & B[1], A[10] & B[0]};
    assign pp1_11 = {A[0] & B[11], A[1] & B[10], A[2] & B[9], A[3] & B[8], A[4] & B[7], A[5] & B[6], A[6] & B[5], A[7] & B[4], A[8] & B[3], A[9] & B[2], A[10] & B[1], A[11] & B[0]};
    assign pp1_12 = {A[0] & B[12], A[1] & B[11], A[2] & B[10], A[3] & B[9], A[4] & B[8], A[5] & B[7], A[6] & B[6], A[7] & B[5], A[8] & B[4], A[9] & B[3], A[10] & B[2], A[11] & B[1], A[12] & B[0]};
    assign pp1_13 = {A[0] & B[13], A[1] & B[12], A[2] & B[11], A[3] & B[10], A[4] & B[9], A[5] & B[8], A[6] & B[7], A[7] & B[6], A[8] & B[5], A[9] & B[4], A[10] & B[3], A[11] & B[2], A[12] & B[1], A[13] & B[0]};
    assign pp1_14 = {A[0] & B[14], A[1] & B[13], A[2] & B[12], A[3] & B[11], A[4] & B[10], A[5] & B[9], A[6] & B[8], A[7] & B[7], A[8] & B[6], A[9] & B[5], A[10] & B[4], A[11] & B[3], A[12] & B[2], A[13] & B[1], A[14] & B[0]};
    assign pp1_15 = {A[0] & B[15], A[1] & B[14], A[2] & B[13], A[3] & B[12], A[4] & B[11], A[5] & B[10], A[6] & B[9], A[7] & B[8], A[8] & B[7], A[9] & B[6], A[10] & B[5], A[11] & B[4], A[12] & B[3], A[13] & B[2], A[14] & B[1], A[15] & B[0]};
    Half_adder Half_adder_pp_16_1(
        .a(A[0] & B[16]),
        .b(A[1] & B[15]),
        .S(pp1_16_ha_1_s),
        .C(pp1_16_ha_1_c)
    );
    assign pp1_16 = {A[2] & B[14], A[3] & B[13], A[4] & B[12], A[5] & B[11], A[6] & B[10], A[7] & B[9], A[8] & B[8], A[9] & B[7], A[10] & B[6], A[11] & B[5], A[12] & B[4], A[13] & B[3], A[14] & B[2], A[15] & B[1], A[16] & B[0], pp1_16_ha_1_s};
  
    E_4_2 E_4_2_pp_17_1(
        .a(A[0] & B[17]),
        .b(A[1] & B[16]),
        .c(A[2] & B[15]),
        .d(A[3] & B[14]),
        .CIN(cin_net),
        .S(pp1_17_e42_1_s),
        .C(pp1_17_e42_1_c),
        .COUT(pp1_17_e42_1_cout)
    );
    assign pp1_17 = {A[4] & B[13], A[5] & B[12], A[6] & B[11], A[7] & B[10], A[8] & B[9], A[9] & B[8], A[10] & B[7], A[11] & B[6], A[12] & B[5], A[13] & B[4], A[14] & B[3], A[15] & B[2], A[16] & B[1], A[17] & B[0], pp1_16_ha_1_c, pp1_17_e42_1_s};
    E_4_2 E_4_2_pp_18_1(
        .a(A[0] & B[18]),
        .b(A[1] & B[17]),
        .c(A[2] & B[16]),
        .d(A[3] & B[15]),
        .CIN(pp1_17_e42_1_cout),
        .S(pp1_18_e42_1_s),
        .C(pp1_18_e42_1_c),
        .COUT(pp1_18_e42_1_cout)
    );
    Half_adder Half_adder_pp_18_1(
        .a(A[4] & B[14]),
        .b(A[5] & B[13]),
        .S(pp1_18_ha_1_s),
        .C(pp1_18_ha_1_c)
    );
    assign pp1_18 = {A[6] & B[12], A[7] & B[11], A[8] & B[10], A[9] & B[9], A[10] & B[8], A[11] & B[7], A[12] & B[6], A[13] & B[5], A[14] & B[4], A[15] & B[3], A[16] & B[2], A[17] & B[1], A[18] & B[0], pp1_17_e42_1_c, pp1_18_e42_1_s, pp1_18_ha_1_s};
    E_4_2 E_4_2_pp_19_1(
        .a(A[0] & B[19]),
        .b(A[1] & B[18]),
        .c(A[2] & B[17]),
        .d(A[3] & B[16]),
        .CIN(pp1_18_e42_1_cout),
        .S(pp1_19_e42_1_s),
        .C(pp1_19_e42_1_c),
        .COUT(pp1_19_e42_1_cout)
    );


    E_4_2 E_4_2_pp_19_2(
        .a(A[4] & B[15]),
        .b(A[5] & B[14]),
        .c(A[6] & B[13]),
        .d(A[7] & B[12]),
        .CIN(cin_net),
        .S(pp1_19_e42_2_s),
        .C(pp1_19_e42_2_c),
        .COUT(pp1_19_e42_2_cout)
    );
    assign pp1_19 = {A[8] & B[11], A[9] & B[10], A[10] & B[9], A[11] & B[8], A[12] & B[7], A[13] & B[6], A[14] & B[5], A[15] & B[4], A[16] & B[3], A[17] & B[2], A[18] & B[1], A[19] & B[0], pp1_18_e42_1_c, pp1_18_ha_1_c, pp1_19_e42_1_s, pp1_19_e42_2_s};
    E_4_2 E_4_2_pp_20_1(
        .a(A[0] & B[20]),
        .b(A[1] & B[19]),
        .c(A[2] & B[18]),
        .d(A[3] & B[17]),
        .CIN(pp1_19_e42_1_cout),
        .S(pp1_20_e42_1_s),
        .C(pp1_20_e42_1_c),
        .COUT(pp1_20_e42_1_cout)
    );
    E_4_2 E_4_2_pp_20_2(
        .a(A[4] & B[16]),
        .b(A[5] & B[15]),
        .c(A[6] & B[14]),
        .d(A[7] & B[13]),
        .CIN(pp1_19_e42_2_cout),
        .S(pp1_20_e42_2_s),
        .C(pp1_20_e42_2_c),
        .COUT(pp1_20_e42_2_cout)
    );
    Half_adder Half_adder_pp_20_1(
        .a(A[8] & B[12]),
        .b(A[9] & B[11]),
        .S(pp1_20_ha_1_s),
        .C(pp1_20_ha_1_c)
    );
    assign pp1_20 = {A[10] & B[10], A[11] & B[9], A[12] & B[8], A[13] & B[7], A[14] & B[6], A[15] & B[5], A[16] & B[4], A[17] & B[3], A[18] & B[2], A[19] & B[1], A[20] & B[0], pp1_19_e42_1_c, pp1_19_e42_2_c, pp1_20_e42_1_s, pp1_20_e42_2_s, pp1_20_ha_1_s};
    E_4_2 E_4_2_pp_21_1(
        .a(A[0] & B[21]),
        .b(A[1] & B[20]),
        .c(A[2] & B[19]),
        .d(A[3] & B[18]),
        .CIN(pp1_20_e42_1_cout),
        .S(pp1_21_e42_1_s),
        .C(pp1_21_e42_1_c),
        .COUT(pp1_21_e42_1_cout)
    );
    E_4_2 E_4_2_pp_21_2(
        .a(A[4] & B[17]),
        .b(A[5] & B[16]),
        .c(A[6] & B[15]),
        .d(A[7] & B[14]),
        .CIN(pp1_20_e42_2_cout),
        .S(pp1_21_e42_2_s),
        .C(pp1_21_e42_2_c),
        .COUT(pp1_21_e42_2_cout)
    );


    E_4_2 E_4_2_pp_21_3(
        .a(A[8] & B[13]),
        .b(A[9] & B[12]),
        .c(A[10] & B[11]),
        .d(A[11] & B[10]),
        .CIN(cin_net),
        .S(pp1_21_e42_3_s),
        .C(pp1_21_e42_3_c),
        .COUT(pp1_21_e42_3_cout)
    );
    assign pp1_21 = {A[12] & B[9], A[13] & B[8], A[14] & B[7], A[15] & B[6], A[16] & B[5], A[17] & B[4], A[18] & B[3], A[19] & B[2], A[20] & B[1], A[21] & B[0], pp1_20_e42_1_c, pp1_20_e42_2_c, pp1_20_ha_1_c, pp1_21_e42_1_s, pp1_21_e42_2_s, pp1_21_e42_3_s};
    E_4_2 E_4_2_pp_22_1(
        .a(A[0] & B[22]),
        .b(A[1] & B[21]),
        .c(A[2] & B[20]),
        .d(A[3] & B[19]),
        .CIN(pp1_21_e42_1_cout),
        .S(pp1_22_e42_1_s),
        .C(pp1_22_e42_1_c),
        .COUT(pp1_22_e42_1_cout)
    );
    E_4_2 E_4_2_pp_22_2(
        .a(A[4] & B[18]),
        .b(A[5] & B[17]),
        .c(A[6] & B[16]),
        .d(A[7] & B[15]),
        .CIN(pp1_21_e42_2_cout),
        .S(pp1_22_e42_2_s),
        .C(pp1_22_e42_2_c),
        .COUT(pp1_22_e42_2_cout)
    );
    E_4_2 E_4_2_pp_22_3(
        .a(A[8] & B[14]),
        .b(A[9] & B[13]),
        .c(A[10] & B[12]),
        .d(A[11] & B[11]),
        .CIN(pp1_21_e42_3_cout),
        .S(pp1_22_e42_3_s),
        .C(pp1_22_e42_3_c),
        .COUT(pp1_22_e42_3_cout)
    );
    Half_adder Half_adder_pp_22_1(
        .a(A[12] & B[10]),
        .b(A[13] & B[9]),
        .S(pp1_22_ha_1_s),
        .C(pp1_22_ha_1_c)
    );
    assign pp1_22 = {A[14] & B[8], A[15] & B[7], A[16] & B[6], A[17] & B[5], A[18] & B[4], A[19] & B[3], A[20] & B[2], A[21] & B[1], A[22] & B[0], pp1_21_e42_1_c, pp1_21_e42_2_c, pp1_21_e42_3_c, pp1_22_e42_1_s, pp1_22_e42_2_s, pp1_22_e42_3_s, pp1_22_ha_1_s};
    E_4_2 E_4_2_pp_23_1(
        .a(A[0] & B[23]),
        .b(A[1] & B[22]),
        .c(A[2] & B[21]),
        .d(A[3] & B[20]),
        .CIN(pp1_22_e42_1_cout),
        .S(pp1_23_e42_1_s),
        .C(pp1_23_e42_1_c),
        .COUT(pp1_23_e42_1_cout)
    );
    E_4_2 E_4_2_pp_23_2(
        .a(A[4] & B[19]),
        .b(A[5] & B[18]),
        .c(A[6] & B[17]),
        .d(A[7] & B[16]),
        .CIN(pp1_22_e42_2_cout),
        .S(pp1_23_e42_2_s),
        .C(pp1_23_e42_2_c),
        .COUT(pp1_23_e42_2_cout)
    );
    E_4_2 E_4_2_pp_23_3(
        .a(A[8] & B[15]),
        .b(A[9] & B[14]),
        .c(A[10] & B[13]),
        .d(A[11] & B[12]),
        .CIN(pp1_22_e42_3_cout),
        .S(pp1_23_e42_3_s),
        .C(pp1_23_e42_3_c),
        .COUT(pp1_23_e42_3_cout)
    );



    E_4_2 E_4_2_pp_23_4(
        .a(A[12] & B[11]),
        .b(A[13] & B[10]),
        .c(A[14] & B[9]),
        .d(A[15] & B[8]),
        .CIN(cin_net),
        .S(pp1_23_e42_4_s),
        .C(pp1_23_e42_4_c),
        .COUT(pp1_23_e42_4_cout)
    );
    assign pp1_23 = {A[16] & B[7], A[17] & B[6], A[18] & B[5], A[19] & B[4], A[20] & B[3], A[21] & B[2], A[22] & B[1], A[23] & B[0], pp1_22_e42_1_c, pp1_22_e42_2_c, pp1_22_e42_3_c, pp1_22_ha_1_c, pp1_23_e42_1_s, pp1_23_e42_2_s, pp1_23_e42_3_s, pp1_23_e42_4_s};
    E_4_2 E_4_2_pp_24_1(
        .a(A[0] & B[24]),
        .b(A[1] & B[23]),
        .c(A[2] & B[22]),
        .d(A[3] & B[21]),
        .CIN(pp1_23_e42_1_cout),
        .S(pp1_24_e42_1_s),
        .C(pp1_24_e42_1_c),
        .COUT(pp1_24_e42_1_cout)
    );
    E_4_2 E_4_2_pp_24_2(
        .a(A[4] & B[20]),
        .b(A[5] & B[19]),
        .c(A[6] & B[18]),
        .d(A[7] & B[17]),
        .CIN(pp1_23_e42_2_cout),
        .S(pp1_24_e42_2_s),
        .C(pp1_24_e42_2_c),
        .COUT(pp1_24_e42_2_cout)
    );
    E_4_2 E_4_2_pp_24_3(
        .a(A[8] & B[16]),
        .b(A[9] & B[15]),
        .c(A[10] & B[14]),
        .d(A[11] & B[13]),
        .CIN(pp1_23_e42_3_cout),
        .S(pp1_24_e42_3_s),
        .C(pp1_24_e42_3_c),
        .COUT(pp1_24_e42_3_cout)
    );
    E_4_2 E_4_2_pp_24_4(
        .a(A[12] & B[12]),
        .b(A[13] & B[11]),
        .c(A[14] & B[10]),
        .d(A[15] & B[9]),
        .CIN(pp1_23_e42_4_cout),
        .S(pp1_24_e42_4_s),
        .C(pp1_24_e42_4_c),
        .COUT(pp1_24_e42_4_cout)
    );
    Half_adder Half_adder_pp_24_1(
        .a(A[16] & B[8]),
        .b(A[17] & B[7]),
        .S(pp1_24_ha_1_s),
        .C(pp1_24_ha_1_c)
    );
    assign pp1_24 = {A[18] & B[6], A[19] & B[5], A[20] & B[4], A[21] & B[3], A[22] & B[2], A[23] & B[1], A[24] & B[0], pp1_23_e42_1_c, pp1_23_e42_2_c, pp1_23_e42_3_c, pp1_23_e42_4_c, pp1_24_e42_1_s, pp1_24_e42_2_s, pp1_24_e42_3_s, pp1_24_e42_4_s, pp1_24_ha_1_s};
    E_4_2 E_4_2_pp_25_1(
        .a(A[0] & B[25]),
        .b(A[1] & B[24]),
        .c(A[2] & B[23]),
        .d(A[3] & B[22]),
        .CIN(pp1_24_e42_1_cout),
        .S(pp1_25_e42_1_s),
        .C(pp1_25_e42_1_c),
        .COUT(pp1_25_e42_1_cout)
    );
    E_4_2 E_4_2_pp_25_2(
        .a(A[4] & B[21]),
        .b(A[5] & B[20]),
        .c(A[6] & B[19]),
        .d(A[7] & B[18]),
        .CIN(pp1_24_e42_2_cout),
        .S(pp1_25_e42_2_s),
        .C(pp1_25_e42_2_c),
        .COUT(pp1_25_e42_2_cout)
    );
    E_4_2 E_4_2_pp_25_3(
        .a(A[8] & B[17]),
        .b(A[9] & B[16]),
        .c(A[10] & B[15]),
        .d(A[11] & B[14]),
        .CIN(pp1_24_e42_3_cout),
        .S(pp1_25_e42_3_s),
        .C(pp1_25_e42_3_c),
        .COUT(pp1_25_e42_3_cout)
    );
    E_4_2 E_4_2_pp_25_4(
        .a(A[12] & B[13]),
        .b(A[13] & B[12]),
        .c(A[14] & B[11]),
        .d(A[15] & B[10]),
        .CIN(pp1_24_e42_4_cout),
        .S(pp1_25_e42_4_s),
        .C(pp1_25_e42_4_c),
        .COUT(pp1_25_e42_4_cout)
    );


    E_4_2 E_4_2_pp_25_5(
        .a(A[16] & B[9]),
        .b(A[17] & B[8]),
        .c(A[18] & B[7]),
        .d(A[19] & B[6]),
        .CIN(cin_net),
        .S(pp1_25_e42_5_s),
        .C(pp1_25_e42_5_c),
        .COUT(pp1_25_e42_5_cout)
    );
    assign pp1_25 = {A[20] & B[5], A[21] & B[4], A[22] & B[3], A[23] & B[2], A[24] & B[1], A[25] & B[0], pp1_24_e42_1_c, pp1_24_e42_2_c, pp1_24_e42_3_c, pp1_24_e42_4_c, pp1_24_ha_1_c, pp1_25_e42_1_s, pp1_25_e42_2_s, pp1_25_e42_3_s, pp1_25_e42_4_s, pp1_25_e42_5_s};
    E_4_2 E_4_2_pp_26_1(
        .a(A[0] & B[26]),
        .b(A[1] & B[25]),
        .c(A[2] & B[24]),
        .d(A[3] & B[23]),
        .CIN(pp1_25_e42_1_cout),
        .S(pp1_26_e42_1_s),
        .C(pp1_26_e42_1_c),
        .COUT(pp1_26_e42_1_cout)
    );
    E_4_2 E_4_2_pp_26_2(
        .a(A[4] & B[22]),
        .b(A[5] & B[21]),
        .c(A[6] & B[20]),
        .d(A[7] & B[19]),
        .CIN(pp1_25_e42_2_cout),
        .S(pp1_26_e42_2_s),
        .C(pp1_26_e42_2_c),
        .COUT(pp1_26_e42_2_cout)
    );
    E_4_2 E_4_2_pp_26_3(
        .a(A[8] & B[18]),
        .b(A[9] & B[17]),
        .c(A[10] & B[16]),
        .d(A[11] & B[15]),
        .CIN(pp1_25_e42_3_cout),
        .S(pp1_26_e42_3_s),
        .C(pp1_26_e42_3_c),
        .COUT(pp1_26_e42_3_cout)
    );
    E_4_2 E_4_2_pp_26_4(
        .a(A[12] & B[14]),
        .b(A[13] & B[13]),
        .c(A[14] & B[12]),
        .d(A[15] & B[11]),
        .CIN(pp1_25_e42_4_cout),
        .S(pp1_26_e42_4_s),
        .C(pp1_26_e42_4_c),
        .COUT(pp1_26_e42_4_cout)
    );
    E_4_2 E_4_2_pp_26_5(
        .a(A[16] & B[10]),
        .b(A[17] & B[9]),
        .c(A[18] & B[8]),
        .d(A[19] & B[7]),
        .CIN(pp1_25_e42_5_cout),
        .S(pp1_26_e42_5_s),
        .C(pp1_26_e42_5_c),
        .COUT(pp1_26_e42_5_cout)
    );
    Half_adder Half_adder_pp_26_1(
        .a(A[20] & B[6]),
        .b(A[21] & B[5]),
        .S(pp1_26_ha_1_s),
        .C(pp1_26_ha_1_c)
    );
    assign pp1_26 = {A[22] & B[4], A[23] & B[3], A[24] & B[2], A[25] & B[1], A[26] & B[0], pp1_25_e42_1_c, pp1_25_e42_2_c, pp1_25_e42_3_c, pp1_25_e42_4_c, pp1_25_e42_5_c, pp1_26_e42_1_s, pp1_26_e42_2_s, pp1_26_e42_3_s, pp1_26_e42_4_s, pp1_26_e42_5_s, pp1_26_ha_1_s};
    E_4_2 E_4_2_pp_27_1(
        .a(A[0] & B[27]),
        .b(A[1] & B[26]),
        .c(A[2] & B[25]),
        .d(A[3] & B[24]),
        .CIN(pp1_26_e42_1_cout),
        .S(pp1_27_e42_1_s),
        .C(pp1_27_e42_1_c),
        .COUT(pp1_27_e42_1_cout)
    );
    E_4_2 E_4_2_pp_27_2(
        .a(A[4] & B[23]),
        .b(A[5] & B[22]),
        .c(A[6] & B[21]),
        .d(A[7] & B[20]),
        .CIN(pp1_26_e42_2_cout),
        .S(pp1_27_e42_2_s),
        .C(pp1_27_e42_2_c),
        .COUT(pp1_27_e42_2_cout)
    );
    E_4_2 E_4_2_pp_27_3(
        .a(A[8] & B[19]),
        .b(A[9] & B[18]),
        .c(A[10] & B[17]),
        .d(A[11] & B[16]),
        .CIN(pp1_26_e42_3_cout),
        .S(pp1_27_e42_3_s),
        .C(pp1_27_e42_3_c),
        .COUT(pp1_27_e42_3_cout)
    );
    E_4_2 E_4_2_pp_27_4(
        .a(A[12] & B[15]),
        .b(A[13] & B[14]),
        .c(A[14] & B[13]),
        .d(A[15] & B[12]),
        .CIN(pp1_26_e42_4_cout),
        .S(pp1_27_e42_4_s),
        .C(pp1_27_e42_4_c),
        .COUT(pp1_27_e42_4_cout)
    );
    E_4_2 E_4_2_pp_27_5(
        .a(A[16] & B[11]),
        .b(A[17] & B[10]),
        .c(A[18] & B[9]),
        .d(A[19] & B[8]),
        .CIN(pp1_26_e42_5_cout),
        .S(pp1_27_e42_5_s),
        .C(pp1_27_e42_5_c),
        .COUT(pp1_27_e42_5_cout)
    );

    

    E_4_2 E_4_2_pp_27_6(
        .a(A[20] & B[7]),
        .b(A[21] & B[6]),
        .c(A[22] & B[5]),
        .d(A[23] & B[4]),
        .CIN(cin_net),
        .S(pp1_27_e42_6_s),
        .C(pp1_27_e42_6_c),
        .COUT(pp1_27_e42_6_cout)
    );
    assign pp1_27 = {A[24] & B[3], A[25] & B[2], A[26] & B[1], A[27] & B[0], pp1_26_e42_1_c, pp1_26_e42_2_c, pp1_26_e42_3_c, pp1_26_e42_4_c, pp1_26_e42_5_c, pp1_26_ha_1_c, pp1_27_e42_1_s, pp1_27_e42_2_s, pp1_27_e42_3_s, pp1_27_e42_4_s, pp1_27_e42_5_s, pp1_27_e42_6_s};
    E_4_2 E_4_2_pp_28_1(
        .a(A[0] & B[28]),
        .b(A[1] & B[27]),
        .c(A[2] & B[26]),
        .d(A[3] & B[25]),
        .CIN(pp1_27_e42_1_cout),
        .S(pp1_28_e42_1_s),
        .C(pp1_28_e42_1_c),
        .COUT(pp1_28_e42_1_cout)
    );
    E_4_2 E_4_2_pp_28_2(
        .a(A[4] & B[24]),
        .b(A[5] & B[23]),
        .c(A[6] & B[22]),
        .d(A[7] & B[21]),
        .CIN(pp1_27_e42_2_cout),
        .S(pp1_28_e42_2_s),
        .C(pp1_28_e42_2_c),
        .COUT(pp1_28_e42_2_cout)
    );
    E_4_2 E_4_2_pp_28_3(
        .a(A[8] & B[20]),
        .b(A[9] & B[19]),
        .c(A[10] & B[18]),
        .d(A[11] & B[17]),
        .CIN(pp1_27_e42_3_cout),
        .S(pp1_28_e42_3_s),
        .C(pp1_28_e42_3_c),
        .COUT(pp1_28_e42_3_cout)
    );
    E_4_2 E_4_2_pp_28_4(
        .a(A[12] & B[16]),
        .b(A[13] & B[15]),
        .c(A[14] & B[14]),
        .d(A[15] & B[13]),
        .CIN(pp1_27_e42_4_cout),
        .S(pp1_28_e42_4_s),
        .C(pp1_28_e42_4_c),
        .COUT(pp1_28_e42_4_cout)
    );
    E_4_2 E_4_2_pp_28_5(
        .a(A[16] & B[12]),
        .b(A[17] & B[11]),
        .c(A[18] & B[10]),
        .d(A[19] & B[9]),
        .CIN(pp1_27_e42_5_cout),
        .S(pp1_28_e42_5_s),
        .C(pp1_28_e42_5_c),
        .COUT(pp1_28_e42_5_cout)
    );
    E_4_2 E_4_2_pp_28_6(
        .a(A[20] & B[8]),
        .b(A[21] & B[7]),
        .c(A[22] & B[6]),
        .d(A[23] & B[5]),
        .CIN(pp1_27_e42_6_cout),
        .S(pp1_28_e42_6_s),
        .C(pp1_28_e42_6_c),
        .COUT(pp1_28_e42_6_cout)
    );
    Half_adder Half_adder_pp_28_1(
        .a(A[24] & B[4]),
        .b(A[25] & B[3]),
        .S(pp1_28_ha_1_s),
        .C(pp1_28_ha_1_c)
    );
    assign pp1_28 = {A[26] & B[2], A[27] & B[1], A[28] & B[0], pp1_27_e42_1_c, pp1_27_e42_2_c, pp1_27_e42_3_c, pp1_27_e42_4_c, pp1_27_e42_5_c, pp1_27_e42_6_c, pp1_28_e42_1_s, pp1_28_e42_2_s, pp1_28_e42_3_s, pp1_28_e42_4_s, pp1_28_e42_5_s, pp1_28_e42_6_s, pp1_28_ha_1_s};
    E_4_2 E_4_2_pp_29_1(
        .a(A[0] & B[29]),
        .b(A[1] & B[28]),
        .c(A[2] & B[27]),
        .d(A[3] & B[26]),
        .CIN(pp1_28_e42_1_cout),
        .S(pp1_29_e42_1_s),
        .C(pp1_29_e42_1_c),
        .COUT(pp1_29_e42_1_cout)
    );
    E_4_2 E_4_2_pp_29_2(
        .a(A[4] & B[25]),
        .b(A[5] & B[24]),
        .c(A[6] & B[23]),
        .d(A[7] & B[22]),
        .CIN(pp1_28_e42_2_cout),
        .S(pp1_29_e42_2_s),
        .C(pp1_29_e42_2_c),
        .COUT(pp1_29_e42_2_cout)
    );
    E_4_2 E_4_2_pp_29_3(
        .a(A[8] & B[21]),
        .b(A[9] & B[20]),
        .c(A[10] & B[19]),
        .d(A[11] & B[18]),
        .CIN(pp1_28_e42_3_cout),
        .S(pp1_29_e42_3_s),
        .C(pp1_29_e42_3_c),
        .COUT(pp1_29_e42_3_cout)
    );
    E_4_2 E_4_2_pp_29_4(
        .a(A[12] & B[17]),
        .b(A[13] & B[16]),
        .c(A[14] & B[15]),
        .d(A[15] & B[14]),
        .CIN(pp1_28_e42_4_cout),
        .S(pp1_29_e42_4_s),
        .C(pp1_29_e42_4_c),
        .COUT(pp1_29_e42_4_cout)
    );
    E_4_2 E_4_2_pp_29_5(
        .a(A[16] & B[13]),
        .b(A[17] & B[12]),
        .c(A[18] & B[11]),
        .d(A[19] & B[10]),
        .CIN(pp1_28_e42_5_cout),
        .S(pp1_29_e42_5_s),
        .C(pp1_29_e42_5_c),
        .COUT(pp1_29_e42_5_cout)
    );
    E_4_2 E_4_2_pp_29_6(
        .a(A[20] & B[9]),
        .b(A[21] & B[8]),
        .c(A[22] & B[7]),
        .d(A[23] & B[6]),
        .CIN(pp1_28_e42_6_cout),
        .S(pp1_29_e42_6_s),
        .C(pp1_29_e42_6_c),
        .COUT(pp1_29_e42_6_cout)
    );

    E_4_2 E_4_2_pp_29_7(
        .a(A[24] & B[5]),
        .b(A[25] & B[4]),
        .c(A[26] & B[3]),
        .d(A[27] & B[2]),
        .CIN(cin_net),
        .S(pp1_29_e42_7_s),
        .C(pp1_29_e42_7_c),
        .COUT(pp1_29_e42_7_cout)
    );
    assign pp1_29 = {A[28] & B[1], A[29] & B[0], pp1_28_e42_1_c, pp1_28_e42_2_c, pp1_28_e42_3_c, pp1_28_e42_4_c, pp1_28_e42_5_c, pp1_28_e42_6_c, pp1_28_ha_1_c, pp1_29_e42_1_s, pp1_29_e42_2_s, pp1_29_e42_3_s, pp1_29_e42_4_s, pp1_29_e42_5_s, pp1_29_e42_6_s, pp1_29_e42_7_s};
    E_4_2 E_4_2_pp_30_1(
        .a(A[0] & B[30]),
        .b(A[1] & B[29]),
        .c(A[2] & B[28]),
        .d(A[3] & B[27]),
        .CIN(pp1_29_e42_1_cout),
        .S(pp1_30_e42_1_s),
        .C(pp1_30_e42_1_c),
        .COUT(pp1_30_e42_1_cout)
    );
    E_4_2 E_4_2_pp_30_2(
        .a(A[4] & B[26]),
        .b(A[5] & B[25]),
        .c(A[6] & B[24]),
        .d(A[7] & B[23]),
        .CIN(pp1_29_e42_2_cout),
        .S(pp1_30_e42_2_s),
        .C(pp1_30_e42_2_c),
        .COUT(pp1_30_e42_2_cout)
    );
    E_4_2 E_4_2_pp_30_3(
        .a(A[8] & B[22]),
        .b(A[9] & B[21]),
        .c(A[10] & B[20]),
        .d(A[11] & B[19]),
        .CIN(pp1_29_e42_3_cout),
        .S(pp1_30_e42_3_s),
        .C(pp1_30_e42_3_c),
        .COUT(pp1_30_e42_3_cout)
    );
    E_4_2 E_4_2_pp_30_4(
        .a(A[12] & B[18]),
        .b(A[13] & B[17]),
        .c(A[14] & B[16]),
        .d(A[15] & B[15]),
        .CIN(pp1_29_e42_4_cout),
        .S(pp1_30_e42_4_s),
        .C(pp1_30_e42_4_c),
        .COUT(pp1_30_e42_4_cout)
    );
    E_4_2 E_4_2_pp_30_5(
        .a(A[16] & B[14]),
        .b(A[17] & B[13]),
        .c(A[18] & B[12]),
        .d(A[19] & B[11]),
        .CIN(pp1_29_e42_5_cout),
        .S(pp1_30_e42_5_s),
        .C(pp1_30_e42_5_c),
        .COUT(pp1_30_e42_5_cout)
    );
    E_4_2 E_4_2_pp_30_6(
        .a(A[20] & B[10]),
        .b(A[21] & B[9]),
        .c(A[22] & B[8]),
        .d(A[23] & B[7]),
        .CIN(pp1_29_e42_6_cout),
        .S(pp1_30_e42_6_s),
        .C(pp1_30_e42_6_c),
        .COUT(pp1_30_e42_6_cout)
    );
    E_4_2 E_4_2_pp_30_7(
        .a(A[24] & B[6]),
        .b(A[25] & B[5]),
        .c(A[26] & B[4]),
        .d(A[27] & B[3]),
        .CIN(pp1_29_e42_7_cout),
        .S(pp1_30_e42_7_s),
        .C(pp1_30_e42_7_c),
        .COUT(pp1_30_e42_7_cout)
    );
    Half_adder Half_adder_pp_30_1(
        .a(A[28] & B[2]),
        .b(A[29] & B[1]),
        .S(pp1_30_ha_1_s),
        .C(pp1_30_ha_1_c)
    );
    assign pp1_30 = {A[30] & B[0], pp1_29_e42_1_c, pp1_29_e42_2_c, pp1_29_e42_3_c, pp1_29_e42_4_c, pp1_29_e42_5_c, pp1_29_e42_6_c, pp1_29_e42_7_c, pp1_30_e42_1_s, pp1_30_e42_2_s, pp1_30_e42_3_s, pp1_30_e42_4_s, pp1_30_e42_5_s, pp1_30_e42_6_s, pp1_30_e42_7_s, pp1_30_ha_1_s};
    E_4_2 E_4_2_pp_31_1(
        .a(A[0] & B[31]),
        .b(A[1] & B[30]),
        .c(A[2] & B[29]),
        .d(A[3] & B[28]),
        .CIN(pp1_30_e42_1_cout),
        .S(pp1_31_e42_1_s),
        .C(pp1_31_e42_1_c),
        .COUT(pp1_31_e42_1_cout)
    );
    E_4_2 E_4_2_pp_31_2(
        .a(A[4] & B[27]),
        .b(A[5] & B[26]),
        .c(A[6] & B[25]),
        .d(A[7] & B[24]),
        .CIN(pp1_30_e42_2_cout),
        .S(pp1_31_e42_2_s),
        .C(pp1_31_e42_2_c),
        .COUT(pp1_31_e42_2_cout)
    );
    E_4_2 E_4_2_pp_31_3(
        .a(A[8] & B[23]),
        .b(A[9] & B[22]),
        .c(A[10] & B[21]),
        .d(A[11] & B[20]),
        .CIN(pp1_30_e42_3_cout),
        .S(pp1_31_e42_3_s),
        .C(pp1_31_e42_3_c),
        .COUT(pp1_31_e42_3_cout)
    );
    E_4_2 E_4_2_pp_31_4(
        .a(A[12] & B[19]),
        .b(A[13] & B[18]),
        .c(A[14] & B[17]),
        .d(A[15] & B[16]),
        .CIN(pp1_30_e42_4_cout),
        .S(pp1_31_e42_4_s),
        .C(pp1_31_e42_4_c),
        .COUT(pp1_31_e42_4_cout)
    );
    E_4_2 E_4_2_pp_31_5(
        .a(A[16] & B[15]),
        .b(A[17] & B[14]),
        .c(A[18] & B[13]),
        .d(A[19] & B[12]),
        .CIN(pp1_30_e42_5_cout),
        .S(pp1_31_e42_5_s),
        .C(pp1_31_e42_5_c),
        .COUT(pp1_31_e42_5_cout)
    );
    E_4_2 E_4_2_pp_31_6(
        .a(A[20] & B[11]),
        .b(A[21] & B[10]),
        .c(A[22] & B[9]),
        .d(A[23] & B[8]),
        .CIN(pp1_30_e42_6_cout),
        .S(pp1_31_e42_6_s),
        .C(pp1_31_e42_6_c),
        .COUT(pp1_31_e42_6_cout)
    );
    E_4_2 E_4_2_pp_31_7(
        .a(A[24] & B[7]),
        .b(A[25] & B[6]),
        .c(A[26] & B[5]),
        .d(A[27] & B[4]),
        .CIN(pp1_30_e42_7_cout),
        .S(pp1_31_e42_7_s),
        .C(pp1_31_e42_7_c),
        .COUT(pp1_31_e42_7_cout)
    );

    E_4_2 E_4_2_pp_31_8(
        .a(A[28] & B[3]),
        .b(A[29] & B[2]),
        .c(A[30] & B[1]),
        .d(A[31] & B[0]),
        .CIN(cin_net),
        .S(pp1_31_e42_8_s),
        .C(pp1_31_e42_8_c),
        .COUT(pp1_31_e42_8_cout)
    );
    assign pp1_31 = {pp1_30_e42_1_c, pp1_30_e42_2_c, pp1_30_e42_3_c, pp1_30_e42_4_c, pp1_30_e42_5_c, pp1_30_e42_6_c, pp1_30_e42_7_c, pp1_30_ha_1_c, pp1_31_e42_1_s, pp1_31_e42_2_s, pp1_31_e42_3_s, pp1_31_e42_4_s, pp1_31_e42_5_s, pp1_31_e42_6_s, pp1_31_e42_7_s, pp1_31_e42_8_s};
    E_4_2 E_4_2_pp_32_1(
        .a(A[1] & B[31]),
        .b(A[2] & B[30]),
        .c(A[3] & B[29]),
        .d(A[4] & B[28]),
        .CIN(pp1_31_e42_1_cout),
        .S(pp1_32_e42_1_s),
        .C(pp1_32_e42_1_c),
        .COUT(pp1_32_e42_1_cout)
    );
    E_4_2 E_4_2_pp_32_2(
        .a(A[5] & B[27]),
        .b(A[6] & B[26]),
        .c(A[7] & B[25]),
        .d(A[8] & B[24]),
        .CIN(pp1_31_e42_2_cout),
        .S(pp1_32_e42_2_s),
        .C(pp1_32_e42_2_c),
        .COUT(pp1_32_e42_2_cout)
    );
    E_4_2 E_4_2_pp_32_3(
        .a(A[9] & B[23]),
        .b(A[10] & B[22]),
        .c(A[11] & B[21]),
        .d(A[12] & B[20]),
        .CIN(pp1_31_e42_3_cout),
        .S(pp1_32_e42_3_s),
        .C(pp1_32_e42_3_c),
        .COUT(pp1_32_e42_3_cout)
    );
    E_4_2 E_4_2_pp_32_4(
        .a(A[13] & B[19]),
        .b(A[14] & B[18]),
        .c(A[15] & B[17]),
        .d(A[16] & B[16]),
        .CIN(pp1_31_e42_4_cout),
        .S(pp1_32_e42_4_s),
        .C(pp1_32_e42_4_c),
        .COUT(pp1_32_e42_4_cout)
    );
    E_4_2 E_4_2_pp_32_5(
        .a(A[17] & B[15]),
        .b(A[18] & B[14]),
        .c(A[19] & B[13]),
        .d(A[20] & B[12]),
        .CIN(pp1_31_e42_5_cout),
        .S(pp1_32_e42_5_s),
        .C(pp1_32_e42_5_c),
        .COUT(pp1_32_e42_5_cout)
    );
    E_4_2 E_4_2_pp_32_6(
        .a(A[21] & B[11]),
        .b(A[22] & B[10]),
        .c(A[23] & B[9]),
        .d(A[24] & B[8]),
        .CIN(pp1_31_e42_6_cout),
        .S(pp1_32_e42_6_s),
        .C(pp1_32_e42_6_c),
        .COUT(pp1_32_e42_6_cout)
    );
    E_4_2 E_4_2_pp_32_7(
        .a(A[25] & B[7]),
        .b(A[26] & B[6]),
        .c(A[27] & B[5]),
        .d(A[28] & B[4]),
        .CIN(pp1_31_e42_7_cout),
        .S(pp1_32_e42_7_s),
        .C(pp1_32_e42_7_c),
        .COUT(pp1_32_e42_7_cout)
    );

    E_4_2 E_4_2_pp_32_8(
        .a(A[29] & B[3]),
        .b(A[30] & B[2]),
        .c(A[31] & B[1]),
        .d(cin_net),
        .CIN(pp1_31_e42_8_cout),
        .S(pp1_32_e42_8_s),
        .C(pp1_32_e42_8_c),
        .COUT(pp1_32_e42_8_cout)
    );
    assign pp1_32 = {pp1_31_e42_1_c, pp1_31_e42_2_c, pp1_31_e42_3_c, pp1_31_e42_4_c, pp1_31_e42_5_c, pp1_31_e42_6_c, pp1_31_e42_7_c, pp1_31_e42_8_c, pp1_32_e42_1_s, pp1_32_e42_2_s, pp1_32_e42_3_s, pp1_32_e42_4_s, pp1_32_e42_5_s, pp1_32_e42_6_s, pp1_32_e42_7_s, pp1_32_e42_8_s};
    E_4_2 E_4_2_pp_33_1(
        .a(A[2] & B[31]),
        .b(A[3] & B[30]),
        .c(A[4] & B[29]),
        .d(A[5] & B[28]),
        .CIN(pp1_32_e42_1_cout),
        .S(pp1_33_e42_1_s),
        .C(pp1_33_e42_1_c),
        .COUT(pp1_33_e42_1_cout)
    );
    E_4_2 E_4_2_pp_33_2(
        .a(A[6] & B[27]),
        .b(A[7] & B[26]),
        .c(A[8] & B[25]),
        .d(A[9] & B[24]),
        .CIN(pp1_32_e42_2_cout),
        .S(pp1_33_e42_2_s),
        .C(pp1_33_e42_2_c),
        .COUT(pp1_33_e42_2_cout)
    );
    E_4_2 E_4_2_pp_33_3(
        .a(A[10] & B[23]),
        .b(A[11] & B[22]),
        .c(A[12] & B[21]),
        .d(A[13] & B[20]),
        .CIN(pp1_32_e42_3_cout),
        .S(pp1_33_e42_3_s),
        .C(pp1_33_e42_3_c),
        .COUT(pp1_33_e42_3_cout)
    );
    E_4_2 E_4_2_pp_33_4(
        .a(A[14] & B[19]),
        .b(A[15] & B[18]),
        .c(A[16] & B[17]),
        .d(A[17] & B[16]),
        .CIN(pp1_32_e42_4_cout),
        .S(pp1_33_e42_4_s),
        .C(pp1_33_e42_4_c),
        .COUT(pp1_33_e42_4_cout)
    );
    E_4_2 E_4_2_pp_33_5(
        .a(A[18] & B[15]),
        .b(A[19] & B[14]),
        .c(A[20] & B[13]),
        .d(A[21] & B[12]),
        .CIN(pp1_32_e42_5_cout),
        .S(pp1_33_e42_5_s),
        .C(pp1_33_e42_5_c),
        .COUT(pp1_33_e42_5_cout)
    );
    E_4_2 E_4_2_pp_33_6(
        .a(A[22] & B[11]),
        .b(A[23] & B[10]),
        .c(A[24] & B[9]),
        .d(A[25] & B[8]),
        .CIN(pp1_32_e42_6_cout),
        .S(pp1_33_e42_6_s),
        .C(pp1_33_e42_6_c),
        .COUT(pp1_33_e42_6_cout)
    );
    E_4_2 E_4_2_pp_33_7(
        .a(A[26] & B[7]),
        .b(A[27] & B[6]),
        .c(A[28] & B[5]),
        .d(A[29] & B[4]),
        .CIN(pp1_32_e42_7_cout),
        .S(pp1_33_e42_7_s),
        .C(pp1_33_e42_7_c),
        .COUT(pp1_33_e42_7_cout)
    );
    Full_adder Full_adder_pp_33_1(
        .a(A[30] & B[3]),
        .b(A[31] & B[2]),
        .CIN(pp1_32_e42_8_cout),
        .S(pp1_33_fa_1_s),
        .C(pp1_33_fa_1_c)
    );
    assign pp1_33 = {pp1_32_e42_1_c, pp1_32_e42_2_c, pp1_32_e42_3_c, pp1_32_e42_4_c, pp1_32_e42_5_c, pp1_32_e42_6_c, pp1_32_e42_7_c, pp1_32_e42_8_c, pp1_33_e42_1_s, pp1_33_e42_2_s, pp1_33_e42_3_s, pp1_33_e42_4_s, pp1_33_e42_5_s, pp1_33_e42_6_s, pp1_33_e42_7_s, pp1_33_fa_1_s};
    E_4_2 E_4_2_pp_34_1(
        .a(A[3] & B[31]),
        .b(A[4] & B[30]),
        .c(A[5] & B[29]),
        .d(A[6] & B[28]),
        .CIN(pp1_33_e42_1_cout),
        .S(pp1_34_e42_1_s),
        .C(pp1_34_e42_1_c),
        .COUT(pp1_34_e42_1_cout)
    );
    E_4_2 E_4_2_pp_34_2(
        .a(A[7] & B[27]),
        .b(A[8] & B[26]),
        .c(A[9] & B[25]),
        .d(A[10] & B[24]),
        .CIN(pp1_33_e42_2_cout),
        .S(pp1_34_e42_2_s),
        .C(pp1_34_e42_2_c),
        .COUT(pp1_34_e42_2_cout)
    );
    E_4_2 E_4_2_pp_34_3(
        .a(A[11] & B[23]),
        .b(A[12] & B[22]),
        .c(A[13] & B[21]),
        .d(A[14] & B[20]),
        .CIN(pp1_33_e42_3_cout),
        .S(pp1_34_e42_3_s),
        .C(pp1_34_e42_3_c),
        .COUT(pp1_34_e42_3_cout)
    );
    E_4_2 E_4_2_pp_34_4(
        .a(A[15] & B[19]),
        .b(A[16] & B[18]),
        .c(A[17] & B[17]),
        .d(A[18] & B[16]),
        .CIN(pp1_33_e42_4_cout),
        .S(pp1_34_e42_4_s),
        .C(pp1_34_e42_4_c),
        .COUT(pp1_34_e42_4_cout)
    );
    E_4_2 E_4_2_pp_34_5(
        .a(A[19] & B[15]),
        .b(A[20] & B[14]),
        .c(A[21] & B[13]),
        .d(A[22] & B[12]),
        .CIN(pp1_33_e42_5_cout),
        .S(pp1_34_e42_5_s),
        .C(pp1_34_e42_5_c),
        .COUT(pp1_34_e42_5_cout)
    );
    E_4_2 E_4_2_pp_34_6(
        .a(A[23] & B[11]),
        .b(A[24] & B[10]),
        .c(A[25] & B[9]),
        .d(A[26] & B[8]),
        .CIN(pp1_33_e42_6_cout),
        .S(pp1_34_e42_6_s),
        .C(pp1_34_e42_6_c),
        .COUT(pp1_34_e42_6_cout)
    );
    E_4_2 E_4_2_pp_34_7(
        .a(A[27] & B[7]),
        .b(A[28] & B[6]),
        .c(A[29] & B[5]),
        .d(A[30] & B[4]),
        .CIN(pp1_33_e42_7_cout),
        .S(pp1_34_e42_7_s),
        .C(pp1_34_e42_7_c),
        .COUT(pp1_34_e42_7_cout)
    );
    assign pp1_34 = {A[31] & B[3], pp1_33_e42_1_c, pp1_33_e42_2_c, pp1_33_e42_3_c, pp1_33_e42_4_c, pp1_33_e42_5_c, pp1_33_e42_6_c, pp1_33_e42_7_c, pp1_33_fa_1_c, pp1_34_e42_1_s, pp1_34_e42_2_s, pp1_34_e42_3_s, pp1_34_e42_4_s, pp1_34_e42_5_s, pp1_34_e42_6_s, pp1_34_e42_7_s};
    E_4_2 E_4_2_pp_35_1(
        .a(A[4] & B[31]),
        .b(A[5] & B[30]),
        .c(A[6] & B[29]),
        .d(A[7] & B[28]),
        .CIN(pp1_34_e42_1_cout),
        .S(pp1_35_e42_1_s),
        .C(pp1_35_e42_1_c),
        .COUT(pp1_35_e42_1_cout)
    );
    E_4_2 E_4_2_pp_35_2(
        .a(A[8] & B[27]),
        .b(A[9] & B[26]),
        .c(A[10] & B[25]),
        .d(A[11] & B[24]),
        .CIN(pp1_34_e42_2_cout),
        .S(pp1_35_e42_2_s),
        .C(pp1_35_e42_2_c),
        .COUT(pp1_35_e42_2_cout)
    );
    E_4_2 E_4_2_pp_35_3(
        .a(A[12] & B[23]),
        .b(A[13] & B[22]),
        .c(A[14] & B[21]),
        .d(A[15] & B[20]),
        .CIN(pp1_34_e42_3_cout),
        .S(pp1_35_e42_3_s),
        .C(pp1_35_e42_3_c),
        .COUT(pp1_35_e42_3_cout)
    );
    E_4_2 E_4_2_pp_35_4(
        .a(A[16] & B[19]),
        .b(A[17] & B[18]),
        .c(A[18] & B[17]),
        .d(A[19] & B[16]),
        .CIN(pp1_34_e42_4_cout),
        .S(pp1_35_e42_4_s),
        .C(pp1_35_e42_4_c),
        .COUT(pp1_35_e42_4_cout)
    );
    E_4_2 E_4_2_pp_35_5(
        .a(A[20] & B[15]),
        .b(A[21] & B[14]),
        .c(A[22] & B[13]),
        .d(A[23] & B[12]),
        .CIN(pp1_34_e42_5_cout),
        .S(pp1_35_e42_5_s),
        .C(pp1_35_e42_5_c),
        .COUT(pp1_35_e42_5_cout)
    );
    E_4_2 E_4_2_pp_35_6(
        .a(A[24] & B[11]),
        .b(A[25] & B[10]),
        .c(A[26] & B[9]),
        .d(A[27] & B[8]),
        .CIN(pp1_34_e42_6_cout),
        .S(pp1_35_e42_6_s),
        .C(pp1_35_e42_6_c),
        .COUT(pp1_35_e42_6_cout)
    );
    Full_adder Full_adder_pp_35_1(
        .a(A[28] & B[7]),
        .b(A[29] & B[6]),
        .CIN(pp1_34_e42_7_cout),
        .S(pp1_35_fa_1_s),
        .C(pp1_35_fa_1_c)
    );
    assign pp1_35 = {A[30] & B[5], A[31] & B[4], pp1_34_e42_1_c, pp1_34_e42_2_c, pp1_34_e42_3_c, pp1_34_e42_4_c, pp1_34_e42_5_c, pp1_34_e42_6_c, pp1_34_e42_7_c, pp1_35_e42_1_s, pp1_35_e42_2_s, pp1_35_e42_3_s, pp1_35_e42_4_s, pp1_35_e42_5_s, pp1_35_e42_6_s, pp1_35_fa_1_s};
    E_4_2 E_4_2_pp_36_1(
        .a(A[5] & B[31]),
        .b(A[6] & B[30]),
        .c(A[7] & B[29]),
        .d(A[8] & B[28]),
        .CIN(pp1_35_e42_1_cout),
        .S(pp1_36_e42_1_s),
        .C(pp1_36_e42_1_c),
        .COUT(pp1_36_e42_1_cout)
    );
    E_4_2 E_4_2_pp_36_2(
        .a(A[9] & B[27]),
        .b(A[10] & B[26]),
        .c(A[11] & B[25]),
        .d(A[12] & B[24]),
        .CIN(pp1_35_e42_2_cout),
        .S(pp1_36_e42_2_s),
        .C(pp1_36_e42_2_c),
        .COUT(pp1_36_e42_2_cout)
    );
    E_4_2 E_4_2_pp_36_3(
        .a(A[13] & B[23]),
        .b(A[14] & B[22]),
        .c(A[15] & B[21]),
        .d(A[16] & B[20]),
        .CIN(pp1_35_e42_3_cout),
        .S(pp1_36_e42_3_s),
        .C(pp1_36_e42_3_c),
        .COUT(pp1_36_e42_3_cout)
    );
    E_4_2 E_4_2_pp_36_4(
        .a(A[17] & B[19]),
        .b(A[18] & B[18]),
        .c(A[19] & B[17]),
        .d(A[20] & B[16]),
        .CIN(pp1_35_e42_4_cout),
        .S(pp1_36_e42_4_s),
        .C(pp1_36_e42_4_c),
        .COUT(pp1_36_e42_4_cout)
    );
    E_4_2 E_4_2_pp_36_5(
        .a(A[21] & B[15]),
        .b(A[22] & B[14]),
        .c(A[23] & B[13]),
        .d(A[24] & B[12]),
        .CIN(pp1_35_e42_5_cout),
        .S(pp1_36_e42_5_s),
        .C(pp1_36_e42_5_c),
        .COUT(pp1_36_e42_5_cout)
    );
    E_4_2 E_4_2_pp_36_6(
        .a(A[25] & B[11]),
        .b(A[26] & B[10]),
        .c(A[27] & B[9]),
        .d(A[28] & B[8]),
        .CIN(pp1_35_e42_6_cout),
        .S(pp1_36_e42_6_s),
        .C(pp1_36_e42_6_c),
        .COUT(pp1_36_e42_6_cout)
    );
    assign pp1_36 = {A[29] & B[7], A[30] & B[6], A[31] & B[5], pp1_35_e42_1_c, pp1_35_e42_2_c, pp1_35_e42_3_c, pp1_35_e42_4_c, pp1_35_e42_5_c, pp1_35_e42_6_c, pp1_35_fa_1_c, pp1_36_e42_1_s, pp1_36_e42_2_s, pp1_36_e42_3_s, pp1_36_e42_4_s, pp1_36_e42_5_s, pp1_36_e42_6_s};
    E_4_2 E_4_2_pp_37_1(
        .a(A[6] & B[31]),
        .b(A[7] & B[30]),
        .c(A[8] & B[29]),
        .d(A[9] & B[28]),
        .CIN(pp1_36_e42_1_cout),
        .S(pp1_37_e42_1_s),
        .C(pp1_37_e42_1_c),
        .COUT(pp1_37_e42_1_cout)
    );
    E_4_2 E_4_2_pp_37_2(
        .a(A[10] & B[27]),
        .b(A[11] & B[26]),
        .c(A[12] & B[25]),
        .d(A[13] & B[24]),
        .CIN(pp1_36_e42_2_cout),
        .S(pp1_37_e42_2_s),
        .C(pp1_37_e42_2_c),
        .COUT(pp1_37_e42_2_cout)
    );
    E_4_2 E_4_2_pp_37_3(
        .a(A[14] & B[23]),
        .b(A[15] & B[22]),
        .c(A[16] & B[21]),
        .d(A[17] & B[20]),
        .CIN(pp1_36_e42_3_cout),
        .S(pp1_37_e42_3_s),
        .C(pp1_37_e42_3_c),
        .COUT(pp1_37_e42_3_cout)
    );
    E_4_2 E_4_2_pp_37_4(
        .a(A[18] & B[19]),
        .b(A[19] & B[18]),
        .c(A[20] & B[17]),
        .d(A[21] & B[16]),
        .CIN(pp1_36_e42_4_cout),
        .S(pp1_37_e42_4_s),
        .C(pp1_37_e42_4_c),
        .COUT(pp1_37_e42_4_cout)
    );
    E_4_2 E_4_2_pp_37_5(
        .a(A[22] & B[15]),
        .b(A[23] & B[14]),
        .c(A[24] & B[13]),
        .d(A[25] & B[12]),
        .CIN(pp1_36_e42_5_cout),
        .S(pp1_37_e42_5_s),
        .C(pp1_37_e42_5_c),
        .COUT(pp1_37_e42_5_cout)
    );
    Full_adder Full_adder_pp_37_1(
        .a(A[26] & B[11]),
        .b(A[27] & B[10]),
        .CIN(pp1_36_e42_6_cout),
        .S(pp1_37_fa_1_s),
        .C(pp1_37_fa_1_c)
    );
    assign pp1_37 = {A[28] & B[9], A[29] & B[8], A[30] & B[7], A[31] & B[6], pp1_36_e42_1_c, pp1_36_e42_2_c, pp1_36_e42_3_c, pp1_36_e42_4_c, pp1_36_e42_5_c, pp1_36_e42_6_c, pp1_37_e42_1_s, pp1_37_e42_2_s, pp1_37_e42_3_s, pp1_37_e42_4_s, pp1_37_e42_5_s, pp1_37_fa_1_s};
    E_4_2 E_4_2_pp_38_1(
        .a(A[7] & B[31]),
        .b(A[8] & B[30]),
        .c(A[9] & B[29]),
        .d(A[10] & B[28]),
        .CIN(pp1_37_e42_1_cout),
        .S(pp1_38_e42_1_s),
        .C(pp1_38_e42_1_c),
        .COUT(pp1_38_e42_1_cout)
    );
    E_4_2 E_4_2_pp_38_2(
        .a(A[11] & B[27]),
        .b(A[12] & B[26]),
        .c(A[13] & B[25]),
        .d(A[14] & B[24]),
        .CIN(pp1_37_e42_2_cout),
        .S(pp1_38_e42_2_s),
        .C(pp1_38_e42_2_c),
        .COUT(pp1_38_e42_2_cout)
    );
    E_4_2 E_4_2_pp_38_3(
        .a(A[15] & B[23]),
        .b(A[16] & B[22]),
        .c(A[17] & B[21]),
        .d(A[18] & B[20]),
        .CIN(pp1_37_e42_3_cout),
        .S(pp1_38_e42_3_s),
        .C(pp1_38_e42_3_c),
        .COUT(pp1_38_e42_3_cout)
    );
    E_4_2 E_4_2_pp_38_4(
        .a(A[19] & B[19]),
        .b(A[20] & B[18]),
        .c(A[21] & B[17]),
        .d(A[22] & B[16]),
        .CIN(pp1_37_e42_4_cout),
        .S(pp1_38_e42_4_s),
        .C(pp1_38_e42_4_c),
        .COUT(pp1_38_e42_4_cout)
    );
    E_4_2 E_4_2_pp_38_5(
        .a(A[23] & B[15]),
        .b(A[24] & B[14]),
        .c(A[25] & B[13]),
        .d(A[26] & B[12]),
        .CIN(pp1_37_e42_5_cout),
        .S(pp1_38_e42_5_s),
        .C(pp1_38_e42_5_c),
        .COUT(pp1_38_e42_5_cout)
    );
    assign pp1_38 = {A[27] & B[11], A[28] & B[10], A[29] & B[9], A[30] & B[8], A[31] & B[7], pp1_37_e42_1_c, pp1_37_e42_2_c, pp1_37_e42_3_c, pp1_37_e42_4_c, pp1_37_e42_5_c, pp1_37_fa_1_c, pp1_38_e42_1_s, pp1_38_e42_2_s, pp1_38_e42_3_s, pp1_38_e42_4_s, pp1_38_e42_5_s};
    E_4_2 E_4_2_pp_39_1(
        .a(A[8] & B[31]),
        .b(A[9] & B[30]),
        .c(A[10] & B[29]),
        .d(A[11] & B[28]),
        .CIN(pp1_38_e42_1_cout),
        .S(pp1_39_e42_1_s),
        .C(pp1_39_e42_1_c),
        .COUT(pp1_39_e42_1_cout)
    );
    E_4_2 E_4_2_pp_39_2(
        .a(A[12] & B[27]),
        .b(A[13] & B[26]),
        .c(A[14] & B[25]),
        .d(A[15] & B[24]),
        .CIN(pp1_38_e42_2_cout),
        .S(pp1_39_e42_2_s),
        .C(pp1_39_e42_2_c),
        .COUT(pp1_39_e42_2_cout)
    );
    E_4_2 E_4_2_pp_39_3(
        .a(A[16] & B[23]),
        .b(A[17] & B[22]),
        .c(A[18] & B[21]),
        .d(A[19] & B[20]),
        .CIN(pp1_38_e42_3_cout),
        .S(pp1_39_e42_3_s),
        .C(pp1_39_e42_3_c),
        .COUT(pp1_39_e42_3_cout)
    );
    E_4_2 E_4_2_pp_39_4(
        .a(A[20] & B[19]),
        .b(A[21] & B[18]),
        .c(A[22] & B[17]),
        .d(A[23] & B[16]),
        .CIN(pp1_38_e42_4_cout),
        .S(pp1_39_e42_4_s),
        .C(pp1_39_e42_4_c),
        .COUT(pp1_39_e42_4_cout)
    );
    Full_adder Full_adder_pp_39_1(
        .a(A[24] & B[15]),
        .b(A[25] & B[14]),
        .CIN(pp1_38_e42_5_cout),
        .S(pp1_39_fa_1_s),
        .C(pp1_39_fa_1_c)
    );
    assign pp1_39 = {A[26] & B[13], A[27] & B[12], A[28] & B[11], A[29] & B[10], A[30] & B[9], A[31] & B[8], pp1_38_e42_1_c, pp1_38_e42_2_c, pp1_38_e42_3_c, pp1_38_e42_4_c, pp1_38_e42_5_c, pp1_39_e42_1_s, pp1_39_e42_2_s, pp1_39_e42_3_s, pp1_39_e42_4_s, pp1_39_fa_1_s};
    E_4_2 E_4_2_pp_40_1(
        .a(A[9] & B[31]),
        .b(A[10] & B[30]),
        .c(A[11] & B[29]),
        .d(A[12] & B[28]),
        .CIN(pp1_39_e42_1_cout),
        .S(pp1_40_e42_1_s),
        .C(pp1_40_e42_1_c),
        .COUT(pp1_40_e42_1_cout)
    );
    E_4_2 E_4_2_pp_40_2(
        .a(A[13] & B[27]),
        .b(A[14] & B[26]),
        .c(A[15] & B[25]),
        .d(A[16] & B[24]),
        .CIN(pp1_39_e42_2_cout),
        .S(pp1_40_e42_2_s),
        .C(pp1_40_e42_2_c),
        .COUT(pp1_40_e42_2_cout)
    );
    E_4_2 E_4_2_pp_40_3(
        .a(A[17] & B[23]),
        .b(A[18] & B[22]),
        .c(A[19] & B[21]),
        .d(A[20] & B[20]),
        .CIN(pp1_39_e42_3_cout),
        .S(pp1_40_e42_3_s),
        .C(pp1_40_e42_3_c),
        .COUT(pp1_40_e42_3_cout)
    );
    E_4_2 E_4_2_pp_40_4(
        .a(A[21] & B[19]),
        .b(A[22] & B[18]),
        .c(A[23] & B[17]),
        .d(A[24] & B[16]),
        .CIN(pp1_39_e42_4_cout),
        .S(pp1_40_e42_4_s),
        .C(pp1_40_e42_4_c),
        .COUT(pp1_40_e42_4_cout)
    );
    assign pp1_40 = {A[25] & B[15], A[26] & B[14], A[27] & B[13], A[28] & B[12], A[29] & B[11], A[30] & B[10], A[31] & B[9], pp1_39_e42_1_c, pp1_39_e42_2_c, pp1_39_e42_3_c, pp1_39_e42_4_c, pp1_39_fa_1_c, pp1_40_e42_1_s, pp1_40_e42_2_s, pp1_40_e42_3_s, pp1_40_e42_4_s};
    E_4_2 E_4_2_pp_41_1(
        .a(A[10] & B[31]),
        .b(A[11] & B[30]),
        .c(A[12] & B[29]),
        .d(A[13] & B[28]),
        .CIN(pp1_40_e42_1_cout),
        .S(pp1_41_e42_1_s),
        .C(pp1_41_e42_1_c),
        .COUT(pp1_41_e42_1_cout)
    );
    E_4_2 E_4_2_pp_41_2(
        .a(A[14] & B[27]),
        .b(A[15] & B[26]),
        .c(A[16] & B[25]),
        .d(A[17] & B[24]),
        .CIN(pp1_40_e42_2_cout),
        .S(pp1_41_e42_2_s),
        .C(pp1_41_e42_2_c),
        .COUT(pp1_41_e42_2_cout)
    );
    E_4_2 E_4_2_pp_41_3(
        .a(A[18] & B[23]),
        .b(A[19] & B[22]),
        .c(A[20] & B[21]),
        .d(A[21] & B[20]),
        .CIN(pp1_40_e42_3_cout),
        .S(pp1_41_e42_3_s),
        .C(pp1_41_e42_3_c),
        .COUT(pp1_41_e42_3_cout)
    );
    Full_adder Full_adder_pp_41_1(
        .a(A[22] & B[19]),
        .b(A[23] & B[18]),
        .CIN(pp1_40_e42_4_cout),
        .S(pp1_41_fa_1_s),
        .C(pp1_41_fa_1_c)
    );
    assign pp1_41 = {A[24] & B[17], A[25] & B[16], A[26] & B[15], A[27] & B[14], A[28] & B[13], A[29] & B[12], A[30] & B[11], A[31] & B[10], pp1_40_e42_1_c, pp1_40_e42_2_c, pp1_40_e42_3_c, pp1_40_e42_4_c, pp1_41_e42_1_s, pp1_41_e42_2_s, pp1_41_e42_3_s, pp1_41_fa_1_s};
    E_4_2 E_4_2_pp_42_1(
        .a(A[11] & B[31]),
        .b(A[12] & B[30]),
        .c(A[13] & B[29]),
        .d(A[14] & B[28]),
        .CIN(pp1_41_e42_1_cout),
        .S(pp1_42_e42_1_s),
        .C(pp1_42_e42_1_c),
        .COUT(pp1_42_e42_1_cout)
    );
    E_4_2 E_4_2_pp_42_2(
        .a(A[15] & B[27]),
        .b(A[16] & B[26]),
        .c(A[17] & B[25]),
        .d(A[18] & B[24]),
        .CIN(pp1_41_e42_2_cout),
        .S(pp1_42_e42_2_s),
        .C(pp1_42_e42_2_c),
        .COUT(pp1_42_e42_2_cout)
    );
    E_4_2 E_4_2_pp_42_3(
        .a(A[19] & B[23]),
        .b(A[20] & B[22]),
        .c(A[21] & B[21]),
        .d(A[22] & B[20]),
        .CIN(pp1_41_e42_3_cout),
        .S(pp1_42_e42_3_s),
        .C(pp1_42_e42_3_c),
        .COUT(pp1_42_e42_3_cout)
    );
    assign pp1_42 = {A[23] & B[19], A[24] & B[18], A[25] & B[17], A[26] & B[16], A[27] & B[15], A[28] & B[14], A[29] & B[13], A[30] & B[12], A[31] & B[11], pp1_41_e42_1_c, pp1_41_e42_2_c, pp1_41_e42_3_c, pp1_41_fa_1_c, pp1_42_e42_1_s, pp1_42_e42_2_s, pp1_42_e42_3_s};
    E_4_2 E_4_2_pp_43_1(
        .a(A[12] & B[31]),
        .b(A[13] & B[30]),
        .c(A[14] & B[29]),
        .d(A[15] & B[28]),
        .CIN(pp1_42_e42_1_cout),
        .S(pp1_43_e42_1_s),
        .C(pp1_43_e42_1_c),
        .COUT(pp1_43_e42_1_cout)
    );
    E_4_2 E_4_2_pp_43_2(
        .a(A[16] & B[27]),
        .b(A[17] & B[26]),
        .c(A[18] & B[25]),
        .d(A[19] & B[24]),
        .CIN(pp1_42_e42_2_cout),
        .S(pp1_43_e42_2_s),
        .C(pp1_43_e42_2_c),
        .COUT(pp1_43_e42_2_cout)
    );
    Full_adder Full_adder_pp_43_1(
        .a(A[20] & B[23]),
        .b(A[21] & B[22]),
        .CIN(pp1_42_e42_3_cout),
        .S(pp1_43_fa_1_s),
        .C(pp1_43_fa_1_c)
    );
    assign pp1_43 = {A[22] & B[21], A[23] & B[20], A[24] & B[19], A[25] & B[18], A[26] & B[17], A[27] & B[16], A[28] & B[15], A[29] & B[14], A[30] & B[13], A[31] & B[12], pp1_42_e42_1_c, pp1_42_e42_2_c, pp1_42_e42_3_c, pp1_43_e42_1_s, pp1_43_e42_2_s, pp1_43_fa_1_s};
    E_4_2 E_4_2_pp_44_1(
        .a(A[13] & B[31]),
        .b(A[14] & B[30]),
        .c(A[15] & B[29]),
        .d(A[16] & B[28]),
        .CIN(pp1_43_e42_1_cout),
        .S(pp1_44_e42_1_s),
        .C(pp1_44_e42_1_c),
        .COUT(pp1_44_e42_1_cout)
    );
    E_4_2 E_4_2_pp_44_2(
        .a(A[17] & B[27]),
        .b(A[18] & B[26]),
        .c(A[19] & B[25]),
        .d(A[20] & B[24]),
        .CIN(pp1_43_e42_2_cout),
        .S(pp1_44_e42_2_s),
        .C(pp1_44_e42_2_c),
        .COUT(pp1_44_e42_2_cout)
    );
    assign pp1_44 = {A[21] & B[23], A[22] & B[22], A[23] & B[21], A[24] & B[20], A[25] & B[19], A[26] & B[18], A[27] & B[17], A[28] & B[16], A[29] & B[15], A[30] & B[14], A[31] & B[13], pp1_43_e42_1_c, pp1_43_e42_2_c, pp1_43_fa_1_c, pp1_44_e42_1_s, pp1_44_e42_2_s};
    E_4_2 E_4_2_pp_45_1(
        .a(A[14] & B[31]),
        .b(A[15] & B[30]),
        .c(A[16] & B[29]),
        .d(A[17] & B[28]),
        .CIN(pp1_44_e42_1_cout),
        .S(pp1_45_e42_1_s),
        .C(pp1_45_e42_1_c),
        .COUT(pp1_45_e42_1_cout)
    );
    Full_adder Full_adder_pp_45_1(
        .a(A[18] & B[27]),
        .b(A[19] & B[26]),
        .CIN(pp1_44_e42_2_cout),
        .S(pp1_45_fa_1_s),
        .C(pp1_45_fa_1_c)
    );
    assign pp1_45 = {A[20] & B[25], A[21] & B[24], A[22] & B[23], A[23] & B[22], A[24] & B[21], A[25] & B[20], A[26] & B[19], A[27] & B[18], A[28] & B[17], A[29] & B[16], A[30] & B[15], A[31] & B[14], pp1_44_e42_1_c, pp1_44_e42_2_c, pp1_45_e42_1_s, pp1_45_fa_1_s};
    E_4_2 E_4_2_pp_46_1(
        .a(A[15] & B[31]),
        .b(A[16] & B[30]),
        .c(A[17] & B[29]),
        .d(A[18] & B[28]),
        .CIN(pp1_45_e42_1_cout),
        .S(pp1_46_e42_1_s),
        .C(pp1_46_e42_1_c),
        .COUT(pp1_46_e42_1_cout)
    );
    assign pp1_46 = {A[19] & B[27], A[20] & B[26], A[21] & B[25], A[22] & B[24], A[23] & B[23], A[24] & B[22], A[25] & B[21], A[26] & B[20], A[27] & B[19], A[28] & B[18], A[29] & B[17], A[30] & B[16], A[31] & B[15], pp1_45_e42_1_c, pp1_45_fa_1_c, pp1_46_e42_1_s};
    Full_adder Full_adder_pp_47_1(
        .a(A[16] & B[31]),
        .b(A[17] & B[30]),
        .CIN(pp1_46_e42_1_cout),
        .S(pp1_47_fa_1_s),
        .C(pp1_47_fa_1_c)
    );
    assign pp1_47 = {A[18] & B[29], A[19] & B[28], A[20] & B[27], A[21] & B[26], A[22] & B[25], A[23] & B[24], A[24] & B[23], A[25] & B[22], A[26] & B[21], A[27] & B[20], A[28] & B[19], A[29] & B[18], A[30] & B[17], A[31] & B[16], pp1_46_e42_1_c, pp1_47_fa_1_s};
    assign pp1_48 = {A[17] & B[31], A[18] & B[30], A[19] & B[29], A[20] & B[28], A[21] & B[27], A[22] & B[26], A[23] & B[25], A[24] & B[24], A[25] & B[23], A[26] & B[22], A[27] & B[21], A[28] & B[20], A[29] & B[19], A[30] & B[18], A[31] & B[17], pp1_47_fa_1_c};
    assign pp1_49 = {A[18] & B[31], A[19] & B[30], A[20] & B[29], A[21] & B[28], A[22] & B[27], A[23] & B[26], A[24] & B[25], A[25] & B[24], A[26] & B[23], A[27] & B[22], A[28] & B[21], A[29] & B[20], A[30] & B[19], A[31] & B[18]};
    assign pp1_50 = {A[19] & B[31], A[20] & B[30], A[21] & B[29], A[22] & B[28], A[23] & B[27], A[24] & B[26], A[25] & B[25], A[26] & B[24], A[27] & B[23], A[28] & B[22], A[29] & B[21], A[30] & B[20], A[31] & B[19]};
    assign pp1_51 = {A[20] & B[31], A[21] & B[30], A[22] & B[29], A[23] & B[28], A[24] & B[27], A[25] & B[26], A[26] & B[25], A[27] & B[24], A[28] & B[23], A[29] & B[22], A[30] & B[21], A[31] & B[20]};
    assign pp1_52 = {A[21] & B[31], A[22] & B[30], A[23] & B[29], A[24] & B[28], A[25] & B[27], A[26] & B[26], A[27] & B[25], A[28] & B[24], A[29] & B[23], A[30] & B[22], A[31] & B[21]};
    assign pp1_53 = {A[22] & B[31], A[23] & B[30], A[24] & B[29], A[25] & B[28], A[26] & B[27], A[27] & B[26], A[28] & B[25], A[29] & B[24], A[30] & B[23], A[31] & B[22]};
    assign pp1_54 = {A[23] & B[31], A[24] & B[30], A[25] & B[29], A[26] & B[28], A[27] & B[27], A[28] & B[26], A[29] & B[25], A[30] & B[24], A[31] & B[23]};
    assign pp1_55 = {A[24] & B[31], A[25] & B[30], A[26] & B[29], A[27] & B[28], A[28] & B[27], A[29] & B[26], A[30] & B[25], A[31] & B[24]};
    assign pp1_56 = {A[25] & B[31], A[26] & B[30], A[27] & B[29], A[28] & B[28], A[29] & B[27], A[30] & B[26], A[31] & B[25]};
    assign pp1_57 = {A[26] & B[31], A[27] & B[30], A[28] & B[29], A[29] & B[28], A[30] & B[27], A[31] & B[26]};
    assign pp1_58 = {A[27] & B[31], A[28] & B[30], A[29] & B[29], A[30] & B[28], A[31] & B[27]};
    assign pp1_59 = {A[28] & B[31], A[29] & B[30], A[30] & B[29], A[31] & B[28]};
    assign pp1_60 = {A[29] & B[31], A[30] & B[30], A[31] & B[29]};
    assign pp1_61 = {A[30] & B[31], A[31] & B[30]};
    assign pp1_62 = A[31] & B[31];
    //assign pp1_63 = cin_net;
    LOGIC0_X1  u_gnd2 (
    .Z(pp1_63)
);
endmodule



module STAGE2_32(
    input pp1_0,
    input [1:0] pp1_1,
    input [2:0] pp1_2,
    input [3:0] pp1_3,
    input [4:0] pp1_4,
    input [5:0] pp1_5,
    input [6:0] pp1_6,
    input [7:0] pp1_7,
    input [8:0] pp1_8,
    input [9:0] pp1_9,
    input [10:0] pp1_10,
    input [11:0] pp1_11,
    input [12:0] pp1_12,
    input [13:0] pp1_13,
    input [14:0] pp1_14,
    input [15:0] pp1_15,
    input [15:0] pp1_16,
    input [15:0] pp1_17,
    input [15:0] pp1_18,
    input [15:0] pp1_19,
    input [15:0] pp1_20,
    input [15:0] pp1_21,
    input [15:0] pp1_22,
    input [15:0] pp1_23,
    input [15:0] pp1_24,
    input [15:0] pp1_25,
    input [15:0] pp1_26,
    input [15:0] pp1_27,
    input [15:0] pp1_28,
    input [15:0] pp1_29,
    input [15:0] pp1_30,
    input [15:0] pp1_31,
    input [15:0] pp1_32,
    input [15:0] pp1_33,
    input [15:0] pp1_34,
    input [15:0] pp1_35,
    input [15:0] pp1_36,
    input [15:0] pp1_37,
    input [15:0] pp1_38,
    input [15:0] pp1_39,
    input [15:0] pp1_40,
    input [15:0] pp1_41,
    input [15:0] pp1_42,
    input [15:0] pp1_43,
    input [15:0] pp1_44,
    input [15:0] pp1_45,
    input [15:0] pp1_46,
    input [15:0] pp1_47,
    input [15:0] pp1_48,
    input [13:0] pp1_49,
    input [12:0] pp1_50,
    input [11:0] pp1_51,
    input [10:0] pp1_52,
    input [9:0] pp1_53,
    input [8:0] pp1_54,
    input [7:0] pp1_55,
    input [6:0] pp1_56,
    input [5:0] pp1_57,
    input [4:0] pp1_58,
    input [3:0] pp1_59,
    input [2:0] pp1_60,
    input [1:0] pp1_61,
    input pp1_62,
    input pp1_63,
    output pp2_0,
    output [1:0] pp2_1,
    output [2:0] pp2_2,
    output [3:0] pp2_3,
    output [4:0] pp2_4,
    output [5:0] pp2_5,
    output [6:0] pp2_6,
    output [7:0] pp2_7,
    output [7:0] pp2_8,
    output [7:0] pp2_9,
    output [7:0] pp2_10,
    output [7:0] pp2_11,
    output [7:0] pp2_12,
    output [7:0] pp2_13,
    output [7:0] pp2_14,
    output [7:0] pp2_15,
    output [7:0] pp2_16,
    output [7:0] pp2_17,
    output [7:0] pp2_18,
    output [7:0] pp2_19,
    output [7:0] pp2_20,
    output [7:0] pp2_21,
    output [7:0] pp2_22,
    output [7:0] pp2_23,
    output [7:0] pp2_24,
    output [7:0] pp2_25,
    output [7:0] pp2_26,
    output [7:0] pp2_27,
    output [7:0] pp2_28,
    output [7:0] pp2_29,
    output [7:0] pp2_30,
    output [7:0] pp2_31,
    output [7:0] pp2_32,
    output [7:0] pp2_33,
    output [7:0] pp2_34,
    output [7:0] pp2_35,
    output [7:0] pp2_36,
    output [7:0] pp2_37,
    output [7:0] pp2_38,
    output [7:0] pp2_39,
    output [7:0] pp2_40,
    output [7:0] pp2_41,
    output [7:0] pp2_42,
    output [7:0] pp2_43,
    output [7:0] pp2_44,
    output [7:0] pp2_45,
    output [7:0] pp2_46,
    output [7:0] pp2_47,
    output [7:0] pp2_48,
    output [7:0] pp2_49,
    output [7:0] pp2_50,
    output [7:0] pp2_51,
    output [7:0] pp2_52,
    output [7:0] pp2_53,
    output [7:0] pp2_54,
    output [7:0] pp2_55,
    output [7:0] pp2_56,
    output [5:0] pp2_57,
    output [4:0] pp2_58,
    output [3:0] pp2_59,
    output [2:0] pp2_60,
    output [1:0] pp2_61,
    output pp2_62,
    output pp2_63
);
    wire cin_net;
LOGIC0_X1 u_gnd (.Z(cin_net));
    wire pp2_9_e42_1_s;
    wire pp2_9_e42_1_c;
    wire pp2_9_e42_1_cout;
    wire pp2_10_e42_1_s;
    wire pp2_10_e42_1_c;
    wire pp2_10_e42_1_cout;
    wire pp2_10_ha_1_s;
    wire pp2_10_ha_1_c;
    wire pp2_11_e42_1_s;
    wire pp2_11_e42_1_c;
    wire pp2_11_e42_1_cout;
    wire pp2_11_e42_2_s;
    wire pp2_11_e42_2_c;
    wire pp2_11_e42_2_cout;
    wire pp2_12_e42_1_s;
    wire pp2_12_e42_1_c;
    wire pp2_12_e42_1_cout;
    wire pp2_12_e42_2_s;
    wire pp2_12_e42_2_c;
    wire pp2_12_e42_2_cout;
    wire pp2_12_ha_1_s;
    wire pp2_12_ha_1_c;
    wire pp2_13_e42_1_s;
    wire pp2_13_e42_1_c;
    wire pp2_13_e42_1_cout;
    wire pp2_13_e42_2_s;
    wire pp2_13_e42_2_c;
    wire pp2_13_e42_2_cout;
    wire pp2_13_e42_3_s;
    wire pp2_13_e42_3_c;
    wire pp2_13_e42_3_cout;
    wire pp2_14_e42_1_s;
    wire pp2_14_e42_1_c;
    wire pp2_14_e42_1_cout;
    wire pp2_14_e42_2_s;
    wire pp2_14_e42_2_c;
    wire pp2_14_e42_2_cout;
    wire pp2_14_e42_3_s;
    wire pp2_14_e42_3_c;
    wire pp2_14_e42_3_cout;
    wire pp2_14_ha_1_s;
    wire pp2_14_ha_1_c;
    wire pp2_15_e42_1_s;
    wire pp2_15_e42_1_c;
    wire pp2_15_e42_1_cout;
    wire pp2_15_e42_2_s;
    wire pp2_15_e42_2_c;
    wire pp2_15_e42_2_cout;
    wire pp2_15_e42_3_s;
    wire pp2_15_e42_3_c;
    wire pp2_15_e42_3_cout;
    wire pp2_15_e42_4_s;
    wire pp2_15_e42_4_c;
    wire pp2_15_e42_4_cout;
    wire pp2_16_e42_1_s;
    wire pp2_16_e42_1_c;
    wire pp2_16_e42_1_cout;
    wire pp2_16_e42_2_s;
    wire pp2_16_e42_2_c;
    wire pp2_16_e42_2_cout;
    wire pp2_16_e42_3_s;
    wire pp2_16_e42_3_c;
    wire pp2_16_e42_3_cout;
    wire pp2_16_e42_4_s;
    wire pp2_16_e42_4_c;
    wire pp2_16_e42_4_cout;
    wire pp2_17_e42_1_s;
    wire pp2_17_e42_1_c;
    wire pp2_17_e42_1_cout;
    wire pp2_17_e42_2_s;
    wire pp2_17_e42_2_c;
    wire pp2_17_e42_2_cout;
    wire pp2_17_e42_3_s;
    wire pp2_17_e42_3_c;
    wire pp2_17_e42_3_cout;
    wire pp2_17_e42_4_s;
    wire pp2_17_e42_4_c;
    wire pp2_17_e42_4_cout;
    wire pp2_18_e42_1_s;
    wire pp2_18_e42_1_c;
    wire pp2_18_e42_1_cout;
    wire pp2_18_e42_2_s;
    wire pp2_18_e42_2_c;
    wire pp2_18_e42_2_cout;
    wire pp2_18_e42_3_s;
    wire pp2_18_e42_3_c;
    wire pp2_18_e42_3_cout;
    wire pp2_18_e42_4_s;
    wire pp2_18_e42_4_c;
    wire pp2_18_e42_4_cout;
    wire pp2_19_e42_1_s;
    wire pp2_19_e42_1_c;
    wire pp2_19_e42_1_cout;
    wire pp2_19_e42_2_s;
    wire pp2_19_e42_2_c;
    wire pp2_19_e42_2_cout;
    wire pp2_19_e42_3_s;
    wire pp2_19_e42_3_c;
    wire pp2_19_e42_3_cout;
    wire pp2_19_e42_4_s;
    wire pp2_19_e42_4_c;
    wire pp2_19_e42_4_cout;
    wire pp2_20_e42_1_s;
    wire pp2_20_e42_1_c;
    wire pp2_20_e42_1_cout;
    wire pp2_20_e42_2_s;
    wire pp2_20_e42_2_c;
    wire pp2_20_e42_2_cout;
    wire pp2_20_e42_3_s;
    wire pp2_20_e42_3_c;
    wire pp2_20_e42_3_cout;
    wire pp2_20_e42_4_s;
    wire pp2_20_e42_4_c;
    wire pp2_20_e42_4_cout;
    wire pp2_21_e42_1_s;
    wire pp2_21_e42_1_c;
    wire pp2_21_e42_1_cout;
    wire pp2_21_e42_2_s;
    wire pp2_21_e42_2_c;
    wire pp2_21_e42_2_cout;
    wire pp2_21_e42_3_s;
    wire pp2_21_e42_3_c;
    wire pp2_21_e42_3_cout;
    wire pp2_21_e42_4_s;
    wire pp2_21_e42_4_c;
    wire pp2_21_e42_4_cout;
    wire pp2_22_e42_1_s;
    wire pp2_22_e42_1_c;
    wire pp2_22_e42_1_cout;
    wire pp2_22_e42_2_s;
    wire pp2_22_e42_2_c;
    wire pp2_22_e42_2_cout;
    wire pp2_22_e42_3_s;
    wire pp2_22_e42_3_c;
    wire pp2_22_e42_3_cout;
    wire pp2_22_e42_4_s;
    wire pp2_22_e42_4_c;
    wire pp2_22_e42_4_cout;
    wire pp2_23_e42_1_s;
    wire pp2_23_e42_1_c;
    wire pp2_23_e42_1_cout;
    wire pp2_23_e42_2_s;
    wire pp2_23_e42_2_c;
    wire pp2_23_e42_2_cout;
    wire pp2_23_e42_3_s;
    wire pp2_23_e42_3_c;
    wire pp2_23_e42_3_cout;
    wire pp2_23_e42_4_s;
    wire pp2_23_e42_4_c;
    wire pp2_23_e42_4_cout;
    wire pp2_24_e42_1_s;
    wire pp2_24_e42_1_c;
    wire pp2_24_e42_1_cout;
    wire pp2_24_e42_2_s;
    wire pp2_24_e42_2_c;
    wire pp2_24_e42_2_cout;
    wire pp2_24_e42_3_s;
    wire pp2_24_e42_3_c;
    wire pp2_24_e42_3_cout;
    wire pp2_24_e42_4_s;
    wire pp2_24_e42_4_c;
    wire pp2_24_e42_4_cout;
    wire pp2_25_e42_1_s;
    wire pp2_25_e42_1_c;
    wire pp2_25_e42_1_cout;
    wire pp2_25_e42_2_s;
    wire pp2_25_e42_2_c;
    wire pp2_25_e42_2_cout;
    wire pp2_25_e42_3_s;
    wire pp2_25_e42_3_c;
    wire pp2_25_e42_3_cout;
    wire pp2_25_e42_4_s;
    wire pp2_25_e42_4_c;
    wire pp2_25_e42_4_cout;
    wire pp2_26_e42_1_s;
    wire pp2_26_e42_1_c;
    wire pp2_26_e42_1_cout;
    wire pp2_26_e42_2_s;
    wire pp2_26_e42_2_c;
    wire pp2_26_e42_2_cout;
    wire pp2_26_e42_3_s;
    wire pp2_26_e42_3_c;
    wire pp2_26_e42_3_cout;
    wire pp2_26_e42_4_s;
    wire pp2_26_e42_4_c;
    wire pp2_26_e42_4_cout;
    wire pp2_27_e42_1_s;
    wire pp2_27_e42_1_c;
    wire pp2_27_e42_1_cout;
    wire pp2_27_e42_2_s;
    wire pp2_27_e42_2_c;
    wire pp2_27_e42_2_cout;
    wire pp2_27_e42_3_s;
    wire pp2_27_e42_3_c;
    wire pp2_27_e42_3_cout;
    wire pp2_27_e42_4_s;
    wire pp2_27_e42_4_c;
    wire pp2_27_e42_4_cout;
    wire pp2_28_e42_1_s;
    wire pp2_28_e42_1_c;
    wire pp2_28_e42_1_cout;
    wire pp2_28_e42_2_s;
    wire pp2_28_e42_2_c;
    wire pp2_28_e42_2_cout;
    wire pp2_28_e42_3_s;
    wire pp2_28_e42_3_c;
    wire pp2_28_e42_3_cout;
    wire pp2_28_e42_4_s;
    wire pp2_28_e42_4_c;
    wire pp2_28_e42_4_cout;
    wire pp2_29_e42_1_s;
    wire pp2_29_e42_1_c;
    wire pp2_29_e42_1_cout;
    wire pp2_29_e42_2_s;
    wire pp2_29_e42_2_c;
    wire pp2_29_e42_2_cout;
    wire pp2_29_e42_3_s;
    wire pp2_29_e42_3_c;
    wire pp2_29_e42_3_cout;
    wire pp2_29_e42_4_s;
    wire pp2_29_e42_4_c;
    wire pp2_29_e42_4_cout;
    wire pp2_30_e42_1_s;
    wire pp2_30_e42_1_c;
    wire pp2_30_e42_1_cout;
    wire pp2_30_e42_2_s;
    wire pp2_30_e42_2_c;
    wire pp2_30_e42_2_cout;
    wire pp2_30_e42_3_s;
    wire pp2_30_e42_3_c;
    wire pp2_30_e42_3_cout;
    wire pp2_30_e42_4_s;
    wire pp2_30_e42_4_c;
    wire pp2_30_e42_4_cout;
    wire pp2_31_e42_1_s;
    wire pp2_31_e42_1_c;
    wire pp2_31_e42_1_cout;
    wire pp2_31_e42_2_s;
    wire pp2_31_e42_2_c;
    wire pp2_31_e42_2_cout;
    wire pp2_31_e42_3_s;
    wire pp2_31_e42_3_c;
    wire pp2_31_e42_3_cout;
    wire pp2_31_e42_4_s;
    wire pp2_31_e42_4_c;
    wire pp2_31_e42_4_cout;
    wire pp2_32_e42_1_s;
    wire pp2_32_e42_1_c;
    wire pp2_32_e42_1_cout;
    wire pp2_32_e42_2_s;
    wire pp2_32_e42_2_c;
    wire pp2_32_e42_2_cout;
    wire pp2_32_e42_3_s;
    wire pp2_32_e42_3_c;
    wire pp2_32_e42_3_cout;
    wire pp2_32_e42_4_s;
    wire pp2_32_e42_4_c;
    wire pp2_32_e42_4_cout;
    wire pp2_33_e42_1_s;
    wire pp2_33_e42_1_c;
    wire pp2_33_e42_1_cout;
    wire pp2_33_e42_2_s;
    wire pp2_33_e42_2_c;
    wire pp2_33_e42_2_cout;
    wire pp2_33_e42_3_s;
    wire pp2_33_e42_3_c;
    wire pp2_33_e42_3_cout;
    wire pp2_33_e42_4_s;
    wire pp2_33_e42_4_c;
    wire pp2_33_e42_4_cout;
    wire pp2_34_e42_1_s;
    wire pp2_34_e42_1_c;
    wire pp2_34_e42_1_cout;
    wire pp2_34_e42_2_s;
    wire pp2_34_e42_2_c;
    wire pp2_34_e42_2_cout;
    wire pp2_34_e42_3_s;
    wire pp2_34_e42_3_c;
    wire pp2_34_e42_3_cout;
    wire pp2_34_e42_4_s;
    wire pp2_34_e42_4_c;
    wire pp2_34_e42_4_cout;
    wire pp2_35_e42_1_s;
    wire pp2_35_e42_1_c;
    wire pp2_35_e42_1_cout;
    wire pp2_35_e42_2_s;
    wire pp2_35_e42_2_c;
    wire pp2_35_e42_2_cout;
    wire pp2_35_e42_3_s;
    wire pp2_35_e42_3_c;
    wire pp2_35_e42_3_cout;
    wire pp2_35_e42_4_s;
    wire pp2_35_e42_4_c;
    wire pp2_35_e42_4_cout;
    wire pp2_36_e42_1_s;
    wire pp2_36_e42_1_c;
    wire pp2_36_e42_1_cout;
    wire pp2_36_e42_2_s;
    wire pp2_36_e42_2_c;
    wire pp2_36_e42_2_cout;
    wire pp2_36_e42_3_s;
    wire pp2_36_e42_3_c;
    wire pp2_36_e42_3_cout;
    wire pp2_36_e42_4_s;
    wire pp2_36_e42_4_c;
    wire pp2_36_e42_4_cout;
    wire pp2_37_e42_1_s;
    wire pp2_37_e42_1_c;
    wire pp2_37_e42_1_cout;
    wire pp2_37_e42_2_s;
    wire pp2_37_e42_2_c;
    wire pp2_37_e42_2_cout;
    wire pp2_37_e42_3_s;
    wire pp2_37_e42_3_c;
    wire pp2_37_e42_3_cout;
    wire pp2_37_e42_4_s;
    wire pp2_37_e42_4_c;
    wire pp2_37_e42_4_cout;
    wire pp2_38_e42_1_s;
    wire pp2_38_e42_1_c;
    wire pp2_38_e42_1_cout;
    wire pp2_38_e42_2_s;
    wire pp2_38_e42_2_c;
    wire pp2_38_e42_2_cout;
    wire pp2_38_e42_3_s;
    wire pp2_38_e42_3_c;
    wire pp2_38_e42_3_cout;
    wire pp2_38_e42_4_s;
    wire pp2_38_e42_4_c;
    wire pp2_38_e42_4_cout;
    wire pp2_39_e42_1_s;
    wire pp2_39_e42_1_c;
    wire pp2_39_e42_1_cout;
    wire pp2_39_e42_2_s;
    wire pp2_39_e42_2_c;
    wire pp2_39_e42_2_cout;
    wire pp2_39_e42_3_s;
    wire pp2_39_e42_3_c;
    wire pp2_39_e42_3_cout;
    wire pp2_39_e42_4_s;
    wire pp2_39_e42_4_c;
    wire pp2_39_e42_4_cout;
    wire pp2_40_e42_1_s;
    wire pp2_40_e42_1_c;
    wire pp2_40_e42_1_cout;
    wire pp2_40_e42_2_s;
    wire pp2_40_e42_2_c;
    wire pp2_40_e42_2_cout;
    wire pp2_40_e42_3_s;
    wire pp2_40_e42_3_c;
    wire pp2_40_e42_3_cout;
    wire pp2_40_e42_4_s;
    wire pp2_40_e42_4_c;
    wire pp2_40_e42_4_cout;
    wire pp2_41_e42_1_s;
    wire pp2_41_e42_1_c;
    wire pp2_41_e42_1_cout;
    wire pp2_41_e42_2_s;
    wire pp2_41_e42_2_c;
    wire pp2_41_e42_2_cout;
    wire pp2_41_e42_3_s;
    wire pp2_41_e42_3_c;
    wire pp2_41_e42_3_cout;
    wire pp2_41_e42_4_s;
    wire pp2_41_e42_4_c;
    wire pp2_41_e42_4_cout;
    wire pp2_42_e42_1_s;
    wire pp2_42_e42_1_c;
    wire pp2_42_e42_1_cout;
    wire pp2_42_e42_2_s;
    wire pp2_42_e42_2_c;
    wire pp2_42_e42_2_cout;
    wire pp2_42_e42_3_s;
    wire pp2_42_e42_3_c;
    wire pp2_42_e42_3_cout;
    wire pp2_42_e42_4_s;
    wire pp2_42_e42_4_c;
    wire pp2_42_e42_4_cout;
    wire pp2_43_e42_1_s;
    wire pp2_43_e42_1_c;
    wire pp2_43_e42_1_cout;
    wire pp2_43_e42_2_s;
    wire pp2_43_e42_2_c;
    wire pp2_43_e42_2_cout;
    wire pp2_43_e42_3_s;
    wire pp2_43_e42_3_c;
    wire pp2_43_e42_3_cout;
    wire pp2_43_e42_4_s;
    wire pp2_43_e42_4_c;
    wire pp2_43_e42_4_cout;
    wire pp2_44_e42_1_s;
    wire pp2_44_e42_1_c;
    wire pp2_44_e42_1_cout;
    wire pp2_44_e42_2_s;
    wire pp2_44_e42_2_c;
    wire pp2_44_e42_2_cout;
    wire pp2_44_e42_3_s;
    wire pp2_44_e42_3_c;
    wire pp2_44_e42_3_cout;
    wire pp2_44_e42_4_s;
    wire pp2_44_e42_4_c;
    wire pp2_44_e42_4_cout;
    wire pp2_45_e42_1_s;
    wire pp2_45_e42_1_c;
    wire pp2_45_e42_1_cout;
    wire pp2_45_e42_2_s;
    wire pp2_45_e42_2_c;
    wire pp2_45_e42_2_cout;
    wire pp2_45_e42_3_s;
    wire pp2_45_e42_3_c;
    wire pp2_45_e42_3_cout;
    wire pp2_45_e42_4_s;
    wire pp2_45_e42_4_c;
    wire pp2_45_e42_4_cout;
    wire pp2_46_e42_1_s;
    wire pp2_46_e42_1_c;
    wire pp2_46_e42_1_cout;
    wire pp2_46_e42_2_s;
    wire pp2_46_e42_2_c;
    wire pp2_46_e42_2_cout;
    wire pp2_46_e42_3_s;
    wire pp2_46_e42_3_c;
    wire pp2_46_e42_3_cout;
    wire pp2_46_e42_4_s;
    wire pp2_46_e42_4_c;
    wire pp2_46_e42_4_cout;
    wire pp2_47_e42_1_s;
    wire pp2_47_e42_1_c;
    wire pp2_47_e42_1_cout;
    wire pp2_47_e42_2_s;
    wire pp2_47_e42_2_c;
    wire pp2_47_e42_2_cout;
    wire pp2_47_e42_3_s;
    wire pp2_47_e42_3_c;
    wire pp2_47_e42_3_cout;
    wire pp2_47_e42_4_s;
    wire pp2_47_e42_4_c;
    wire pp2_47_e42_4_cout;
    wire pp2_48_e42_1_s;
    wire pp2_48_e42_1_c;
    wire pp2_48_e42_1_cout;
    wire pp2_48_e42_2_s;
    wire pp2_48_e42_2_c;
    wire pp2_48_e42_2_cout;
    wire pp2_48_e42_3_s;
    wire pp2_48_e42_3_c;
    wire pp2_48_e42_3_cout;
    wire pp2_48_e42_4_s;
    wire pp2_48_e42_4_c;
    wire pp2_48_e42_4_cout;
    wire pp2_49_e42_1_s;
    wire pp2_49_e42_1_c;
    wire pp2_49_e42_1_cout;
    wire pp2_49_e42_2_s;
    wire pp2_49_e42_2_c;
    wire pp2_49_e42_2_cout;
    wire pp2_49_e42_3_s;
    wire pp2_49_e42_3_c;
    wire pp2_49_e42_3_cout;
    wire pp2_49_fa_1_s;
    wire pp2_49_fa_1_c;
    wire pp2_50_e42_1_s;
    wire pp2_50_e42_1_c;
    wire pp2_50_e42_1_cout;
    wire pp2_50_e42_2_s;
    wire pp2_50_e42_2_c;
    wire pp2_50_e42_2_cout;
    wire pp2_50_e42_3_s;
    wire pp2_50_e42_3_c;
    wire pp2_50_e42_3_cout;
    wire pp2_51_e42_1_s;
    wire pp2_51_e42_1_c;
    wire pp2_51_e42_1_cout;
    wire pp2_51_e42_2_s;
    wire pp2_51_e42_2_c;
    wire pp2_51_e42_2_cout;
    wire pp2_51_fa_1_s;
    wire pp2_51_fa_1_c;
    wire pp2_52_e42_1_s;
    wire pp2_52_e42_1_c;
    wire pp2_52_e42_1_cout;
    wire pp2_52_e42_2_s;
    wire pp2_52_e42_2_c;
    wire pp2_52_e42_2_cout;
    wire pp2_53_e42_1_s;
    wire pp2_53_e42_1_c;
    wire pp2_53_e42_1_cout;
    wire pp2_53_fa_1_s;
    wire pp2_53_fa_1_c;
    wire pp2_54_e42_1_s;
    wire pp2_54_e42_1_c;
    wire pp2_54_e42_1_cout;

// 压缩器模块实例化
    assign pp2_0 = pp1_0;
    assign pp2_1 = {pp1_1[0], pp1_1[1]};
    assign pp2_2 = {pp1_2[0], pp1_2[1], pp1_2[2]};
    assign pp2_3 = {pp1_3[0], pp1_3[1], pp1_3[2], pp1_3[3]};
    assign pp2_4 = {pp1_4[0], pp1_4[1], pp1_4[2], pp1_4[3], pp1_4[4]};
    assign pp2_5 = {pp1_5[0], pp1_5[1], pp1_5[2], pp1_5[3], pp1_5[4], pp1_5[5]};
    assign pp2_6 = {pp1_6[0], pp1_6[1], pp1_6[2], pp1_6[3], pp1_6[4], pp1_6[5], pp1_6[6]};
    assign pp2_7 = {pp1_7[0], pp1_7[1], pp1_7[2], pp1_7[3], pp1_7[4], pp1_7[5], pp1_7[6], pp1_7[7]};
    Half_adder Half_adder_pp2_8_1(
        .a(pp1_8[0]),
        .b(pp1_8[1]),
        .S(pp2_8_ha_1_s),
        .C(pp2_8_ha_1_c)
    );
    assign pp2_8 = {pp1_8[2], pp1_8[3], pp1_8[4], pp1_8[5], pp1_8[6], pp1_8[7], pp1_8[8], pp2_8_ha_1_s};

    E_4_2 E_4_2_pp2_9_1(
        .a(pp1_9[0]),
        .b(pp1_9[1]),
        .c(pp1_9[2]),
        .d(pp1_9[3]),
        .CIN(cin_net),
        .S(pp2_9_e42_1_s),
        .C(pp2_9_e42_1_c),
        .COUT(pp2_9_e42_1_cout)
    );
    assign pp2_9 = {pp1_9[4], pp1_9[5], pp1_9[6], pp1_9[7], pp1_9[8], pp1_9[9], pp2_8_ha_1_c, pp2_9_e42_1_s};
    E_4_2 E_4_2_pp2_10_1(
        .a(pp1_10[0]),
        .b(pp1_10[1]),
        .c(pp1_10[2]),
        .d(pp1_10[3]),
        .CIN(pp2_9_e42_1_cout),
        .S(pp2_10_e42_1_s),
        .C(pp2_10_e42_1_c),
        .COUT(pp2_10_e42_1_cout)
    );
    Half_adder Half_adder_pp2_10_1(
        .a(pp1_10[4]),
        .b(pp1_10[5]),
        .S(pp2_10_ha_1_s),
        .C(pp2_10_ha_1_c)
    );
    assign pp2_10 = {pp1_10[6], pp1_10[7], pp1_10[8], pp1_10[9], pp1_10[10], pp2_9_e42_1_c, pp2_10_e42_1_s, pp2_10_ha_1_s};
    E_4_2 E_4_2_pp2_11_1(
        .a(pp1_11[0]),
        .b(pp1_11[1]),
        .c(pp1_11[2]),
        .d(pp1_11[3]),
        .CIN(pp2_10_e42_1_cout),
        .S(pp2_11_e42_1_s),
        .C(pp2_11_e42_1_c),
        .COUT(pp2_11_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_11_2(
        .a(pp1_11[4]),
        .b(pp1_11[5]),
        .c(pp1_11[6]),
        .d(pp1_11[7]),
        .CIN(cin_net),
        .S(pp2_11_e42_2_s),
        .C(pp2_11_e42_2_c),
        .COUT(pp2_11_e42_2_cout)
    );
    assign pp2_11 = {pp1_11[8], pp1_11[9], pp1_11[10], pp1_11[11], pp2_10_e42_1_c, pp2_10_ha_1_c, pp2_11_e42_1_s, pp2_11_e42_2_s};
    E_4_2 E_4_2_pp2_12_1(
        .a(pp1_12[0]),
        .b(pp1_12[1]),
        .c(pp1_12[2]),
        .d(pp1_12[3]),
        .CIN(pp2_11_e42_1_cout),
        .S(pp2_12_e42_1_s),
        .C(pp2_12_e42_1_c),
        .COUT(pp2_12_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_12_2(
        .a(pp1_12[4]),
        .b(pp1_12[5]),
        .c(pp1_12[6]),
        .d(pp1_12[7]),
        .CIN(pp2_11_e42_2_cout),
        .S(pp2_12_e42_2_s),
        .C(pp2_12_e42_2_c),
        .COUT(pp2_12_e42_2_cout)
    );
    Half_adder Half_adder_pp2_12_1(
        .a(pp1_12[8]),
        .b(pp1_12[9]),
        .S(pp2_12_ha_1_s),
        .C(pp2_12_ha_1_c)
    );
    assign pp2_12 = {pp1_12[10], pp1_12[11], pp1_12[12], pp2_11_e42_1_c, pp2_11_e42_2_c, pp2_12_e42_1_s, pp2_12_e42_2_s, pp2_12_ha_1_s};
    E_4_2 E_4_2_pp2_13_1(
        .a(pp1_13[0]),
        .b(pp1_13[1]),
        .c(pp1_13[2]),
        .d(pp1_13[3]),
        .CIN(pp2_12_e42_1_cout),
        .S(pp2_13_e42_1_s),
        .C(pp2_13_e42_1_c),
        .COUT(pp2_13_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_13_2(
        .a(pp1_13[4]),
        .b(pp1_13[5]),
        .c(pp1_13[6]),
        .d(pp1_13[7]),
        .CIN(pp2_12_e42_2_cout),
        .S(pp2_13_e42_2_s),
        .C(pp2_13_e42_2_c),
        .COUT(pp2_13_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_13_3(
        .a(pp1_13[8]),
        .b(pp1_13[9]),
        .c(pp1_13[10]),
        .d(pp1_13[11]),
        .CIN(cin_net),
        .S(pp2_13_e42_3_s),
        .C(pp2_13_e42_3_c),
        .COUT(pp2_13_e42_3_cout)
    );
    assign pp2_13 = {pp1_13[12], pp1_13[13], pp2_12_e42_1_c, pp2_12_e42_2_c, pp2_12_ha_1_c, pp2_13_e42_1_s, pp2_13_e42_2_s, pp2_13_e42_3_s};
    E_4_2 E_4_2_pp2_14_1(
        .a(pp1_14[0]),
        .b(pp1_14[1]),
        .c(pp1_14[2]),
        .d(pp1_14[3]),
        .CIN(pp2_13_e42_1_cout),
        .S(pp2_14_e42_1_s),
        .C(pp2_14_e42_1_c),
        .COUT(pp2_14_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_14_2(
        .a(pp1_14[4]),
        .b(pp1_14[5]),
        .c(pp1_14[6]),
        .d(pp1_14[7]),
        .CIN(pp2_13_e42_2_cout),
        .S(pp2_14_e42_2_s),
        .C(pp2_14_e42_2_c),
        .COUT(pp2_14_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_14_3(
        .a(pp1_14[8]),
        .b(pp1_14[9]),
        .c(pp1_14[10]),
        .d(pp1_14[11]),
        .CIN(pp2_13_e42_3_cout),
        .S(pp2_14_e42_3_s),
        .C(pp2_14_e42_3_c),
        .COUT(pp2_14_e42_3_cout)
    );
    Half_adder Half_adder_pp2_14_1(
        .a(pp1_14[12]),
        .b(pp1_14[13]),
        .S(pp2_14_ha_1_s),
        .C(pp2_14_ha_1_c)
    );
    assign pp2_14 = {pp1_14[14], pp2_13_e42_1_c, pp2_13_e42_2_c, pp2_13_e42_3_c, pp2_14_e42_1_s, pp2_14_e42_2_s, pp2_14_e42_3_s, pp2_14_ha_1_s};
    E_4_2 E_4_2_pp2_15_1(
        .a(pp1_15[0]),
        .b(pp1_15[1]),
        .c(pp1_15[2]),
        .d(pp1_15[3]),
        .CIN(pp2_14_e42_1_cout),
        .S(pp2_15_e42_1_s),
        .C(pp2_15_e42_1_c),
        .COUT(pp2_15_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_15_2(
        .a(pp1_15[4]),
        .b(pp1_15[5]),
        .c(pp1_15[6]),
        .d(pp1_15[7]),
        .CIN(pp2_14_e42_2_cout),
        .S(pp2_15_e42_2_s),
        .C(pp2_15_e42_2_c),
        .COUT(pp2_15_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_15_3(
        .a(pp1_15[8]),
        .b(pp1_15[9]),
        .c(pp1_15[10]),
        .d(pp1_15[11]),
        .CIN(pp2_14_e42_3_cout),
        .S(pp2_15_e42_3_s),
        .C(pp2_15_e42_3_c),
        .COUT(pp2_15_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_15_4(
        .a(pp1_15[12]),
        .b(pp1_15[13]),
        .c(pp1_15[14]),
        .d(pp1_15[15]),
        .CIN(cin_net),
        .S(pp2_15_e42_4_s),
        .C(pp2_15_e42_4_c),
        .COUT(pp2_15_e42_4_cout)
    );
    assign pp2_15 = {pp2_14_e42_1_c, pp2_14_e42_2_c, pp2_14_e42_3_c, pp2_14_ha_1_c, pp2_15_e42_1_s, pp2_15_e42_2_s, pp2_15_e42_3_s, pp2_15_e42_4_s};
    E_4_2 E_4_2_pp2_16_1(
        .a(pp1_16[0]),
        .b(pp1_16[1]),
        .c(pp1_16[2]),
        .d(pp1_16[3]),
        .CIN(pp2_15_e42_1_cout),
        .S(pp2_16_e42_1_s),
        .C(pp2_16_e42_1_c),
        .COUT(pp2_16_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_16_2(
        .a(pp1_16[4]),
        .b(pp1_16[5]),
        .c(pp1_16[6]),
        .d(pp1_16[7]),
        .CIN(pp2_15_e42_2_cout),
        .S(pp2_16_e42_2_s),
        .C(pp2_16_e42_2_c),
        .COUT(pp2_16_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_16_3(
        .a(pp1_16[8]),
        .b(pp1_16[9]),
        .c(pp1_16[10]),
        .d(pp1_16[11]),
        .CIN(pp2_15_e42_3_cout),
        .S(pp2_16_e42_3_s),
        .C(pp2_16_e42_3_c),
        .COUT(pp2_16_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_16_4(
        .a(pp1_16[12]),
        .b(pp1_16[13]),
        .c(pp1_16[14]),
        .d(pp1_16[15]),
        .CIN(pp2_15_e42_4_cout),
        .S(pp2_16_e42_4_s),
        .C(pp2_16_e42_4_c),
        .COUT(pp2_16_e42_4_cout)
    );
    assign pp2_16 = {pp2_15_e42_1_c, pp2_15_e42_2_c, pp2_15_e42_3_c, pp2_15_e42_4_c, pp2_16_e42_1_s, pp2_16_e42_2_s, pp2_16_e42_3_s, pp2_16_e42_4_s};
    E_4_2 E_4_2_pp2_17_1(
        .a(pp1_17[0]),
        .b(pp1_17[1]),
        .c(pp1_17[2]),
        .d(pp1_17[3]),
        .CIN(pp2_16_e42_1_cout),
        .S(pp2_17_e42_1_s),
        .C(pp2_17_e42_1_c),
        .COUT(pp2_17_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_17_2(
        .a(pp1_17[4]),
        .b(pp1_17[5]),
        .c(pp1_17[6]),
        .d(pp1_17[7]),
        .CIN(pp2_16_e42_2_cout),
        .S(pp2_17_e42_2_s),
        .C(pp2_17_e42_2_c),
        .COUT(pp2_17_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_17_3(
        .a(pp1_17[8]),
        .b(pp1_17[9]),
        .c(pp1_17[10]),
        .d(pp1_17[11]),
        .CIN(pp2_16_e42_3_cout),
        .S(pp2_17_e42_3_s),
        .C(pp2_17_e42_3_c),
        .COUT(pp2_17_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_17_4(
        .a(pp1_17[12]),
        .b(pp1_17[13]),
        .c(pp1_17[14]),
        .d(pp1_17[15]),
        .CIN(pp2_16_e42_4_cout),
        .S(pp2_17_e42_4_s),
        .C(pp2_17_e42_4_c),
        .COUT(pp2_17_e42_4_cout)
    );
    assign pp2_17 = {pp2_16_e42_1_c, pp2_16_e42_2_c, pp2_16_e42_3_c, pp2_16_e42_4_c, pp2_17_e42_1_s, pp2_17_e42_2_s, pp2_17_e42_3_s, pp2_17_e42_4_s};
    E_4_2 E_4_2_pp2_18_1(
        .a(pp1_18[0]),
        .b(pp1_18[1]),
        .c(pp1_18[2]),
        .d(pp1_18[3]),
        .CIN(pp2_17_e42_1_cout),
        .S(pp2_18_e42_1_s),
        .C(pp2_18_e42_1_c),
        .COUT(pp2_18_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_18_2(
        .a(pp1_18[4]),
        .b(pp1_18[5]),
        .c(pp1_18[6]),
        .d(pp1_18[7]),
        .CIN(pp2_17_e42_2_cout),
        .S(pp2_18_e42_2_s),
        .C(pp2_18_e42_2_c),
        .COUT(pp2_18_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_18_3(
        .a(pp1_18[8]),
        .b(pp1_18[9]),
        .c(pp1_18[10]),
        .d(pp1_18[11]),
        .CIN(pp2_17_e42_3_cout),
        .S(pp2_18_e42_3_s),
        .C(pp2_18_e42_3_c),
        .COUT(pp2_18_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_18_4(
        .a(pp1_18[12]),
        .b(pp1_18[13]),
        .c(pp1_18[14]),
        .d(pp1_18[15]),
        .CIN(pp2_17_e42_4_cout),
        .S(pp2_18_e42_4_s),
        .C(pp2_18_e42_4_c),
        .COUT(pp2_18_e42_4_cout)
    );
    assign pp2_18 = {pp2_17_e42_1_c, pp2_17_e42_2_c, pp2_17_e42_3_c, pp2_17_e42_4_c, pp2_18_e42_1_s, pp2_18_e42_2_s, pp2_18_e42_3_s, pp2_18_e42_4_s};
    E_4_2 E_4_2_pp2_19_1(
        .a(pp1_19[0]),
        .b(pp1_19[1]),
        .c(pp1_19[2]),
        .d(pp1_19[3]),
        .CIN(pp2_18_e42_1_cout),
        .S(pp2_19_e42_1_s),
        .C(pp2_19_e42_1_c),
        .COUT(pp2_19_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_19_2(
        .a(pp1_19[4]),
        .b(pp1_19[5]),
        .c(pp1_19[6]),
        .d(pp1_19[7]),
        .CIN(pp2_18_e42_2_cout),
        .S(pp2_19_e42_2_s),
        .C(pp2_19_e42_2_c),
        .COUT(pp2_19_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_19_3(
        .a(pp1_19[8]),
        .b(pp1_19[9]),
        .c(pp1_19[10]),
        .d(pp1_19[11]),
        .CIN(pp2_18_e42_3_cout),
        .S(pp2_19_e42_3_s),
        .C(pp2_19_e42_3_c),
        .COUT(pp2_19_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_19_4(
        .a(pp1_19[12]),
        .b(pp1_19[13]),
        .c(pp1_19[14]),
        .d(pp1_19[15]),
        .CIN(pp2_18_e42_4_cout),
        .S(pp2_19_e42_4_s),
        .C(pp2_19_e42_4_c),
        .COUT(pp2_19_e42_4_cout)
    );
    assign pp2_19 = {pp2_18_e42_1_c, pp2_18_e42_2_c, pp2_18_e42_3_c, pp2_18_e42_4_c, pp2_19_e42_1_s, pp2_19_e42_2_s, pp2_19_e42_3_s, pp2_19_e42_4_s};
    E_4_2 E_4_2_pp2_20_1(
        .a(pp1_20[0]),
        .b(pp1_20[1]),
        .c(pp1_20[2]),
        .d(pp1_20[3]),
        .CIN(pp2_19_e42_1_cout),
        .S(pp2_20_e42_1_s),
        .C(pp2_20_e42_1_c),
        .COUT(pp2_20_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_20_2(
        .a(pp1_20[4]),
        .b(pp1_20[5]),
        .c(pp1_20[6]),
        .d(pp1_20[7]),
        .CIN(pp2_19_e42_2_cout),
        .S(pp2_20_e42_2_s),
        .C(pp2_20_e42_2_c),
        .COUT(pp2_20_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_20_3(
        .a(pp1_20[8]),
        .b(pp1_20[9]),
        .c(pp1_20[10]),
        .d(pp1_20[11]),
        .CIN(pp2_19_e42_3_cout),
        .S(pp2_20_e42_3_s),
        .C(pp2_20_e42_3_c),
        .COUT(pp2_20_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_20_4(
        .a(pp1_20[12]),
        .b(pp1_20[13]),
        .c(pp1_20[14]),
        .d(pp1_20[15]),
        .CIN(pp2_19_e42_4_cout),
        .S(pp2_20_e42_4_s),
        .C(pp2_20_e42_4_c),
        .COUT(pp2_20_e42_4_cout)
    );
    assign pp2_20 = {pp2_19_e42_1_c, pp2_19_e42_2_c, pp2_19_e42_3_c, pp2_19_e42_4_c, pp2_20_e42_1_s, pp2_20_e42_2_s, pp2_20_e42_3_s, pp2_20_e42_4_s};
    E_4_2 E_4_2_pp2_21_1(
        .a(pp1_21[0]),
        .b(pp1_21[1]),
        .c(pp1_21[2]),
        .d(pp1_21[3]),
        .CIN(pp2_20_e42_1_cout),
        .S(pp2_21_e42_1_s),
        .C(pp2_21_e42_1_c),
        .COUT(pp2_21_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_21_2(
        .a(pp1_21[4]),
        .b(pp1_21[5]),
        .c(pp1_21[6]),
        .d(pp1_21[7]),
        .CIN(pp2_20_e42_2_cout),
        .S(pp2_21_e42_2_s),
        .C(pp2_21_e42_2_c),
        .COUT(pp2_21_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_21_3(
        .a(pp1_21[8]),
        .b(pp1_21[9]),
        .c(pp1_21[10]),
        .d(pp1_21[11]),
        .CIN(pp2_20_e42_3_cout),
        .S(pp2_21_e42_3_s),
        .C(pp2_21_e42_3_c),
        .COUT(pp2_21_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_21_4(
        .a(pp1_21[12]),
        .b(pp1_21[13]),
        .c(pp1_21[14]),
        .d(pp1_21[15]),
        .CIN(pp2_20_e42_4_cout),
        .S(pp2_21_e42_4_s),
        .C(pp2_21_e42_4_c),
        .COUT(pp2_21_e42_4_cout)
    );
    assign pp2_21 = {pp2_20_e42_1_c, pp2_20_e42_2_c, pp2_20_e42_3_c, pp2_20_e42_4_c, pp2_21_e42_1_s, pp2_21_e42_2_s, pp2_21_e42_3_s, pp2_21_e42_4_s};
    E_4_2 E_4_2_pp2_22_1(
        .a(pp1_22[0]),
        .b(pp1_22[1]),
        .c(pp1_22[2]),
        .d(pp1_22[3]),
        .CIN(pp2_21_e42_1_cout),
        .S(pp2_22_e42_1_s),
        .C(pp2_22_e42_1_c),
        .COUT(pp2_22_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_22_2(
        .a(pp1_22[4]),
        .b(pp1_22[5]),
        .c(pp1_22[6]),
        .d(pp1_22[7]),
        .CIN(pp2_21_e42_2_cout),
        .S(pp2_22_e42_2_s),
        .C(pp2_22_e42_2_c),
        .COUT(pp2_22_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_22_3(
        .a(pp1_22[8]),
        .b(pp1_22[9]),
        .c(pp1_22[10]),
        .d(pp1_22[11]),
        .CIN(pp2_21_e42_3_cout),
        .S(pp2_22_e42_3_s),
        .C(pp2_22_e42_3_c),
        .COUT(pp2_22_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_22_4(
        .a(pp1_22[12]),
        .b(pp1_22[13]),
        .c(pp1_22[14]),
        .d(pp1_22[15]),
        .CIN(pp2_21_e42_4_cout),
        .S(pp2_22_e42_4_s),
        .C(pp2_22_e42_4_c),
        .COUT(pp2_22_e42_4_cout)
    );
    assign pp2_22 = {pp2_21_e42_1_c, pp2_21_e42_2_c, pp2_21_e42_3_c, pp2_21_e42_4_c, pp2_22_e42_1_s, pp2_22_e42_2_s, pp2_22_e42_3_s, pp2_22_e42_4_s};
    E_4_2 E_4_2_pp2_23_1(
        .a(pp1_23[0]),
        .b(pp1_23[1]),
        .c(pp1_23[2]),
        .d(pp1_23[3]),
        .CIN(pp2_22_e42_1_cout),
        .S(pp2_23_e42_1_s),
        .C(pp2_23_e42_1_c),
        .COUT(pp2_23_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_23_2(
        .a(pp1_23[4]),
        .b(pp1_23[5]),
        .c(pp1_23[6]),
        .d(pp1_23[7]),
        .CIN(pp2_22_e42_2_cout),
        .S(pp2_23_e42_2_s),
        .C(pp2_23_e42_2_c),
        .COUT(pp2_23_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_23_3(
        .a(pp1_23[8]),
        .b(pp1_23[9]),
        .c(pp1_23[10]),
        .d(pp1_23[11]),
        .CIN(pp2_22_e42_3_cout),
        .S(pp2_23_e42_3_s),
        .C(pp2_23_e42_3_c),
        .COUT(pp2_23_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_23_4(
        .a(pp1_23[12]),
        .b(pp1_23[13]),
        .c(pp1_23[14]),
        .d(pp1_23[15]),
        .CIN(pp2_22_e42_4_cout),
        .S(pp2_23_e42_4_s),
        .C(pp2_23_e42_4_c),
        .COUT(pp2_23_e42_4_cout)
    );
    assign pp2_23 = {pp2_22_e42_1_c, pp2_22_e42_2_c, pp2_22_e42_3_c, pp2_22_e42_4_c, pp2_23_e42_1_s, pp2_23_e42_2_s, pp2_23_e42_3_s, pp2_23_e42_4_s};
    E_4_2 E_4_2_pp2_24_1(
        .a(pp1_24[0]),
        .b(pp1_24[1]),
        .c(pp1_24[2]),
        .d(pp1_24[3]),
        .CIN(pp2_23_e42_1_cout),
        .S(pp2_24_e42_1_s),
        .C(pp2_24_e42_1_c),
        .COUT(pp2_24_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_24_2(
        .a(pp1_24[4]),
        .b(pp1_24[5]),
        .c(pp1_24[6]),
        .d(pp1_24[7]),
        .CIN(pp2_23_e42_2_cout),
        .S(pp2_24_e42_2_s),
        .C(pp2_24_e42_2_c),
        .COUT(pp2_24_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_24_3(
        .a(pp1_24[8]),
        .b(pp1_24[9]),
        .c(pp1_24[10]),
        .d(pp1_24[11]),
        .CIN(pp2_23_e42_3_cout),
        .S(pp2_24_e42_3_s),
        .C(pp2_24_e42_3_c),
        .COUT(pp2_24_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_24_4(
        .a(pp1_24[12]),
        .b(pp1_24[13]),
        .c(pp1_24[14]),
        .d(pp1_24[15]),
        .CIN(pp2_23_e42_4_cout),
        .S(pp2_24_e42_4_s),
        .C(pp2_24_e42_4_c),
        .COUT(pp2_24_e42_4_cout)
    );
    assign pp2_24 = {pp2_23_e42_1_c, pp2_23_e42_2_c, pp2_23_e42_3_c, pp2_23_e42_4_c, pp2_24_e42_1_s, pp2_24_e42_2_s, pp2_24_e42_3_s, pp2_24_e42_4_s};
    E_4_2 E_4_2_pp2_25_1(
        .a(pp1_25[0]),
        .b(pp1_25[1]),
        .c(pp1_25[2]),
        .d(pp1_25[3]),
        .CIN(pp2_24_e42_1_cout),
        .S(pp2_25_e42_1_s),
        .C(pp2_25_e42_1_c),
        .COUT(pp2_25_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_25_2(
        .a(pp1_25[4]),
        .b(pp1_25[5]),
        .c(pp1_25[6]),
        .d(pp1_25[7]),
        .CIN(pp2_24_e42_2_cout),
        .S(pp2_25_e42_2_s),
        .C(pp2_25_e42_2_c),
        .COUT(pp2_25_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_25_3(
        .a(pp1_25[8]),
        .b(pp1_25[9]),
        .c(pp1_25[10]),
        .d(pp1_25[11]),
        .CIN(pp2_24_e42_3_cout),
        .S(pp2_25_e42_3_s),
        .C(pp2_25_e42_3_c),
        .COUT(pp2_25_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_25_4(
        .a(pp1_25[12]),
        .b(pp1_25[13]),
        .c(pp1_25[14]),
        .d(pp1_25[15]),
        .CIN(pp2_24_e42_4_cout),
        .S(pp2_25_e42_4_s),
        .C(pp2_25_e42_4_c),
        .COUT(pp2_25_e42_4_cout)
    );
    assign pp2_25 = {pp2_24_e42_1_c, pp2_24_e42_2_c, pp2_24_e42_3_c, pp2_24_e42_4_c, pp2_25_e42_1_s, pp2_25_e42_2_s, pp2_25_e42_3_s, pp2_25_e42_4_s};
    E_4_2 E_4_2_pp2_26_1(
        .a(pp1_26[0]),
        .b(pp1_26[1]),
        .c(pp1_26[2]),
        .d(pp1_26[3]),
        .CIN(pp2_25_e42_1_cout),
        .S(pp2_26_e42_1_s),
        .C(pp2_26_e42_1_c),
        .COUT(pp2_26_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_26_2(
        .a(pp1_26[4]),
        .b(pp1_26[5]),
        .c(pp1_26[6]),
        .d(pp1_26[7]),
        .CIN(pp2_25_e42_2_cout),
        .S(pp2_26_e42_2_s),
        .C(pp2_26_e42_2_c),
        .COUT(pp2_26_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_26_3(
        .a(pp1_26[8]),
        .b(pp1_26[9]),
        .c(pp1_26[10]),
        .d(pp1_26[11]),
        .CIN(pp2_25_e42_3_cout),
        .S(pp2_26_e42_3_s),
        .C(pp2_26_e42_3_c),
        .COUT(pp2_26_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_26_4(
        .a(pp1_26[12]),
        .b(pp1_26[13]),
        .c(pp1_26[14]),
        .d(pp1_26[15]),
        .CIN(pp2_25_e42_4_cout),
        .S(pp2_26_e42_4_s),
        .C(pp2_26_e42_4_c),
        .COUT(pp2_26_e42_4_cout)
    );
    assign pp2_26 = {pp2_25_e42_1_c, pp2_25_e42_2_c, pp2_25_e42_3_c, pp2_25_e42_4_c, pp2_26_e42_1_s, pp2_26_e42_2_s, pp2_26_e42_3_s, pp2_26_e42_4_s};
    E_4_2 E_4_2_pp2_27_1(
        .a(pp1_27[0]),
        .b(pp1_27[1]),
        .c(pp1_27[2]),
        .d(pp1_27[3]),
        .CIN(pp2_26_e42_1_cout),
        .S(pp2_27_e42_1_s),
        .C(pp2_27_e42_1_c),
        .COUT(pp2_27_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_27_2(
        .a(pp1_27[4]),
        .b(pp1_27[5]),
        .c(pp1_27[6]),
        .d(pp1_27[7]),
        .CIN(pp2_26_e42_2_cout),
        .S(pp2_27_e42_2_s),
        .C(pp2_27_e42_2_c),
        .COUT(pp2_27_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_27_3(
        .a(pp1_27[8]),
        .b(pp1_27[9]),
        .c(pp1_27[10]),
        .d(pp1_27[11]),
        .CIN(pp2_26_e42_3_cout),
        .S(pp2_27_e42_3_s),
        .C(pp2_27_e42_3_c),
        .COUT(pp2_27_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_27_4(
        .a(pp1_27[12]),
        .b(pp1_27[13]),
        .c(pp1_27[14]),
        .d(pp1_27[15]),
        .CIN(pp2_26_e42_4_cout),
        .S(pp2_27_e42_4_s),
        .C(pp2_27_e42_4_c),
        .COUT(pp2_27_e42_4_cout)
    );
    assign pp2_27 = {pp2_26_e42_1_c, pp2_26_e42_2_c, pp2_26_e42_3_c, pp2_26_e42_4_c, pp2_27_e42_1_s, pp2_27_e42_2_s, pp2_27_e42_3_s, pp2_27_e42_4_s};
    E_4_2 E_4_2_pp2_28_1(
        .a(pp1_28[0]),
        .b(pp1_28[1]),
        .c(pp1_28[2]),
        .d(pp1_28[3]),
        .CIN(pp2_27_e42_1_cout),
        .S(pp2_28_e42_1_s),
        .C(pp2_28_e42_1_c),
        .COUT(pp2_28_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_28_2(
        .a(pp1_28[4]),
        .b(pp1_28[5]),
        .c(pp1_28[6]),
        .d(pp1_28[7]),
        .CIN(pp2_27_e42_2_cout),
        .S(pp2_28_e42_2_s),
        .C(pp2_28_e42_2_c),
        .COUT(pp2_28_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_28_3(
        .a(pp1_28[8]),
        .b(pp1_28[9]),
        .c(pp1_28[10]),
        .d(pp1_28[11]),
        .CIN(pp2_27_e42_3_cout),
        .S(pp2_28_e42_3_s),
        .C(pp2_28_e42_3_c),
        .COUT(pp2_28_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_28_4(
        .a(pp1_28[12]),
        .b(pp1_28[13]),
        .c(pp1_28[14]),
        .d(pp1_28[15]),
        .CIN(pp2_27_e42_4_cout),
        .S(pp2_28_e42_4_s),
        .C(pp2_28_e42_4_c),
        .COUT(pp2_28_e42_4_cout)
    );
    assign pp2_28 = {pp2_27_e42_1_c, pp2_27_e42_2_c, pp2_27_e42_3_c, pp2_27_e42_4_c, pp2_28_e42_1_s, pp2_28_e42_2_s, pp2_28_e42_3_s, pp2_28_e42_4_s};
    E_4_2 E_4_2_pp2_29_1(
        .a(pp1_29[0]),
        .b(pp1_29[1]),
        .c(pp1_29[2]),
        .d(pp1_29[3]),
        .CIN(pp2_28_e42_1_cout),
        .S(pp2_29_e42_1_s),
        .C(pp2_29_e42_1_c),
        .COUT(pp2_29_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_29_2(
        .a(pp1_29[4]),
        .b(pp1_29[5]),
        .c(pp1_29[6]),
        .d(pp1_29[7]),
        .CIN(pp2_28_e42_2_cout),
        .S(pp2_29_e42_2_s),
        .C(pp2_29_e42_2_c),
        .COUT(pp2_29_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_29_3(
        .a(pp1_29[8]),
        .b(pp1_29[9]),
        .c(pp1_29[10]),
        .d(pp1_29[11]),
        .CIN(pp2_28_e42_3_cout),
        .S(pp2_29_e42_3_s),
        .C(pp2_29_e42_3_c),
        .COUT(pp2_29_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_29_4(
        .a(pp1_29[12]),
        .b(pp1_29[13]),
        .c(pp1_29[14]),
        .d(pp1_29[15]),
        .CIN(pp2_28_e42_4_cout),
        .S(pp2_29_e42_4_s),
        .C(pp2_29_e42_4_c),
        .COUT(pp2_29_e42_4_cout)
    );
    assign pp2_29 = {pp2_28_e42_1_c, pp2_28_e42_2_c, pp2_28_e42_3_c, pp2_28_e42_4_c, pp2_29_e42_1_s, pp2_29_e42_2_s, pp2_29_e42_3_s, pp2_29_e42_4_s};
    E_4_2 E_4_2_pp2_30_1(
        .a(pp1_30[0]),
        .b(pp1_30[1]),
        .c(pp1_30[2]),
        .d(pp1_30[3]),
        .CIN(pp2_29_e42_1_cout),
        .S(pp2_30_e42_1_s),
        .C(pp2_30_e42_1_c),
        .COUT(pp2_30_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_30_2(
        .a(pp1_30[4]),
        .b(pp1_30[5]),
        .c(pp1_30[6]),
        .d(pp1_30[7]),
        .CIN(pp2_29_e42_2_cout),
        .S(pp2_30_e42_2_s),
        .C(pp2_30_e42_2_c),
        .COUT(pp2_30_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_30_3(
        .a(pp1_30[8]),
        .b(pp1_30[9]),
        .c(pp1_30[10]),
        .d(pp1_30[11]),
        .CIN(pp2_29_e42_3_cout),
        .S(pp2_30_e42_3_s),
        .C(pp2_30_e42_3_c),
        .COUT(pp2_30_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_30_4(
        .a(pp1_30[12]),
        .b(pp1_30[13]),
        .c(pp1_30[14]),
        .d(pp1_30[15]),
        .CIN(pp2_29_e42_4_cout),
        .S(pp2_30_e42_4_s),
        .C(pp2_30_e42_4_c),
        .COUT(pp2_30_e42_4_cout)
    );
    assign pp2_30 = {pp2_29_e42_1_c, pp2_29_e42_2_c, pp2_29_e42_3_c, pp2_29_e42_4_c, pp2_30_e42_1_s, pp2_30_e42_2_s, pp2_30_e42_3_s, pp2_30_e42_4_s};
    E_4_2 E_4_2_pp2_31_1(
        .a(pp1_31[0]),
        .b(pp1_31[1]),
        .c(pp1_31[2]),
        .d(pp1_31[3]),
        .CIN(pp2_30_e42_1_cout),
        .S(pp2_31_e42_1_s),
        .C(pp2_31_e42_1_c),
        .COUT(pp2_31_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_31_2(
        .a(pp1_31[4]),
        .b(pp1_31[5]),
        .c(pp1_31[6]),
        .d(pp1_31[7]),
        .CIN(pp2_30_e42_2_cout),
        .S(pp2_31_e42_2_s),
        .C(pp2_31_e42_2_c),
        .COUT(pp2_31_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_31_3(
        .a(pp1_31[8]),
        .b(pp1_31[9]),
        .c(pp1_31[10]),
        .d(pp1_31[11]),
        .CIN(pp2_30_e42_3_cout),
        .S(pp2_31_e42_3_s),
        .C(pp2_31_e42_3_c),
        .COUT(pp2_31_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_31_4(
        .a(pp1_31[12]),
        .b(pp1_31[13]),
        .c(pp1_31[14]),
        .d(pp1_31[15]),
        .CIN(pp2_30_e42_4_cout),
        .S(pp2_31_e42_4_s),
        .C(pp2_31_e42_4_c),
        .COUT(pp2_31_e42_4_cout)
    );
    assign pp2_31 = {pp2_30_e42_1_c, pp2_30_e42_2_c, pp2_30_e42_3_c, pp2_30_e42_4_c, pp2_31_e42_1_s, pp2_31_e42_2_s, pp2_31_e42_3_s, pp2_31_e42_4_s};
    E_4_2 E_4_2_pp2_32_1(
        .a(pp1_32[0]),
        .b(pp1_32[1]),
        .c(pp1_32[2]),
        .d(pp1_32[3]),
        .CIN(pp2_31_e42_1_cout),
        .S(pp2_32_e42_1_s),
        .C(pp2_32_e42_1_c),
        .COUT(pp2_32_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_32_2(
        .a(pp1_32[4]),
        .b(pp1_32[5]),
        .c(pp1_32[6]),
        .d(pp1_32[7]),
        .CIN(pp2_31_e42_2_cout),
        .S(pp2_32_e42_2_s),
        .C(pp2_32_e42_2_c),
        .COUT(pp2_32_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_32_3(
        .a(pp1_32[8]),
        .b(pp1_32[9]),
        .c(pp1_32[10]),
        .d(pp1_32[11]),
        .CIN(pp2_31_e42_3_cout),
        .S(pp2_32_e42_3_s),
        .C(pp2_32_e42_3_c),
        .COUT(pp2_32_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_32_4(
        .a(pp1_32[12]),
        .b(pp1_32[13]),
        .c(pp1_32[14]),
        .d(pp1_32[15]),
        .CIN(pp2_31_e42_4_cout),
        .S(pp2_32_e42_4_s),
        .C(pp2_32_e42_4_c),
        .COUT(pp2_32_e42_4_cout)
    );
    assign pp2_32 = {pp2_31_e42_1_c, pp2_31_e42_2_c, pp2_31_e42_3_c, pp2_31_e42_4_c, pp2_32_e42_1_s, pp2_32_e42_2_s, pp2_32_e42_3_s, pp2_32_e42_4_s};
    E_4_2 E_4_2_pp2_33_1(
        .a(pp1_33[0]),
        .b(pp1_33[1]),
        .c(pp1_33[2]),
        .d(pp1_33[3]),
        .CIN(pp2_32_e42_1_cout),
        .S(pp2_33_e42_1_s),
        .C(pp2_33_e42_1_c),
        .COUT(pp2_33_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_33_2(
        .a(pp1_33[4]),
        .b(pp1_33[5]),
        .c(pp1_33[6]),
        .d(pp1_33[7]),
        .CIN(pp2_32_e42_2_cout),
        .S(pp2_33_e42_2_s),
        .C(pp2_33_e42_2_c),
        .COUT(pp2_33_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_33_3(
        .a(pp1_33[8]),
        .b(pp1_33[9]),
        .c(pp1_33[10]),
        .d(pp1_33[11]),
        .CIN(pp2_32_e42_3_cout),
        .S(pp2_33_e42_3_s),
        .C(pp2_33_e42_3_c),
        .COUT(pp2_33_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_33_4(
        .a(pp1_33[12]),
        .b(pp1_33[13]),
        .c(pp1_33[14]),
        .d(pp1_33[15]),
        .CIN(pp2_32_e42_4_cout),
        .S(pp2_33_e42_4_s),
        .C(pp2_33_e42_4_c),
        .COUT(pp2_33_e42_4_cout)
    );
    assign pp2_33 = {pp2_32_e42_1_c, pp2_32_e42_2_c, pp2_32_e42_3_c, pp2_32_e42_4_c, pp2_33_e42_1_s, pp2_33_e42_2_s, pp2_33_e42_3_s, pp2_33_e42_4_s};
    E_4_2 E_4_2_pp2_34_1(
        .a(pp1_34[0]),
        .b(pp1_34[1]),
        .c(pp1_34[2]),
        .d(pp1_34[3]),
        .CIN(pp2_33_e42_1_cout),
        .S(pp2_34_e42_1_s),
        .C(pp2_34_e42_1_c),
        .COUT(pp2_34_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_34_2(
        .a(pp1_34[4]),
        .b(pp1_34[5]),
        .c(pp1_34[6]),
        .d(pp1_34[7]),
        .CIN(pp2_33_e42_2_cout),
        .S(pp2_34_e42_2_s),
        .C(pp2_34_e42_2_c),
        .COUT(pp2_34_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_34_3(
        .a(pp1_34[8]),
        .b(pp1_34[9]),
        .c(pp1_34[10]),
        .d(pp1_34[11]),
        .CIN(pp2_33_e42_3_cout),
        .S(pp2_34_e42_3_s),
        .C(pp2_34_e42_3_c),
        .COUT(pp2_34_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_34_4(
        .a(pp1_34[12]),
        .b(pp1_34[13]),
        .c(pp1_34[14]),
        .d(pp1_34[15]),
        .CIN(pp2_33_e42_4_cout),
        .S(pp2_34_e42_4_s),
        .C(pp2_34_e42_4_c),
        .COUT(pp2_34_e42_4_cout)
    );
    assign pp2_34 = {pp2_33_e42_1_c, pp2_33_e42_2_c, pp2_33_e42_3_c, pp2_33_e42_4_c, pp2_34_e42_1_s, pp2_34_e42_2_s, pp2_34_e42_3_s, pp2_34_e42_4_s};
    E_4_2 E_4_2_pp2_35_1(
        .a(pp1_35[0]),
        .b(pp1_35[1]),
        .c(pp1_35[2]),
        .d(pp1_35[3]),
        .CIN(pp2_34_e42_1_cout),
        .S(pp2_35_e42_1_s),
        .C(pp2_35_e42_1_c),
        .COUT(pp2_35_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_35_2(
        .a(pp1_35[4]),
        .b(pp1_35[5]),
        .c(pp1_35[6]),
        .d(pp1_35[7]),
        .CIN(pp2_34_e42_2_cout),
        .S(pp2_35_e42_2_s),
        .C(pp2_35_e42_2_c),
        .COUT(pp2_35_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_35_3(
        .a(pp1_35[8]),
        .b(pp1_35[9]),
        .c(pp1_35[10]),
        .d(pp1_35[11]),
        .CIN(pp2_34_e42_3_cout),
        .S(pp2_35_e42_3_s),
        .C(pp2_35_e42_3_c),
        .COUT(pp2_35_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_35_4(
        .a(pp1_35[12]),
        .b(pp1_35[13]),
        .c(pp1_35[14]),
        .d(pp1_35[15]),
        .CIN(pp2_34_e42_4_cout),
        .S(pp2_35_e42_4_s),
        .C(pp2_35_e42_4_c),
        .COUT(pp2_35_e42_4_cout)
    );
    assign pp2_35 = {pp2_34_e42_1_c, pp2_34_e42_2_c, pp2_34_e42_3_c, pp2_34_e42_4_c, pp2_35_e42_1_s, pp2_35_e42_2_s, pp2_35_e42_3_s, pp2_35_e42_4_s};
    E_4_2 E_4_2_pp2_36_1(
        .a(pp1_36[0]),
        .b(pp1_36[1]),
        .c(pp1_36[2]),
        .d(pp1_36[3]),
        .CIN(pp2_35_e42_1_cout),
        .S(pp2_36_e42_1_s),
        .C(pp2_36_e42_1_c),
        .COUT(pp2_36_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_36_2(
        .a(pp1_36[4]),
        .b(pp1_36[5]),
        .c(pp1_36[6]),
        .d(pp1_36[7]),
        .CIN(pp2_35_e42_2_cout),
        .S(pp2_36_e42_2_s),
        .C(pp2_36_e42_2_c),
        .COUT(pp2_36_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_36_3(
        .a(pp1_36[8]),
        .b(pp1_36[9]),
        .c(pp1_36[10]),
        .d(pp1_36[11]),
        .CIN(pp2_35_e42_3_cout),
        .S(pp2_36_e42_3_s),
        .C(pp2_36_e42_3_c),
        .COUT(pp2_36_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_36_4(
        .a(pp1_36[12]),
        .b(pp1_36[13]),
        .c(pp1_36[14]),
        .d(pp1_36[15]),
        .CIN(pp2_35_e42_4_cout),
        .S(pp2_36_e42_4_s),
        .C(pp2_36_e42_4_c),
        .COUT(pp2_36_e42_4_cout)
    );
    assign pp2_36 = {pp2_35_e42_1_c, pp2_35_e42_2_c, pp2_35_e42_3_c, pp2_35_e42_4_c, pp2_36_e42_1_s, pp2_36_e42_2_s, pp2_36_e42_3_s, pp2_36_e42_4_s};
    E_4_2 E_4_2_pp2_37_1(
        .a(pp1_37[0]),
        .b(pp1_37[1]),
        .c(pp1_37[2]),
        .d(pp1_37[3]),
        .CIN(pp2_36_e42_1_cout),
        .S(pp2_37_e42_1_s),
        .C(pp2_37_e42_1_c),
        .COUT(pp2_37_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_37_2(
        .a(pp1_37[4]),
        .b(pp1_37[5]),
        .c(pp1_37[6]),
        .d(pp1_37[7]),
        .CIN(pp2_36_e42_2_cout),
        .S(pp2_37_e42_2_s),
        .C(pp2_37_e42_2_c),
        .COUT(pp2_37_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_37_3(
        .a(pp1_37[8]),
        .b(pp1_37[9]),
        .c(pp1_37[10]),
        .d(pp1_37[11]),
        .CIN(pp2_36_e42_3_cout),
        .S(pp2_37_e42_3_s),
        .C(pp2_37_e42_3_c),
        .COUT(pp2_37_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_37_4(
        .a(pp1_37[12]),
        .b(pp1_37[13]),
        .c(pp1_37[14]),
        .d(pp1_37[15]),
        .CIN(pp2_36_e42_4_cout),
        .S(pp2_37_e42_4_s),
        .C(pp2_37_e42_4_c),
        .COUT(pp2_37_e42_4_cout)
    );
    assign pp2_37 = {pp2_36_e42_1_c, pp2_36_e42_2_c, pp2_36_e42_3_c, pp2_36_e42_4_c, pp2_37_e42_1_s, pp2_37_e42_2_s, pp2_37_e42_3_s, pp2_37_e42_4_s};
    E_4_2 E_4_2_pp2_38_1(
        .a(pp1_38[0]),
        .b(pp1_38[1]),
        .c(pp1_38[2]),
        .d(pp1_38[3]),
        .CIN(pp2_37_e42_1_cout),
        .S(pp2_38_e42_1_s),
        .C(pp2_38_e42_1_c),
        .COUT(pp2_38_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_38_2(
        .a(pp1_38[4]),
        .b(pp1_38[5]),
        .c(pp1_38[6]),
        .d(pp1_38[7]),
        .CIN(pp2_37_e42_2_cout),
        .S(pp2_38_e42_2_s),
        .C(pp2_38_e42_2_c),
        .COUT(pp2_38_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_38_3(
        .a(pp1_38[8]),
        .b(pp1_38[9]),
        .c(pp1_38[10]),
        .d(pp1_38[11]),
        .CIN(pp2_37_e42_3_cout),
        .S(pp2_38_e42_3_s),
        .C(pp2_38_e42_3_c),
        .COUT(pp2_38_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_38_4(
        .a(pp1_38[12]),
        .b(pp1_38[13]),
        .c(pp1_38[14]),
        .d(pp1_38[15]),
        .CIN(pp2_37_e42_4_cout),
        .S(pp2_38_e42_4_s),
        .C(pp2_38_e42_4_c),
        .COUT(pp2_38_e42_4_cout)
    );
    assign pp2_38 = {pp2_37_e42_1_c, pp2_37_e42_2_c, pp2_37_e42_3_c, pp2_37_e42_4_c, pp2_38_e42_1_s, pp2_38_e42_2_s, pp2_38_e42_3_s, pp2_38_e42_4_s};
    E_4_2 E_4_2_pp2_39_1(
        .a(pp1_39[0]),
        .b(pp1_39[1]),
        .c(pp1_39[2]),
        .d(pp1_39[3]),
        .CIN(pp2_38_e42_1_cout),
        .S(pp2_39_e42_1_s),
        .C(pp2_39_e42_1_c),
        .COUT(pp2_39_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_39_2(
        .a(pp1_39[4]),
        .b(pp1_39[5]),
        .c(pp1_39[6]),
        .d(pp1_39[7]),
        .CIN(pp2_38_e42_2_cout),
        .S(pp2_39_e42_2_s),
        .C(pp2_39_e42_2_c),
        .COUT(pp2_39_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_39_3(
        .a(pp1_39[8]),
        .b(pp1_39[9]),
        .c(pp1_39[10]),
        .d(pp1_39[11]),
        .CIN(pp2_38_e42_3_cout),
        .S(pp2_39_e42_3_s),
        .C(pp2_39_e42_3_c),
        .COUT(pp2_39_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_39_4(
        .a(pp1_39[12]),
        .b(pp1_39[13]),
        .c(pp1_39[14]),
        .d(pp1_39[15]),
        .CIN(pp2_38_e42_4_cout),
        .S(pp2_39_e42_4_s),
        .C(pp2_39_e42_4_c),
        .COUT(pp2_39_e42_4_cout)
    );
    assign pp2_39 = {pp2_38_e42_1_c, pp2_38_e42_2_c, pp2_38_e42_3_c, pp2_38_e42_4_c, pp2_39_e42_1_s, pp2_39_e42_2_s, pp2_39_e42_3_s, pp2_39_e42_4_s};
    E_4_2 E_4_2_pp2_40_1(
        .a(pp1_40[0]),
        .b(pp1_40[1]),
        .c(pp1_40[2]),
        .d(pp1_40[3]),
        .CIN(pp2_39_e42_1_cout),
        .S(pp2_40_e42_1_s),
        .C(pp2_40_e42_1_c),
        .COUT(pp2_40_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_40_2(
        .a(pp1_40[4]),
        .b(pp1_40[5]),
        .c(pp1_40[6]),
        .d(pp1_40[7]),
        .CIN(pp2_39_e42_2_cout),
        .S(pp2_40_e42_2_s),
        .C(pp2_40_e42_2_c),
        .COUT(pp2_40_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_40_3(
        .a(pp1_40[8]),
        .b(pp1_40[9]),
        .c(pp1_40[10]),
        .d(pp1_40[11]),
        .CIN(pp2_39_e42_3_cout),
        .S(pp2_40_e42_3_s),
        .C(pp2_40_e42_3_c),
        .COUT(pp2_40_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_40_4(
        .a(pp1_40[12]),
        .b(pp1_40[13]),
        .c(pp1_40[14]),
        .d(pp1_40[15]),
        .CIN(pp2_39_e42_4_cout),
        .S(pp2_40_e42_4_s),
        .C(pp2_40_e42_4_c),
        .COUT(pp2_40_e42_4_cout)
    );
    assign pp2_40 = {pp2_39_e42_1_c, pp2_39_e42_2_c, pp2_39_e42_3_c, pp2_39_e42_4_c, pp2_40_e42_1_s, pp2_40_e42_2_s, pp2_40_e42_3_s, pp2_40_e42_4_s};
    E_4_2 E_4_2_pp2_41_1(
        .a(pp1_41[0]),
        .b(pp1_41[1]),
        .c(pp1_41[2]),
        .d(pp1_41[3]),
        .CIN(pp2_40_e42_1_cout),
        .S(pp2_41_e42_1_s),
        .C(pp2_41_e42_1_c),
        .COUT(pp2_41_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_41_2(
        .a(pp1_41[4]),
        .b(pp1_41[5]),
        .c(pp1_41[6]),
        .d(pp1_41[7]),
        .CIN(pp2_40_e42_2_cout),
        .S(pp2_41_e42_2_s),
        .C(pp2_41_e42_2_c),
        .COUT(pp2_41_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_41_3(
        .a(pp1_41[8]),
        .b(pp1_41[9]),
        .c(pp1_41[10]),
        .d(pp1_41[11]),
        .CIN(pp2_40_e42_3_cout),
        .S(pp2_41_e42_3_s),
        .C(pp2_41_e42_3_c),
        .COUT(pp2_41_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_41_4(
        .a(pp1_41[12]),
        .b(pp1_41[13]),
        .c(pp1_41[14]),
        .d(pp1_41[15]),
        .CIN(pp2_40_e42_4_cout),
        .S(pp2_41_e42_4_s),
        .C(pp2_41_e42_4_c),
        .COUT(pp2_41_e42_4_cout)
    );
    assign pp2_41 = {pp2_40_e42_1_c, pp2_40_e42_2_c, pp2_40_e42_3_c, pp2_40_e42_4_c, pp2_41_e42_1_s, pp2_41_e42_2_s, pp2_41_e42_3_s, pp2_41_e42_4_s};
    E_4_2 E_4_2_pp2_42_1(
        .a(pp1_42[0]),
        .b(pp1_42[1]),
        .c(pp1_42[2]),
        .d(pp1_42[3]),
        .CIN(pp2_41_e42_1_cout),
        .S(pp2_42_e42_1_s),
        .C(pp2_42_e42_1_c),
        .COUT(pp2_42_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_42_2(
        .a(pp1_42[4]),
        .b(pp1_42[5]),
        .c(pp1_42[6]),
        .d(pp1_42[7]),
        .CIN(pp2_41_e42_2_cout),
        .S(pp2_42_e42_2_s),
        .C(pp2_42_e42_2_c),
        .COUT(pp2_42_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_42_3(
        .a(pp1_42[8]),
        .b(pp1_42[9]),
        .c(pp1_42[10]),
        .d(pp1_42[11]),
        .CIN(pp2_41_e42_3_cout),
        .S(pp2_42_e42_3_s),
        .C(pp2_42_e42_3_c),
        .COUT(pp2_42_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_42_4(
        .a(pp1_42[12]),
        .b(pp1_42[13]),
        .c(pp1_42[14]),
        .d(pp1_42[15]),
        .CIN(pp2_41_e42_4_cout),
        .S(pp2_42_e42_4_s),
        .C(pp2_42_e42_4_c),
        .COUT(pp2_42_e42_4_cout)
    );
    assign pp2_42 = {pp2_41_e42_1_c, pp2_41_e42_2_c, pp2_41_e42_3_c, pp2_41_e42_4_c, pp2_42_e42_1_s, pp2_42_e42_2_s, pp2_42_e42_3_s, pp2_42_e42_4_s};
    E_4_2 E_4_2_pp2_43_1(
        .a(pp1_43[0]),
        .b(pp1_43[1]),
        .c(pp1_43[2]),
        .d(pp1_43[3]),
        .CIN(pp2_42_e42_1_cout),
        .S(pp2_43_e42_1_s),
        .C(pp2_43_e42_1_c),
        .COUT(pp2_43_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_43_2(
        .a(pp1_43[4]),
        .b(pp1_43[5]),
        .c(pp1_43[6]),
        .d(pp1_43[7]),
        .CIN(pp2_42_e42_2_cout),
        .S(pp2_43_e42_2_s),
        .C(pp2_43_e42_2_c),
        .COUT(pp2_43_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_43_3(
        .a(pp1_43[8]),
        .b(pp1_43[9]),
        .c(pp1_43[10]),
        .d(pp1_43[11]),
        .CIN(pp2_42_e42_3_cout),
        .S(pp2_43_e42_3_s),
        .C(pp2_43_e42_3_c),
        .COUT(pp2_43_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_43_4(
        .a(pp1_43[12]),
        .b(pp1_43[13]),
        .c(pp1_43[14]),
        .d(pp1_43[15]),
        .CIN(pp2_42_e42_4_cout),
        .S(pp2_43_e42_4_s),
        .C(pp2_43_e42_4_c),
        .COUT(pp2_43_e42_4_cout)
    );
    assign pp2_43 = {pp2_42_e42_1_c, pp2_42_e42_2_c, pp2_42_e42_3_c, pp2_42_e42_4_c, pp2_43_e42_1_s, pp2_43_e42_2_s, pp2_43_e42_3_s, pp2_43_e42_4_s};
    E_4_2 E_4_2_pp2_44_1(
        .a(pp1_44[0]),
        .b(pp1_44[1]),
        .c(pp1_44[2]),
        .d(pp1_44[3]),
        .CIN(pp2_43_e42_1_cout),
        .S(pp2_44_e42_1_s),
        .C(pp2_44_e42_1_c),
        .COUT(pp2_44_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_44_2(
        .a(pp1_44[4]),
        .b(pp1_44[5]),
        .c(pp1_44[6]),
        .d(pp1_44[7]),
        .CIN(pp2_43_e42_2_cout),
        .S(pp2_44_e42_2_s),
        .C(pp2_44_e42_2_c),
        .COUT(pp2_44_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_44_3(
        .a(pp1_44[8]),
        .b(pp1_44[9]),
        .c(pp1_44[10]),
        .d(pp1_44[11]),
        .CIN(pp2_43_e42_3_cout),
        .S(pp2_44_e42_3_s),
        .C(pp2_44_e42_3_c),
        .COUT(pp2_44_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_44_4(
        .a(pp1_44[12]),
        .b(pp1_44[13]),
        .c(pp1_44[14]),
        .d(pp1_44[15]),
        .CIN(pp2_43_e42_4_cout),
        .S(pp2_44_e42_4_s),
        .C(pp2_44_e42_4_c),
        .COUT(pp2_44_e42_4_cout)
    );
    assign pp2_44 = {pp2_43_e42_1_c, pp2_43_e42_2_c, pp2_43_e42_3_c, pp2_43_e42_4_c, pp2_44_e42_1_s, pp2_44_e42_2_s, pp2_44_e42_3_s, pp2_44_e42_4_s};
    E_4_2 E_4_2_pp2_45_1(
        .a(pp1_45[0]),
        .b(pp1_45[1]),
        .c(pp1_45[2]),
        .d(pp1_45[3]),
        .CIN(pp2_44_e42_1_cout),
        .S(pp2_45_e42_1_s),
        .C(pp2_45_e42_1_c),
        .COUT(pp2_45_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_45_2(
        .a(pp1_45[4]),
        .b(pp1_45[5]),
        .c(pp1_45[6]),
        .d(pp1_45[7]),
        .CIN(pp2_44_e42_2_cout),
        .S(pp2_45_e42_2_s),
        .C(pp2_45_e42_2_c),
        .COUT(pp2_45_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_45_3(
        .a(pp1_45[8]),
        .b(pp1_45[9]),
        .c(pp1_45[10]),
        .d(pp1_45[11]),
        .CIN(pp2_44_e42_3_cout),
        .S(pp2_45_e42_3_s),
        .C(pp2_45_e42_3_c),
        .COUT(pp2_45_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_45_4(
        .a(pp1_45[12]),
        .b(pp1_45[13]),
        .c(pp1_45[14]),
        .d(pp1_45[15]),
        .CIN(pp2_44_e42_4_cout),
        .S(pp2_45_e42_4_s),
        .C(pp2_45_e42_4_c),
        .COUT(pp2_45_e42_4_cout)
    );
    assign pp2_45 = {pp2_44_e42_1_c, pp2_44_e42_2_c, pp2_44_e42_3_c, pp2_44_e42_4_c, pp2_45_e42_1_s, pp2_45_e42_2_s, pp2_45_e42_3_s, pp2_45_e42_4_s};
    E_4_2 E_4_2_pp2_46_1(
        .a(pp1_46[0]),
        .b(pp1_46[1]),
        .c(pp1_46[2]),
        .d(pp1_46[3]),
        .CIN(pp2_45_e42_1_cout),
        .S(pp2_46_e42_1_s),
        .C(pp2_46_e42_1_c),
        .COUT(pp2_46_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_46_2(
        .a(pp1_46[4]),
        .b(pp1_46[5]),
        .c(pp1_46[6]),
        .d(pp1_46[7]),
        .CIN(pp2_45_e42_2_cout),
        .S(pp2_46_e42_2_s),
        .C(pp2_46_e42_2_c),
        .COUT(pp2_46_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_46_3(
        .a(pp1_46[8]),
        .b(pp1_46[9]),
        .c(pp1_46[10]),
        .d(pp1_46[11]),
        .CIN(pp2_45_e42_3_cout),
        .S(pp2_46_e42_3_s),
        .C(pp2_46_e42_3_c),
        .COUT(pp2_46_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_46_4(
        .a(pp1_46[12]),
        .b(pp1_46[13]),
        .c(pp1_46[14]),
        .d(pp1_46[15]),
        .CIN(pp2_45_e42_4_cout),
        .S(pp2_46_e42_4_s),
        .C(pp2_46_e42_4_c),
        .COUT(pp2_46_e42_4_cout)
    );
    assign pp2_46 = {pp2_45_e42_1_c, pp2_45_e42_2_c, pp2_45_e42_3_c, pp2_45_e42_4_c, pp2_46_e42_1_s, pp2_46_e42_2_s, pp2_46_e42_3_s, pp2_46_e42_4_s};
    E_4_2 E_4_2_pp2_47_1(
        .a(pp1_47[0]),
        .b(pp1_47[1]),
        .c(pp1_47[2]),
        .d(pp1_47[3]),
        .CIN(pp2_46_e42_1_cout),
        .S(pp2_47_e42_1_s),
        .C(pp2_47_e42_1_c),
        .COUT(pp2_47_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_47_2(
        .a(pp1_47[4]),
        .b(pp1_47[5]),
        .c(pp1_47[6]),
        .d(pp1_47[7]),
        .CIN(pp2_46_e42_2_cout),
        .S(pp2_47_e42_2_s),
        .C(pp2_47_e42_2_c),
        .COUT(pp2_47_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_47_3(
        .a(pp1_47[8]),
        .b(pp1_47[9]),
        .c(pp1_47[10]),
        .d(pp1_47[11]),
        .CIN(pp2_46_e42_3_cout),
        .S(pp2_47_e42_3_s),
        .C(pp2_47_e42_3_c),
        .COUT(pp2_47_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_47_4(
        .a(pp1_47[12]),
        .b(pp1_47[13]),
        .c(pp1_47[14]),
        .d(pp1_47[15]),
        .CIN(pp2_46_e42_4_cout),
        .S(pp2_47_e42_4_s),
        .C(pp2_47_e42_4_c),
        .COUT(pp2_47_e42_4_cout)
    );
    assign pp2_47 = {pp2_46_e42_1_c, pp2_46_e42_2_c, pp2_46_e42_3_c, pp2_46_e42_4_c, pp2_47_e42_1_s, pp2_47_e42_2_s, pp2_47_e42_3_s, pp2_47_e42_4_s};
    E_4_2 E_4_2_pp2_48_1(
        .a(pp1_48[0]),
        .b(pp1_48[1]),
        .c(pp1_48[2]),
        .d(pp1_48[3]),
        .CIN(pp2_47_e42_1_cout),
        .S(pp2_48_e42_1_s),
        .C(pp2_48_e42_1_c),
        .COUT(pp2_48_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_48_2(
        .a(pp1_48[4]),
        .b(pp1_48[5]),
        .c(pp1_48[6]),
        .d(pp1_48[7]),
        .CIN(pp2_47_e42_2_cout),
        .S(pp2_48_e42_2_s),
        .C(pp2_48_e42_2_c),
        .COUT(pp2_48_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_48_3(
        .a(pp1_48[8]),
        .b(pp1_48[9]),
        .c(pp1_48[10]),
        .d(pp1_48[11]),
        .CIN(pp2_47_e42_3_cout),
        .S(pp2_48_e42_3_s),
        .C(pp2_48_e42_3_c),
        .COUT(pp2_48_e42_3_cout)
    );
    E_4_2 E_4_2_pp2_48_4(
        .a(pp1_48[12]),
        .b(pp1_48[13]),
        .c(pp1_48[14]),
        .d(pp1_48[15]),
        .CIN(pp2_47_e42_4_cout),
        .S(pp2_48_e42_4_s),
        .C(pp2_48_e42_4_c),
        .COUT(pp2_48_e42_4_cout)
    );
    assign pp2_48 = {pp2_47_e42_1_c, pp2_47_e42_2_c, pp2_47_e42_3_c, pp2_47_e42_4_c, pp2_48_e42_1_s, pp2_48_e42_2_s, pp2_48_e42_3_s, pp2_48_e42_4_s};
    E_4_2 E_4_2_pp2_49_1(
        .a(pp1_49[0]),
        .b(pp1_49[1]),
        .c(pp1_49[2]),
        .d(pp1_49[3]),
        .CIN(pp2_48_e42_1_cout),
        .S(pp2_49_e42_1_s),
        .C(pp2_49_e42_1_c),
        .COUT(pp2_49_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_49_2(
        .a(pp1_49[4]),
        .b(pp1_49[5]),
        .c(pp1_49[6]),
        .d(pp1_49[7]),
        .CIN(pp2_48_e42_2_cout),
        .S(pp2_49_e42_2_s),
        .C(pp2_49_e42_2_c),
        .COUT(pp2_49_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_49_3(
        .a(pp1_49[8]),
        .b(pp1_49[9]),
        .c(pp1_49[10]),
        .d(pp1_49[11]),
        .CIN(pp2_48_e42_3_cout),
        .S(pp2_49_e42_3_s),
        .C(pp2_49_e42_3_c),
        .COUT(pp2_49_e42_3_cout)
    );
    Full_adder Full_adder_pp2_49_1(
        .a(pp1_49[12]),
        .b(pp1_49[13]),
        .CIN(pp2_48_e42_4_cout),
        .S(pp2_49_fa_1_s),
        .C(pp2_49_fa_1_c)
    );
    assign pp2_49 = {pp2_48_e42_1_c, pp2_48_e42_2_c, pp2_48_e42_3_c, pp2_48_e42_4_c, pp2_49_e42_1_s, pp2_49_e42_2_s, pp2_49_e42_3_s, pp2_49_fa_1_s};
    E_4_2 E_4_2_pp2_50_1(
        .a(pp1_50[0]),
        .b(pp1_50[1]),
        .c(pp1_50[2]),
        .d(pp1_50[3]),
        .CIN(pp2_49_e42_1_cout),
        .S(pp2_50_e42_1_s),
        .C(pp2_50_e42_1_c),
        .COUT(pp2_50_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_50_2(
        .a(pp1_50[4]),
        .b(pp1_50[5]),
        .c(pp1_50[6]),
        .d(pp1_50[7]),
        .CIN(pp2_49_e42_2_cout),
        .S(pp2_50_e42_2_s),
        .C(pp2_50_e42_2_c),
        .COUT(pp2_50_e42_2_cout)
    );
    E_4_2 E_4_2_pp2_50_3(
        .a(pp1_50[8]),
        .b(pp1_50[9]),
        .c(pp1_50[10]),
        .d(pp1_50[11]),
        .CIN(pp2_49_e42_3_cout),
        .S(pp2_50_e42_3_s),
        .C(pp2_50_e42_3_c),
        .COUT(pp2_50_e42_3_cout)
    );
    assign pp2_50 = {pp1_50[12], pp2_49_e42_1_c, pp2_49_e42_2_c, pp2_49_e42_3_c, pp2_49_fa_1_c, pp2_50_e42_1_s, pp2_50_e42_2_s, pp2_50_e42_3_s};
    E_4_2 E_4_2_pp2_51_1(
        .a(pp1_51[0]),
        .b(pp1_51[1]),
        .c(pp1_51[2]),
        .d(pp1_51[3]),
        .CIN(pp2_50_e42_1_cout),
        .S(pp2_51_e42_1_s),
        .C(pp2_51_e42_1_c),
        .COUT(pp2_51_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_51_2(
        .a(pp1_51[4]),
        .b(pp1_51[5]),
        .c(pp1_51[6]),
        .d(pp1_51[7]),
        .CIN(pp2_50_e42_2_cout),
        .S(pp2_51_e42_2_s),
        .C(pp2_51_e42_2_c),
        .COUT(pp2_51_e42_2_cout)
    );
    Full_adder Full_adder_pp2_51_1(
        .a(pp1_51[8]),
        .b(pp1_51[9]),
        .CIN(pp2_50_e42_3_cout),
        .S(pp2_51_fa_1_s),
        .C(pp2_51_fa_1_c)
    );
    assign pp2_51 = {pp1_51[10], pp1_51[11], pp2_50_e42_1_c, pp2_50_e42_2_c, pp2_50_e42_3_c, pp2_51_e42_1_s, pp2_51_e42_2_s, pp2_51_fa_1_s};
    E_4_2 E_4_2_pp2_52_1(
        .a(pp1_52[0]),
        .b(pp1_52[1]),
        .c(pp1_52[2]),
        .d(pp1_52[3]),
        .CIN(pp2_51_e42_1_cout),
        .S(pp2_52_e42_1_s),
        .C(pp2_52_e42_1_c),
        .COUT(pp2_52_e42_1_cout)
    );
    E_4_2 E_4_2_pp2_52_2(
        .a(pp1_52[4]),
        .b(pp1_52[5]),
        .c(pp1_52[6]),
        .d(pp1_52[7]),
        .CIN(pp2_51_e42_2_cout),
        .S(pp2_52_e42_2_s),
        .C(pp2_52_e42_2_c),
        .COUT(pp2_52_e42_2_cout)
    );
    assign pp2_52 = {pp1_52[8], pp1_52[9], pp1_52[10], pp2_51_e42_1_c, pp2_51_e42_2_c, pp2_51_fa_1_c, pp2_52_e42_1_s, pp2_52_e42_2_s};
    E_4_2 E_4_2_pp2_53_1(
        .a(pp1_53[0]),
        .b(pp1_53[1]),
        .c(pp1_53[2]),
        .d(pp1_53[3]),
        .CIN(pp2_52_e42_1_cout),
        .S(pp2_53_e42_1_s),
        .C(pp2_53_e42_1_c),
        .COUT(pp2_53_e42_1_cout)
    );
    Full_adder Full_adder_pp2_53_1(
        .a(pp1_53[4]),
        .b(pp1_53[5]),
        .CIN(pp2_52_e42_2_cout),
        .S(pp2_53_fa_1_s),
        .C(pp2_53_fa_1_c)
    );
    assign pp2_53 = {pp1_53[6], pp1_53[7], pp1_53[8], pp1_53[9], pp2_52_e42_1_c, pp2_52_e42_2_c, pp2_53_e42_1_s, pp2_53_fa_1_s};
    E_4_2 E_4_2_pp2_54_1(
        .a(pp1_54[0]),
        .b(pp1_54[1]),
        .c(pp1_54[2]),
        .d(pp1_54[3]),
        .CIN(pp2_53_e42_1_cout),
        .S(pp2_54_e42_1_s),
        .C(pp2_54_e42_1_c),
        .COUT(pp2_54_e42_1_cout)
    );
    assign pp2_54 = {pp1_54[4], pp1_54[5], pp1_54[6], pp1_54[7], pp1_54[8], pp2_53_e42_1_c, pp2_53_fa_1_c, pp2_54_e42_1_s};
    Full_adder Full_adder_pp2_55_1(
        .a(pp1_55[0]),
        .b(pp1_55[1]),
        .CIN(pp2_54_e42_1_cout),
        .S(pp2_55_fa_1_s),
        .C(pp2_55_fa_1_c)
    );
    assign pp2_55 = {pp1_55[2], pp1_55[3], pp1_55[4], pp1_55[5], pp1_55[6], pp1_55[7], pp2_54_e42_1_c, pp2_55_fa_1_s};
    assign pp2_56 = {pp1_56[0], pp1_56[1], pp1_56[2], pp1_56[3], pp1_56[4], pp1_56[5], pp1_56[6], pp2_55_fa_1_c};
    assign pp2_57 = {pp1_57[0], pp1_57[1], pp1_57[2], pp1_57[3], pp1_57[4], pp1_57[5]};
    assign pp2_58 = {pp1_58[0], pp1_58[1], pp1_58[2], pp1_58[3], pp1_58[4]};
    assign pp2_59 = {pp1_59[0], pp1_59[1], pp1_59[2], pp1_59[3]};
    assign pp2_60 = {pp1_60[0], pp1_60[1], pp1_60[2]};
    assign pp2_61 = {pp1_61[0], pp1_61[1]};
    assign pp2_62 = pp1_62;
    assign pp2_63 = cin_net;
endmodule



module STAGE3_32(
    input pp2_0,
    input [1:0] pp2_1,
    input [2:0] pp2_2,
    input [3:0] pp2_3,
    input [4:0] pp2_4,
    input [5:0] pp2_5,
    input [6:0] pp2_6,
    input [7:0] pp2_7,
    input [7:0] pp2_8,
    input [7:0] pp2_9,
    input [7:0] pp2_10,
    input [7:0] pp2_11,
    input [7:0] pp2_12,
    input [7:0] pp2_13,
    input [7:0] pp2_14,
    input [7:0] pp2_15,
    input [7:0] pp2_16,
    input [7:0] pp2_17,
    input [7:0] pp2_18,
    input [7:0] pp2_19,
    input [7:0] pp2_20,
    input [7:0] pp2_21,
    input [7:0] pp2_22,
    input [7:0] pp2_23,
    input [7:0] pp2_24,
    input [7:0] pp2_25,
    input [7:0] pp2_26,
    input [7:0] pp2_27,
    input [7:0] pp2_28,
    input [7:0] pp2_29,
    input [7:0] pp2_30,
    input [7:0] pp2_31,
    input [7:0] pp2_32,
    input [7:0] pp2_33,
    input [7:0] pp2_34,
    input [7:0] pp2_35,
    input [7:0] pp2_36,
    input [7:0] pp2_37,
    input [7:0] pp2_38,
    input [7:0] pp2_39,
    input [7:0] pp2_40,
    input [7:0] pp2_41,
    input [7:0] pp2_42,
    input [7:0] pp2_43,
    input [7:0] pp2_44,
    input [7:0] pp2_45,
    input [7:0] pp2_46,
    input [7:0] pp2_47,
    input [7:0] pp2_48,
    input [7:0] pp2_49,
    input [7:0] pp2_50,
    input [7:0] pp2_51,
    input [7:0] pp2_52,
    input [7:0] pp2_53,
    input [7:0] pp2_54,
    input [7:0] pp2_55,
    input [7:0] pp2_56,
    input [5:0] pp2_57,
    input [4:0] pp2_58,
    input [3:0] pp2_59,
    input [2:0] pp2_60,
    input [1:0] pp2_61,
    input pp2_62,
    input pp2_63,
    output pp3_0,
    output [1:0] pp3_1,
    output [2:0] pp3_2,
    output [3:0] pp3_3,
    output [3:0] pp3_4,
    output [3:0] pp3_5,
    output [3:0] pp3_6,
    output [3:0] pp3_7,
    output [3:0] pp3_8,
    output [3:0] pp3_9,
    output [3:0] pp3_10,
    output [3:0] pp3_11,
    output [3:0] pp3_12,
    output [3:0] pp3_13,
    output [3:0] pp3_14,
    output [3:0] pp3_15,
    output [3:0] pp3_16,
    output [3:0] pp3_17,
    output [3:0] pp3_18,
    output [3:0] pp3_19,
    output [3:0] pp3_20,
    output [3:0] pp3_21,
    output [3:0] pp3_22,
    output [3:0] pp3_23,
    output [3:0] pp3_24,
    output [3:0] pp3_25,
    output [3:0] pp3_26,
    output [3:0] pp3_27,
    output [3:0] pp3_28,
    output [3:0] pp3_29,
    output [3:0] pp3_30,
    output [3:0] pp3_31,
    output [3:0] pp3_32,
    output [3:0] pp3_33,
    output [3:0] pp3_34,
    output [3:0] pp3_35,
    output [3:0] pp3_36,
    output [3:0] pp3_37,
    output [3:0] pp3_38,
    output [3:0] pp3_39,
    output [3:0] pp3_40,
    output [3:0] pp3_41,
    output [3:0] pp3_42,
    output [3:0] pp3_43,
    output [3:0] pp3_44,
    output [3:0] pp3_45,
    output [3:0] pp3_46,
    output [3:0] pp3_47,
    output [3:0] pp3_48,
    output [3:0] pp3_49,
    output [3:0] pp3_50,
    output [3:0] pp3_51,
    output [3:0] pp3_52,
    output [3:0] pp3_53,
    output [3:0] pp3_54,
    output [3:0] pp3_55,
    output [3:0] pp3_56,
    output [3:0] pp3_57,
    output [3:0] pp3_58,
    output [3:0] pp3_59,
    output [3:0] pp3_60,
    output [1:0] pp3_61,
    output pp3_62,
    output pp3_63
);
wire cin_net;
LOGIC0_X1 u_gnd (.Z(cin_net));
    wire pp3_7_e42_1_s;
    wire pp3_7_e42_1_c;
    wire pp3_7_e42_1_cout;
    wire pp3_7_e42_2_s;
    wire pp3_7_e42_2_c;
    wire pp3_7_e42_2_cout;
    wire pp3_8_e42_1_s;
    wire pp3_8_e42_1_c;
    wire pp3_8_e42_1_cout;
    wire pp3_8_e42_2_s;
    wire pp3_8_e42_2_c;
    wire pp3_8_e42_2_cout;
    wire pp3_9_e42_1_s;
    wire pp3_9_e42_1_c;
    wire pp3_9_e42_1_cout;
    wire pp3_9_e42_2_s;
    wire pp3_9_e42_2_c;
    wire pp3_9_e42_2_cout;
    wire pp3_10_e42_1_s;
    wire pp3_10_e42_1_c;
    wire pp3_10_e42_1_cout;
    wire pp3_10_e42_2_s;
    wire pp3_10_e42_2_c;
    wire pp3_10_e42_2_cout;
    wire pp3_11_e42_1_s;
    wire pp3_11_e42_1_c;
    wire pp3_11_e42_1_cout;
    wire pp3_11_e42_2_s;
    wire pp3_11_e42_2_c;
    wire pp3_11_e42_2_cout;
    wire pp3_12_e42_1_s;
    wire pp3_12_e42_1_c;
    wire pp3_12_e42_1_cout;
    wire pp3_12_e42_2_s;
    wire pp3_12_e42_2_c;
    wire pp3_12_e42_2_cout;
    wire pp3_13_e42_1_s;
    wire pp3_13_e42_1_c;
    wire pp3_13_e42_1_cout;
    wire pp3_13_e42_2_s;
    wire pp3_13_e42_2_c;
    wire pp3_13_e42_2_cout;
    wire pp3_14_e42_1_s;
    wire pp3_14_e42_1_c;
    wire pp3_14_e42_1_cout;
    wire pp3_14_e42_2_s;
    wire pp3_14_e42_2_c;
    wire pp3_14_e42_2_cout;
    wire pp3_15_e42_1_s;
    wire pp3_15_e42_1_c;
    wire pp3_15_e42_1_cout;
    wire pp3_15_e42_2_s;
    wire pp3_15_e42_2_c;
    wire pp3_15_e42_2_cout;
    wire pp3_16_e42_1_s;
    wire pp3_16_e42_1_c;
    wire pp3_16_e42_1_cout;
    wire pp3_16_e42_2_s;
    wire pp3_16_e42_2_c;
    wire pp3_16_e42_2_cout;
    wire pp3_17_e42_1_s;
    wire pp3_17_e42_1_c;
    wire pp3_17_e42_1_cout;
    wire pp3_17_e42_2_s;
    wire pp3_17_e42_2_c;
    wire pp3_17_e42_2_cout;
    wire pp3_18_e42_1_s;
    wire pp3_18_e42_1_c;
    wire pp3_18_e42_1_cout;
    wire pp3_18_e42_2_s;
    wire pp3_18_e42_2_c;
    wire pp3_18_e42_2_cout;
    wire pp3_19_e42_1_s;
    wire pp3_19_e42_1_c;
    wire pp3_19_e42_1_cout;
    wire pp3_19_e42_2_s;
    wire pp3_19_e42_2_c;
    wire pp3_19_e42_2_cout;
    wire pp3_20_e42_1_s;
    wire pp3_20_e42_1_c;
    wire pp3_20_e42_1_cout;
    wire pp3_20_e42_2_s;
    wire pp3_20_e42_2_c;
    wire pp3_20_e42_2_cout;
    wire pp3_21_e42_1_s;
    wire pp3_21_e42_1_c;
    wire pp3_21_e42_1_cout;
    wire pp3_21_e42_2_s;
    wire pp3_21_e42_2_c;
    wire pp3_21_e42_2_cout;
    wire pp3_22_e42_1_s;
    wire pp3_22_e42_1_c;
    wire pp3_22_e42_1_cout;
    wire pp3_22_e42_2_s;
    wire pp3_22_e42_2_c;
    wire pp3_22_e42_2_cout;
    wire pp3_23_e42_1_s;
    wire pp3_23_e42_1_c;
    wire pp3_23_e42_1_cout;
    wire pp3_23_e42_2_s;
    wire pp3_23_e42_2_c;
    wire pp3_23_e42_2_cout;
    wire pp3_24_e42_1_s;
    wire pp3_24_e42_1_c;
    wire pp3_24_e42_1_cout;
    wire pp3_24_e42_2_s;
    wire pp3_24_e42_2_c;
    wire pp3_24_e42_2_cout;
    wire pp3_25_e42_1_s;
    wire pp3_25_e42_1_c;
    wire pp3_25_e42_1_cout;
    wire pp3_25_e42_2_s;
    wire pp3_25_e42_2_c;
    wire pp3_25_e42_2_cout;
    wire pp3_26_e42_1_s;
    wire pp3_26_e42_1_c;
    wire pp3_26_e42_1_cout;
    wire pp3_26_e42_2_s;
    wire pp3_26_e42_2_c;
    wire pp3_26_e42_2_cout;
    wire pp3_27_e42_1_s;
    wire pp3_27_e42_1_c;
    wire pp3_27_e42_1_cout;
    wire pp3_27_e42_2_s;
    wire pp3_27_e42_2_c;
    wire pp3_27_e42_2_cout;
    wire pp3_28_e42_1_s;
    wire pp3_28_e42_1_c;
    wire pp3_28_e42_1_cout;
    wire pp3_28_e42_2_s;
    wire pp3_28_e42_2_c;
    wire pp3_28_e42_2_cout;
    wire pp3_29_e42_1_s;
    wire pp3_29_e42_1_c;
    wire pp3_29_e42_1_cout;
    wire pp3_29_e42_2_s;
    wire pp3_29_e42_2_c;
    wire pp3_29_e42_2_cout;
    wire pp3_30_e42_1_s;
    wire pp3_30_e42_1_c;
    wire pp3_30_e42_1_cout;
    wire pp3_30_e42_2_s;
    wire pp3_30_e42_2_c;
    wire pp3_30_e42_2_cout;
    wire pp3_31_e42_1_s;
    wire pp3_31_e42_1_c;
    wire pp3_31_e42_1_cout;
    wire pp3_31_e42_2_s;
    wire pp3_31_e42_2_c;
    wire pp3_31_e42_2_cout;
    wire pp3_32_e42_1_s;
    wire pp3_32_e42_1_c;
    wire pp3_32_e42_1_cout;
    wire pp3_32_e42_2_s;
    wire pp3_32_e42_2_c;
    wire pp3_32_e42_2_cout;
    wire pp3_33_e42_1_s;
    wire pp3_33_e42_1_c;
    wire pp3_33_e42_1_cout;
    wire pp3_33_e42_2_s;
    wire pp3_33_e42_2_c;
    wire pp3_33_e42_2_cout;
    wire pp3_34_e42_1_s;
    wire pp3_34_e42_1_c;
    wire pp3_34_e42_1_cout;
    wire pp3_34_e42_2_s;
    wire pp3_34_e42_2_c;
    wire pp3_34_e42_2_cout;
    wire pp3_35_e42_1_s;
    wire pp3_35_e42_1_c;
    wire pp3_35_e42_1_cout;
    wire pp3_35_e42_2_s;
    wire pp3_35_e42_2_c;
    wire pp3_35_e42_2_cout;
    wire pp3_36_e42_1_s;
    wire pp3_36_e42_1_c;
    wire pp3_36_e42_1_cout;
    wire pp3_36_e42_2_s;
    wire pp3_36_e42_2_c;
    wire pp3_36_e42_2_cout;
    wire pp3_37_e42_1_s;
    wire pp3_37_e42_1_c;
    wire pp3_37_e42_1_cout;
    wire pp3_37_e42_2_s;
    wire pp3_37_e42_2_c;
    wire pp3_37_e42_2_cout;
    wire pp3_38_e42_1_s;
    wire pp3_38_e42_1_c;
    wire pp3_38_e42_1_cout;
    wire pp3_38_e42_2_s;
    wire pp3_38_e42_2_c;
    wire pp3_38_e42_2_cout;
    wire pp3_39_e42_1_s;
    wire pp3_39_e42_1_c;
    wire pp3_39_e42_1_cout;
    wire pp3_39_e42_2_s;
    wire pp3_39_e42_2_c;
    wire pp3_39_e42_2_cout;
    wire pp3_40_e42_1_s;
    wire pp3_40_e42_1_c;
    wire pp3_40_e42_1_cout;
    wire pp3_40_e42_2_s;
    wire pp3_40_e42_2_c;
    wire pp3_40_e42_2_cout;
    wire pp3_41_e42_1_s;
    wire pp3_41_e42_1_c;
    wire pp3_41_e42_1_cout;
    wire pp3_41_e42_2_s;
    wire pp3_41_e42_2_c;
    wire pp3_41_e42_2_cout;
    wire pp3_42_e42_1_s;
    wire pp3_42_e42_1_c;
    wire pp3_42_e42_1_cout;
    wire pp3_42_e42_2_s;
    wire pp3_42_e42_2_c;
    wire pp3_42_e42_2_cout;
    wire pp3_43_e42_1_s;
    wire pp3_43_e42_1_c;
    wire pp3_43_e42_1_cout;
    wire pp3_43_e42_2_s;
    wire pp3_43_e42_2_c;
    wire pp3_43_e42_2_cout;
    wire pp3_44_e42_1_s;
    wire pp3_44_e42_1_c;
    wire pp3_44_e42_1_cout;
    wire pp3_44_e42_2_s;
    wire pp3_44_e42_2_c;
    wire pp3_44_e42_2_cout;
    wire pp3_45_e42_1_s;
    wire pp3_45_e42_1_c;
    wire pp3_45_e42_1_cout;
    wire pp3_45_e42_2_s;
    wire pp3_45_e42_2_c;
    wire pp3_45_e42_2_cout;
    wire pp3_46_e42_1_s;
    wire pp3_46_e42_1_c;
    wire pp3_46_e42_1_cout;
    wire pp3_46_e42_2_s;
    wire pp3_46_e42_2_c;
    wire pp3_46_e42_2_cout;
    wire pp3_47_e42_1_s;
    wire pp3_47_e42_1_c;
    wire pp3_47_e42_1_cout;
    wire pp3_47_e42_2_s;
    wire pp3_47_e42_2_c;
    wire pp3_47_e42_2_cout;
    wire pp3_48_e42_1_s;
    wire pp3_48_e42_1_c;
    wire pp3_48_e42_1_cout;
    wire pp3_48_e42_2_s;
    wire pp3_48_e42_2_c;
    wire pp3_48_e42_2_cout;
    wire pp3_49_e42_1_s;
    wire pp3_49_e42_1_c;
    wire pp3_49_e42_1_cout;
    wire pp3_49_e42_2_s;
    wire pp3_49_e42_2_c;
    wire pp3_49_e42_2_cout;
    wire pp3_50_e42_1_s;
    wire pp3_50_e42_1_c;
    wire pp3_50_e42_1_cout;
    wire pp3_50_e42_2_s;
    wire pp3_50_e42_2_c;
    wire pp3_50_e42_2_cout;
    wire pp3_51_e42_1_s;
    wire pp3_51_e42_1_c;
    wire pp3_51_e42_1_cout;
    wire pp3_51_e42_2_s;
    wire pp3_51_e42_2_c;
    wire pp3_51_e42_2_cout;
    wire pp3_52_e42_1_s;
    wire pp3_52_e42_1_c;
    wire pp3_52_e42_1_cout;
    wire pp3_52_e42_2_s;
    wire pp3_52_e42_2_c;
    wire pp3_52_e42_2_cout;
    wire pp3_53_e42_1_s;
    wire pp3_53_e42_1_c;
    wire pp3_53_e42_1_cout;
    wire pp3_53_e42_2_s;
    wire pp3_53_e42_2_c;
    wire pp3_53_e42_2_cout;
    wire pp3_54_e42_1_s;
    wire pp3_54_e42_1_c;
    wire pp3_54_e42_1_cout;
    wire pp3_54_e42_2_s;
    wire pp3_54_e42_2_c;
    wire pp3_54_e42_2_cout;
    wire pp3_55_e42_1_s;
    wire pp3_55_e42_1_c;
    wire pp3_55_e42_1_cout;
    wire pp3_55_e42_2_s;
    wire pp3_55_e42_2_c;
    wire pp3_55_e42_2_cout;

// 压缩器模块实例化
    assign pp3_0 = pp2_0;
    assign pp3_1 = {pp2_1[0], pp2_1[1]};
    assign pp3_2 = {pp2_2[0], pp2_2[1], pp2_2[2]};
    assign pp3_3 = {pp2_3[0], pp2_3[1], pp2_3[2], pp2_3[3]};
    Half_adder Half_adder_pp3_4_1(
        .a(pp2_4[0]),
        .b(pp2_4[1]),
        .S(pp3_4_ha_1_s),
        .C(pp3_4_ha_1_c)
    );
    assign pp3_4 = {pp2_4[2], pp2_4[3], pp2_4[4], pp3_4_ha_1_s};
    E_4_2 E_4_2_pp3_5_1(
        .a(pp2_5[0]),
        .b(pp2_5[1]),
        .c(pp2_5[2]),
        .d(pp2_5[3]),
        .CIN(cin_net),
        .S(pp3_5_e42_1_s),
        .C(pp3_5_e42_1_c),
        .COUT(pp3_5_e42_1_cout)
    );
    assign pp3_5 = {pp2_5[4], pp2_5[5], pp3_4_ha_1_c, pp3_5_e42_1_s};
    E_4_2 E_4_2_pp3_6_1(
        .a(pp2_6[0]),
        .b(pp2_6[1]),
        .c(pp2_6[2]),
        .d(pp2_6[3]),
        .CIN(pp3_5_e42_1_cout),
        .S(pp3_6_e42_1_s),
        .C(pp3_6_e42_1_c),
        .COUT(pp3_6_e42_1_cout)
    );
    Half_adder Half_adder_pp3_6_1(
        .a(pp2_6[4]),
        .b(pp2_6[5]),
        .S(pp3_6_ha_1_s),
        .C(pp3_6_ha_1_c)
    );
    assign pp3_6 = {pp2_6[6], pp3_5_e42_1_c, pp3_6_e42_1_s, pp3_6_ha_1_s};
    E_4_2 E_4_2_pp3_7_1(
        .a(pp2_7[0]),
        .b(pp2_7[1]),
        .c(pp2_7[2]),
        .d(pp2_7[3]),
        .CIN(pp3_6_e42_1_cout),
        .S(pp3_7_e42_1_s),
        .C(pp3_7_e42_1_c),
        .COUT(pp3_7_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_7_2(
        .a(pp2_7[4]),
        .b(pp2_7[5]),
        .c(pp2_7[6]),
        .d(pp2_7[7]),
        .CIN(cin_net),
        .S(pp3_7_e42_2_s),
        .C(pp3_7_e42_2_c),
        .COUT(pp3_7_e42_2_cout)
    );
    assign pp3_7 = {pp3_6_e42_1_c, pp3_6_ha_1_c, pp3_7_e42_1_s, pp3_7_e42_2_s};
    E_4_2 E_4_2_pp3_8_1(
        .a(pp2_8[0]),
        .b(pp2_8[1]),
        .c(pp2_8[2]),
        .d(pp2_8[3]),
        .CIN(pp3_7_e42_1_cout),
        .S(pp3_8_e42_1_s),
        .C(pp3_8_e42_1_c),
        .COUT(pp3_8_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_8_2(
        .a(pp2_8[4]),
        .b(pp2_8[5]),
        .c(pp2_8[6]),
        .d(pp2_8[7]),
        .CIN(pp3_7_e42_2_cout),
        .S(pp3_8_e42_2_s),
        .C(pp3_8_e42_2_c),
        .COUT(pp3_8_e42_2_cout)
    );
    assign pp3_8 = {pp3_7_e42_1_c, pp3_7_e42_2_c, pp3_8_e42_1_s, pp3_8_e42_2_s};
    E_4_2 E_4_2_pp3_9_1(
        .a(pp2_9[0]),
        .b(pp2_9[1]),
        .c(pp2_9[2]),
        .d(pp2_9[3]),
        .CIN(pp3_8_e42_1_cout),
        .S(pp3_9_e42_1_s),
        .C(pp3_9_e42_1_c),
        .COUT(pp3_9_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_9_2(
        .a(pp2_9[4]),
        .b(pp2_9[5]),
        .c(pp2_9[6]),
        .d(pp2_9[7]),
        .CIN(pp3_8_e42_2_cout),
        .S(pp3_9_e42_2_s),
        .C(pp3_9_e42_2_c),
        .COUT(pp3_9_e42_2_cout)
    );
    assign pp3_9 = {pp3_8_e42_1_c, pp3_8_e42_2_c, pp3_9_e42_1_s, pp3_9_e42_2_s};
    E_4_2 E_4_2_pp3_10_1(
        .a(pp2_10[0]),
        .b(pp2_10[1]),
        .c(pp2_10[2]),
        .d(pp2_10[3]),
        .CIN(pp3_9_e42_1_cout),
        .S(pp3_10_e42_1_s),
        .C(pp3_10_e42_1_c),
        .COUT(pp3_10_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_10_2(
        .a(pp2_10[4]),
        .b(pp2_10[5]),
        .c(pp2_10[6]),
        .d(pp2_10[7]),
        .CIN(pp3_9_e42_2_cout),
        .S(pp3_10_e42_2_s),
        .C(pp3_10_e42_2_c),
        .COUT(pp3_10_e42_2_cout)
    );
    assign pp3_10 = {pp3_9_e42_1_c, pp3_9_e42_2_c, pp3_10_e42_1_s, pp3_10_e42_2_s};
    E_4_2 E_4_2_pp3_11_1(
        .a(pp2_11[0]),
        .b(pp2_11[1]),
        .c(pp2_11[2]),
        .d(pp2_11[3]),
        .CIN(pp3_10_e42_1_cout),
        .S(pp3_11_e42_1_s),
        .C(pp3_11_e42_1_c),
        .COUT(pp3_11_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_11_2(
        .a(pp2_11[4]),
        .b(pp2_11[5]),
        .c(pp2_11[6]),
        .d(pp2_11[7]),
        .CIN(pp3_10_e42_2_cout),
        .S(pp3_11_e42_2_s),
        .C(pp3_11_e42_2_c),
        .COUT(pp3_11_e42_2_cout)
    );
    assign pp3_11 = {pp3_10_e42_1_c, pp3_10_e42_2_c, pp3_11_e42_1_s, pp3_11_e42_2_s};
    E_4_2 E_4_2_pp3_12_1(
        .a(pp2_12[0]),
        .b(pp2_12[1]),
        .c(pp2_12[2]),
        .d(pp2_12[3]),
        .CIN(pp3_11_e42_1_cout),
        .S(pp3_12_e42_1_s),
        .C(pp3_12_e42_1_c),
        .COUT(pp3_12_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_12_2(
        .a(pp2_12[4]),
        .b(pp2_12[5]),
        .c(pp2_12[6]),
        .d(pp2_12[7]),
        .CIN(pp3_11_e42_2_cout),
        .S(pp3_12_e42_2_s),
        .C(pp3_12_e42_2_c),
        .COUT(pp3_12_e42_2_cout)
    );
    assign pp3_12 = {pp3_11_e42_1_c, pp3_11_e42_2_c, pp3_12_e42_1_s, pp3_12_e42_2_s};
    E_4_2 E_4_2_pp3_13_1(
        .a(pp2_13[0]),
        .b(pp2_13[1]),
        .c(pp2_13[2]),
        .d(pp2_13[3]),
        .CIN(pp3_12_e42_1_cout),
        .S(pp3_13_e42_1_s),
        .C(pp3_13_e42_1_c),
        .COUT(pp3_13_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_13_2(
        .a(pp2_13[4]),
        .b(pp2_13[5]),
        .c(pp2_13[6]),
        .d(pp2_13[7]),
        .CIN(pp3_12_e42_2_cout),
        .S(pp3_13_e42_2_s),
        .C(pp3_13_e42_2_c),
        .COUT(pp3_13_e42_2_cout)
    );
    assign pp3_13 = {pp3_12_e42_1_c, pp3_12_e42_2_c, pp3_13_e42_1_s, pp3_13_e42_2_s};
    E_4_2 E_4_2_pp3_14_1(
        .a(pp2_14[0]),
        .b(pp2_14[1]),
        .c(pp2_14[2]),
        .d(pp2_14[3]),
        .CIN(pp3_13_e42_1_cout),
        .S(pp3_14_e42_1_s),
        .C(pp3_14_e42_1_c),
        .COUT(pp3_14_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_14_2(
        .a(pp2_14[4]),
        .b(pp2_14[5]),
        .c(pp2_14[6]),
        .d(pp2_14[7]),
        .CIN(pp3_13_e42_2_cout),
        .S(pp3_14_e42_2_s),
        .C(pp3_14_e42_2_c),
        .COUT(pp3_14_e42_2_cout)
    );
    assign pp3_14 = {pp3_13_e42_1_c, pp3_13_e42_2_c, pp3_14_e42_1_s, pp3_14_e42_2_s};
    E_4_2 E_4_2_pp3_15_1(
        .a(pp2_15[0]),
        .b(pp2_15[1]),
        .c(pp2_15[2]),
        .d(pp2_15[3]),
        .CIN(pp3_14_e42_1_cout),
        .S(pp3_15_e42_1_s),
        .C(pp3_15_e42_1_c),
        .COUT(pp3_15_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_15_2(
        .a(pp2_15[4]),
        .b(pp2_15[5]),
        .c(pp2_15[6]),
        .d(pp2_15[7]),
        .CIN(pp3_14_e42_2_cout),
        .S(pp3_15_e42_2_s),
        .C(pp3_15_e42_2_c),
        .COUT(pp3_15_e42_2_cout)
    );
    assign pp3_15 = {pp3_14_e42_1_c, pp3_14_e42_2_c, pp3_15_e42_1_s, pp3_15_e42_2_s};
    E_4_2 E_4_2_pp3_16_1(
        .a(pp2_16[0]),
        .b(pp2_16[1]),
        .c(pp2_16[2]),
        .d(pp2_16[3]),
        .CIN(pp3_15_e42_1_cout),
        .S(pp3_16_e42_1_s),
        .C(pp3_16_e42_1_c),
        .COUT(pp3_16_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_16_2(
        .a(pp2_16[4]),
        .b(pp2_16[5]),
        .c(pp2_16[6]),
        .d(pp2_16[7]),
        .CIN(pp3_15_e42_2_cout),
        .S(pp3_16_e42_2_s),
        .C(pp3_16_e42_2_c),
        .COUT(pp3_16_e42_2_cout)
    );
    assign pp3_16 = {pp3_15_e42_1_c, pp3_15_e42_2_c, pp3_16_e42_1_s, pp3_16_e42_2_s};
    E_4_2 E_4_2_pp3_17_1(
        .a(pp2_17[0]),
        .b(pp2_17[1]),
        .c(pp2_17[2]),
        .d(pp2_17[3]),
        .CIN(pp3_16_e42_1_cout),
        .S(pp3_17_e42_1_s),
        .C(pp3_17_e42_1_c),
        .COUT(pp3_17_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_17_2(
        .a(pp2_17[4]),
        .b(pp2_17[5]),
        .c(pp2_17[6]),
        .d(pp2_17[7]),
        .CIN(pp3_16_e42_2_cout),
        .S(pp3_17_e42_2_s),
        .C(pp3_17_e42_2_c),
        .COUT(pp3_17_e42_2_cout)
    );
    assign pp3_17 = {pp3_16_e42_1_c, pp3_16_e42_2_c, pp3_17_e42_1_s, pp3_17_e42_2_s};
    E_4_2 E_4_2_pp3_18_1(
        .a(pp2_18[0]),
        .b(pp2_18[1]),
        .c(pp2_18[2]),
        .d(pp2_18[3]),
        .CIN(pp3_17_e42_1_cout),
        .S(pp3_18_e42_1_s),
        .C(pp3_18_e42_1_c),
        .COUT(pp3_18_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_18_2(
        .a(pp2_18[4]),
        .b(pp2_18[5]),
        .c(pp2_18[6]),
        .d(pp2_18[7]),
        .CIN(pp3_17_e42_2_cout),
        .S(pp3_18_e42_2_s),
        .C(pp3_18_e42_2_c),
        .COUT(pp3_18_e42_2_cout)
    );
    assign pp3_18 = {pp3_17_e42_1_c, pp3_17_e42_2_c, pp3_18_e42_1_s, pp3_18_e42_2_s};
    E_4_2 E_4_2_pp3_19_1(
        .a(pp2_19[0]),
        .b(pp2_19[1]),
        .c(pp2_19[2]),
        .d(pp2_19[3]),
        .CIN(pp3_18_e42_1_cout),
        .S(pp3_19_e42_1_s),
        .C(pp3_19_e42_1_c),
        .COUT(pp3_19_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_19_2(
        .a(pp2_19[4]),
        .b(pp2_19[5]),
        .c(pp2_19[6]),
        .d(pp2_19[7]),
        .CIN(pp3_18_e42_2_cout),
        .S(pp3_19_e42_2_s),
        .C(pp3_19_e42_2_c),
        .COUT(pp3_19_e42_2_cout)
    );
    assign pp3_19 = {pp3_18_e42_1_c, pp3_18_e42_2_c, pp3_19_e42_1_s, pp3_19_e42_2_s};
    E_4_2 E_4_2_pp3_20_1(
        .a(pp2_20[0]),
        .b(pp2_20[1]),
        .c(pp2_20[2]),
        .d(pp2_20[3]),
        .CIN(pp3_19_e42_1_cout),
        .S(pp3_20_e42_1_s),
        .C(pp3_20_e42_1_c),
        .COUT(pp3_20_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_20_2(
        .a(pp2_20[4]),
        .b(pp2_20[5]),
        .c(pp2_20[6]),
        .d(pp2_20[7]),
        .CIN(pp3_19_e42_2_cout),
        .S(pp3_20_e42_2_s),
        .C(pp3_20_e42_2_c),
        .COUT(pp3_20_e42_2_cout)
    );
    assign pp3_20 = {pp3_19_e42_1_c, pp3_19_e42_2_c, pp3_20_e42_1_s, pp3_20_e42_2_s};
    E_4_2 E_4_2_pp3_21_1(
        .a(pp2_21[0]),
        .b(pp2_21[1]),
        .c(pp2_21[2]),
        .d(pp2_21[3]),
        .CIN(pp3_20_e42_1_cout),
        .S(pp3_21_e42_1_s),
        .C(pp3_21_e42_1_c),
        .COUT(pp3_21_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_21_2(
        .a(pp2_21[4]),
        .b(pp2_21[5]),
        .c(pp2_21[6]),
        .d(pp2_21[7]),
        .CIN(pp3_20_e42_2_cout),
        .S(pp3_21_e42_2_s),
        .C(pp3_21_e42_2_c),
        .COUT(pp3_21_e42_2_cout)
    );
    assign pp3_21 = {pp3_20_e42_1_c, pp3_20_e42_2_c, pp3_21_e42_1_s, pp3_21_e42_2_s};
    E_4_2 E_4_2_pp3_22_1(
        .a(pp2_22[0]),
        .b(pp2_22[1]),
        .c(pp2_22[2]),
        .d(pp2_22[3]),
        .CIN(pp3_21_e42_1_cout),
        .S(pp3_22_e42_1_s),
        .C(pp3_22_e42_1_c),
        .COUT(pp3_22_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_22_2(
        .a(pp2_22[4]),
        .b(pp2_22[5]),
        .c(pp2_22[6]),
        .d(pp2_22[7]),
        .CIN(pp3_21_e42_2_cout),
        .S(pp3_22_e42_2_s),
        .C(pp3_22_e42_2_c),
        .COUT(pp3_22_e42_2_cout)
    );
    assign pp3_22 = {pp3_21_e42_1_c, pp3_21_e42_2_c, pp3_22_e42_1_s, pp3_22_e42_2_s};
    E_4_2 E_4_2_pp3_23_1(
        .a(pp2_23[0]),
        .b(pp2_23[1]),
        .c(pp2_23[2]),
        .d(pp2_23[3]),
        .CIN(pp3_22_e42_1_cout),
        .S(pp3_23_e42_1_s),
        .C(pp3_23_e42_1_c),
        .COUT(pp3_23_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_23_2(
        .a(pp2_23[4]),
        .b(pp2_23[5]),
        .c(pp2_23[6]),
        .d(pp2_23[7]),
        .CIN(pp3_22_e42_2_cout),
        .S(pp3_23_e42_2_s),
        .C(pp3_23_e42_2_c),
        .COUT(pp3_23_e42_2_cout)
    );
    assign pp3_23 = {pp3_22_e42_1_c, pp3_22_e42_2_c, pp3_23_e42_1_s, pp3_23_e42_2_s};
    E_4_2 E_4_2_pp3_24_1(
        .a(pp2_24[0]),
        .b(pp2_24[1]),
        .c(pp2_24[2]),
        .d(pp2_24[3]),
        .CIN(pp3_23_e42_1_cout),
        .S(pp3_24_e42_1_s),
        .C(pp3_24_e42_1_c),
        .COUT(pp3_24_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_24_2(
        .a(pp2_24[4]),
        .b(pp2_24[5]),
        .c(pp2_24[6]),
        .d(pp2_24[7]),
        .CIN(pp3_23_e42_2_cout),
        .S(pp3_24_e42_2_s),
        .C(pp3_24_e42_2_c),
        .COUT(pp3_24_e42_2_cout)
    );
    assign pp3_24 = {pp3_23_e42_1_c, pp3_23_e42_2_c, pp3_24_e42_1_s, pp3_24_e42_2_s};
    E_4_2 E_4_2_pp3_25_1(
        .a(pp2_25[0]),
        .b(pp2_25[1]),
        .c(pp2_25[2]),
        .d(pp2_25[3]),
        .CIN(pp3_24_e42_1_cout),
        .S(pp3_25_e42_1_s),
        .C(pp3_25_e42_1_c),
        .COUT(pp3_25_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_25_2(
        .a(pp2_25[4]),
        .b(pp2_25[5]),
        .c(pp2_25[6]),
        .d(pp2_25[7]),
        .CIN(pp3_24_e42_2_cout),
        .S(pp3_25_e42_2_s),
        .C(pp3_25_e42_2_c),
        .COUT(pp3_25_e42_2_cout)
    );
    assign pp3_25 = {pp3_24_e42_1_c, pp3_24_e42_2_c, pp3_25_e42_1_s, pp3_25_e42_2_s};
    E_4_2 E_4_2_pp3_26_1(
        .a(pp2_26[0]),
        .b(pp2_26[1]),
        .c(pp2_26[2]),
        .d(pp2_26[3]),
        .CIN(pp3_25_e42_1_cout),
        .S(pp3_26_e42_1_s),
        .C(pp3_26_e42_1_c),
        .COUT(pp3_26_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_26_2(
        .a(pp2_26[4]),
        .b(pp2_26[5]),
        .c(pp2_26[6]),
        .d(pp2_26[7]),
        .CIN(pp3_25_e42_2_cout),
        .S(pp3_26_e42_2_s),
        .C(pp3_26_e42_2_c),
        .COUT(pp3_26_e42_2_cout)
    );
    assign pp3_26 = {pp3_25_e42_1_c, pp3_25_e42_2_c, pp3_26_e42_1_s, pp3_26_e42_2_s};
    E_4_2 E_4_2_pp3_27_1(
        .a(pp2_27[0]),
        .b(pp2_27[1]),
        .c(pp2_27[2]),
        .d(pp2_27[3]),
        .CIN(pp3_26_e42_1_cout),
        .S(pp3_27_e42_1_s),
        .C(pp3_27_e42_1_c),
        .COUT(pp3_27_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_27_2(
        .a(pp2_27[4]),
        .b(pp2_27[5]),
        .c(pp2_27[6]),
        .d(pp2_27[7]),
        .CIN(pp3_26_e42_2_cout),
        .S(pp3_27_e42_2_s),
        .C(pp3_27_e42_2_c),
        .COUT(pp3_27_e42_2_cout)
    );
    assign pp3_27 = {pp3_26_e42_1_c, pp3_26_e42_2_c, pp3_27_e42_1_s, pp3_27_e42_2_s};
    E_4_2 E_4_2_pp3_28_1(
        .a(pp2_28[0]),
        .b(pp2_28[1]),
        .c(pp2_28[2]),
        .d(pp2_28[3]),
        .CIN(pp3_27_e42_1_cout),
        .S(pp3_28_e42_1_s),
        .C(pp3_28_e42_1_c),
        .COUT(pp3_28_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_28_2(
        .a(pp2_28[4]),
        .b(pp2_28[5]),
        .c(pp2_28[6]),
        .d(pp2_28[7]),
        .CIN(pp3_27_e42_2_cout),
        .S(pp3_28_e42_2_s),
        .C(pp3_28_e42_2_c),
        .COUT(pp3_28_e42_2_cout)
    );
    assign pp3_28 = {pp3_27_e42_1_c, pp3_27_e42_2_c, pp3_28_e42_1_s, pp3_28_e42_2_s};
    E_4_2 E_4_2_pp3_29_1(
        .a(pp2_29[0]),
        .b(pp2_29[1]),
        .c(pp2_29[2]),
        .d(pp2_29[3]),
        .CIN(pp3_28_e42_1_cout),
        .S(pp3_29_e42_1_s),
        .C(pp3_29_e42_1_c),
        .COUT(pp3_29_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_29_2(
        .a(pp2_29[4]),
        .b(pp2_29[5]),
        .c(pp2_29[6]),
        .d(pp2_29[7]),
        .CIN(pp3_28_e42_2_cout),
        .S(pp3_29_e42_2_s),
        .C(pp3_29_e42_2_c),
        .COUT(pp3_29_e42_2_cout)
    );
    assign pp3_29 = {pp3_28_e42_1_c, pp3_28_e42_2_c, pp3_29_e42_1_s, pp3_29_e42_2_s};
    E_4_2 E_4_2_pp3_30_1(
        .a(pp2_30[0]),
        .b(pp2_30[1]),
        .c(pp2_30[2]),
        .d(pp2_30[3]),
        .CIN(pp3_29_e42_1_cout),
        .S(pp3_30_e42_1_s),
        .C(pp3_30_e42_1_c),
        .COUT(pp3_30_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_30_2(
        .a(pp2_30[4]),
        .b(pp2_30[5]),
        .c(pp2_30[6]),
        .d(pp2_30[7]),
        .CIN(pp3_29_e42_2_cout),
        .S(pp3_30_e42_2_s),
        .C(pp3_30_e42_2_c),
        .COUT(pp3_30_e42_2_cout)
    );
    assign pp3_30 = {pp3_29_e42_1_c, pp3_29_e42_2_c, pp3_30_e42_1_s, pp3_30_e42_2_s};
    E_4_2 E_4_2_pp3_31_1(
        .a(pp2_31[0]),
        .b(pp2_31[1]),
        .c(pp2_31[2]),
        .d(pp2_31[3]),
        .CIN(pp3_30_e42_1_cout),
        .S(pp3_31_e42_1_s),
        .C(pp3_31_e42_1_c),
        .COUT(pp3_31_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_31_2(
        .a(pp2_31[4]),
        .b(pp2_31[5]),
        .c(pp2_31[6]),
        .d(pp2_31[7]),
        .CIN(pp3_30_e42_2_cout),
        .S(pp3_31_e42_2_s),
        .C(pp3_31_e42_2_c),
        .COUT(pp3_31_e42_2_cout)
    );
    assign pp3_31 = {pp3_30_e42_1_c, pp3_30_e42_2_c, pp3_31_e42_1_s, pp3_31_e42_2_s};
    E_4_2 E_4_2_pp3_32_1(
        .a(pp2_32[0]),
        .b(pp2_32[1]),
        .c(pp2_32[2]),
        .d(pp2_32[3]),
        .CIN(pp3_31_e42_1_cout),
        .S(pp3_32_e42_1_s),
        .C(pp3_32_e42_1_c),
        .COUT(pp3_32_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_32_2(
        .a(pp2_32[4]),
        .b(pp2_32[5]),
        .c(pp2_32[6]),
        .d(pp2_32[7]),
        .CIN(pp3_31_e42_2_cout),
        .S(pp3_32_e42_2_s),
        .C(pp3_32_e42_2_c),
        .COUT(pp3_32_e42_2_cout)
    );
    assign pp3_32 = {pp3_31_e42_1_c, pp3_31_e42_2_c, pp3_32_e42_1_s, pp3_32_e42_2_s};
    E_4_2 E_4_2_pp3_33_1(
        .a(pp2_33[0]),
        .b(pp2_33[1]),
        .c(pp2_33[2]),
        .d(pp2_33[3]),
        .CIN(pp3_32_e42_1_cout),
        .S(pp3_33_e42_1_s),
        .C(pp3_33_e42_1_c),
        .COUT(pp3_33_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_33_2(
        .a(pp2_33[4]),
        .b(pp2_33[5]),
        .c(pp2_33[6]),
        .d(pp2_33[7]),
        .CIN(pp3_32_e42_2_cout),
        .S(pp3_33_e42_2_s),
        .C(pp3_33_e42_2_c),
        .COUT(pp3_33_e42_2_cout)
    );
    assign pp3_33 = {pp3_32_e42_1_c, pp3_32_e42_2_c, pp3_33_e42_1_s, pp3_33_e42_2_s};
    E_4_2 E_4_2_pp3_34_1(
        .a(pp2_34[0]),
        .b(pp2_34[1]),
        .c(pp2_34[2]),
        .d(pp2_34[3]),
        .CIN(pp3_33_e42_1_cout),
        .S(pp3_34_e42_1_s),
        .C(pp3_34_e42_1_c),
        .COUT(pp3_34_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_34_2(
        .a(pp2_34[4]),
        .b(pp2_34[5]),
        .c(pp2_34[6]),
        .d(pp2_34[7]),
        .CIN(pp3_33_e42_2_cout),
        .S(pp3_34_e42_2_s),
        .C(pp3_34_e42_2_c),
        .COUT(pp3_34_e42_2_cout)
    );
    assign pp3_34 = {pp3_33_e42_1_c, pp3_33_e42_2_c, pp3_34_e42_1_s, pp3_34_e42_2_s};
    E_4_2 E_4_2_pp3_35_1(
        .a(pp2_35[0]),
        .b(pp2_35[1]),
        .c(pp2_35[2]),
        .d(pp2_35[3]),
        .CIN(pp3_34_e42_1_cout),
        .S(pp3_35_e42_1_s),
        .C(pp3_35_e42_1_c),
        .COUT(pp3_35_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_35_2(
        .a(pp2_35[4]),
        .b(pp2_35[5]),
        .c(pp2_35[6]),
        .d(pp2_35[7]),
        .CIN(pp3_34_e42_2_cout),
        .S(pp3_35_e42_2_s),
        .C(pp3_35_e42_2_c),
        .COUT(pp3_35_e42_2_cout)
    );
    assign pp3_35 = {pp3_34_e42_1_c, pp3_34_e42_2_c, pp3_35_e42_1_s, pp3_35_e42_2_s};
    E_4_2 E_4_2_pp3_36_1(
        .a(pp2_36[0]),
        .b(pp2_36[1]),
        .c(pp2_36[2]),
        .d(pp2_36[3]),
        .CIN(pp3_35_e42_1_cout),
        .S(pp3_36_e42_1_s),
        .C(pp3_36_e42_1_c),
        .COUT(pp3_36_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_36_2(
        .a(pp2_36[4]),
        .b(pp2_36[5]),
        .c(pp2_36[6]),
        .d(pp2_36[7]),
        .CIN(pp3_35_e42_2_cout),
        .S(pp3_36_e42_2_s),
        .C(pp3_36_e42_2_c),
        .COUT(pp3_36_e42_2_cout)
    );
    assign pp3_36 = {pp3_35_e42_1_c, pp3_35_e42_2_c, pp3_36_e42_1_s, pp3_36_e42_2_s};
    E_4_2 E_4_2_pp3_37_1(
        .a(pp2_37[0]),
        .b(pp2_37[1]),
        .c(pp2_37[2]),
        .d(pp2_37[3]),
        .CIN(pp3_36_e42_1_cout),
        .S(pp3_37_e42_1_s),
        .C(pp3_37_e42_1_c),
        .COUT(pp3_37_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_37_2(
        .a(pp2_37[4]),
        .b(pp2_37[5]),
        .c(pp2_37[6]),
        .d(pp2_37[7]),
        .CIN(pp3_36_e42_2_cout),
        .S(pp3_37_e42_2_s),
        .C(pp3_37_e42_2_c),
        .COUT(pp3_37_e42_2_cout)
    );
    assign pp3_37 = {pp3_36_e42_1_c, pp3_36_e42_2_c, pp3_37_e42_1_s, pp3_37_e42_2_s};
    E_4_2 E_4_2_pp3_38_1(
        .a(pp2_38[0]),
        .b(pp2_38[1]),
        .c(pp2_38[2]),
        .d(pp2_38[3]),
        .CIN(pp3_37_e42_1_cout),
        .S(pp3_38_e42_1_s),
        .C(pp3_38_e42_1_c),
        .COUT(pp3_38_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_38_2(
        .a(pp2_38[4]),
        .b(pp2_38[5]),
        .c(pp2_38[6]),
        .d(pp2_38[7]),
        .CIN(pp3_37_e42_2_cout),
        .S(pp3_38_e42_2_s),
        .C(pp3_38_e42_2_c),
        .COUT(pp3_38_e42_2_cout)
    );
    assign pp3_38 = {pp3_37_e42_1_c, pp3_37_e42_2_c, pp3_38_e42_1_s, pp3_38_e42_2_s};
    E_4_2 E_4_2_pp3_39_1(
        .a(pp2_39[0]),
        .b(pp2_39[1]),
        .c(pp2_39[2]),
        .d(pp2_39[3]),
        .CIN(pp3_38_e42_1_cout),
        .S(pp3_39_e42_1_s),
        .C(pp3_39_e42_1_c),
        .COUT(pp3_39_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_39_2(
        .a(pp2_39[4]),
        .b(pp2_39[5]),
        .c(pp2_39[6]),
        .d(pp2_39[7]),
        .CIN(pp3_38_e42_2_cout),
        .S(pp3_39_e42_2_s),
        .C(pp3_39_e42_2_c),
        .COUT(pp3_39_e42_2_cout)
    );
    assign pp3_39 = {pp3_38_e42_1_c, pp3_38_e42_2_c, pp3_39_e42_1_s, pp3_39_e42_2_s};
    E_4_2 E_4_2_pp3_40_1(
        .a(pp2_40[0]),
        .b(pp2_40[1]),
        .c(pp2_40[2]),
        .d(pp2_40[3]),
        .CIN(pp3_39_e42_1_cout),
        .S(pp3_40_e42_1_s),
        .C(pp3_40_e42_1_c),
        .COUT(pp3_40_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_40_2(
        .a(pp2_40[4]),
        .b(pp2_40[5]),
        .c(pp2_40[6]),
        .d(pp2_40[7]),
        .CIN(pp3_39_e42_2_cout),
        .S(pp3_40_e42_2_s),
        .C(pp3_40_e42_2_c),
        .COUT(pp3_40_e42_2_cout)
    );
    assign pp3_40 = {pp3_39_e42_1_c, pp3_39_e42_2_c, pp3_40_e42_1_s, pp3_40_e42_2_s};
    E_4_2 E_4_2_pp3_41_1(
        .a(pp2_41[0]),
        .b(pp2_41[1]),
        .c(pp2_41[2]),
        .d(pp2_41[3]),
        .CIN(pp3_40_e42_1_cout),
        .S(pp3_41_e42_1_s),
        .C(pp3_41_e42_1_c),
        .COUT(pp3_41_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_41_2(
        .a(pp2_41[4]),
        .b(pp2_41[5]),
        .c(pp2_41[6]),
        .d(pp2_41[7]),
        .CIN(pp3_40_e42_2_cout),
        .S(pp3_41_e42_2_s),
        .C(pp3_41_e42_2_c),
        .COUT(pp3_41_e42_2_cout)
    );
    assign pp3_41 = {pp3_40_e42_1_c, pp3_40_e42_2_c, pp3_41_e42_1_s, pp3_41_e42_2_s};
    E_4_2 E_4_2_pp3_42_1(
        .a(pp2_42[0]),
        .b(pp2_42[1]),
        .c(pp2_42[2]),
        .d(pp2_42[3]),
        .CIN(pp3_41_e42_1_cout),
        .S(pp3_42_e42_1_s),
        .C(pp3_42_e42_1_c),
        .COUT(pp3_42_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_42_2(
        .a(pp2_42[4]),
        .b(pp2_42[5]),
        .c(pp2_42[6]),
        .d(pp2_42[7]),
        .CIN(pp3_41_e42_2_cout),
        .S(pp3_42_e42_2_s),
        .C(pp3_42_e42_2_c),
        .COUT(pp3_42_e42_2_cout)
    );
    assign pp3_42 = {pp3_41_e42_1_c, pp3_41_e42_2_c, pp3_42_e42_1_s, pp3_42_e42_2_s};
    E_4_2 E_4_2_pp3_43_1(
        .a(pp2_43[0]),
        .b(pp2_43[1]),
        .c(pp2_43[2]),
        .d(pp2_43[3]),
        .CIN(pp3_42_e42_1_cout),
        .S(pp3_43_e42_1_s),
        .C(pp3_43_e42_1_c),
        .COUT(pp3_43_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_43_2(
        .a(pp2_43[4]),
        .b(pp2_43[5]),
        .c(pp2_43[6]),
        .d(pp2_43[7]),
        .CIN(pp3_42_e42_2_cout),
        .S(pp3_43_e42_2_s),
        .C(pp3_43_e42_2_c),
        .COUT(pp3_43_e42_2_cout)
    );
    assign pp3_43 = {pp3_42_e42_1_c, pp3_42_e42_2_c, pp3_43_e42_1_s, pp3_43_e42_2_s};
    E_4_2 E_4_2_pp3_44_1(
        .a(pp2_44[0]),
        .b(pp2_44[1]),
        .c(pp2_44[2]),
        .d(pp2_44[3]),
        .CIN(pp3_43_e42_1_cout),
        .S(pp3_44_e42_1_s),
        .C(pp3_44_e42_1_c),
        .COUT(pp3_44_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_44_2(
        .a(pp2_44[4]),
        .b(pp2_44[5]),
        .c(pp2_44[6]),
        .d(pp2_44[7]),
        .CIN(pp3_43_e42_2_cout),
        .S(pp3_44_e42_2_s),
        .C(pp3_44_e42_2_c),
        .COUT(pp3_44_e42_2_cout)
    );
    assign pp3_44 = {pp3_43_e42_1_c, pp3_43_e42_2_c, pp3_44_e42_1_s, pp3_44_e42_2_s};
    E_4_2 E_4_2_pp3_45_1(
        .a(pp2_45[0]),
        .b(pp2_45[1]),
        .c(pp2_45[2]),
        .d(pp2_45[3]),
        .CIN(pp3_44_e42_1_cout),
        .S(pp3_45_e42_1_s),
        .C(pp3_45_e42_1_c),
        .COUT(pp3_45_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_45_2(
        .a(pp2_45[4]),
        .b(pp2_45[5]),
        .c(pp2_45[6]),
        .d(pp2_45[7]),
        .CIN(pp3_44_e42_2_cout),
        .S(pp3_45_e42_2_s),
        .C(pp3_45_e42_2_c),
        .COUT(pp3_45_e42_2_cout)
    );
    assign pp3_45 = {pp3_44_e42_1_c, pp3_44_e42_2_c, pp3_45_e42_1_s, pp3_45_e42_2_s};
    E_4_2 E_4_2_pp3_46_1(
        .a(pp2_46[0]),
        .b(pp2_46[1]),
        .c(pp2_46[2]),
        .d(pp2_46[3]),
        .CIN(pp3_45_e42_1_cout),
        .S(pp3_46_e42_1_s),
        .C(pp3_46_e42_1_c),
        .COUT(pp3_46_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_46_2(
        .a(pp2_46[4]),
        .b(pp2_46[5]),
        .c(pp2_46[6]),
        .d(pp2_46[7]),
        .CIN(pp3_45_e42_2_cout),
        .S(pp3_46_e42_2_s),
        .C(pp3_46_e42_2_c),
        .COUT(pp3_46_e42_2_cout)
    );
    assign pp3_46 = {pp3_45_e42_1_c, pp3_45_e42_2_c, pp3_46_e42_1_s, pp3_46_e42_2_s};
    E_4_2 E_4_2_pp3_47_1(
        .a(pp2_47[0]),
        .b(pp2_47[1]),
        .c(pp2_47[2]),
        .d(pp2_47[3]),
        .CIN(pp3_46_e42_1_cout),
        .S(pp3_47_e42_1_s),
        .C(pp3_47_e42_1_c),
        .COUT(pp3_47_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_47_2(
        .a(pp2_47[4]),
        .b(pp2_47[5]),
        .c(pp2_47[6]),
        .d(pp2_47[7]),
        .CIN(pp3_46_e42_2_cout),
        .S(pp3_47_e42_2_s),
        .C(pp3_47_e42_2_c),
        .COUT(pp3_47_e42_2_cout)
    );
    assign pp3_47 = {pp3_46_e42_1_c, pp3_46_e42_2_c, pp3_47_e42_1_s, pp3_47_e42_2_s};
    E_4_2 E_4_2_pp3_48_1(
        .a(pp2_48[0]),
        .b(pp2_48[1]),
        .c(pp2_48[2]),
        .d(pp2_48[3]),
        .CIN(pp3_47_e42_1_cout),
        .S(pp3_48_e42_1_s),
        .C(pp3_48_e42_1_c),
        .COUT(pp3_48_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_48_2(
        .a(pp2_48[4]),
        .b(pp2_48[5]),
        .c(pp2_48[6]),
        .d(pp2_48[7]),
        .CIN(pp3_47_e42_2_cout),
        .S(pp3_48_e42_2_s),
        .C(pp3_48_e42_2_c),
        .COUT(pp3_48_e42_2_cout)
    );
    assign pp3_48 = {pp3_47_e42_1_c, pp3_47_e42_2_c, pp3_48_e42_1_s, pp3_48_e42_2_s};
    E_4_2 E_4_2_pp3_49_1(
        .a(pp2_49[0]),
        .b(pp2_49[1]),
        .c(pp2_49[2]),
        .d(pp2_49[3]),
        .CIN(pp3_48_e42_1_cout),
        .S(pp3_49_e42_1_s),
        .C(pp3_49_e42_1_c),
        .COUT(pp3_49_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_49_2(
        .a(pp2_49[4]),
        .b(pp2_49[5]),
        .c(pp2_49[6]),
        .d(pp2_49[7]),
        .CIN(pp3_48_e42_2_cout),
        .S(pp3_49_e42_2_s),
        .C(pp3_49_e42_2_c),
        .COUT(pp3_49_e42_2_cout)
    );
    assign pp3_49 = {pp3_48_e42_1_c, pp3_48_e42_2_c, pp3_49_e42_1_s, pp3_49_e42_2_s};
    E_4_2 E_4_2_pp3_50_1(
        .a(pp2_50[0]),
        .b(pp2_50[1]),
        .c(pp2_50[2]),
        .d(pp2_50[3]),
        .CIN(pp3_49_e42_1_cout),
        .S(pp3_50_e42_1_s),
        .C(pp3_50_e42_1_c),
        .COUT(pp3_50_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_50_2(
        .a(pp2_50[4]),
        .b(pp2_50[5]),
        .c(pp2_50[6]),
        .d(pp2_50[7]),
        .CIN(pp3_49_e42_2_cout),
        .S(pp3_50_e42_2_s),
        .C(pp3_50_e42_2_c),
        .COUT(pp3_50_e42_2_cout)
    );
    assign pp3_50 = {pp3_49_e42_1_c, pp3_49_e42_2_c, pp3_50_e42_1_s, pp3_50_e42_2_s};
    E_4_2 E_4_2_pp3_51_1(
        .a(pp2_51[0]),
        .b(pp2_51[1]),
        .c(pp2_51[2]),
        .d(pp2_51[3]),
        .CIN(pp3_50_e42_1_cout),
        .S(pp3_51_e42_1_s),
        .C(pp3_51_e42_1_c),
        .COUT(pp3_51_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_51_2(
        .a(pp2_51[4]),
        .b(pp2_51[5]),
        .c(pp2_51[6]),
        .d(pp2_51[7]),
        .CIN(pp3_50_e42_2_cout),
        .S(pp3_51_e42_2_s),
        .C(pp3_51_e42_2_c),
        .COUT(pp3_51_e42_2_cout)
    );
    assign pp3_51 = {pp3_50_e42_1_c, pp3_50_e42_2_c, pp3_51_e42_1_s, pp3_51_e42_2_s};
    E_4_2 E_4_2_pp3_52_1(
        .a(pp2_52[0]),
        .b(pp2_52[1]),
        .c(pp2_52[2]),
        .d(pp2_52[3]),
        .CIN(pp3_51_e42_1_cout),
        .S(pp3_52_e42_1_s),
        .C(pp3_52_e42_1_c),
        .COUT(pp3_52_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_52_2(
        .a(pp2_52[4]),
        .b(pp2_52[5]),
        .c(pp2_52[6]),
        .d(pp2_52[7]),
        .CIN(pp3_51_e42_2_cout),
        .S(pp3_52_e42_2_s),
        .C(pp3_52_e42_2_c),
        .COUT(pp3_52_e42_2_cout)
    );
    assign pp3_52 = {pp3_51_e42_1_c, pp3_51_e42_2_c, pp3_52_e42_1_s, pp3_52_e42_2_s};
    E_4_2 E_4_2_pp3_53_1(
        .a(pp2_53[0]),
        .b(pp2_53[1]),
        .c(pp2_53[2]),
        .d(pp2_53[3]),
        .CIN(pp3_52_e42_1_cout),
        .S(pp3_53_e42_1_s),
        .C(pp3_53_e42_1_c),
        .COUT(pp3_53_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_53_2(
        .a(pp2_53[4]),
        .b(pp2_53[5]),
        .c(pp2_53[6]),
        .d(pp2_53[7]),
        .CIN(pp3_52_e42_2_cout),
        .S(pp3_53_e42_2_s),
        .C(pp3_53_e42_2_c),
        .COUT(pp3_53_e42_2_cout)
    );
    assign pp3_53 = {pp3_52_e42_1_c, pp3_52_e42_2_c, pp3_53_e42_1_s, pp3_53_e42_2_s};
    E_4_2 E_4_2_pp3_54_1(
        .a(pp2_54[0]),
        .b(pp2_54[1]),
        .c(pp2_54[2]),
        .d(pp2_54[3]),
        .CIN(pp3_53_e42_1_cout),
        .S(pp3_54_e42_1_s),
        .C(pp3_54_e42_1_c),
        .COUT(pp3_54_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_54_2(
        .a(pp2_54[4]),
        .b(pp2_54[5]),
        .c(pp2_54[6]),
        .d(pp2_54[7]),
        .CIN(pp3_53_e42_2_cout),
        .S(pp3_54_e42_2_s),
        .C(pp3_54_e42_2_c),
        .COUT(pp3_54_e42_2_cout)
    );
    assign pp3_54 = {pp3_53_e42_1_c, pp3_53_e42_2_c, pp3_54_e42_1_s, pp3_54_e42_2_s};
    E_4_2 E_4_2_pp3_55_1(
        .a(pp2_55[0]),
        .b(pp2_55[1]),
        .c(pp2_55[2]),
        .d(pp2_55[3]),
        .CIN(pp3_54_e42_1_cout),
        .S(pp3_55_e42_1_s),
        .C(pp3_55_e42_1_c),
        .COUT(pp3_55_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_55_2(
        .a(pp2_55[4]),
        .b(pp2_55[5]),
        .c(pp2_55[6]),
        .d(pp2_55[7]),
        .CIN(pp3_54_e42_2_cout),
        .S(pp3_55_e42_2_s),
        .C(pp3_55_e42_2_c),
        .COUT(pp3_55_e42_2_cout)
    );
    assign pp3_55 = {pp3_54_e42_1_c, pp3_54_e42_2_c, pp3_55_e42_1_s, pp3_55_e42_2_s};
    E_4_2 E_4_2_pp3_56_1(
        .a(pp2_56[0]),
        .b(pp2_56[1]),
        .c(pp2_56[2]),
        .d(pp2_56[3]),
        .CIN(pp3_55_e42_1_cout),
        .S(pp3_56_e42_1_s),
        .C(pp3_56_e42_1_c),
        .COUT(pp3_56_e42_1_cout)
    );
    E_4_2 E_4_2_pp3_56_2(
        .a(pp2_56[4]),
        .b(pp2_56[5]),
        .c(pp2_56[6]),
        .d(pp2_56[7]),
        .CIN(pp3_55_e42_2_cout),
        .S(pp3_56_e42_2_s),
        .C(pp3_56_e42_2_c),
        .COUT(pp3_56_e42_2_cout)
    );
    assign pp3_56 = {pp3_55_e42_1_c, pp3_55_e42_2_c, pp3_56_e42_1_s, pp3_56_e42_2_s};
    E_4_2 E_4_2_pp3_57_1(
        .a(pp2_57[0]),
        .b(pp2_57[1]),
        .c(pp2_57[2]),
        .d(pp2_57[3]),
        .CIN(pp3_56_e42_1_cout),
        .S(pp3_57_e42_1_s),
        .C(pp3_57_e42_1_c),
        .COUT(pp3_57_e42_1_cout)
    );
    Full_adder Full_adder_pp3_57_1(
        .a(pp2_57[4]),
        .b(pp2_57[5]),
        .CIN(pp3_56_e42_2_cout),
        .S(pp3_57_fa_1_s),
        .C(pp3_57_fa_1_c)
    );
    assign pp3_57 = {pp3_56_e42_1_c, pp3_56_e42_2_c, pp3_57_e42_1_s, pp3_57_fa_1_s};
    E_4_2 E_4_2_pp3_58_1(
        .a(pp2_58[0]),
        .b(pp2_58[1]),
        .c(pp2_58[2]),
        .d(pp2_58[3]),
        .CIN(pp3_57_e42_1_cout),
        .S(pp3_58_e42_1_s),
        .C(pp3_58_e42_1_c),
        .COUT(pp3_58_e42_1_cout)
    );
    assign pp3_58 = {pp2_58[4], pp3_57_fa_1_c, pp3_57_e42_1_c, pp3_58_e42_1_s};
    Full_adder Full_adder_pp3_59_1(
        .a(pp2_59[0]),
        .b(pp2_59[1]),
        .CIN(pp3_58_e42_1_cout),
        .S(pp3_59_fa_1_s),
        .C(pp3_59_fa_1_c)
    );
    assign pp3_59 = {pp2_59[2], pp2_59[3], pp3_58_e42_1_c, pp3_59_fa_1_s};
    assign pp3_60 = {pp2_60[0], pp2_60[1], pp2_60[2], pp3_59_fa_1_c};
    assign pp3_61 = {pp2_61[0], pp2_61[1]};
    assign pp3_62 = pp2_62;
    assign pp3_63 = cin_net;
endmodule



module STAGE4_32(
    input pp3_0,
    input [1:0] pp3_1,
    input [2:0] pp3_2,
    input [3:0] pp3_3,
    input [3:0] pp3_4,
    input [3:0] pp3_5,
    input [3:0] pp3_6,
    input [3:0] pp3_7,
    input [3:0] pp3_8,
    input [3:0] pp3_9,
    input [3:0] pp3_10,
    input [3:0] pp3_11,
    input [3:0] pp3_12,
    input [3:0] pp3_13,
    input [3:0] pp3_14,
    input [3:0] pp3_15,
    input [3:0] pp3_16,
    input [3:0] pp3_17,
    input [3:0] pp3_18,
    input [3:0] pp3_19,
    input [3:0] pp3_20,
    input [3:0] pp3_21,
    input [3:0] pp3_22,
    input [3:0] pp3_23,
    input [3:0] pp3_24,
    input [3:0] pp3_25,
    input [3:0] pp3_26,
    input [3:0] pp3_27,
    input [3:0] pp3_28,
    input [3:0] pp3_29,
    input [3:0] pp3_30,
    input [3:0] pp3_31,
    input [3:0] pp3_32,
    input [3:0] pp3_33,
    input [3:0] pp3_34,
    input [3:0] pp3_35,
    input [3:0] pp3_36,
    input [3:0] pp3_37,
    input [3:0] pp3_38,
    input [3:0] pp3_39,
    input [3:0] pp3_40,
    input [3:0] pp3_41,
    input [3:0] pp3_42,
    input [3:0] pp3_43,
    input [3:0] pp3_44,
    input [3:0] pp3_45,
    input [3:0] pp3_46,
    input [3:0] pp3_47,
    input [3:0] pp3_48,
    input [3:0] pp3_49,
    input [3:0] pp3_50,
    input [3:0] pp3_51,
    input [3:0] pp3_52,
    input [3:0] pp3_53,
    input [3:0] pp3_54,
    input [3:0] pp3_55,
    input [3:0] pp3_56,
    input [3:0] pp3_57,
    input [3:0] pp3_58,
    input [3:0] pp3_59,
    input [3:0] pp3_60,
    input [1:0] pp3_61,
    input pp3_62,
    input pp3_63,
    output [63:0] A,
    output [63:0] B
);
wire cin_net;
LOGIC0_X1 u_gnd (.Z(cin_net));
    wire pp4_0_1_s;
    wire pp4_0_1_c;
    wire pp4_0_1_cout;
    wire pp4_0_2_s;
    wire pp4_0_2_c;
    wire pp4_0_2_cout;
    wire pp4_0_3_s;
    wire pp4_0_3_c;
    wire pp4_0_3_cout;
    wire pp4_0_4_s;
    wire pp4_0_4_c;
    wire pp4_0_fa_s;
    wire pp4_0_fa_c;
    wire pp4_0_ha_s;
    wire pp4_0_ha_c;
    wire pp4_1_1_s;
    wire pp4_1_1_c;
    wire pp4_1_1_cout;
    wire pp4_1_2_s;
    wire pp4_1_2_c;
    wire pp4_1_2_cout;
    wire pp4_1_3_s;
    wire pp4_1_3_c;
    wire pp4_1_3_cout;
    wire pp4_1_4_s;
    wire pp4_1_4_c;
    wire pp4_1_fa_s;
    wire pp4_1_fa_c;
    wire pp4_1_ha_s;
    wire pp4_1_ha_c;
    wire pp4_2_1_s;
    wire pp4_2_1_c;
    wire pp4_2_1_cout;
    wire pp4_2_2_s;
    wire pp4_2_2_c;
    wire pp4_2_2_cout;
    wire pp4_2_3_s;
    wire pp4_2_3_c;
    wire pp4_2_3_cout;
    wire pp4_2_4_s;
    wire pp4_2_4_c;
    wire pp4_2_fa_s;
    wire pp4_2_fa_c;
    wire pp4_2_ha_s;
    wire pp4_2_ha_c;
    wire pp4_3_1_s;
    wire pp4_3_1_c;
    wire pp4_3_1_cout;
    wire pp4_3_2_s;
    wire pp4_3_2_c;
    wire pp4_3_2_cout;
    wire pp4_3_3_s;
    wire pp4_3_3_c;
    wire pp4_3_3_cout;
    wire pp4_3_4_s;
    wire pp4_3_4_c;
    wire pp4_3_fa_s;
    wire pp4_3_fa_c;
    wire pp4_3_ha_s;
    wire pp4_3_ha_c;
    wire pp4_4_1_s;
    wire pp4_4_1_c;
    wire pp4_4_1_cout;
    wire pp4_4_2_s;
    wire pp4_4_2_c;
    wire pp4_4_2_cout;
    wire pp4_4_3_s;
    wire pp4_4_3_c;
    wire pp4_4_3_cout;
    wire pp4_4_4_s;
    wire pp4_4_4_c;
    wire pp4_4_fa_s;
    wire pp4_4_fa_c;
    wire pp4_4_ha_s;
    wire pp4_4_ha_c;
    wire pp4_5_1_s;
    wire pp4_5_1_c;
    wire pp4_5_1_cout;
    wire pp4_5_2_s;
    wire pp4_5_2_c;
    wire pp4_5_2_cout;
    wire pp4_5_3_s;
    wire pp4_5_3_c;
    wire pp4_5_3_cout;
    wire pp4_5_4_s;
    wire pp4_5_4_c;
    wire pp4_5_fa_s;
    wire pp4_5_fa_c;
    wire pp4_5_ha_s;
    wire pp4_5_ha_c;
    wire pp4_6_1_s;
    wire pp4_6_1_c;
    wire pp4_6_1_cout;
    wire pp4_6_2_s;
    wire pp4_6_2_c;
    wire pp4_6_2_cout;
    wire pp4_6_3_s;
    wire pp4_6_3_c;
    wire pp4_6_3_cout;
    wire pp4_6_4_s;
    wire pp4_6_4_c;
    wire pp4_6_fa_s;
    wire pp4_6_fa_c;
    wire pp4_6_ha_s;
    wire pp4_6_ha_c;
    wire pp4_7_1_s;
    wire pp4_7_1_c;
    wire pp4_7_1_cout;
    wire pp4_7_2_s;
    wire pp4_7_2_c;
    wire pp4_7_2_cout;
    wire pp4_7_3_s;
    wire pp4_7_3_c;
    wire pp4_7_3_cout;
    wire pp4_7_4_s;
    wire pp4_7_4_c;
    wire pp4_7_fa_s;
    wire pp4_7_fa_c;
    wire pp4_7_ha_s;
    wire pp4_7_ha_c;
    wire pp4_8_1_s;
    wire pp4_8_1_c;
    wire pp4_8_1_cout;
    wire pp4_8_2_s;
    wire pp4_8_2_c;
    wire pp4_8_2_cout;
    wire pp4_8_3_s;
    wire pp4_8_3_c;
    wire pp4_8_3_cout;
    wire pp4_8_4_s;
    wire pp4_8_4_c;
    wire pp4_8_fa_s;
    wire pp4_8_fa_c;
    wire pp4_8_ha_s;
    wire pp4_8_ha_c;
    wire pp4_9_1_s;
    wire pp4_9_1_c;
    wire pp4_9_1_cout;
    wire pp4_9_2_s;
    wire pp4_9_2_c;
    wire pp4_9_2_cout;
    wire pp4_9_3_s;
    wire pp4_9_3_c;
    wire pp4_9_3_cout;
    wire pp4_9_4_s;
    wire pp4_9_4_c;
    wire pp4_9_fa_s;
    wire pp4_9_fa_c;
    wire pp4_9_ha_s;
    wire pp4_9_ha_c;
    wire pp4_10_1_s;
    wire pp4_10_1_c;
    wire pp4_10_1_cout;
    wire pp4_10_2_s;
    wire pp4_10_2_c;
    wire pp4_10_2_cout;
    wire pp4_10_3_s;
    wire pp4_10_3_c;
    wire pp4_10_3_cout;
    wire pp4_10_4_s;
    wire pp4_10_4_c;
    wire pp4_10_fa_s;
    wire pp4_10_fa_c;
    wire pp4_10_ha_s;
    wire pp4_10_ha_c;
    wire pp4_11_1_s;
    wire pp4_11_1_c;
    wire pp4_11_1_cout;
    wire pp4_11_2_s;
    wire pp4_11_2_c;
    wire pp4_11_2_cout;
    wire pp4_11_3_s;
    wire pp4_11_3_c;
    wire pp4_11_3_cout;
    wire pp4_11_4_s;
    wire pp4_11_4_c;
    wire pp4_11_fa_s;
    wire pp4_11_fa_c;
    wire pp4_11_ha_s;
    wire pp4_11_ha_c;
    wire pp4_12_1_s;
    wire pp4_12_1_c;
    wire pp4_12_1_cout;
    wire pp4_12_2_s;
    wire pp4_12_2_c;
    wire pp4_12_2_cout;
    wire pp4_12_3_s;
    wire pp4_12_3_c;
    wire pp4_12_3_cout;
    wire pp4_12_4_s;
    wire pp4_12_4_c;
    wire pp4_12_fa_s;
    wire pp4_12_fa_c;
    wire pp4_12_ha_s;
    wire pp4_12_ha_c;
    wire pp4_13_1_s;
    wire pp4_13_1_c;
    wire pp4_13_1_cout;
    wire pp4_13_2_s;
    wire pp4_13_2_c;
    wire pp4_13_2_cout;
    wire pp4_13_3_s;
    wire pp4_13_3_c;
    wire pp4_13_3_cout;
    wire pp4_13_4_s;
    wire pp4_13_4_c;
    wire pp4_13_fa_s;
    wire pp4_13_fa_c;
    wire pp4_13_ha_s;
    wire pp4_13_ha_c;
    wire pp4_14_1_s;
    wire pp4_14_1_c;
    wire pp4_14_1_cout;
    wire pp4_14_2_s;
    wire pp4_14_2_c;
    wire pp4_14_2_cout;
    wire pp4_14_3_s;
    wire pp4_14_3_c;
    wire pp4_14_3_cout;
    wire pp4_14_4_s;
    wire pp4_14_4_c;
    wire pp4_14_fa_s;
    wire pp4_14_fa_c;
    wire pp4_14_ha_s;
    wire pp4_14_ha_c;
    wire pp4_15_1_s;
    wire pp4_15_1_c;
    wire pp4_15_1_cout;
    wire pp4_15_2_s;
    wire pp4_15_2_c;
    wire pp4_15_2_cout;
    wire pp4_15_3_s;
    wire pp4_15_3_c;
    wire pp4_15_3_cout;
    wire pp4_15_4_s;
    wire pp4_15_4_c;
    wire pp4_15_fa_s;
    wire pp4_15_fa_c;
    wire pp4_15_ha_s;
    wire pp4_15_ha_c;
    wire pp4_16_1_s;
    wire pp4_16_1_c;
    wire pp4_16_1_cout;
    wire pp4_16_2_s;
    wire pp4_16_2_c;
    wire pp4_16_2_cout;
    wire pp4_16_3_s;
    wire pp4_16_3_c;
    wire pp4_16_3_cout;
    wire pp4_16_4_s;
    wire pp4_16_4_c;
    wire pp4_16_fa_s;
    wire pp4_16_fa_c;
    wire pp4_16_ha_s;
    wire pp4_16_ha_c;
    wire pp4_17_1_s;
    wire pp4_17_1_c;
    wire pp4_17_1_cout;
    wire pp4_17_2_s;
    wire pp4_17_2_c;
    wire pp4_17_2_cout;
    wire pp4_17_3_s;
    wire pp4_17_3_c;
    wire pp4_17_3_cout;
    wire pp4_17_4_s;
    wire pp4_17_4_c;
    wire pp4_17_fa_s;
    wire pp4_17_fa_c;
    wire pp4_17_ha_s;
    wire pp4_17_ha_c;
    wire pp4_18_1_s;
    wire pp4_18_1_c;
    wire pp4_18_1_cout;
    wire pp4_18_2_s;
    wire pp4_18_2_c;
    wire pp4_18_2_cout;
    wire pp4_18_3_s;
    wire pp4_18_3_c;
    wire pp4_18_3_cout;
    wire pp4_18_4_s;
    wire pp4_18_4_c;
    wire pp4_18_fa_s;
    wire pp4_18_fa_c;
    wire pp4_18_ha_s;
    wire pp4_18_ha_c;
    wire pp4_19_1_s;
    wire pp4_19_1_c;
    wire pp4_19_1_cout;
    wire pp4_19_2_s;
    wire pp4_19_2_c;
    wire pp4_19_2_cout;
    wire pp4_19_3_s;
    wire pp4_19_3_c;
    wire pp4_19_3_cout;
    wire pp4_19_4_s;
    wire pp4_19_4_c;
    wire pp4_19_fa_s;
    wire pp4_19_fa_c;
    wire pp4_19_ha_s;
    wire pp4_19_ha_c;
    wire pp4_20_1_s;
    wire pp4_20_1_c;
    wire pp4_20_1_cout;
    wire pp4_20_2_s;
    wire pp4_20_2_c;
    wire pp4_20_2_cout;
    wire pp4_20_3_s;
    wire pp4_20_3_c;
    wire pp4_20_3_cout;
    wire pp4_20_4_s;
    wire pp4_20_4_c;
    wire pp4_20_fa_s;
    wire pp4_20_fa_c;
    wire pp4_20_ha_s;
    wire pp4_20_ha_c;
    wire pp4_21_1_s;
    wire pp4_21_1_c;
    wire pp4_21_1_cout;
    wire pp4_21_2_s;
    wire pp4_21_2_c;
    wire pp4_21_2_cout;
    wire pp4_21_3_s;
    wire pp4_21_3_c;
    wire pp4_21_3_cout;
    wire pp4_21_4_s;
    wire pp4_21_4_c;
    wire pp4_21_fa_s;
    wire pp4_21_fa_c;
    wire pp4_21_ha_s;
    wire pp4_21_ha_c;
    wire pp4_22_1_s;
    wire pp4_22_1_c;
    wire pp4_22_1_cout;
    wire pp4_22_2_s;
    wire pp4_22_2_c;
    wire pp4_22_2_cout;
    wire pp4_22_3_s;
    wire pp4_22_3_c;
    wire pp4_22_3_cout;
    wire pp4_22_4_s;
    wire pp4_22_4_c;
    wire pp4_22_fa_s;
    wire pp4_22_fa_c;
    wire pp4_22_ha_s;
    wire pp4_22_ha_c;
    wire pp4_23_1_s;
    wire pp4_23_1_c;
    wire pp4_23_1_cout;
    wire pp4_23_2_s;
    wire pp4_23_2_c;
    wire pp4_23_2_cout;
    wire pp4_23_3_s;
    wire pp4_23_3_c;
    wire pp4_23_3_cout;
    wire pp4_23_4_s;
    wire pp4_23_4_c;
    wire pp4_23_fa_s;
    wire pp4_23_fa_c;
    wire pp4_23_ha_s;
    wire pp4_23_ha_c;
    wire pp4_24_1_s;
    wire pp4_24_1_c;
    wire pp4_24_1_cout;
    wire pp4_24_2_s;
    wire pp4_24_2_c;
    wire pp4_24_2_cout;
    wire pp4_24_3_s;
    wire pp4_24_3_c;
    wire pp4_24_3_cout;
    wire pp4_24_4_s;
    wire pp4_24_4_c;
    wire pp4_24_fa_s;
    wire pp4_24_fa_c;
    wire pp4_24_ha_s;
    wire pp4_24_ha_c;
    wire pp4_25_1_s;
    wire pp4_25_1_c;
    wire pp4_25_1_cout;
    wire pp4_25_2_s;
    wire pp4_25_2_c;
    wire pp4_25_2_cout;
    wire pp4_25_3_s;
    wire pp4_25_3_c;
    wire pp4_25_3_cout;
    wire pp4_25_4_s;
    wire pp4_25_4_c;
    wire pp4_25_fa_s;
    wire pp4_25_fa_c;
    wire pp4_25_ha_s;
    wire pp4_25_ha_c;
    wire pp4_26_1_s;
    wire pp4_26_1_c;
    wire pp4_26_1_cout;
    wire pp4_26_2_s;
    wire pp4_26_2_c;
    wire pp4_26_2_cout;
    wire pp4_26_3_s;
    wire pp4_26_3_c;
    wire pp4_26_3_cout;
    wire pp4_26_4_s;
    wire pp4_26_4_c;
    wire pp4_26_fa_s;
    wire pp4_26_fa_c;
    wire pp4_26_ha_s;
    wire pp4_26_ha_c;
    wire pp4_27_1_s;
    wire pp4_27_1_c;
    wire pp4_27_1_cout;
    wire pp4_27_2_s;
    wire pp4_27_2_c;
    wire pp4_27_2_cout;
    wire pp4_27_3_s;
    wire pp4_27_3_c;
    wire pp4_27_3_cout;
    wire pp4_27_4_s;
    wire pp4_27_4_c;
    wire pp4_27_fa_s;
    wire pp4_27_fa_c;
    wire pp4_27_ha_s;
    wire pp4_27_ha_c;
    wire pp4_28_1_s;
    wire pp4_28_1_c;
    wire pp4_28_1_cout;
    wire pp4_28_2_s;
    wire pp4_28_2_c;
    wire pp4_28_2_cout;
    wire pp4_28_3_s;
    wire pp4_28_3_c;
    wire pp4_28_3_cout;
    wire pp4_28_4_s;
    wire pp4_28_4_c;
    wire pp4_28_fa_s;
    wire pp4_28_fa_c;
    wire pp4_28_ha_s;
    wire pp4_28_ha_c;
    wire pp4_29_1_s;
    wire pp4_29_1_c;
    wire pp4_29_1_cout;
    wire pp4_29_2_s;
    wire pp4_29_2_c;
    wire pp4_29_2_cout;
    wire pp4_29_3_s;
    wire pp4_29_3_c;
    wire pp4_29_3_cout;
    wire pp4_29_4_s;
    wire pp4_29_4_c;
    wire pp4_29_fa_s;
    wire pp4_29_fa_c;
    wire pp4_29_ha_s;
    wire pp4_29_ha_c;
    wire pp4_30_1_s;
    wire pp4_30_1_c;
    wire pp4_30_1_cout;
    wire pp4_30_2_s;
    wire pp4_30_2_c;
    wire pp4_30_2_cout;
    wire pp4_30_3_s;
    wire pp4_30_3_c;
    wire pp4_30_3_cout;
    wire pp4_30_4_s;
    wire pp4_30_4_c;
    wire pp4_30_fa_s;
    wire pp4_30_fa_c;
    wire pp4_30_ha_s;
    wire pp4_30_ha_c;
    wire pp4_31_1_s;
    wire pp4_31_1_c;
    wire pp4_31_1_cout;
    wire pp4_31_2_s;
    wire pp4_31_2_c;
    wire pp4_31_2_cout;
    wire pp4_31_3_s;
    wire pp4_31_3_c;
    wire pp4_31_3_cout;
    wire pp4_31_4_s;
    wire pp4_31_4_c;
    wire pp4_31_fa_s;
    wire pp4_31_fa_c;
    wire pp4_31_ha_s;
    wire pp4_31_ha_c;
    wire pp4_32_1_s;
    wire pp4_32_1_c;
    wire pp4_32_1_cout;
    wire pp4_32_2_s;
    wire pp4_32_2_c;
    wire pp4_32_2_cout;
    wire pp4_32_3_s;
    wire pp4_32_3_c;
    wire pp4_32_3_cout;
    wire pp4_32_4_s;
    wire pp4_32_4_c;
    wire pp4_32_fa_s;
    wire pp4_32_fa_c;
    wire pp4_32_ha_s;
    wire pp4_32_ha_c;
    wire pp4_33_1_s;
    wire pp4_33_1_c;
    wire pp4_33_1_cout;
    wire pp4_33_2_s;
    wire pp4_33_2_c;
    wire pp4_33_2_cout;
    wire pp4_33_3_s;
    wire pp4_33_3_c;
    wire pp4_33_3_cout;
    wire pp4_33_4_s;
    wire pp4_33_4_c;
    wire pp4_33_fa_s;
    wire pp4_33_fa_c;
    wire pp4_33_ha_s;
    wire pp4_33_ha_c;
    wire pp4_34_1_s;
    wire pp4_34_1_c;
    wire pp4_34_1_cout;
    wire pp4_34_2_s;
    wire pp4_34_2_c;
    wire pp4_34_2_cout;
    wire pp4_34_3_s;
    wire pp4_34_3_c;
    wire pp4_34_3_cout;
    wire pp4_34_4_s;
    wire pp4_34_4_c;
    wire pp4_34_fa_s;
    wire pp4_34_fa_c;
    wire pp4_34_ha_s;
    wire pp4_34_ha_c;
    wire pp4_35_1_s;
    wire pp4_35_1_c;
    wire pp4_35_1_cout;
    wire pp4_35_2_s;
    wire pp4_35_2_c;
    wire pp4_35_2_cout;
    wire pp4_35_3_s;
    wire pp4_35_3_c;
    wire pp4_35_3_cout;
    wire pp4_35_4_s;
    wire pp4_35_4_c;
    wire pp4_35_fa_s;
    wire pp4_35_fa_c;
    wire pp4_35_ha_s;
    wire pp4_35_ha_c;
    wire pp4_36_1_s;
    wire pp4_36_1_c;
    wire pp4_36_1_cout;
    wire pp4_36_2_s;
    wire pp4_36_2_c;
    wire pp4_36_2_cout;
    wire pp4_36_3_s;
    wire pp4_36_3_c;
    wire pp4_36_3_cout;
    wire pp4_36_4_s;
    wire pp4_36_4_c;
    wire pp4_36_fa_s;
    wire pp4_36_fa_c;
    wire pp4_36_ha_s;
    wire pp4_36_ha_c;
    wire pp4_37_1_s;
    wire pp4_37_1_c;
    wire pp4_37_1_cout;
    wire pp4_37_2_s;
    wire pp4_37_2_c;
    wire pp4_37_2_cout;
    wire pp4_37_3_s;
    wire pp4_37_3_c;
    wire pp4_37_3_cout;
    wire pp4_37_4_s;
    wire pp4_37_4_c;
    wire pp4_37_fa_s;
    wire pp4_37_fa_c;
    wire pp4_37_ha_s;
    wire pp4_37_ha_c;
    wire pp4_38_1_s;
    wire pp4_38_1_c;
    wire pp4_38_1_cout;
    wire pp4_38_2_s;
    wire pp4_38_2_c;
    wire pp4_38_2_cout;
    wire pp4_38_3_s;
    wire pp4_38_3_c;
    wire pp4_38_3_cout;
    wire pp4_38_4_s;
    wire pp4_38_4_c;
    wire pp4_38_fa_s;
    wire pp4_38_fa_c;
    wire pp4_38_ha_s;
    wire pp4_38_ha_c;
    wire pp4_39_1_s;
    wire pp4_39_1_c;
    wire pp4_39_1_cout;
    wire pp4_39_2_s;
    wire pp4_39_2_c;
    wire pp4_39_2_cout;
    wire pp4_39_3_s;
    wire pp4_39_3_c;
    wire pp4_39_3_cout;
    wire pp4_39_4_s;
    wire pp4_39_4_c;
    wire pp4_39_fa_s;
    wire pp4_39_fa_c;
    wire pp4_39_ha_s;
    wire pp4_39_ha_c;
    wire pp4_40_1_s;
    wire pp4_40_1_c;
    wire pp4_40_1_cout;
    wire pp4_40_2_s;
    wire pp4_40_2_c;
    wire pp4_40_2_cout;
    wire pp4_40_3_s;
    wire pp4_40_3_c;
    wire pp4_40_3_cout;
    wire pp4_40_4_s;
    wire pp4_40_4_c;
    wire pp4_40_fa_s;
    wire pp4_40_fa_c;
    wire pp4_40_ha_s;
    wire pp4_40_ha_c;
    wire pp4_41_1_s;
    wire pp4_41_1_c;
    wire pp4_41_1_cout;
    wire pp4_41_2_s;
    wire pp4_41_2_c;
    wire pp4_41_2_cout;
    wire pp4_41_3_s;
    wire pp4_41_3_c;
    wire pp4_41_3_cout;
    wire pp4_41_4_s;
    wire pp4_41_4_c;
    wire pp4_41_fa_s;
    wire pp4_41_fa_c;
    wire pp4_41_ha_s;
    wire pp4_41_ha_c;
    wire pp4_42_1_s;
    wire pp4_42_1_c;
    wire pp4_42_1_cout;
    wire pp4_42_2_s;
    wire pp4_42_2_c;
    wire pp4_42_2_cout;
    wire pp4_42_3_s;
    wire pp4_42_3_c;
    wire pp4_42_3_cout;
    wire pp4_42_4_s;
    wire pp4_42_4_c;
    wire pp4_42_fa_s;
    wire pp4_42_fa_c;
    wire pp4_42_ha_s;
    wire pp4_42_ha_c;
    wire pp4_43_1_s;
    wire pp4_43_1_c;
    wire pp4_43_1_cout;
    wire pp4_43_2_s;
    wire pp4_43_2_c;
    wire pp4_43_2_cout;
    wire pp4_43_3_s;
    wire pp4_43_3_c;
    wire pp4_43_3_cout;
    wire pp4_43_4_s;
    wire pp4_43_4_c;
    wire pp4_43_fa_s;
    wire pp4_43_fa_c;
    wire pp4_43_ha_s;
    wire pp4_43_ha_c;
    wire pp4_44_1_s;
    wire pp4_44_1_c;
    wire pp4_44_1_cout;
    wire pp4_44_2_s;
    wire pp4_44_2_c;
    wire pp4_44_2_cout;
    wire pp4_44_3_s;
    wire pp4_44_3_c;
    wire pp4_44_3_cout;
    wire pp4_44_4_s;
    wire pp4_44_4_c;
    wire pp4_44_fa_s;
    wire pp4_44_fa_c;
    wire pp4_44_ha_s;
    wire pp4_44_ha_c;
    wire pp4_45_1_s;
    wire pp4_45_1_c;
    wire pp4_45_1_cout;
    wire pp4_45_2_s;
    wire pp4_45_2_c;
    wire pp4_45_2_cout;
    wire pp4_45_3_s;
    wire pp4_45_3_c;
    wire pp4_45_3_cout;
    wire pp4_45_4_s;
    wire pp4_45_4_c;
    wire pp4_45_fa_s;
    wire pp4_45_fa_c;
    wire pp4_45_ha_s;
    wire pp4_45_ha_c;
    wire pp4_46_1_s;
    wire pp4_46_1_c;
    wire pp4_46_1_cout;
    wire pp4_46_2_s;
    wire pp4_46_2_c;
    wire pp4_46_2_cout;
    wire pp4_46_3_s;
    wire pp4_46_3_c;
    wire pp4_46_3_cout;
    wire pp4_46_4_s;
    wire pp4_46_4_c;
    wire pp4_46_fa_s;
    wire pp4_46_fa_c;
    wire pp4_46_ha_s;
    wire pp4_46_ha_c;
    wire pp4_47_1_s;
    wire pp4_47_1_c;
    wire pp4_47_1_cout;
    wire pp4_47_2_s;
    wire pp4_47_2_c;
    wire pp4_47_2_cout;
    wire pp4_47_3_s;
    wire pp4_47_3_c;
    wire pp4_47_3_cout;
    wire pp4_47_4_s;
    wire pp4_47_4_c;
    wire pp4_47_fa_s;
    wire pp4_47_fa_c;
    wire pp4_47_ha_s;
    wire pp4_47_ha_c;
    wire pp4_48_1_s;
    wire pp4_48_1_c;
    wire pp4_48_1_cout;
    wire pp4_48_2_s;
    wire pp4_48_2_c;
    wire pp4_48_2_cout;
    wire pp4_48_3_s;
    wire pp4_48_3_c;
    wire pp4_48_3_cout;
    wire pp4_48_4_s;
    wire pp4_48_4_c;
    wire pp4_48_fa_s;
    wire pp4_48_fa_c;
    wire pp4_48_ha_s;
    wire pp4_48_ha_c;
    wire pp4_49_1_s;
    wire pp4_49_1_c;
    wire pp4_49_1_cout;
    wire pp4_49_2_s;
    wire pp4_49_2_c;
    wire pp4_49_2_cout;
    wire pp4_49_3_s;
    wire pp4_49_3_c;
    wire pp4_49_3_cout;
    wire pp4_49_4_s;
    wire pp4_49_4_c;
    wire pp4_49_fa_s;
    wire pp4_49_fa_c;
    wire pp4_49_ha_s;
    wire pp4_49_ha_c;
    wire pp4_50_1_s;
    wire pp4_50_1_c;
    wire pp4_50_1_cout;
    wire pp4_50_2_s;
    wire pp4_50_2_c;
    wire pp4_50_2_cout;
    wire pp4_50_3_s;
    wire pp4_50_3_c;
    wire pp4_50_3_cout;
    wire pp4_50_4_s;
    wire pp4_50_4_c;
    wire pp4_50_fa_s;
    wire pp4_50_fa_c;
    wire pp4_50_ha_s;
    wire pp4_50_ha_c;
    wire pp4_51_1_s;
    wire pp4_51_1_c;
    wire pp4_51_1_cout;
    wire pp4_51_2_s;
    wire pp4_51_2_c;
    wire pp4_51_2_cout;
    wire pp4_51_3_s;
    wire pp4_51_3_c;
    wire pp4_51_3_cout;
    wire pp4_51_4_s;
    wire pp4_51_4_c;
    wire pp4_51_fa_s;
    wire pp4_51_fa_c;
    wire pp4_51_ha_s;
    wire pp4_51_ha_c;
    wire pp4_52_1_s;
    wire pp4_52_1_c;
    wire pp4_52_1_cout;
    wire pp4_52_2_s;
    wire pp4_52_2_c;
    wire pp4_52_2_cout;
    wire pp4_52_3_s;
    wire pp4_52_3_c;
    wire pp4_52_3_cout;
    wire pp4_52_4_s;
    wire pp4_52_4_c;
    wire pp4_52_fa_s;
    wire pp4_52_fa_c;
    wire pp4_52_ha_s;
    wire pp4_52_ha_c;
    wire pp4_53_1_s;
    wire pp4_53_1_c;
    wire pp4_53_1_cout;
    wire pp4_53_2_s;
    wire pp4_53_2_c;
    wire pp4_53_2_cout;
    wire pp4_53_3_s;
    wire pp4_53_3_c;
    wire pp4_53_3_cout;
    wire pp4_53_4_s;
    wire pp4_53_4_c;
    wire pp4_53_fa_s;
    wire pp4_53_fa_c;
    wire pp4_53_ha_s;
    wire pp4_53_ha_c;
    wire pp4_54_1_s;
    wire pp4_54_1_c;
    wire pp4_54_1_cout;
    wire pp4_54_2_s;
    wire pp4_54_2_c;
    wire pp4_54_2_cout;
    wire pp4_54_3_s;
    wire pp4_54_3_c;
    wire pp4_54_3_cout;
    wire pp4_54_4_s;
    wire pp4_54_4_c;
    wire pp4_54_fa_s;
    wire pp4_54_fa_c;
    wire pp4_54_ha_s;
    wire pp4_54_ha_c;
    wire pp4_55_1_s;
    wire pp4_55_1_c;
    wire pp4_55_1_cout;
    wire pp4_55_2_s;
    wire pp4_55_2_c;
    wire pp4_55_2_cout;
    wire pp4_55_3_s;
    wire pp4_55_3_c;
    wire pp4_55_3_cout;
    wire pp4_55_4_s;
    wire pp4_55_4_c;
    wire pp4_55_fa_s;
    wire pp4_55_fa_c;
    wire pp4_55_ha_s;
    wire pp4_55_ha_c;
    wire pp4_56_1_s;
    wire pp4_56_1_c;
    wire pp4_56_1_cout;
    wire pp4_56_2_s;
    wire pp4_56_2_c;
    wire pp4_56_2_cout;
    wire pp4_56_3_s;
    wire pp4_56_3_c;
    wire pp4_56_3_cout;
    wire pp4_56_4_s;
    wire pp4_56_4_c;
    wire pp4_56_fa_s;
    wire pp4_56_fa_c;
    wire pp4_56_ha_s;
    wire pp4_56_ha_c;
    wire pp4_57_1_s;
    wire pp4_57_1_c;
    wire pp4_57_1_cout;
    wire pp4_57_2_s;
    wire pp4_57_2_c;
    wire pp4_57_2_cout;
    wire pp4_57_3_s;
    wire pp4_57_3_c;
    wire pp4_57_3_cout;
    wire pp4_57_4_s;
    wire pp4_57_4_c;
    wire pp4_57_fa_s;
    wire pp4_57_fa_c;
    wire pp4_57_ha_s;
    wire pp4_57_ha_c;
    wire pp4_58_1_s;
    wire pp4_58_1_c;
    wire pp4_58_1_cout;
    wire pp4_58_2_s;
    wire pp4_58_2_c;
    wire pp4_58_2_cout;
    wire pp4_58_3_s;
    wire pp4_58_3_c;
    wire pp4_58_3_cout;
    wire pp4_58_4_s;
    wire pp4_58_4_c;
    wire pp4_58_fa_s;
    wire pp4_58_fa_c;
    wire pp4_58_ha_s;
    wire pp4_58_ha_c;
    wire pp4_59_1_s;
    wire pp4_59_1_c;
    wire pp4_59_1_cout;
    wire pp4_59_2_s;
    wire pp4_59_2_c;
    wire pp4_59_2_cout;
    wire pp4_59_3_s;
    wire pp4_59_3_c;
    wire pp4_59_3_cout;
    wire pp4_59_4_s;
    wire pp4_59_4_c;
    wire pp4_59_fa_s;
    wire pp4_59_fa_c;
    wire pp4_59_ha_s;
    wire pp4_59_ha_c;
    wire pp4_60_1_s;
    wire pp4_60_1_c;
    wire pp4_60_1_cout;
    wire pp4_60_2_s;
    wire pp4_60_2_c;
    wire pp4_60_2_cout;
    wire pp4_60_3_s;
    wire pp4_60_3_c;
    wire pp4_60_3_cout;
    wire pp4_60_4_s;
    wire pp4_60_4_c;
    wire pp4_60_fa_s;
    wire pp4_60_fa_c;
    wire pp4_60_ha_s;
    wire pp4_60_ha_c;
    wire pp4_61_1_s;
    wire pp4_61_1_c;
    wire pp4_61_1_cout;
    wire pp4_61_2_s;
    wire pp4_61_2_c;
    wire pp4_61_2_cout;
    wire pp4_61_3_s;
    wire pp4_61_3_c;
    wire pp4_61_3_cout;
    wire pp4_61_4_s;
    wire pp4_61_4_c;
    wire pp4_61_fa_s;
    wire pp4_61_fa_c;
    wire pp4_61_ha_s;
    wire pp4_61_ha_c;
    wire pp4_62_1_s;
    wire pp4_62_1_c;
    wire pp4_62_1_cout;
    wire pp4_62_2_s;
    wire pp4_62_2_c;
    wire pp4_62_2_cout;
    wire pp4_62_3_s;
    wire pp4_62_3_c;
    wire pp4_62_3_cout;
    wire pp4_62_4_s;
    wire pp4_62_4_c;
    wire pp4_62_fa_s;
    wire pp4_62_fa_c;
    wire pp4_62_ha_s;
    wire pp4_62_ha_c;

    Half_adder Half_adder_pp4_1(
        .a(pp3_1[0]),
        .b(pp3_1[1]),
        .S(pp4_1_ha_s),
        .C(pp4_1_ha_c)
    );
    E_4_2 E_4_2_pp4_2(
        .a(pp3_2[0]),
        .b(pp3_2[1]),
        .c(pp3_2[2]),
        .d(cin_net),
        .CIN(pp4_1_ha_c),
        .S(pp4_2_s),
        .C(pp4_2_c),
        .COUT(pp4_2_cout)
    );
    E_4_2 E_4_2_pp4_3(
        .a(pp3_3[0]),
        .b(pp3_3[1]),
        .c(pp3_3[2]),
        .d(pp3_3[3]),
        .CIN(pp4_2_cout),
        .S(pp4_3_s),
        .C(pp4_3_c),
        .COUT(pp4_3_cout)
    );
    E_4_2 E_4_2_pp4_4(
        .a(pp3_4[0]),
        .b(pp3_4[1]),
        .c(pp3_4[2]),
        .d(pp3_4[3]),
        .CIN(pp4_3_cout),
        .S(pp4_4_s),
        .C(pp4_4_c),
        .COUT(pp4_4_cout)
    );
    E_4_2 E_4_2_pp4_5(
        .a(pp3_5[0]),
        .b(pp3_5[1]),
        .c(pp3_5[2]),
        .d(pp3_5[3]),
        .CIN(pp4_4_cout),
        .S(pp4_5_s),
        .C(pp4_5_c),
        .COUT(pp4_5_cout)
    );
    E_4_2 E_4_2_pp4_6(
        .a(pp3_6[0]),
        .b(pp3_6[1]),
        .c(pp3_6[2]),
        .d(pp3_6[3]),
        .CIN(pp4_5_cout),
        .S(pp4_6_s),
        .C(pp4_6_c),
        .COUT(pp4_6_cout)
    );
    E_4_2 E_4_2_pp4_7(
        .a(pp3_7[0]),
        .b(pp3_7[1]),
        .c(pp3_7[2]),
        .d(pp3_7[3]),
        .CIN(pp4_6_cout),
        .S(pp4_7_s),
        .C(pp4_7_c),
        .COUT(pp4_7_cout)
    );
    E_4_2 E_4_2_pp4_8(
        .a(pp3_8[0]),
        .b(pp3_8[1]),
        .c(pp3_8[2]),
        .d(pp3_8[3]),
        .CIN(pp4_7_cout),
        .S(pp4_8_s),
        .C(pp4_8_c),
        .COUT(pp4_8_cout)
    );
    E_4_2 E_4_2_pp4_9(
        .a(pp3_9[0]),
        .b(pp3_9[1]),
        .c(pp3_9[2]),
        .d(pp3_9[3]),
        .CIN(pp4_8_cout),
        .S(pp4_9_s),
        .C(pp4_9_c),
        .COUT(pp4_9_cout)
    );
    E_4_2 E_4_2_pp4_10(
        .a(pp3_10[0]),
        .b(pp3_10[1]),
        .c(pp3_10[2]),
        .d(pp3_10[3]),
        .CIN(pp4_9_cout),
        .S(pp4_10_s),
        .C(pp4_10_c),
        .COUT(pp4_10_cout)
    );
    E_4_2 E_4_2_pp4_11(
        .a(pp3_11[0]),
        .b(pp3_11[1]),
        .c(pp3_11[2]),
        .d(pp3_11[3]),
        .CIN(pp4_10_cout),
        .S(pp4_11_s),
        .C(pp4_11_c),
        .COUT(pp4_11_cout)
    );
    E_4_2 E_4_2_pp4_12(
        .a(pp3_12[0]),
        .b(pp3_12[1]),
        .c(pp3_12[2]),
        .d(pp3_12[3]),
        .CIN(pp4_11_cout),
        .S(pp4_12_s),
        .C(pp4_12_c),
        .COUT(pp4_12_cout)
    );
    E_4_2 E_4_2_pp4_13(
        .a(pp3_13[0]),
        .b(pp3_13[1]),
        .c(pp3_13[2]),
        .d(pp3_13[3]),
        .CIN(pp4_12_cout),
        .S(pp4_13_s),
        .C(pp4_13_c),
        .COUT(pp4_13_cout)
    );
    E_4_2 E_4_2_pp4_14(
        .a(pp3_14[0]),
        .b(pp3_14[1]),
        .c(pp3_14[2]),
        .d(pp3_14[3]),
        .CIN(pp4_13_cout),
        .S(pp4_14_s),
        .C(pp4_14_c),
        .COUT(pp4_14_cout)
    );
    E_4_2 E_4_2_pp4_15(
        .a(pp3_15[0]),
        .b(pp3_15[1]),
        .c(pp3_15[2]),
        .d(pp3_15[3]),
        .CIN(pp4_14_cout),
        .S(pp4_15_s),
        .C(pp4_15_c),
        .COUT(pp4_15_cout)
    );
    E_4_2 E_4_2_pp4_16(
        .a(pp3_16[0]),
        .b(pp3_16[1]),
        .c(pp3_16[2]),
        .d(pp3_16[3]),
        .CIN(pp4_15_cout),
        .S(pp4_16_s),
        .C(pp4_16_c),
        .COUT(pp4_16_cout)
    );
    E_4_2 E_4_2_pp4_17(
        .a(pp3_17[0]),
        .b(pp3_17[1]),
        .c(pp3_17[2]),
        .d(pp3_17[3]),
        .CIN(pp4_16_cout),
        .S(pp4_17_s),
        .C(pp4_17_c),
        .COUT(pp4_17_cout)
    );
    E_4_2 E_4_2_pp4_18(
        .a(pp3_18[0]),
        .b(pp3_18[1]),
        .c(pp3_18[2]),
        .d(pp3_18[3]),
        .CIN(pp4_17_cout),
        .S(pp4_18_s),
        .C(pp4_18_c),
        .COUT(pp4_18_cout)
    );
    E_4_2 E_4_2_pp4_19(
        .a(pp3_19[0]),
        .b(pp3_19[1]),
        .c(pp3_19[2]),
        .d(pp3_19[3]),
        .CIN(pp4_18_cout),
        .S(pp4_19_s),
        .C(pp4_19_c),
        .COUT(pp4_19_cout)
    );
    E_4_2 E_4_2_pp4_20(
        .a(pp3_20[0]),
        .b(pp3_20[1]),
        .c(pp3_20[2]),
        .d(pp3_20[3]),
        .CIN(pp4_19_cout),
        .S(pp4_20_s),
        .C(pp4_20_c),
        .COUT(pp4_20_cout)
    );
    E_4_2 E_4_2_pp4_21(
        .a(pp3_21[0]),
        .b(pp3_21[1]),
        .c(pp3_21[2]),
        .d(pp3_21[3]),
        .CIN(pp4_20_cout),
        .S(pp4_21_s),
        .C(pp4_21_c),
        .COUT(pp4_21_cout)
    );
    E_4_2 E_4_2_pp4_22(
        .a(pp3_22[0]),
        .b(pp3_22[1]),
        .c(pp3_22[2]),
        .d(pp3_22[3]),
        .CIN(pp4_21_cout),
        .S(pp4_22_s),
        .C(pp4_22_c),
        .COUT(pp4_22_cout)
    );
    E_4_2 E_4_2_pp4_23(
        .a(pp3_23[0]),
        .b(pp3_23[1]),
        .c(pp3_23[2]),
        .d(pp3_23[3]),
        .CIN(pp4_22_cout),
        .S(pp4_23_s),
        .C(pp4_23_c),
        .COUT(pp4_23_cout)
    );
    E_4_2 E_4_2_pp4_24(
        .a(pp3_24[0]),
        .b(pp3_24[1]),
        .c(pp3_24[2]),
        .d(pp3_24[3]),
        .CIN(pp4_23_cout),
        .S(pp4_24_s),
        .C(pp4_24_c),
        .COUT(pp4_24_cout)
    );
    E_4_2 E_4_2_pp4_25(
        .a(pp3_25[0]),
        .b(pp3_25[1]),
        .c(pp3_25[2]),
        .d(pp3_25[3]),
        .CIN(pp4_24_cout),
        .S(pp4_25_s),
        .C(pp4_25_c),
        .COUT(pp4_25_cout)
    );
    E_4_2 E_4_2_pp4_26(
        .a(pp3_26[0]),
        .b(pp3_26[1]),
        .c(pp3_26[2]),
        .d(pp3_26[3]),
        .CIN(pp4_25_cout),
        .S(pp4_26_s),
        .C(pp4_26_c),
        .COUT(pp4_26_cout)
    );
    E_4_2 E_4_2_pp4_27(
        .a(pp3_27[0]),
        .b(pp3_27[1]),
        .c(pp3_27[2]),
        .d(pp3_27[3]),
        .CIN(pp4_26_cout),
        .S(pp4_27_s),
        .C(pp4_27_c),
        .COUT(pp4_27_cout)
    );
    E_4_2 E_4_2_pp4_28(
        .a(pp3_28[0]),
        .b(pp3_28[1]),
        .c(pp3_28[2]),
        .d(pp3_28[3]),
        .CIN(pp4_27_cout),
        .S(pp4_28_s),
        .C(pp4_28_c),
        .COUT(pp4_28_cout)
    );
    E_4_2 E_4_2_pp4_29(
        .a(pp3_29[0]),
        .b(pp3_29[1]),
        .c(pp3_29[2]),
        .d(pp3_29[3]),
        .CIN(pp4_28_cout),
        .S(pp4_29_s),
        .C(pp4_29_c),
        .COUT(pp4_29_cout)
    );
    E_4_2 E_4_2_pp4_30(
        .a(pp3_30[0]),
        .b(pp3_30[1]),
        .c(pp3_30[2]),
        .d(pp3_30[3]),
        .CIN(pp4_29_cout),
        .S(pp4_30_s),
        .C(pp4_30_c),
        .COUT(pp4_30_cout)
    );
    E_4_2 E_4_2_pp4_31(
        .a(pp3_31[0]),
        .b(pp3_31[1]),
        .c(pp3_31[2]),
        .d(pp3_31[3]),
        .CIN(pp4_30_cout),
        .S(pp4_31_s),
        .C(pp4_31_c),
        .COUT(pp4_31_cout)
    );
    E_4_2 E_4_2_pp4_32(
        .a(pp3_32[0]),
        .b(pp3_32[1]),
        .c(pp3_32[2]),
        .d(pp3_32[3]),
        .CIN(pp4_31_cout),
        .S(pp4_32_s),
        .C(pp4_32_c),
        .COUT(pp4_32_cout)
    );
    E_4_2 E_4_2_pp4_33(
        .a(pp3_33[0]),
        .b(pp3_33[1]),
        .c(pp3_33[2]),
        .d(pp3_33[3]),
        .CIN(pp4_32_cout),
        .S(pp4_33_s),
        .C(pp4_33_c),
        .COUT(pp4_33_cout)
    );
    E_4_2 E_4_2_pp4_34(
        .a(pp3_34[0]),
        .b(pp3_34[1]),
        .c(pp3_34[2]),
        .d(pp3_34[3]),
        .CIN(pp4_33_cout),
        .S(pp4_34_s),
        .C(pp4_34_c),
        .COUT(pp4_34_cout)
    );
    E_4_2 E_4_2_pp4_35(
        .a(pp3_35[0]),
        .b(pp3_35[1]),
        .c(pp3_35[2]),
        .d(pp3_35[3]),
        .CIN(pp4_34_cout),
        .S(pp4_35_s),
        .C(pp4_35_c),
        .COUT(pp4_35_cout)
    );
    E_4_2 E_4_2_pp4_36(
        .a(pp3_36[0]),
        .b(pp3_36[1]),
        .c(pp3_36[2]),
        .d(pp3_36[3]),
        .CIN(pp4_35_cout),
        .S(pp4_36_s),
        .C(pp4_36_c),
        .COUT(pp4_36_cout)
    );
    E_4_2 E_4_2_pp4_37(
        .a(pp3_37[0]),
        .b(pp3_37[1]),
        .c(pp3_37[2]),
        .d(pp3_37[3]),
        .CIN(pp4_36_cout),
        .S(pp4_37_s),
        .C(pp4_37_c),
        .COUT(pp4_37_cout)
    );
    E_4_2 E_4_2_pp4_38(
        .a(pp3_38[0]),
        .b(pp3_38[1]),
        .c(pp3_38[2]),
        .d(pp3_38[3]),
        .CIN(pp4_37_cout),
        .S(pp4_38_s),
        .C(pp4_38_c),
        .COUT(pp4_38_cout)
    );
    E_4_2 E_4_2_pp4_39(
        .a(pp3_39[0]),
        .b(pp3_39[1]),
        .c(pp3_39[2]),
        .d(pp3_39[3]),
        .CIN(pp4_38_cout),
        .S(pp4_39_s),
        .C(pp4_39_c),
        .COUT(pp4_39_cout)
    );
    E_4_2 E_4_2_pp4_40(
        .a(pp3_40[0]),
        .b(pp3_40[1]),
        .c(pp3_40[2]),
        .d(pp3_40[3]),
        .CIN(pp4_39_cout),
        .S(pp4_40_s),
        .C(pp4_40_c),
        .COUT(pp4_40_cout)
    );
    E_4_2 E_4_2_pp4_41(
        .a(pp3_41[0]),
        .b(pp3_41[1]),
        .c(pp3_41[2]),
        .d(pp3_41[3]),
        .CIN(pp4_40_cout),
        .S(pp4_41_s),
        .C(pp4_41_c),
        .COUT(pp4_41_cout)
    );
    E_4_2 E_4_2_pp4_42(
        .a(pp3_42[0]),
        .b(pp3_42[1]),
        .c(pp3_42[2]),
        .d(pp3_42[3]),
        .CIN(pp4_41_cout),
        .S(pp4_42_s),
        .C(pp4_42_c),
        .COUT(pp4_42_cout)
    );
    E_4_2 E_4_2_pp4_43(
        .a(pp3_43[0]),
        .b(pp3_43[1]),
        .c(pp3_43[2]),
        .d(pp3_43[3]),
        .CIN(pp4_42_cout),
        .S(pp4_43_s),
        .C(pp4_43_c),
        .COUT(pp4_43_cout)
    );
    E_4_2 E_4_2_pp4_44(
        .a(pp3_44[0]),
        .b(pp3_44[1]),
        .c(pp3_44[2]),
        .d(pp3_44[3]),
        .CIN(pp4_43_cout),
        .S(pp4_44_s),
        .C(pp4_44_c),
        .COUT(pp4_44_cout)
    );
    E_4_2 E_4_2_pp4_45(
        .a(pp3_45[0]),
        .b(pp3_45[1]),
        .c(pp3_45[2]),
        .d(pp3_45[3]),
        .CIN(pp4_44_cout),
        .S(pp4_45_s),
        .C(pp4_45_c),
        .COUT(pp4_45_cout)
    );
    E_4_2 E_4_2_pp4_46(
        .a(pp3_46[0]),
        .b(pp3_46[1]),
        .c(pp3_46[2]),
        .d(pp3_46[3]),
        .CIN(pp4_45_cout),
        .S(pp4_46_s),
        .C(pp4_46_c),
        .COUT(pp4_46_cout)
    );
    E_4_2 E_4_2_pp4_47(
        .a(pp3_47[0]),
        .b(pp3_47[1]),
        .c(pp3_47[2]),
        .d(pp3_47[3]),
        .CIN(pp4_46_cout),
        .S(pp4_47_s),
        .C(pp4_47_c),
        .COUT(pp4_47_cout)
    );
    E_4_2 E_4_2_pp4_48(
        .a(pp3_48[0]),
        .b(pp3_48[1]),
        .c(pp3_48[2]),
        .d(pp3_48[3]),
        .CIN(pp4_47_cout),
        .S(pp4_48_s),
        .C(pp4_48_c),
        .COUT(pp4_48_cout)
    );
    E_4_2 E_4_2_pp4_49(
        .a(pp3_49[0]),
        .b(pp3_49[1]),
        .c(pp3_49[2]),
        .d(pp3_49[3]),
        .CIN(pp4_48_cout),
        .S(pp4_49_s),
        .C(pp4_49_c),
        .COUT(pp4_49_cout)
    );
    E_4_2 E_4_2_pp4_50(
        .a(pp3_50[0]),
        .b(pp3_50[1]),
        .c(pp3_50[2]),
        .d(pp3_50[3]),
        .CIN(pp4_49_cout),
        .S(pp4_50_s),
        .C(pp4_50_c),
        .COUT(pp4_50_cout)
    );
    E_4_2 E_4_2_pp4_51(
        .a(pp3_51[0]),
        .b(pp3_51[1]),
        .c(pp3_51[2]),
        .d(pp3_51[3]),
        .CIN(pp4_50_cout),
        .S(pp4_51_s),
        .C(pp4_51_c),
        .COUT(pp4_51_cout)
    );
    E_4_2 E_4_2_pp4_52(
        .a(pp3_52[0]),
        .b(pp3_52[1]),
        .c(pp3_52[2]),
        .d(pp3_52[3]),
        .CIN(pp4_51_cout),
        .S(pp4_52_s),
        .C(pp4_52_c),
        .COUT(pp4_52_cout)
    );
    E_4_2 E_4_2_pp4_53(
        .a(pp3_53[0]),
        .b(pp3_53[1]),
        .c(pp3_53[2]),
        .d(pp3_53[3]),
        .CIN(pp4_52_cout),
        .S(pp4_53_s),
        .C(pp4_53_c),
        .COUT(pp4_53_cout)
    );
    E_4_2 E_4_2_pp4_54(
        .a(pp3_54[0]),
        .b(pp3_54[1]),
        .c(pp3_54[2]),
        .d(pp3_54[3]),
        .CIN(pp4_53_cout),
        .S(pp4_54_s),
        .C(pp4_54_c),
        .COUT(pp4_54_cout)
    );
    E_4_2 E_4_2_pp4_55(
        .a(pp3_55[0]),
        .b(pp3_55[1]),
        .c(pp3_55[2]),
        .d(pp3_55[3]),
        .CIN(pp4_54_cout),
        .S(pp4_55_s),
        .C(pp4_55_c),
        .COUT(pp4_55_cout)
    );
    E_4_2 E_4_2_pp4_56(
        .a(pp3_56[0]),
        .b(pp3_56[1]),
        .c(pp3_56[2]),
        .d(pp3_56[3]),
        .CIN(pp4_55_cout),
        .S(pp4_56_s),
        .C(pp4_56_c),
        .COUT(pp4_56_cout)
    );
    E_4_2 E_4_2_pp4_57(
        .a(pp3_57[0]),
        .b(pp3_57[1]),
        .c(pp3_57[2]),
        .d(pp3_57[3]),
        .CIN(pp4_56_cout),
        .S(pp4_57_s),
        .C(pp4_57_c),
        .COUT(pp4_57_cout)
    );
    E_4_2 E_4_2_pp4_58(
        .a(pp3_58[0]),
        .b(pp3_58[1]),
        .c(pp3_58[2]),
        .d(pp3_58[3]),
        .CIN(pp4_57_cout),
        .S(pp4_58_s),
        .C(pp4_58_c),
        .COUT(pp4_58_cout)
    );
    E_4_2 E_4_2_pp4_59(
        .a(pp3_59[0]),
        .b(pp3_59[1]),
        .c(pp3_59[2]),
        .d(pp3_59[3]),
        .CIN(pp4_58_cout),
        .S(pp4_59_s),
        .C(pp4_59_c),
        .COUT(pp4_59_cout)
    );
    E_4_2 E_4_2_pp4_60(
        .a(pp3_60[0]),
        .b(pp3_60[1]),
        .c(pp3_60[2]),
        .d(pp3_60[3]),
        .CIN(pp4_59_cout),
        .S(pp4_60_s),
        .C(pp4_60_c),
        .COUT(pp4_60_cout)
    );
    Full_adder Full_adder_pp4_61(
        .a(pp3_61[0]),
        .b(pp3_61[1]),
        .CIN(pp4_60_cout),
        .S(pp4_61_fa_s),
        .C(pp4_61_fa_c)
    );
           

    assign A = {pp3_63, pp3_62, pp4_61_fa_s, pp4_60_s, pp4_59_s, pp4_58_s, pp4_57_s, pp4_56_s, pp4_55_s, pp4_54_s, pp4_53_s, pp4_52_s, pp4_51_s, pp4_50_s, pp4_49_s, pp4_48_s, pp4_47_s, pp4_46_s, pp4_45_s, pp4_44_s, pp4_43_s, pp4_42_s, pp4_41_s, pp4_40_s, pp4_39_s, pp4_38_s, pp4_37_s, pp4_36_s, pp4_35_s, pp4_34_s, pp4_33_s, pp4_32_s, pp4_31_s, pp4_30_s, pp4_29_s, pp4_28_s, pp4_27_s, pp4_26_s, pp4_25_s, pp4_24_s, pp4_23_s, pp4_22_s, pp4_21_s, pp4_20_s, pp4_19_s, pp4_18_s, pp4_17_s, pp4_16_s, pp4_15_s, pp4_14_s, pp4_13_s, pp4_12_s, pp4_11_s, pp4_10_s, pp4_9_s, pp4_8_s, pp4_7_s, pp4_6_s, pp4_5_s, pp4_4_s, pp4_3_s, pp4_2_s, pp4_1_ha_s, pp3_0};
    assign B = {cin_net, pp4_61_fa_c, pp4_60_c, pp4_59_c, pp4_58_c, pp4_57_c, pp4_56_c, pp4_55_c, pp4_54_c, pp4_53_c, pp4_52_c, pp4_51_c, pp4_50_c, pp4_49_c, pp4_48_c, pp4_47_c, pp4_46_c, pp4_45_c, pp4_44_c, pp4_43_c, pp4_42_c, pp4_41_c, pp4_40_c, pp4_39_c, pp4_38_c, pp4_37_c, pp4_36_c, pp4_35_c, pp4_34_c, pp4_33_c, pp4_32_c, pp4_31_c, pp4_30_c, pp4_29_c, pp4_28_c, pp4_27_c, pp4_26_c, pp4_25_c, pp4_24_c, pp4_23_c, pp4_22_c, pp4_21_c, pp4_20_c, pp4_19_c, pp4_18_c, pp4_17_c, pp4_16_c, pp4_15_c, pp4_14_c, pp4_13_c, pp4_12_c, pp4_11_c, pp4_10_c, pp4_9_c, pp4_8_c, pp4_7_c, pp4_6_c, pp4_5_c, pp4_4_c, pp4_3_c, pp4_2_c, cin_net, cin_net, cin_net};
endmodule

