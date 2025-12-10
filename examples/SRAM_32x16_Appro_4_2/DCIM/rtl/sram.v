// File Name: sram.v
// Module   : SRAM_6T_CORE_32x16_MC_TB
module SRAM_6T_CORE_32x16_MC_TB (
        input                    clk,
        input                    ce_in,     
        input                    we_in,     
        input  [4:0]  addr_in,   
        input  [15:0]        wd_in,     
        output reg [15:0]    rd_out 
);

    reg [15:0] mem [0:31];

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
        $setuphold(posedge clk, we_in, 0.000, 0.000, notifier);
        $setuphold(posedge clk, ce_in, 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[0], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[1], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[2], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[3], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[4], 0.000, 0.000, notifier);
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
        $width(posedge clk, 0, 0, notifier);
        $width(negedge clk, 0, 0, notifier);
        $period(posedge clk, 0, notifier);
    endspecify
endmodule