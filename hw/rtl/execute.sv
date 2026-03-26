//
// Sirius GPGPU - Execute Module
// 执行模块
//

module execute (
    input  wire        clk,
    input  wire        rst_n,
    
    // 输出到写回
    output reg  [31:0] alu_result,
    output reg  [4:0]  alu_rd,
    output reg         alu_rd_valid
);

    // 简化执行模块
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            alu_result <= 32'd0;
            alu_rd <= 5'd0;
            alu_rd_valid <= 1'b0;
        end else begin
            // 占位：实际需要完整的ALU和FPU
            alu_rd_valid <= 1'b0;
        end
    end

endmodule
