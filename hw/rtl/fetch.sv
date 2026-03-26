//
// Sirius GPGPU - Fetch Module
// 取指模块
//

module fetch (
    input  wire        clk,
    input  wire        rst_n,
    
    // 启动接口
    input  wire [31:0] start_addr,
    input  wire        start,
    
    // PC输出
    output reg  [31:0] pc,
    
    // 指令输出
    output reg  [31:0] inst,
    output reg         inst_valid,
    input  wire        inst_ready,
    
    // 内存接口
    output reg  [31:0] mem_addr,
    input  wire [31:0] mem_rdata,
    output reg         mem_req,
    input  wire        mem_ack
);

    reg [31:0] next_pc;
    reg [1:0] state;
    
    localparam IDLE = 2'd0;
    localparam REQ  = 2'd1;
    localparam WAIT = 2'd2;
    localparam OUT  = 2'd3;
    
    // 状态机
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            pc <= 32'd0;
            next_pc <= 32'd0;
            inst <= 32'd0;
            inst_valid <= 1'b0;
            mem_addr <= 32'd0;
            mem_req <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    inst_valid <= 1'b0;
                    mem_req <= 1'b0;
                    if (start) begin
                        pc <= start_addr;
                        next_pc <= start_addr + 32'd4;
                        state <= REQ;
                    end
                end
                
                REQ: begin
                    mem_addr <= pc;
                    mem_req <= 1'b1;
                    state <= WAIT;
                end
                
                WAIT: begin
                    mem_req <= 1'b0;
                    if (mem_ack) begin
                        inst <= mem_rdata;
                        state <= OUT;
                    end
                end
                
                OUT: begin
                    inst_valid <= 1'b1;
                    if (inst_ready) begin
                        pc <= next_pc;
                        next_pc <= next_pc + 32'd4;
                        inst_valid <= 1'b0;
                        state <= REQ;
                    end
                end
                
                default: state <= IDLE;
            endcase
        end
    end

endmodule
