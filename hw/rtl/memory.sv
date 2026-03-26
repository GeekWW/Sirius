//
// Sirius GPGPU - Memory Module
// 访存模块
//

module memory (
    input  wire        clk,
    input  wire        rst_n,
    
    // 输出到写回
    output reg  [31:0] lsu_result,
    output reg  [4:0]  lsu_rd,
    output reg         lsu_rd_valid
);

    // 简化访存模块
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            lsu_result <= 32'd0;
            lsu_rd <= 5'd0;
            lsu_rd_valid <= 1'b0;
        end else begin
            // 占位：实际需要完整的LSU和缓存
            lsu_rd_valid <= 1'b0;
        end
    end

endmodule
