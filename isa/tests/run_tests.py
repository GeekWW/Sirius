#!/usr/bin/env python3
"""
Sirius GPGPU - Test Runner
测试运行脚本
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from assembler.assembler import Assembler
from disassembler.disassembler import Disassembler
from isa_emulator.simulator import Simulator


def test_assembler():
    """测试汇编器"""
    print("=" * 60)
    print("Testing Assembler")
    print("=" * 60)
    
    try:
        asm = Assembler()
        test_code = """
            ADD.I32 R1, R0, R0
            ADD.I32 R2, R1, R1
            SUB.I32 R3, R2, R1
        """
        
        result = asm.assemble(test_code)
        
        print(f"✓ Assembled {len(result)} instructions")
        for addr, code in result:
            print(f"  0x{addr:08x}: 0x{code:08x}")
        
        return True
    except Exception as e:
        print(f"✗ Assembler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_disassembler():
    """测试反汇编器"""
    print("\n" + "=" * 60)
    print("Testing Disassembler")
    print("=" * 60)
    
    try:
        disasm = Disassembler()
        # 测试用的机器码 - ADD.I32 R1, R0, R0
        test_binary = b'\x05\x10\x20\x00'
        
        result = disasm.disassemble(test_binary)
        
        print(f"✓ Disassembled {len(result)} instructions")
        for addr, asm, code in result:
            print(f"  0x{addr:08x}: 0x{code:08x} - {asm}")
        
        return True
    except Exception as e:
        print(f"✗ Disassembler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simulator():
    """测试模拟器"""
    print("\n" + "=" * 60)
    print("Testing Simulator (Simplified)")
    print("=" * 60)
    
    try:
        sim = Simulator()
        
        # 设置简单的ID
        sim.id_regs.global_id[0] = 0
        sim.id_regs.local_id[0] = 0
        sim.id_regs.global_size[0] = 1
        sim.id_regs.local_size[0] = 1
        
        # 加载简单程序（占位）
        # sim.load_program(b'')
        
        print("✓ Simulator initialized successfully")
        print("  Note: Full simulation requires complete implementation")
        
        return True
    except Exception as e:
        print(f"✗ Simulator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("Sirius GPGPU Test Suite")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # 运行所有测试
    if test_assembler():
        passed += 1
    else:
        failed += 1
    
    if test_disassembler():
        passed += 1
    else:
        failed += 1
    
    if test_simulator():
        passed += 1
    else:
        failed += 1
    
    # 总结
    print("\n" + "=" * 60)
    print(f"Test Summary: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
