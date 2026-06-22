module MMssm_corr2_n23_m16(a, b, ris);

input wire [22:0] a;
input wire [22:0] b;
output wire [25:0] ris;

wire alfa_a, alfa_b;
reg  [15:0] assm, bssm;

assign alfa_a = (a[22] || a[21] || a[20] || a[19] || a[18] || a[17] || a[16]);
assign alfa_b = (b[22] || b[21] || b[20] || b[19] || b[18] || b[17] || b[16]);

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : assm <= a[15:12];
        2'b01 : assm <= a[15:12];
        2'b10 : assm <= a[22:19];
        default: assm <= a[22:15];
    endcase
end

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : bssm <= b[15:11];
        2'b01 : bssm <= b[22:18];
        2'b10 : bssm <= b[15:11];
        default: bssm <= b[22:15];
    endcase
end

reg [15:0] assum,bssum;
always@* begin
    case({alfa_a,alfa_b})
        2'b00 : assum <= a[15:0];
        2'b01 : assum <= a[15:7];
        2'b10 : assum <= a[22:7];
        default: assum <= a[22:7];
    endcase
end

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : bssum <= b[15:0];
        2'b01 : bssum <= b[22:7];
        2'b10 : bssum <= b[15:7];
        default: bssum <= b[22:7];
    endcase
end

// **** CORRECTION FACTOR ****
wire f11;
assign f11= alfa_a && alfa_b;
wire [17:0] correction_MSP;
assign correction_MSP = {(((a[14] && b[22]) || (b[14] && a[22])) && f11), (((a[14] && b[21]) || (b[14] && a[21])) && f11), 6'd0};

wire [17:0] mac_ssm;
assign mac_ssm = assm* /* cadence sub_arch non_booth */ bssm + assum + bssum + correction_MSP;

assign ris = ({alfa_a, alfa_b}==2'd0)? {mac_ssm,1'd0} : {mac_ssm, 8'd0};
endmodule
