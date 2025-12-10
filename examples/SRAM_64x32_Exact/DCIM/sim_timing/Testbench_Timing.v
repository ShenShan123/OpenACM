`timescale 1ns / 1ps

module testbench;

    parameter DATA_WIDTH = 32;
    parameter ADDR_COUNT = 64;
    parameter ADDR_WIDTH = 6;
    parameter MULT_WIDTH = DATA_WIDTH * 2;

    reg clk;
    reg rst_n;
    reg sram_ce;
    reg init_enable;
    reg [DATA_WIDTH-1:0] data_in;
    wire [MULT_WIDTH-1:0] data_out;
    wire init_done;
    wire valid_out;

    sram_multiplier_system dut (
        .clk(clk),
        .rst_n(rst_n),
        .pe_ce(sram_ce),
        .init_enable(init_enable),
        .data_in(data_in),
        .data_out(data_out),
        .init_done(init_done),
        .valid_out(valid_out)
    );

    always #5 clk = ~clk;

    reg [DATA_WIDTH-1:0] sram_data [0:ADDR_COUNT-1];
    integer i;

    initial begin
        clk         = 0;
        rst_n       = 1;
        sram_ce     = 1;
        init_enable = 0;
        data_in     = 0;
        
        repeat(3) begin
            @(negedge clk);
            rst_n = 0;
            #20
            rst_n = 1;

            init_enable = 1;
            for (i = 0; i < ADDR_COUNT; i = i + 1) begin
                @(negedge clk);
                data_in = $urandom;
                
            end
            init_enable = 0;

            for (i = 0; i < ADDR_COUNT; i = i + 1) begin
                @(negedge clk);
                data_in = $urandom;
                
            end
        end
        $finish;
    end

    reg [ADDR_WIDTH-1:0] addr_counter;
    initial addr_counter = 0;

    always @(posedge clk) begin
        if (rst_n && valid_out) begin
            $display("Output = %0d",data_out);
            if (addr_counter == ADDR_COUNT - 1)
                addr_counter <= 0;
            else
                addr_counter <= addr_counter + 1;
        end
    end

   initial begin
       $sdf_annotate("./DCIM/results/routing/timing_rout.sdf", dut,,, "MAXIMUM", "1:1:1", "FROM_MTM");
   end
   
   initial begin
       $dumpfile("./DCIM/results/routing/power_rout.vcd");
       $dumpvars(0, testbench);
       $vcdpluson;
   end

endmodule