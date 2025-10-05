// File Name: sram.v
// Module   : SRAM_6T_CORE_64x32_MC_TB
module SRAM_6T_CORE_64x32_MC_TB (
        input                    clk,
        input                    ce_in,     
        input                    we_in,     
        input  [5:0]  addr_in,   
        input  [31:0]        wd_in,     
        output reg [31:0]    rd_out 
);

    reg [31:0] mem [0:63];

    always @(posedge clk) begin
        if (!ce_in && !we_in) begin
            mem[addr_in] <= wd_in;
        end
    end
    
    always @(negedge clk) begin
        if (!ce_in && we_in) begin
            rd_out <= mem[addr_in]; 
        end
    end
    reg notifier;
    specify
        (posedge clk => rd_out[0]) = (0.000, 0.000);
        (posedge clk => rd_out[1]) = (0.000, 0.000);
        (posedge clk => rd_out[2]) = (0.000, 0.000);
        (posedge clk => rd_out[3]) = (0.000, 0.000);
        (posedge clk => rd_out[4]) = (0.000, 0.000);
        (posedge clk => rd_out[5]) = (0.000, 0.000);
        (posedge clk => rd_out[6]) = (0.000, 0.000);
        (posedge clk => rd_out[7]) = (0.000, 0.000);
        (posedge clk => rd_out[8]) = (0.000, 0.000);
        (posedge clk => rd_out[9]) = (0.000, 0.000);
        (posedge clk => rd_out[10]) = (0.000, 0.000);
        (posedge clk => rd_out[11]) = (0.000, 0.000);
        (posedge clk => rd_out[12]) = (0.000, 0.000);
        (posedge clk => rd_out[13]) = (0.000, 0.000);
        (posedge clk => rd_out[14]) = (0.000, 0.000);
        (posedge clk => rd_out[15]) = (0.000, 0.000);
        (posedge clk => rd_out[16]) = (0.000, 0.000);
        (posedge clk => rd_out[17]) = (0.000, 0.000);
        (posedge clk => rd_out[18]) = (0.000, 0.000);
        (posedge clk => rd_out[19]) = (0.000, 0.000);
        (posedge clk => rd_out[20]) = (0.000, 0.000);
        (posedge clk => rd_out[21]) = (0.000, 0.000);
        (posedge clk => rd_out[22]) = (0.000, 0.000);
        (posedge clk => rd_out[23]) = (0.000, 0.000);
        (posedge clk => rd_out[24]) = (0.000, 0.000);
        (posedge clk => rd_out[25]) = (0.000, 0.000);
        (posedge clk => rd_out[26]) = (0.000, 0.000);
        (posedge clk => rd_out[27]) = (0.000, 0.000);
        (posedge clk => rd_out[28]) = (0.000, 0.000);
        (posedge clk => rd_out[29]) = (0.000, 0.000);
        (posedge clk => rd_out[30]) = (0.000, 0.000);
        (posedge clk => rd_out[31]) = (0.000, 0.000);
        $setuphold(posedge clk, we_in, 0.000, 0.000, notifier);
        $setuphold(posedge clk, ce_in, 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[0], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[1], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[2], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[3], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[4], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[5], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[0], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[1], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[2], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[3], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[4], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[5], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[6], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[7], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[8], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[9], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[10], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[11], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[12], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[13], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[14], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[15], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[16], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[17], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[18], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[19], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[20], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[21], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[22], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[23], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[24], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[25], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[26], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[27], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[28], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[29], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[30], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[31], 0.000, 0.000, notifier);
        $width(posedge clk, 0, 0, notifier);
        $width(negedge clk, 0, 0, notifier);
        $period(posedge clk, 0, notifier);
    endspecify
endmodule