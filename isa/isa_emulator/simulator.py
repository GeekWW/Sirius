#!/usr/bin/env python3
"""
Sirius GPGPU ISA Simulator
ISA模拟器：模拟执行Sirius GPGPU指令
"""

from typing import List, Dict, Optional, Tuple
import struct


class RegisterFile:
    """寄存器堆"""
    
    def __init__(self, num_regs: int = 32):
        self.num_regs = num_regs
        self.regs = [0] * num_regs
        self.regs[0] = 0  # R0硬连线为0
        self.ready = [True] * num_regs  # 寄存器就绪标记
    
    def read(self, reg_num: int) -> int:
        """读取寄存器"""
        if reg_num < 0 or reg_num >= self.num_regs:
            raise ValueError(f"Invalid register number: {reg_num}")
        return self.regs[reg_num]
    
    def write(self, reg_num: int, value: int):
        """写入寄存器"""
        if reg_num < 0 or reg_num >= self.num_regs:
            raise ValueError(f"Invalid register number: {reg_num}")
        if reg_num != 0:  # R0不能写
            self.regs[reg_num] = value & 0xFFFFFFFF  # 32位
    
    def set_ready(self, reg_num: int, ready: bool):
        """设置寄存器就绪状态"""
        if reg_num >= 0 and reg_num < self.num_regs:
            self.ready[reg_num] = ready
    
    def is_ready(self, reg_num: int) -> bool:
        """检查寄存器是否就绪"""
        if reg_num < 0 or reg_num >= self.num_regs:
            return False
        return self.ready[reg_num]


class Memory:
    """内存模型"""
    
    def __init__(self, size: int = 1024 * 1024):  # 默认1MB
        self.size = size
        self.memory = bytearray(size)
    
    def read(self, address: int, num_bytes: int = 4) -> int:
        """读取内存，返回32位整数"""
        if address < 0 or address + num_bytes > self.size:
            raise ValueError(f"Memory access out of bounds: 0x{address:x}")
        # 小端序读取
        value = 0
        for i in range(num_bytes):
            value |= (self.memory[address + i] << (i * 8))
        return value
    
    def write(self, address: int, value: int, num_bytes: int = 4):
        """写入内存，32位整数"""
        if address < 0 or address + num_bytes > self.size:
            raise ValueError(f"Memory access out of bounds: 0x{address:x}")
        # 小端序写入
        for i in range(num_bytes):
            self.memory[address + i] = (value >> (i * 8)) & 0xFF


class IDRegisters:
    """专用ID寄存器（OpenCL线程ID等）"""
    
    def __init__(self):
        # 全局线程ID
        self.global_id = [0, 0, 0]
        # 局部线程ID
        self.local_id = [0, 0, 0]
        # 全局网格尺寸
        self.global_size = [1, 1, 1]
        # 局部工作组尺寸
        self.local_size = [1, 1, 1]
        # 工作组ID
        self.group_id = [0, 0, 0]
        # 工作组数量
        self.num_groups = [1, 1, 1]
    
    def get_global_id(self, dim: int) -> int:
        if dim < 0 or dim >= 3:
            return 0
        return self.global_id[dim]
    
    def get_local_id(self, dim: int) -> int:
        if dim < 0 or dim >= 3:
            return 0
        return self.local_id[dim]
    
    def get_global_size(self, dim: int) -> int:
        if dim < 0 or dim >= 3:
            return 1
        return self.global_size[dim]
    
    def get_local_size(self, dim: int) -> int:
        if dim < 0 or dim >= 3:
            return 1
        return self.local_size[dim]
    
    def get_group_id(self, dim: int) -> int:
        if dim < 0 or dim >= 3:
            return 0
        return self.group_id[dim]
    
    def get_num_groups(self, dim: int) -> int:
        if dim < 0 or dim >= 3:
            return 1
        return self.num_groups[dim]


class Simulator:
    """Sirius GPGPU ISA模拟器"""
    
    def __init__(self):
        self.pc = 0  # 程序计数器
        self.rf = RegisterFile(32)  # 32个通用寄存器
        self.mem = Memory()  # 内存
        self.id_regs = IDRegisters()  # 专用ID寄存器
        self.running = False
        self.cycle_count = 0
        self.instructions_retired = 0
        
        # 指令处理函数表
        self.opcode_handlers = {
            # 算术运算
            0x01: self.handle_add_f32,
            0x02: self.handle_sub_f32,
            0x03: self.handle_mul_f32,
            0x04: self.handle_div_f32,
            0x05: self.handle_add_i32,
            0x06: self.handle_sub_i32,
            0x07: self.handle_mul_i32,
            0x08: self.handle_neg_f32,
            0x09: self.handle_neg_i32,
            0x0A: self.handle_rem_i32,
            0x0B: self.handle_div_u32,
            
            # 逻辑运算
            0x10: self.handle_and,
            0x11: self.handle_or,
            0x12: self.handle_xor,
            0x13: self.handle_not,
            0x14: self.handle_icmp,
            0x15: self.handle_fcmp,
            0x16: self.handle_icmp_u,
            0x17: self.handle_fcmp_nan,
            
            # 内存访问
            0x20: self.handle_ld_global,
            0x21: self.handle_ld_local,
            0x22: self.handle_ld_private,
            0x23: self.handle_ld_const,
            0x24: self.handle_st_global,
            0x25: self.handle_st_local,
            0x26: self.handle_st_private,
            0x27: self.handle_gep,
            0x28: self.handle_ld_global_stride,
            
            # 控制流
            0x30: self.handle_br_cond,
            0x31: self.handle_br_uncond,
            0x32: self.handle_ret,
            0x33: self.handle_br_loop,
            
            # 并行相关
            0x40: self.handle_get_global_id,
            0x41: self.handle_get_local_id,
            0x42: self.handle_get_global_size,
            0x43: self.handle_get_local_size,
            0x44: self.handle_get_group_id,
            0x45: self.handle_get_num_groups,
            0x46: self.handle_barrier_local,
            0x47: self.handle_barrier_global,
        }
    
    def load_program(self, binary: bytes, start_address: int = 0):
        """加载程序到内存"""
        for i, byte in enumerate(binary):
            if start_address + i < self.mem.size:
                self.mem.memory[start_address + i] = byte
        self.pc = start_address
    
    def step(self) -> bool:
        """单步执行一条指令"""
        if not self.running:
            return False
        
        # 取指
        if self.pc + 4 > self.mem.size:
            print(f"PC out of bounds: 0x{self.pc:x}")
            self.running = False
            return False
        
        # 读取32位指令
        machine_code = self.mem.read(self.pc, 4)
        opcode = (machine_code >> 24) & 0xFF
        
        # 执行指令
        if opcode in self.opcode_handlers:
            self.opcode_handlers[opcode](machine_code)
        else:
            print(f"Unknown opcode: 0x{opcode:02x} at PC=0x{self.pc:x}")
            self.pc += 4
        
        self.cycle_count += 1
        self.instructions_retired += 1
        
        return self.running
    
    def run(self, max_cycles: Optional[int] = None) -> int:
        """运行直到结束或达到最大周期数"""
        self.running = True
        cycles = 0
        
        while self.running:
            if max_cycles is not None and cycles >= max_cycles:
                break
            if not self.step():
                break
            cycles += 1
        
        return cycles
    
    # === 指令处理函数 ===
    
    def decode_rrr(self, machine_code: int) -> Tuple[int, int, int]:
        """解码三寄存器格式"""
        rd = (machine_code >> 16) & 0xFF
        rs1 = (machine_code >> 8) & 0xFF
        rs2 = machine_code & 0xFF
        return rd, rs1, rs2
    
    def decode_rr(self, machine_code: int) -> Tuple[int, int]:
        """解码双寄存器格式"""
        rd = (machine_code >> 16) & 0xFF
        rs1 = (machine_code >> 8) & 0xFF
        return rd, rs1
    
    def decode_ri(self, machine_code: int) -> Tuple[int, int]:
        """解码寄存器+立即数格式"""
        rd = (machine_code >> 16) & 0xFF
        imm = machine_code & 0xFFFF
        if imm & 0x8000:
            imm = imm | 0xFFFF0000
        return rd, imm
    
    def decode_i(self, machine_code: int) -> int:
        """解码仅立即数格式"""
        return machine_code & 0xFFFFFF
    
    def decode_rpf(self, machine_code: int) -> Tuple[int, int, int]:
        """解码多字段功能位格式"""
        rd = (machine_code >> 16) & 0xFF
        rs1 = (machine_code >> 8) & 0xFF
        func = (machine_code >> 4) & 0x0F
        return rd, rs1, func
    
    def decode_rri(self, machine_code: int) -> Tuple[int, int, int]:
        """解码寄存器+寄存器+偏移格式"""
        rd = (machine_code >> 16) & 0xFF
        rs1 = (machine_code >> 8) & 0xFF
        offset = machine_code & 0xFF
        if offset & 0x80:
            offset = offset | 0xFFFFFF00
        return rd, rs1, offset
    
    # 算术运算指令
    def handle_add_f32(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        # 简化浮点加法（实际需要IEEE 754实现）
        result = val1 + val2
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_sub_f32(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        result = val1 - val2
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_mul_f32(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        result = val1 * val2
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_div_f32(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        if val2 != 0:
            result = val1 // val2  # 简化整数除法
            self.rf.write(rd, result)
        self.pc += 4
    
    def handle_add_i32(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        result = (val1 + val2) & 0xFFFFFFFF
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_sub_i32(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        result = (val1 - val2) & 0xFFFFFFFF
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_mul_i32(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        result = (val1 * val2) & 0xFFFFFFFF
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_neg_f32(self, machine_code: int):
        rd, rs1 = self.decode_rr(machine_code)
        val = self.rf.read(rs1)
        result = (-val) & 0xFFFFFFFF
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_neg_i32(self, machine_code: int):
        rd, rs1 = self.decode_rr(machine_code)
        val = self.rf.read(rs1)
        result = (-val) & 0xFFFFFFFF
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_rem_i32(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        if val2 != 0:
            result = val1 % val2
            self.rf.write(rd, result)
        self.pc += 4
    
    def handle_div_u32(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        if val2 != 0:
            result = (val1 & 0xFFFFFFFF) // (val2 & 0xFFFFFFFF)
            self.rf.write(rd, result)
        self.pc += 4
    
    # 逻辑运算指令
    def handle_and(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        result = val1 & val2
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_or(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        result = val1 | val2
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_xor(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        val1 = self.rf.read(rs1)
        val2 = self.rf.read(rs2)
        result = val1 ^ val2
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_not(self, machine_code: int):
        rd, rs1 = self.decode_rr(machine_code)
        val = self.rf.read(rs1)
        result = (~val) & 0xFFFFFFFF
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_icmp(self, machine_code: int):
        rd, rs1, func = self.decode_rpf(machine_code)
        val1 = self.rf.read(rs1)
        # 简化比较，实际需要完整实现
        result = 1 if func == 3 else 0  # 默认等于为真
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_fcmp(self, machine_code: int):
        rd, rs1, func = self.decode_rpf(machine_code)
        # 简化浮点比较
        result = 1 if func == 3 else 0
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_icmp_u(self, machine_code: int):
        rd, rs1, func = self.decode_rpf(machine_code)
        result = 1 if func == 3 else 0
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_fcmp_nan(self, machine_code: int):
        rd, rs1 = self.decode_rr(machine_code)
        # 简化NAN检查
        self.rf.write(rd, 0)
        self.pc += 4
    
    # 内存访问指令（简化实现）
    def handle_ld_global(self, machine_code: int):
        rd, rs1, offset = self.decode_rri(machine_code)
        addr = self.rf.read(rs1) + offset
        val = self.mem.read(addr, 4)
        self.rf.write(rd, val)
        self.pc += 4
    
    def handle_ld_local(self, machine_code: int):
        rd, rs1, offset = self.decode_rri(machine_code)
        addr = self.rf.read(rs1) + offset
        val = self.mem.read(addr, 4)
        self.rf.write(rd, val)
        self.pc += 4
    
    def handle_ld_private(self, machine_code: int):
        rd, rs1, offset = self.decode_rri(machine_code)
        addr = self.rf.read(rs1) + offset
        val = self.mem.read(addr, 4)
        self.rf.write(rd, val)
        self.pc += 4
    
    def handle_ld_const(self, machine_code: int):
        rd, rs1, offset = self.decode_rri(machine_code)
        addr = self.rf.read(rs1) + offset
        val = self.mem.read(addr, 4)
        self.rf.write(rd, val)
        self.pc += 4
    
    def handle_st_global(self, machine_code: int):
        rs1, rs2, offset = self.decode_rri(machine_code)
        addr = self.rf.read(rs1) + offset
        val = self.rf.read(rs2)
        self.mem.write(addr, val, 4)
        self.pc += 4
    
    def handle_st_local(self, machine_code: int):
        rs1, rs2, offset = self.decode_rri(machine_code)
        addr = self.rf.read(rs1) + offset
        val = self.rf.read(rs2)
        self.mem.write(addr, val, 4)
        self.pc += 4
    
    def handle_st_private(self, machine_code: int):
        rs1, rs2, offset = self.decode_rri(machine_code)
        addr = self.rf.read(rs1) + offset
        val = self.rf.read(rs2)
        self.mem.write(addr, val, 4)
        self.pc += 4
    
    def handle_gep(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        base = self.rf.read(rs1)
        index = self.rf.read(rs2)
        result = base + index * 4  # 简化4字节元素
        self.rf.write(rd, result)
        self.pc += 4
    
    def handle_ld_global_stride(self, machine_code: int):
        rd, rs1, rs2 = self.decode_rrr(machine_code)
        base = self.rf.read(rs1)
        stride = self.rf.read(rs2)
        addr = base + stride
        val = self.mem.read(addr, 4)
        self.rf.write(rd, val)
        self.pc += 4
    
    # 控制流指令
    def handle_br_cond(self, machine_code: int):
        rd, imm = self.decode_ri(machine_code)
        cond = self.rf.read(rd)
        if cond != 0:
            self.pc = imm
        else:
            self.pc += 4
    
    def handle_br_uncond(self, machine_code: int):
        imm = self.decode_i(machine_code)
        self.pc = imm
    
    def handle_ret(self, machine_code: int):
        self.running = False
    
    def handle_br_loop(self, machine_code: int):
        rd, imm = self.decode_ri(machine_code)
        count = self.rf.read(rd)
        if count > 0:
            count -= 1
            self.rf.write(rd, count)
            self.pc = imm
        else:
            self.pc += 4
    
    # 并行相关指令
    def handle_get_global_id(self, machine_code: int):
        rd, rs1, offset = self.decode_rri(machine_code)
        dim = self.rf.read(rs1)
        val = self.id_regs.get_global_id(dim)
        self.rf.write(rd, val)
        self.pc += 4
    
    def handle_get_local_id(self, machine_code: int):
        rd, rs1, offset = self.decode_rri(machine_code)
        dim = self.rf.read(rs1)
        val = self.id_regs.get_local_id(dim)
        self.rf.write(rd, val)
        self.pc += 4
    
    def handle_get_global_size(self, machine_code: int):
        rd, rs1, offset = self.decode_rri(machine_code)
        dim = self.rf.read(rs1)
        val = self.id_regs.get_global_size(dim)
        self.rf.write(rd, val)
        self.pc += 4
    
    def handle_get_local_size(self, machine_code: int):
        rd, rs1, offset = self.decode_rri(machine_code)
        dim = self.rf.read(rs1)
        val = self.id_regs.get_local_size(dim)
        self.rf.write(rd, val)
        self.pc += 4
    
    def handle_get_group_id(self, machine_code: int):
        rd, rs1, offset = self.decode_rri(machine_code)
        dim = self.rf.read(rs1)
        val = self.id_regs.get_group_id(dim)
        self.rf.write(rd, val)
        self.pc += 4
    
    def handle_get_num_groups(self, machine_code: int):
        rd, rs1, offset = self.decode_rri(machine_code)
        dim = self.rf.read(rs1)
        val = self.id_regs.get_num_groups(dim)
        self.rf.write(rd, val)
        self.pc += 4
    
    def handle_barrier_local(self, machine_code: int):
        # 简化屏障实现
        self.pc += 4
    
    def handle_barrier_global(self, machine_code: int):
        # 简化屏障实现
        self.pc += 4
    
    def get_state(self) -> Dict:
        """获取当前状态"""
        return {
            "pc": self.pc,
            "cycle_count": self.cycle_count,
            "instructions_retired": self.instructions_retired,
            "running": self.running,
        }


def main():
    """简单的命令行接口"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: simulator.py <input.bin>")
        return
    
    input_file = sys.argv[1]
    
    with open(input_file, 'rb') as f:
        binary = f.read()
    
    sim = Simulator()
    sim.load_program(binary)
    
    print("Starting simulation...")
    cycles = sim.run(max_cycles=1000000)
    
    print(f"Simulation complete: {cycles} cycles")
    print(f"Instructions retired: {sim.instructions_retired}")
    state = sim.get_state()
    print(f"Final PC: 0x{state['pc']:08x}")


if __name__ == "__main__":
    main()
