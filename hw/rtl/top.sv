//
// Sirius GPGPU - Top Module
// 顶层模块
//

module sirius_top (
    input  wire        clk,
    input  wire        rst_n,
    
    // 配置接口
    input  wire [31:0] start_addr,
    input  wire        start,
    output reg         done,
    
    // 内存接口
    output wire [31:0] mem_addr,
    output wire [31:0] mem_wdata,
    output wire [3:0]  mem_wstrb,
    output wire        mem_we,
    input  wire [31:0] mem_rdata,
    output wire        mem_req,
    input  wire        mem_ack
);

    // 内部信号
    wire [31:0] pc;
    wire [31:0] inst;
    wire        inst_valid;
    wire        inst_ready;
    
    wire [31:0] alu_result;
    wire [4:0]  alu_rd;
    wire        alu_rd_valid;
    
    wire [31:0] lsu_result;
    wire [4:0]  lsu_rd;
    wire        lsu_rd_valid;
    
    wire [31:0] rf_rdata1;
    wire [31:0] rf_rdata2;
    wire [4:0]  rf_raddr1;
    wire [4:0]  rf_raddr2;
    wire [31:0] rf_wdata;
    wire [4:0]  rf_waddr;
    wire        rf_we;
    
    // 状态机
    reg [1:0] state;
    localparam IDLE = 2'd0;
    localparam RUN  = 2'd1;
    localparam DONE = 2'd2;
    
    // 实例化取指模块
    fetch u_fetch (
        .clk(clk),
        .rst_n(rst_n),
        .start_addr(start_addr),
        .start(start && (state == IDLE)),
        .pc(pc),
        .inst(inst),
        .inst_valid(inst_valid),
        .inst_ready(inst_ready),
        .mem_addr(mem_addr),
        .mem_rdata(mem_rdata),
        .mem_req(mem_req),
        .mem_ack(mem_ack)
    );
    
    // 实例化译码模块
    decode u_decode (
        .clk(clk),
        .rst_n(rst_n),
        .inst(inst),
        .inst_valid(inst_valid),
        .inst_ready(inst_ready),
        .rf_raddr1(rf_raddr1),
        .rf_raddr2(rf_raddr2),
        .rf_rdata1(rf_rdata1),
        .rf_rdata2(rf_rdata2),
        .alu_result(alu_result),
        .alu_rd(alu_rd),
        .alu_rd_valid(alu_rd_valid),
        .lsu_result(lsu_result),
        .lsu_rd(lsu_rd),
        .lsu_rd_valid(lsu_rd_valid),
        .rf_wdata(rf_wdata),
        .rf_waddr(rf_waddr),
        .rf_we(rf_we)
    );
    
    // 实例化执行模块
    execute u_execute (
        .clk(clk),
        .rst_n(rst_n),
        .alu_result(alu_result),
        .alu_rd(alu_rd),
        .alu_rd_valid(alu_rd_valid)
    );
    
    // 实例化访存模块
    memory u_memory (
        .clk(clk),
        .rst_n(rst_n),
        .lsu_result(lsu_result),
        .lsu_rd(lsu_rd),
        .lsu_rd_valid(lsu_rd_valid)
    );
    
    // 实例化寄存器堆
    regfile u_regfile (
        .clk(clk),
        .rst_n(rst_n),
        .raddr1(rf_raddr1),
        .raddr2(rf_raddr2),
        .rdata1(rf_rdata1),
        .rdata2(rf_rdata2),
        .waddr(rf_waddr),
        .wdata(rf_wdata),
        .we(rf_we)
    );
    
    // 状态机
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            done <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    done <= 1'b0;
                    if (start) begin
                        state <= RUN;
                    end
                end
                RUN: begin
                    // 简化：检测RET指令或超时
                    if (inst_valid && (inst[31:24] == 8'h32)) begin
                        state <= DONE;
                        done <= 1'b1;
                    end
                end
                DONE: begin
                    if (!start) begin
                        state <= IDLE;
                        done <= 1'b0;
                    end
                end
                default: state <= IDLE;
            endcase
        end
    end

endmodule
