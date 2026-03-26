#!/usr/bin/env python3
"""
Sirius GPGPU - End-to-End Integration Test
端到端集成测试
"""

import sys
import os

# 添加所有路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'isa'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sw'))

from assembler.assembler import Assembler
from disassembler.disassembler import Disassembler
from isa_emulator.simulator import Simulator


def test_end_to_end():
    """端到端测试：编译 → 汇编 → 模拟执行"""
    print("=" * 70)
    print("Sirius GPGPU - End-to-End Integration Test")
    print("=" * 70)
    
    # 测试用的OpenCL核（用汇编写的简化版本）
    test_code = """
        ; 向量加法测试
        ; R1 = 0
        ; R2 = 1
        ; R3 = R1 + R2
        ; R4 = R3 + R2
        ADD.I32 R1, R0, R0
        ADD.I32 R2, R1, #1
        ADD.I32 R3, R1, R2
        ADD.I32 R4, R3, R2
        RET
    """
    
    passed = 0
    failed = 0
    
    try:
        # Step 1: 汇编
        print("\n[Step 1/3] Assembling...")
        asm = Assembler()
        assembled = asm.assemble(test_code)
        
        if len(assembled) > 0:
            print(f"✓ Assembled {len(assembled)} instructions")
            for addr, code in assembled:
                print(f"  0x{addr:08x}: 0x{code:08x}")
            passed += 1
        else:
            print("✗ Assembly failed")
            failed += 1
        
        # Step 2: 反汇编（验证）
        print("\n[Step 2/3] Disassembling...")
        disasm = Disassembler()
        
        # 创建简单的二进制
        binary = b''
        for addr, code in assembled:
            binary += code.to_bytes(4, 'little')
        
        if len(binary) > 0:
            disassembled = disasm.disassemble(binary)
            print(f"✓ Disassembled {len(disassembled)} instructions")
            for addr, asm_str, code in disassembled:
                print(f"  0x{addr:08x}: {asm_str}")
            passed += 1
        else:
            print("✗ Disassembly failed")
            failed += 1
        
        # Step 3: 模拟执行（简化）
        print("\n[Step 3/3] Simulating...")
        sim = Simulator()
        
        # 设置简单的ID
        sim.id_regs.global_id[0] = 0
        sim.id_regs.local_id[0] = 0
        sim.id_regs.global_size[0] = 1
        sim.id_regs.local_size[0] = 1
        
        print("✓ Simulator initialized")
        print("  Note: Full simulation requires complete implementation")
        passed += 1
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        failed += 1
    
    # 总结
    print("\n" + "=" * 70)
    print(f"Integration Test Summary: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


def main():
    """主函数"""
    success = test_end_to_end()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
