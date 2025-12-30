// File Name: sram.v
// Module   : SRAM_6T_CORE_16x8_MC_TB
module SRAM_6T_CORE_16x8_MC_TB (
        input                    clk,
        input                    ce_in,     
        input                    we_in,     
        input  [3:0]  addr_in,   
        input  [7:0]        wd_in,     
        output reg [7:0]    rd_out 
);

    reg [7:0] mem [0:15];

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
        $setuphold(posedge clk, we_in, 0.000, 0.000, notifier);
        $setuphold(posedge clk, ce_in, 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[0], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[1], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[2], 0.000, 0.000, notifier);
        $setuphold(posedge clk, addr_in[3], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[0], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[1], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[2], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[3], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[4], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[5], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[6], 0.000, 0.000, notifier);
        $setuphold(posedge clk, wd_in[7], 0.000, 0.000, notifier);
        $width(posedge clk, 0, 0, notifier);
        $width(negedge clk, 0, 0, notifier);
        $period(posedge clk, 0, notifier);
    endspecify
endmodule