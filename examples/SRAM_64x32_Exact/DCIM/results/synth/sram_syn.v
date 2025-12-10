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
endmodule