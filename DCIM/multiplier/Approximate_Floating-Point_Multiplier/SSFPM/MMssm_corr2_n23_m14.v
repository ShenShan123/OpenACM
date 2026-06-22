module MMssm_corr2_n23_m14(a, b, ris);

input wire [22:0] a;
input wire [22:0] b;
output wire [25:0] ris;

wire alfa_a, alfa_b;
reg  [13:0] assm, bssm;

assign alfa_a = (a[22] || a[21] || a[20] || a[19] || a[18] || a[17] || a[16] || a[15] || a[14]);
assign alfa_b = (b[22] || b[21] || b[20] || b[19] || b[18] || b[17] || b[16] || b[15] || b[14]);

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : assm <= a[13:12];
        2'b01 : assm <= a[13:12];
        2'b10 : assm <= a[22:21];
        default: assm <= a[22:16];
    endcase
end

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : bssm <= b[13:11];
        2'b01 : bssm <= b[22:20];
        2'b10 : bssm <= b[13:11];
        default: bssm <= b[22:16];
    endcase
end

reg [13:0] assum,bssum;
always@* begin
    case({alfa_a,alfa_b})
        2'b00 : assum <= a[13:0];
        2'b01 : assum <= a[13:9];
        2'b10 : assum <= a[22:9];
        default: assum <= a[22:9];
    endcase
end

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : bssum <= b[13:0];
        2'b01 : bssum <= b[22:9];
        2'b10 : bssum <= b[13:9];
        default: bssum <= b[22:9];
    endcase
end


// **** CORRECTION FACTOR ****
wire f11;
assign f11= alfa_a && alfa_b;
wire [15:0] correction_MSP;
assign correction_MSP = {(((a[15] && b[22]) || (b[15] && a[22])) && f11), (((a[15] && b[21]) || (b[15] && a[21])) && f11), 5'd0};

wire [15:0] mac_ssm;
assign mac_ssm = assm* /* cadence sub_arch non_booth */ bssm + assum + bssum + correction_MSP;

assign ris = ({alfa_a, alfa_b}==2'd0)? {mac_ssm,1'd0} : {mac_ssm, 10'd0};
endmodule
