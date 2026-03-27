//
// Sirius GPGPU - Memory Module (LSU)
// 访存模块（Load/Store Unit）
//

module memory (
    input  wire        clk,
    input  wire        rst_n,
    
    // 从译码模块输入
    input  wire [31:0] inst,
    input  wire        inst_valid,
    input  wire [31:0] rf_rdata1,
    input  wire [31:0] rf_rdata2,
    
    // 到内存接口
    output reg  [31:0] mem_addr,
    output reg  [31:0] mem_wdata,
    output reg  [3:0]  mem_wstrb,
    output reg         mem_we,
    input  wire [31:0] mem_rdata,
    output reg         mem_req,
    input  wire        mem_ack,
    
    // 写回接口
    output reg  [31:0] lsu_result,
    output reg  [4:0]  lsu_rd,
    output reg         lsu_rd_valid
);

    // 指令译码
    reg [7:0] opcode;
    reg [4:0] rd, rs1, rs2;
    reg [3:0] func;
    reg [15:0] offset;
    reg [1:0] width;  // 00=byte, 01=half-word, 10=word
    reg sign_extend;
    
    // 内部信号
    reg [31:0] addr;
    reg [31:0] data_to_store;
    reg [3:0] byte_enable;
    reg [31:0] loaded_data;
    
    // 状态机
    reg [2:0] state;
    localparam IDLE   = 3'd0;
    localparam DEC    = 3'd1;
    localparam REQ    = 3'd2;
    localparam WAIT   = 3'd3;
    localparam ADJUST = 3'd4;
    localparam WB     = 3'd5;
    
    // 指令译码
    always @(*) begin
        opcode = inst[31:24];
        rd = inst[23:19];
        rs1 = inst[18:14];
        rs2 = inst[13:9];
        func = inst[13:10];
        offset = inst[15:0];
        
        // 默认值
        width = 2'b10;  // 默认 word
        sign_extend = 1'b1;
    end
    
    // 地址计算
    always @(*) begin
        // 地址 = rs1 + offset（符号扩展）
        addr = rf_rdata1 + {{16{offset[15]}}, offset};
    end
    
    // 字节使能和数据准备
    always @(*) begin
        // 默认值
        data_to_store = rf_rdata2;
        byte_enable = 4'b1111;
        
        case (opcode)
            // 字节加载/存储
            8'h20, 8'h28: begin
                width = 2'b00;
                case (addr[1:0])
                    2'b00: byte_enable = 4'b0001;
                    2'b01: byte_enable = 4'b0010;
                    2'b10: byte_enable = 4'b0100;
                    2'b11: byte_enable = 4'b1000;
                endcase
                // 数据对齐
                data_to_store = rf_rdata2 << (addr[1:0] * 8);
            end
            
            // 半字加载/存储
            8'h21, 8'h29: begin
                width = 2'b01;
                if (addr[1]) begin
                    byte_enable = 4'b1100;
                    data_to_store = rf_rdata2 << 16;
                end else begin
                    byte_enable = 4'b0011;
                    data_to_store = rf_rdata2;
                end
            end
            
            // 字加载/存储
            8'h22, 8'h2A: begin
                width = 2'b10;
                byte_enable = 4'b1111;
                data_to_store = rf_rdata2;
            end
            
            default: begin
                byte_enable = 4'b1111;
                data_to_store = rf_rdata2;
            end
        endcase
    end
    
    // 加载数据调整
    always @(*) begin
        loaded_data = mem_rdata;
        
        case (width)
            2'b00: begin  // byte
                case (addr[1:0])
                    2'b00: loaded_data = {{24{sign_extend & mem_rdata[7]}}, mem_rdata[7:0]};
                    2'b01: loaded_data = {{24{sign_extend & mem_rdata[15]}}, mem_rdata[15:8]};
                    2'b10: loaded_data = {{24{sign_extend & mem_rdata[23]}}, mem_rdata[23:16]};
                    2'b11: loaded_data = {{24{sign_extend & mem_rdata[31]}}, mem_rdata[31:24]};
                endcase
            end
            
            2'b01: begin  // half-word
                if (addr[1]) begin
                    loaded_data = {{16{sign_extend & mem_rdata[31]}}, mem_rdata[31:16]};
                end else begin
                    loaded_data = {{16{sign_extend & mem_rdata[15]}}, mem_rdata[15:0]};
                end
            end
            
            2'b10: begin  // word
                loaded_data = mem_rdata;
            end
            
            default: begin
                loaded_data = mem_rdata;
            end
        endcase
    end
    
    // 状态机
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            mem_addr <= 32'd0;
            mem_wdata <= 32'd0;
            mem_wstrb <= 4'b0000;
            mem_we <= 1'b0;
            mem_req <= 1'b0;
            lsu_result <= 32'd0;
            lsu_rd <= 5'd0;
            lsu_rd_valid <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    lsu_rd_valid <= 1'b0;
                    mem_req <= 1'b0;
                    mem_we <= 1'b0;
                    
                    if (inst_valid) begin
                        state <= DEC;
                    end
                end
                
                DEC: begin
                    // 检查是否是 Load/Store 指令
                    case (opcode)
                        8'h20, 8'h21, 8'h22,  // Load
                        8'h28, 8'h29, 8'h2A:  // Store
                        begin
                            state <= REQ;
                        end
                        default: begin
                            // 不是访存指令，直接返回
                            lsu_rd_valid <= 1'b0;
                            state <= IDLE;
                        end
                    endcase
                end
                
                REQ: begin
                    mem_addr <= addr;
                    mem_wdata <= data_to_store;
                    mem_wstrb <= byte_enable;
                    mem_we <= (opcode[7] == 1'b1);  // Store 指令
                    mem_req <= 1'b1;
                    state <= WAIT;
                end
                
                WAIT: begin
                    mem_req <= 1'b0;
                    if (mem_ack) begin
                        state <= ADJUST;
                    end
                end
                
                ADJUST: begin
                    // Load 指令需要写回
                    if (!mem_we) begin
                        lsu_result <= loaded_data;
                        lsu_rd <= rd;
                    end
                    state <= WB;
                end
                
                WB: begin
                    if (!mem_we) begin
                        lsu_rd_valid <= 1'b1;
                    end
                    state <= IDLE;
                end
                
                default: state <= IDLE;
            endcase
        end
    end

endmodule