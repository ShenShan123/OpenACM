module MMssm_corr2_n23_m12(a, b, ris);

input wire [22:0] a;
input wire [22:0] b;
output wire [25:0] ris;

wire alfa_a, alfa_b;
reg  [11:0] assm, bssm;

assign alfa_a = (a[22] || a[21] || a[20] || a[19] || a[18] || a[17] || a[16] || a[15] || a[14] || a[13] || a[12]);
assign alfa_b = (b[22] || b[21] || b[20] || b[19] || b[18] || b[17] || b[16] || b[15] || b[14] || b[13] || b[12]);

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : assm <= 1'b0;
        2'b01 : assm <= 1'b0;
        2'b10 : assm <= 1'b0;
        default: assm <= a[22:17];
    endcase
end

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : bssm <= b[11];
        2'b01 : bssm <= b[22];
        2'b10 : bssm <= b[11];
        default: bssm <= b[22:17];
    endcase
end

reg [11:0] assum,bssum;
always@* begin
    case({alfa_a,alfa_b})
        2'b00 : assum <= a[11:0];
        2'b01 : assum <= a[11];
        2'b10 : assum <= a[22:11];
        default: assum <= a[22:11];
    endcase
end

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : bssum <= b[11:0];
        2'b01 : bssum <= b[22:11];
        2'b10 : bssum <= b[11];
        default: bssum <= b[22:11];
    endcase
end

// **** CORRECTION FACTOR ****
wire f11;
assign f11= alfa_a && alfa_b;
wire [13:0] correction_MSP;
assign correction_MSP = {(((a[16] && b[22]) || (b[16] && a[22])) && f11), (((a[16] && b[21]) || (b[16] && a[21])) && f11), 4'd0};

wire [13:0] mac_ssm;
assign mac_ssm = assm* /* cadence sub_arch non_booth */ bssm + assum + bssum + correction_MSP;

assign ris = ({alfa_a, alfa_b}==2'd0)? {mac_ssm,1'd0} : {mac_ssm, 12'd0};
endmodule
