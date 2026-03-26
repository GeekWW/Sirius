//
// Sirius GPGPU - Register File
// 寄存器堆
//

module regfile (
    input  wire        clk,
    input  wire        rst_n,
    
    // 读端口1
    input  wire [4:0]  raddr1,
    output reg  [31:0] rdata1,
    
    // 读端口2
    input  wire [4:0]  raddr2,
    output reg  [31:0] rdata2,
    
    // 写端口
    input  wire [4:0]  waddr,
    input  wire [31:0] wdata,
    input  wire        we
);

    reg [31:0] regs [0:31];
    integer i;
    
    // R0 硬连线为0
    always @(*) begin
        if (raddr1 == 5'd0) begin
            rdata1 = 32'd0;
        end else begin
            rdata1 = regs[raddr1];
        end
        
        if (raddr2 == 5'd0) begin
            rdata2 = 32'd0;
        end else begin
            rdata2 = regs[raddr2];
        end
    end
    
    // 写操作
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 32; i = i + 1) begin
                regs[i] <= 32'd0;
            end
        end else begin
            if (we && (waddr != 5'd0)) begin
                regs[waddr] <= wdata;
            end
        end
    end

endmodule
