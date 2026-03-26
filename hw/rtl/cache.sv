//
// Sirius GPGPU - Cache Module
// 缓存模块
//

module cache (
    input  wire        clk,
    input  wire        rst_n,
    
    // CPU接口
    input  wire [31:0] cpu_addr,
    input  wire [31:0] cpu_wdata,
    input  wire [3:0]  cpu_wstrb,
    input  wire        cpu_we,
    output reg  [31:0] cpu_rdata,
    input  wire        cpu_req,
    output reg         cpu_ack,
    
    // 内存接口
    output reg  [31:0] mem_addr,
    output reg  [31:0] mem_wdata,
    output reg  [3:0]  mem_wstrb,
    output reg         mem_we,
    input  wire [31:0] mem_rdata,
    output reg         mem_req,
    input  wire        mem_ack
);

    // 简化的缓存实现
    // 实际需要完整的缓存逻辑
    
    reg [1:0] state;
    localparam IDLE = 2'd0;
    localparam READ = 2'd1;
    localparam WRITE = 2'd2;
    localparam WAIT_MEM = 2'd3;
    
    reg [31:0] saved_addr;
    reg [31:0] saved_wdata;
    reg [3:0]  saved_wstrb;
    reg         saved_we;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            cpu_rdata <= 32'd0;
            cpu_ack <= 1'b0;
            mem_addr <= 32'd0;
            mem_wdata <= 32'd0;
            mem_wstrb <= 4'd0;
            mem_we <= 1'b0;
            mem_req <= 1'b0;
            saved_addr <= 32'd0;
            saved_wdata <= 32'd0;
            saved_wstrb <= 4'd0;
            saved_we <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    cpu_ack <= 1'b0;
                    mem_req <= 1'b0;
                    if (cpu_req) begin
                        saved_addr <= cpu_addr;
                        saved_wdata <= cpu_wdata;
                        saved_wstrb <= cpu_wstrb;
                        saved_we <= cpu_we;
                        
                        // 简化：直接访问内存
                        mem_addr <= cpu_addr;
                        mem_wdata <= cpu_wdata;
                        mem_wstrb <= cpu_wstrb;
                        mem_we <= cpu_we;
                        mem_req <= 1'b1;
                        state <= WAIT_MEM;
                    end
                end
                
                WAIT_MEM: begin
                    mem_req <= 1'b0;
                    if (mem_ack) begin
                        if (!saved_we) begin
                            cpu_rdata <= mem_rdata;
                        end
                        cpu_ack <= 1'b1;
                        state <= IDLE;
                    end
                end
                
                default: state <= IDLE;
            endcase
        end
    end

endmodule
