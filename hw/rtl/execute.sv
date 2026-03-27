//
// Sirius GPGPU - Execute Module
// 执行模块
//

module execute (
    input  wire        clk,
    input  wire        rst_n,
    
    // 从译码模块输入
    input  wire [31:0] inst,
    input  wire        inst_valid,
    input  wire [31:0] rf_rdata1,
    input  wire [31:0] rf_rdata2,
    
    // 输出到写回
    output reg  [31:0] alu_result,
    output reg  [4:0]  alu_rd,
    output reg         alu_rd_valid
);

    reg [7:0] opcode;
    reg [4:0] rd;
    reg [3:0] func;
    reg [15:0] imm;
    reg [31:0] operand1, operand2;
    reg [3:0] state;
    
    localparam IDLE = 3'd0;
    localparam DEC  = 3'd1;
    localparam EXEC = 3'd2;
    localparam WB   = 3'd3;
    
    // 指令译码
    always @(*) begin
        opcode = inst[31:24];
        rd = inst[23:19];
        func = inst[13:10];
        imm = inst[15:0];
    end
    
    // ALU操作
    always @(*) begin
        operand1 = rf_rdata1;
        // 立即数扩展（符号扩展）
        operand2 = (opcode[7] == 1'b1) ? {{16{imm[15]}}, imm} : rf_rdata2;
    end
    
    // 状态机
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            alu_result <= 32'd0;
            alu_rd <= 5'd0;
            alu_rd_valid <= 1'b0;
            state <= IDLE;
        end else begin
            case (state)
                IDLE: begin
                    alu_rd_valid <= 1'b0;
                    if (inst_valid) begin
                        state <= DEC;
                    end
                end
                
                DEC: begin
                    state <= EXEC;
                end
                
                EXEC: begin
                    // ALU运算
                    case (opcode)
                        // 算术运算
                        8'h01: alu_result <= operand1 + operand2;                    // ADD
                        8'h02: alu_result <= operand1 - operand2;                    // SUB
                        8'h03: alu_result <= operand1 * operand2;                    // MUL
                        8'h04: alu_result <= operand1 / operand2;                    // DIV
                        8'h05: alu_result <= operand1 % operand2;                    // MOD
                        
                        // 逻辑运算
                        8'h11: alu_result <= operand1 & operand2;                     // AND
                        8'h12: alu_result <= operand1 | operand2;                     // OR
                        8'h13: alu_result <= operand1 ^ operand2;                     // XOR
                        8'h14: alu_result <= ~operand1;                                // NOT
                        
                        // 移位运算
                        8'h21: alu_result <= operand1 << operand2[4:0];               // SLL
                        8'h22: alu_result <= operand1 >> operand2[4:0];               // SRL
                        8'h23: alu_result <= $signed(operand1) >>> operand2[4:0];    // SRA
                        
                        // 比较运算
                        8'h31: alu_result <= (operand1 == operand2) ? 32'd1 : 32'd0;  // EQ
                        8'h32: alu_result <= (operand1 != operand2) ? 32'd1 : 32'd0;  // NE
                        8'h33: alu_result <= (operand1 < operand2) ? 32'd1 : 32'd0;   // LT
                        8'h34: alu_result <= (operand1 <= operand2) ? 32'd1 : 32'd0;  // LE
                        8'h35: alu_result <= (operand1 > operand2) ? 32'd1 : 32'd0;   // GT
                        8'h36: alu_result <= (operand1 >= operand2) ? 32'd1 : 32'd0;  // GE
                        
                        // 立即数加载
                        8'h41: alu_result <= {{16{imm[15]}}, imm};                    // LI
                        8'h42: alu_result <= {imm, 16'd0};                             // LUI
                        
                        // 移动指令
                        8'h51: alu_result <= operand1;                                // MOV
                        
                        // 默认
                        default: alu_result <= 32'd0;
                    endcase
                    
                    alu_rd <= rd;
                    state <= WB;
                end
                
                WB: begin
                    alu_rd_valid <= 1'b1;
                    state <= IDLE;
                end
                
                default: state <= IDLE;
            endcase
        end
    end

endmodule
