module MMssm_n23_m18(a, b, ris);

input wire [22:0] a;
input wire [22:0] b;
output wire [25:0] ris;

wire alfa_a, alfa_b;
reg  [17:0] assm, bssm;

assign alfa_a = (a[22] || a[21] || a[20] || a[19] || a[18]);
assign alfa_b = (b[22] || b[21] || b[20] || b[19] || b[18]);

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : assm <= a[17:12];
        2'b01 : assm <= a[17:12];
        2'b10 : assm <= a[22:17];
        default: assm <= a[22:14];
    endcase
end

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : bssm <= b[17:11];
        2'b01 : bssm <= b[22:16];
        2'b10 : bssm <= b[17:11];
        default: bssm <= b[22:14];
    endcase
end

reg [17:0] assum,bssum;
always@* begin
    case({alfa_a,alfa_b})
        2'b00 : assum <= a[17:0];
        2'b01 : assum <= a[17:5];
        2'b10 : assum <= a[22:5];
        default: assum <= a[22:5];
    endcase
end

always@* begin
    case({alfa_a,alfa_b})
        2'b00 : bssum <= b[17:0];
        2'b01 : bssum <= b[22:5];
        2'b10 : bssum <= b[17:5];
        default: bssum <= b[22:5];
    endcase
end

wire [19:0] mac_ssm;
assign mac_ssm = assm* /* cadence sub_arch non_booth */ bssm +assum+bssum;

assign ris = ({alfa_a, alfa_b}==2'd0)? {mac_ssm,1'd0} : {mac_ssm, 6'd0};
endmodule
