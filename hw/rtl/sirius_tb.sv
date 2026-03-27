//
// Sirius GPGPU - Testbench
// 测试平台
//

`timescale 1ns/1ps

module sirius_tb;

    reg clk;
    reg rst_n;
    
    reg [31:0] start_addr;
    reg start;
    wire done;
    
    wire [31:0] mem_addr;
    wire [31:0] mem_wdata;
    wire [3:0]  mem_wstrb;
    wire        mem_we;
    reg [31:0]  mem_rdata;
    wire        mem_req;
    reg         mem_ack;
    
    // 内存模型（简单的数组）
    reg [31:0] mem [0:1023];
    
    // 实例化DUT
    sirius_integration u_dut (
        .clk(clk),
        .rst_n(rst_n),
        .start_addr(start_addr),
        .start(start),
        .done(done),
        .mem_addr(mem_addr),
        .mem_wdata(mem_wdata),
        .mem_wstrb(mem_wstrb),
        .mem_we(mem_we),
        .mem_rdata(mem_rdata),
        .mem_req(mem_req),
        .mem_ack(mem_ack)
    );
    
    // 时钟生成
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end
    
    // 内存响应
    always @(posedge clk) begin
        mem_ack <= 1'b0;
        if (mem_req) begin
            #1;
            if (!mem_we) begin
                mem_rdata <= mem[mem_addr[11:2]];
            end else begin
                if (mem_wstrb[0]) mem[mem_addr[11:2]][7:0]   <= mem_wdata[7:0];
                if (mem_wstrb[1]) mem[mem_addr[11:2]][15:8]  <= mem_wdata[15:8];
                if (mem_wstrb[2]) mem[mem_addr[11:2]][23:16] <= mem_wdata[23:16];
                if (mem_wstrb[3]) mem[mem_addr[11:2]][31:24] <= mem_wdata[31:24];
            end
            mem_ack <= 1'b1;
        end
    end
    
    // 测试程序
    initial begin
        // 初始化
        rst_n = 0;
        start = 0;
        start_addr = 0;
        
        // 初始化内存（测试程序：1+2）
        // LI r1, 1
        mem[0] = {8'h41, 5'd1, 5'd0, 5'd0, 4'd0, 8'd1};
        // LI r2, 2
        mem[1] = {8'h41, 5'd2, 5'd0, 5'd0, 4'd0, 8'd2};
        // ADD r3, r1, r2
        mem[2] = {8'h01, 5'd3, 5'd1, 5'd2, 4'd0, 8'd0};
        // RET
        mem[3] = {8'h32, 24'd0};
        
        // 复位
        #100;
        rst_n = 1;
        #100;
        
        // 启动测试
        $display("Starting test...");
        start = 1;
        start_addr = 0;
        #10;
        start = 0;
        
        // 等待完成
        wait (done);
        #100;
        
        // 检查结果
        $display("Test completed!");
        $display("Register file r3 should be 3");
        
        // 显示内存内容
        $display("Memory contents:");
        for (int i = 0; i < 4; i++) begin
            $display("mem[%0d] = 0x%h", i, mem[i]);
        end
        
        #100;
        $finish;
    end
    
    // 波形输出
    initial begin
        $dumpfile("sirius_tb.vcd");
        $dumpvars(0, sirius_tb);
    end

endmodule