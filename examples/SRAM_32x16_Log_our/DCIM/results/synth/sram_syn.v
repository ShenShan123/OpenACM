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
endmodule