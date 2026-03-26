#!/usr/bin/env python3
"""
Sirius GPGPU Disassembler
反汇编器：将32位机器码转换为汇编代码
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


# 指令集定义（与汇编器相同）
INSTRUCTIONS = {
    # 算术运算指令
    0x01: Instruction(0x01, "ADD.F32", "RRR", "必选"),
    0x02: Instruction(0x02, "SUB.F32", "RRR", "必选"),
    0x03: Instruction(0x03, "MUL.F32", "RRR", "必选"),
    0x04: Instruction(0x04, "DIV.F32", "RRR", "必选"),
    0x05: Instruction(0x05, "ADD.I32", "RRR", "必选"),
    0x06: Instruction(0x06, "SUB.I32", "RRR", "必选"),
    0x07: Instruction(0x07, "MUL.I32", "RRR", "必选"),
    0x08: Instruction(0x08, "NEG.F32", "RR", "可选"),
    0x09: Instruction(0x09, "NEG.I32", "RR", "可选"),
    0x0A: Instruction(0x0A, "REM.I32", "RRR", "可选"),
    0x0B: Instruction(0x0B, "DIV.U32", "RRR", "可选"),
    
    # 逻辑运算指令
    0x10: Instruction(0x10, "AND", "RRR", "必选"),
    0x11: Instruction(0x11, "OR", "RRR", "必选"),
    0x12: Instruction(0x12, "XOR", "RRR", "必选"),
    0x13: Instruction(0x13, "NOT", "RR", "必选"),
    0x14: Instruction(0x14, "ICMP", "RPF", "必选"),
    0x15: Instruction(0x15, "FCMP", "RPF", "必选"),
    0x16: Instruction(0x16, "ICMP.U", "RPF", "可选"),
    0x17: Instruction(0x17, "FCMP.NAN", "RR", "可选"),
    
    # 内存访问指令
    0x20: Instruction(0x20, "LD.GLOBAL", "RRI", "必选"),
    0x21: Instruction(0x21, "LD.LOCAL", "RRI", "必选"),
    0x22: Instruction(0x22, "LD.PRIVATE", "RRI", "必选"),
    0x23: Instruction(0x23, "LD.CONST", "RRI", "必选"),
    0x24: Instruction(0x24, "ST.GLOBAL", "RRI", "必选"),
    0x25: Instruction(0x25, "ST.LOCAL", "RRI", "必选"),
    0x26: Instruction(0x26, "ST.PRIVATE", "RRI", "必选"),
    0x27: Instruction(0x27, "GEP", "RRR", "必选"),
    0x28: Instruction(0x28, "LD.GLOBAL.STRIDE", "RRR", "可选"),
    
    # 控制流指令
    0x30: Instruction(0x30, "BR.COND", "RI", "必选"),
    0x31: Instruction(0x31, "BR.UNCOND", "I", "必选"),
    0x32: Instruction(0x32, "RET", "", "必选"),
    0x33: Instruction(0x33, "BR.LOOP", "RI", "可选"),
    
    # 并行相关指令
    0x40: Instruction(0x40, "GET_GLOBAL_ID", "RRI", "必选"),
    0x41: Instruction(0x41, "GET_LOCAL_ID", "RRI", "必选"),
    0x42: Instruction(0x42, "GET_GLOBAL_SIZE", "RRI", "必选"),
    0x43: Instruction(0x43, "GET_LOCAL_SIZE", "RRI", "必选"),
    0x44: Instruction(0x44, "GET_GROUP_ID", "RRI", "必选"),
    0x45: Instruction(0x45, "GET_NUM_GROUPS", "RRI", "必选"),
    0x46: Instruction(0x46, "BARRIER_LOCAL", "", "必选"),
    0x47: Instruction(0x47, "BARRIER_GLOBAL", "", "可选"),
}


class Disassembler:
    """Sirius GPGPU 反汇编器"""
    
    def __init__(self):
        self.instructions = INSTRUCTIONS
        self.symbol_table: Dict[int, str] = {}
    
    def format_register(self, reg_num: int) -> str:
        """格式化寄存器编号"""
        return f"R{reg_num}"
    
    def decode_rrr(self, machine_code: int) -> Tuple[int, int, int, int]:
        """三寄存器格式解码：8位opcode + 8位Rd + 8位Rs1 + 8位Rs2"""
        opcode = (machine_code >> 24) & 0xFF
        rd = (machine_code >> 16) & 0xFF
        rs1 = (machine_code >> 8) & 0xFF
        rs2 = machine_code & 0xFF
        return opcode, rd, rs1, rs2
    
    def decode_rr(self, machine_code: int) -> Tuple[int, int, int]:
        """双寄存器格式解码：8位opcode + 8位Rd + 8位Rs1 + 8位保留"""
        opcode = (machine_code >> 24) & 0xFF
        rd = (machine_code >> 16) & 0xFF
        rs1 = (machine_code >> 8) & 0xFF
        return opcode, rd, rs1
    
    def decode_ri(self, machine_code: int) -> Tuple[int, int, int]:
        """寄存器+立即数格式解码：8位opcode + 8位Rd + 16位立即数"""
        opcode = (machine_code >> 24) & 0xFF
        rd = (machine_code >> 16) & 0xFF
        imm = machine_code & 0xFFFF
        # 符号扩展16位立即数到32位
        if imm & 0x8000:
            imm = imm | 0xFFFF0000
        return opcode, rd, imm
    
    def decode_i(self, machine_code: int) -> Tuple[int, int]:
        """仅立即数格式解码：8位opcode + 24位立即数/地址"""
        opcode = (machine_code >> 24) & 0xFF
        imm = machine_code & 0xFFFFFF
        return opcode, imm
    
    def decode_rpf(self, machine_code: int) -> Tuple[int, int, int, int]:
        """多字段功能位格式解码：8位opcode + 8位Rd + 8位Rs1 + 4位功能位 + 4位保留"""
        opcode = (machine_code >> 24) & 0xFF
        rd = (machine_code >> 16) & 0xFF
        rs1 = (machine_code >> 8) & 0xFF
        func = (machine_code >> 4) & 0x0F
        return opcode, rd, rs1, func
    
    def decode_rri(self, machine_code: int) -> Tuple[int, int, int, int]:
        """寄存器+寄存器+偏移格式解码：8位opcode + 8位Rd + 8位Rs1 + 8位偏移"""
        opcode = (machine_code >> 24) & 0xFF
        rd = (machine_code >> 16) & 0xFF
        rs1 = (machine_code >> 8) & 0xFF
        offset = machine_code & 0xFF
        return opcode, rd, rs1, offset
    
    def disassemble_one(self, machine_code: int, address: int = 0) -> str:
        """反汇编单条机器码"""
        opcode = (machine_code >> 24) & 0xFF
        
        if opcode not in self.instructions:
            return f".word 0x{machine_code:08x}  ; Unknown opcode 0x{opcode:02x}"
        
        instr = self.instructions[opcode]
        mnemonic = instr.name
        
        # 根据指令格式反汇编
        if instr.format == "RRR":
            opcode, rd, rs1, rs2 = self.decode_rrr(machine_code)
            return f"{mnemonic} {self.format_register(rd)}, {self.format_register(rs1)}, {self.format_register(rs2)}"
        
        elif instr.format == "RR":
            opcode, rd, rs1 = self.decode_rr(machine_code)
            return f"{mnemonic} {self.format_register(rd)}, {self.format_register(rs1)}"
        
        elif instr.format == "RI":
            opcode, rd, imm = self.decode_ri(machine_code)
            return f"{mnemonic} {self.format_register(rd)}, 0x{imm:x}"
        
        elif instr.format == "I":
            opcode, imm = self.decode_i(machine_code)
            return f"{mnemonic} 0x{imm:x}"
        
        elif instr.format == "RPF":
            opcode, rd, rs1, func = self.decode_rpf(machine_code)
            return f"{mnemonic} {self.format_register(rd)}, {self.format_register(rs1)}, 0x{func:x}"
        
        elif instr.format == "RRI":
            opcode, rd, rs1, offset = self.decode_rri(machine_code)
            return f"{mnemonic} {self.format_register(rd)}, {self.format_register(rs1)}, 0x{offset:x}"
        
        elif instr.format == "":
            return mnemonic
        
        return f".word 0x{machine_code:08x}"
    
    def disassemble(self, binary: bytes, start_address: int = 0) -> List[Tuple[int, str, int]]:
        """反汇编整个二进制文件，返回地址、汇编代码、机器码列表"""
        result = []
        address = start_address
        
        # 每4字节一条指令
        for i in range(0, len(binary), 4):
            if i + 4 > len(binary):
                break
            
            machine_code = struct.unpack('<I', binary[i:i+4])[0]
            assembly = self.disassemble_one(machine_code, address)
            result.append((address, assembly, machine_code))
            address += 4
        
        return result
    
    def to_string(self, disassembled: List[Tuple[int, str, int]]) -> str:
        """将反汇编结果转换为字符串"""
        result = []
        for addr, asm, code in disassembled:
            result.append(f"{addr:08x}: {code:08x}  {asm}")
        return '\n'.join(result)


def main():
    """简单的命令行接口"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: disassembler.py <input.bin> [output.s]")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    with open(input_file, 'rb') as f:
        binary = f.read()
    
    disassembler = Disassembler()
    disassembled = disassembler.disassemble(binary)
    
    print(f"Disassembled {len(disassembled)} instructions")
    print(disassembler.to_string(disassembled))
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(disassembler.to_string(disassembled))
        print(f"Assembly written to {output_file}")


if __name__ == "__main__":
    main()
