//
// Sirius GPGPU - Decode Module
// 译码模块
//

module decode (
    input  wire        clk,
    input  wire        rst_n,
    
    // 指令输入
    input  wire [31:0] inst,
    input  wire        inst_valid,
    output reg         inst_ready,
    
    // 寄存器堆接口
    output reg  [4:0]  rf_raddr1,
    output reg  [4:0]  rf_raddr2,
    input  wire [31:0] rf_rdata1,
    input  wire [31:0] rf_rdata2,
    
    // 输出到执行模块
    output reg  [31:0] dec_inst,
    output reg         dec_inst_valid,
    output reg  [31:0] dec_rf_rdata1,
    output reg  [31:0] dec_rf_rdata2,
    
    // 写回接口
    input  wire [31:0] alu_result,
    input  wire [4:0]  alu_rd,
    input  wire        alu_rd_valid,
    input  wire [31:0] lsu_result,
    input  wire [4:0]  lsu_rd,
    input  wire        lsu_rd_valid,
    
    // 输出到寄存器堆写回
    output reg  [31:0] rf_wdata,
    output reg  [4:0]  rf_waddr,
    output reg         rf_we
);

    reg [7:0] opcode;
    reg [4:0] rd, rs1, rs2;
    reg [15:0] imm;
    reg [3:0] func;
    reg [7:0] offset;
    
    reg [2:0] state;
    
    localparam IDLE = 3'd0;
    localparam DEC  = 3'd1;
    localparam ISSUE = 3'd2;
    localparam WB   = 3'd3;
    
    // 译码逻辑
    always @(*) begin
        opcode = inst[31:24];
        rd = inst[23:19];
        rs1 = inst[18:14];
        rs2 = inst[13:9];
        func = inst[13:10];
        offset = inst[7:0];
        imm = inst[15:0];
    end
    
    // 状态机
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            inst_ready <= 1'b0;
            rf_raddr1 <= 5'd0;
            rf_raddr2 <= 5'd0;
            dec_inst <= 32'd0;
            dec_inst_valid <= 1'b0;
            dec_rf_rdata1 <= 32'd0;
            dec_rf_rdata2 <= 32'd0;
            rf_wdata <= 32'd0;
            rf_waddr <= 5'd0;
            rf_we <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    rf_we <= 1'b0;
                    dec_inst_valid <= 1'b0;
                    if (inst_valid) begin
                        rf_raddr1 <= rs1;
                        rf_raddr2 <= rs2;
                        inst_ready <= 1'b1;
                        state <= DEC;
                    end
                end
                
                DEC: begin
                    inst_ready <= 1'b0;
                    state <= ISSUE;
                end
                
                ISSUE: begin
                    // 发射到执行模块
                    dec_inst <= inst;
                    dec_inst_valid <= 1'b1;
                    dec_rf_rdata1 <= rf_rdata1;
                    dec_rf_rdata2 <= rf_rdata2;
                    state <= WB;
                end
                
                WB: begin
                    dec_inst_valid <= 1'b0;
                    
                    // ALU写回
                    if (alu_rd_valid) begin
                        rf_waddr <= alu_rd;
                        rf_wdata <= alu_result;
                        rf_we <= 1'b1;
                    end
                    // LSU写回
                    else if (lsu_rd_valid) begin
                        rf_waddr <= lsu_rd;
                        rf_wdata <= lsu_result;
                        rf_we <= 1'b1;
                    end
                    else begin
                        rf_we <= 1'b0;
                    end
                    
                    state <= IDLE;
                end
                
                default: state <= IDLE;
            endcase
        end
    end

endmodule
