#!/usr/bin/env python3
"""
Sirius GPGPU Assembler
汇编器：将汇编代码转换为32位机器码
"""

from typing import List, Tuple, Dict, Optional
import struct


class Instruction:
    """指令定义"""
    def __init__(self, opcode: int, name: str, format: str, type: str = "必选"):
        self.opcode = opcode
        self.name = name
        self.format = format  # "RRR", "RI", "RPF"
        self.type = type


# 指令集定义
INSTRUCTIONS = {
    # 算术运算指令
    "ADD.F32": Instruction(0x01, "ADD.F32", "RRR", "必选"),
    "SUB.F32": Instruction(0x02, "SUB.F32", "RRR", "必选"),
    "MUL.F32": Instruction(0x03, "MUL.F32", "RRR", "必选"),
    "DIV.F32": Instruction(0x04, "DIV.F32", "RRR", "必选"),
    "ADD.I32": Instruction(0x05, "ADD.I32", "RRR", "必选"),
    "SUB.I32": Instruction(0x06, "SUB.I32", "RRR", "必选"),
    "MUL.I32": Instruction(0x07, "MUL.I32", "RRR", "必选"),
    "NEG.F32": Instruction(0x08, "NEG.F32", "RR", "可选"),
    "NEG.I32": Instruction(0x09, "NEG.I32", "RR", "可选"),
    "REM.I32": Instruction(0x0A, "REM.I32", "RRR", "可选"),
    "DIV.U32": Instruction(0x0B, "DIV.U32", "RRR", "可选"),
    
    # 逻辑运算指令
    "AND": Instruction(0x10, "AND", "RRR", "必选"),
    "OR": Instruction(0x11, "OR", "RRR", "必选"),
    "XOR": Instruction(0x12, "XOR", "RRR", "必选"),
    "NOT": Instruction(0x13, "NOT", "RR", "必选"),
    "ICMP": Instruction(0x14, "ICMP", "RPF", "必选"),
    "FCMP": Instruction(0x15, "FCMP", "RPF", "必选"),
    "ICMP.U": Instruction(0x16, "ICMP.U", "RPF", "可选"),
    "FCMP.NAN": Instruction(0x17, "FCMP.NAN", "RR", "可选"),
    
    # 内存访问指令
    "LD.GLOBAL": Instruction(0x20, "LD.GLOBAL", "RRI", "必选"),
    "LD.LOCAL": Instruction(0x21, "LD.LOCAL", "RRI", "必选"),
    "LD.PRIVATE": Instruction(0x22, "LD.PRIVATE", "RRI", "必选"),
    "LD.CONST": Instruction(0x23, "LD.CONST", "RRI", "必选"),
    "ST.GLOBAL": Instruction(0x24, "ST.GLOBAL", "RRI", "必选"),
    "ST.LOCAL": Instruction(0x25, "ST.LOCAL", "RRI", "必选"),
    "ST.PRIVATE": Instruction(0x26, "ST.PRIVATE", "RRI", "必选"),
    "GEP": Instruction(0x27, "GEP", "RRR", "必选"),
    "LD.GLOBAL.STRIDE": Instruction(0x28, "LD.GLOBAL.STRIDE", "RRR", "可选"),
    
    # 控制流指令
    "BR.COND": Instruction(0x30, "BR.COND", "RI", "必选"),
    "BR.UNCOND": Instruction(0x31, "BR.UNCOND", "I", "必选"),
    "RET": Instruction(0x32, "RET", "", "必选"),
    "BR.LOOP": Instruction(0x33, "BR.LOOP", "RI", "可选"),
    
    # 并行相关指令
    "GET_GLOBAL_ID": Instruction(0x40, "GET_GLOBAL_ID", "RRI", "必选"),
    "GET_LOCAL_ID": Instruction(0x41, "GET_LOCAL_ID", "RRI", "必选"),
    "GET_GLOBAL_SIZE": Instruction(0x42, "GET_GLOBAL_SIZE", "RRI", "必选"),
    "GET_LOCAL_SIZE": Instruction(0x43, "GET_LOCAL_SIZE", "RRI", "必选"),
    "GET_GROUP_ID": Instruction(0x44, "GET_GROUP_ID", "RRI", "必选"),
    "GET_NUM_GROUPS": Instruction(0x45, "GET_NUM_GROUPS", "RRI", "必选"),
    "BARRIER_LOCAL": Instruction(0x46, "BARRIER_LOCAL", "", "必选"),
    "BARRIER_GLOBAL": Instruction(0x47, "BARRIER_GLOBAL", "", "可选"),
}


class Assembler:
    """Sirius GPGPU 汇编器"""
    
    def __init__(self):
        self.instructions = INSTRUCTIONS
        self.symbol_table: Dict[str, int] = {}
    
    def parse_register(self, reg_str: str) -> int:
        """解析寄存器，返回寄存器编号 (0-31)"""
        if reg_str.startswith('R') or reg_str.startswith('r'):
            return int(reg_str[1:])
        raise ValueError(f"Invalid register: {reg_str}")
    
    def encode_rrr(self, opcode: int, rd: int, rs1: int, rs2: int) -> int:
        """三寄存器格式编码：8位opcode + 8位Rd + 8位Rs1 + 8位Rs2"""
        return (opcode << 24) | ((rd & 0xFF) << 16) | ((rs1 & 0xFF) << 8) | (rs2 & 0xFF)
    
    def encode_rr(self, opcode: int, rd: int, rs1: int) -> int:
        """双寄存器格式编码：8位opcode + 8位Rd + 8位Rs1 + 8位保留"""
        return (opcode << 24) | ((rd & 0xFF) << 16) | ((rs1 & 0xFF) << 8)
    
    def encode_ri(self, opcode: int, rd: int, imm: int) -> int:
        """寄存器+立即数格式编码：8位opcode + 8位Rd + 16位立即数"""
        return (opcode << 24) | ((rd & 0xFF) << 16) | (imm & 0xFFFF)
    
    def encode_i(self, opcode: int, imm: int) -> int:
        """仅立即数格式编码：8位opcode + 24位立即数/地址"""
        return (opcode << 24) | (imm & 0xFFFFFF)
    
    def encode_rpf(self, opcode: int, rd: int, rs1: int, func: int) -> int:
        """多字段功能位格式编码：8位opcode + 8位Rd + 8位Rs1 + 4位功能位 + 4位保留"""
        return (opcode << 24) | ((rd & 0xFF) << 16) | ((rs1 & 0xFF) << 8) | ((func & 0x0F) << 4)
    
    def encode_rri(self, opcode: int, rd: int, rs1: int, offset: int) -> int:
        """寄存器+寄存器+偏移格式编码：8位opcode + 8位Rd + 8位Rs1 + 8位偏移"""
        return (opcode << 24) | ((rd & 0xFF) << 16) | ((rs1 & 0xFF) << 8) | (offset & 0xFF)
    
    def assemble_line(self, line: str) -> Optional[int]:
        """汇编单行代码"""
        line = line.strip()
        if not line or line.startswith(';') or line.startswith('#'):
            return None
        
        # 去除注释
        line = line.split(';')[0].split('#')[0].strip()
        
        parts = line.split()
        if not parts:
            return None
        
        mnemonic = parts[0].upper()
        if mnemonic not in self.instructions:
            raise ValueError(f"Unknown instruction: {mnemonic}")
        
        instr = self.instructions[mnemonic]
        operands = parts[1:] if len(parts) > 1 else []
        
        # 根据指令格式编码
        if instr.format == "RRR":
            if len(operands) != 3:
                raise ValueError(f"Instruction {mnemonic} expects 3 operands")
            rd = self.parse_register(operands[0])
            rs1 = self.parse_register(operands[1])
            rs2 = self.parse_register(operands[2])
            return self.encode_rrr(instr.opcode, rd, rs1, rs2)
        
        elif instr.format == "RR":
            if len(operands) != 2:
                raise ValueError(f"Instruction {mnemonic} expects 2 operands")
            rd = self.parse_register(operands[0])
            rs1 = self.parse_register(operands[1])
            return self.encode_rr(instr.opcode, rd, rs1)
        
        elif instr.format == "RI":
            if len(operands) != 2:
                raise ValueError(f"Instruction {mnemonic} expects 2 operands")
            rd = self.parse_register(operands[0])
            imm = int(operands[1], 0)  # 支持十进制和十六进制
            return self.encode_ri(instr.opcode, rd, imm)
        
        elif instr.format == "I":
            if len(operands) != 1:
                raise ValueError(f"Instruction {mnemonic} expects 1 operand")
            imm = int(operands[0], 0)
            return self.encode_i(instr.opcode, imm)
        
        elif instr.format == "RPF":
            if len(operands) != 3:
                raise ValueError(f"Instruction {mnemonic} expects 3 operands")
            rd = self.parse_register(operands[0])
            rs1 = self.parse_register(operands[1])
            func = int(operands[2], 0)
            return self.encode_rpf(instr.opcode, rd, rs1, func)
        
        elif instr.format == "RRI":
            if len(operands) != 3:
                raise ValueError(f"Instruction {mnemonic} expects 3 operands")
            rd = self.parse_register(operands[0])
            rs1 = self.parse_register(operands[1])
            offset = int(operands[2], 0)
            return self.encode_rri(instr.opcode, rd, rs1, offset)
        
        elif instr.format == "":
            if len(operands) != 0:
                raise ValueError(f"Instruction {mnemonic} expects 0 operands")
            return instr.opcode << 24
        
        raise ValueError(f"Unknown instruction format: {instr.format}")
    
    def assemble(self, source: str) -> List[Tuple[int, int]]:
        """汇编整个源文件，返回地址和机器码列表"""
        lines = source.split('\n')
        address = 0
        result = []
        
        for line in lines:
            # 先处理符号定义
            line = line.strip()
            if line.endswith(':'):
                label = line[:-1]
                self.symbol_table[label] = address
                continue
            
            # 汇编指令
            try:
                machine_code = self.assemble_line(line)
                if machine_code is not None:
                    result.append((address, machine_code))
                    address += 4  # 每条指令4字节
            except Exception as e:
                print(f"Error assembling line: {line}")
                print(f"Error: {e}")
        
        return result
    
    def to_binary(self, assembled: List[Tuple[int, int]]) -> bytes:
        """将汇编结果转换为二进制"""
        binary = b''
        for addr, code in assembled:
            binary += struct.pack('<I', code)
        return binary
    
    def to_hex_string(self, assembled: List[Tuple[int, int]]) -> str:
        """将汇编结果转换为十六进制字符串"""
        result = []
        for addr, code in assembled:
            result.append(f"{addr:08x}: {code:08x}")
        return '\n'.join(result)


def main():
    """简单的命令行接口"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: assembler.py <input.s> [output.bin]")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    with open(input_file, 'r') as f:
        source = f.read()
    
    assembler = Assembler()
    assembled = assembler.assemble(source)
    
    print(f"Assembled {len(assembled)} instructions")
    print(assembler.to_hex_string(assembled))
    
    if output_file:
        binary = assembler.to_binary(assembled)
        with open(output_file, 'wb') as f:
            f.write(binary)
        print(f"Binary written to {output_file}")


if __name__ == "__main__":
    main()
