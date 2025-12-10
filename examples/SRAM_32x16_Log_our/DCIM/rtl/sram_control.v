// File Name: sram_control.v
// Module   : sram_multiplier_system 
module sram_multiplier_system (
    input                       clk,
    input                       rst_n,
    input                       pe_ce,         
    input                       init_enable,   
    input       [15:0]           data_in,      
    output reg  [31:0]          data_out,     
    output                      init_done,   
    output                      valid_out   
);

    parameter DATA_WIDTH = 16;
    parameter ADDR_COUNT = 32;
    parameter ADDR_WIDTH = 5;
    parameter MULT_WIDTH = 32;
    parameter MAX_ADDR = ADDR_COUNT - 1;

    parameter IDLE     = 2'b00;
    parameter INIT     = 2'b01;
    parameter RUN      = 2'b10;
    
    reg [1:0] curr_state;

    reg [ADDR_WIDTH-1:0] addr_ptr;         
    reg [ADDR_WIDTH-1:0] init_count;    
    reg [DATA_WIDTH-1:0] data_in_reg;      
    reg [DATA_WIDTH-1:0] sram_rdata_reg;  
    reg valid_reg_out;              

    wire [DATA_WIDTH-1:0] sram_rdata;
    wire [MULT_WIDTH-1:0] product;

    wire sram_we = (rst_n) ? (curr_state == INIT) : 1'b0;
    wire [ADDR_WIDTH-1:0] sram_addr = addr_ptr;

    SRAM_6T_CORE_32x16_MC_TB sram_inst (
        .clk(clk),
        .ce_in(~pe_ce),
        .we_in(~sram_we),
        .addr_in(sram_addr),
        .wd_in(data_in_reg),
        .rd_out(sram_rdata)
    );

    Log_our_16bit u_multiplier (
        data_in_reg,
        sram_rdata_reg,
        product
    );

    always @(posedge clk) begin
        if (!rst_n) begin
            curr_state <= IDLE;
            addr_ptr   <= 0;
            init_count <= 0;
        end else if (pe_ce) begin
            case (curr_state)
                IDLE: begin
                    if (init_enable) begin
                        curr_state <= INIT;
                        addr_ptr   <= 0;
                        init_count <= 0;
                    end else begin
                        addr_ptr   <= 0;
                        init_count <= 0;
                    end
                end
                INIT: begin
                    if (init_count == MAX_ADDR) begin
                        curr_state <= RUN;
                        addr_ptr   <= 0;
                    end else begin
                        init_count <= init_count + 1;
                        addr_ptr   <= addr_ptr + 1;
                    end
                end
                RUN: begin
                    addr_ptr <= (addr_ptr == MAX_ADDR) ? 0 : addr_ptr + 1;
                end
                default: begin
                    curr_state <= IDLE;
                    addr_ptr   <= 0;
                    init_count <= 0;
                end
            endcase
        end
    end

    always @(posedge clk) begin
        if (!rst_n) begin
            data_in_reg   <= 0;
            data_out      <= 0;
            valid_reg_out <= 0;
            sram_rdata_reg <= 0;
        end 
        else begin
            data_in_reg <= data_in;
            sram_rdata_reg <= sram_rdata;
            case (curr_state)
                IDLE, INIT: begin
                    data_out      <= 0;
                    valid_reg_out <= 1'b0;
                end
                RUN: begin
                    data_out      <= product;
                    valid_reg_out <= 1'b1; 
                end
                default: begin
                    data_out      <= 0;
                    valid_reg_out <= 1'b0;
                end
            endcase
            end
    end

    assign init_done = (curr_state == RUN);
    assign valid_out = valid_reg_out;

endmodule
