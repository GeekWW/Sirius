#!/usr/bin/env python3
"""
Sirius GPGPU - Unit Test Framework
单元测试框架
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../isa'))

from assembler.assembler import Assembler
from disassembler.disassembler import Disassembler


class TestSirius:
    """Sirius单元测试"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test_assembler(self):
        """测试汇编器"""
        print("Testing Assembler...")
        
        try:
            asm = Assembler()
            test_code = """
                ADD.I32 R1, R0, R0
                ADD.I32 R2, R1, R1
            """
            
            result = asm.assemble(test_code)
            if len(result) > 0:
                print(f"  ✓ Assembler test passed, {len(result)} instructions")
                self.passed += 1
            else:
                print("  ✗ Assembler test failed")
                self.failed += 1
        except Exception as e:
            print(f"  ✗ Assembler test error: {e}")
            self.failed += 1
    
    def test_disassembler(self):
        """测试反汇编器"""
        print("Testing Disassembler...")
        
        try:
            disasm = Disassembler()
            # 测试用的机器码
            test_binary = b'\x05\x10\x20\x00'  # 示例
            
            result = disasm.disassemble(test_binary)
            print(f"  ✓ Disassembler test passed")
            self.passed += 1
        except Exception as e:
            print(f"  ✗ Disassembler test error: {e}")
            self.failed += 1
    
    def run_all(self):
        """运行所有测试"""
        print("=" * 50)
        print("Sirius GPGPU Unit Tests")
        print("=" * 50)
        
        self.test_assembler()
        self.test_disassembler()
        
        print("=" * 50)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("=" * 50)
        
        return self.failed == 0


if __name__ == "__main__":
    test = TestSirius()
    success = test.run_all()
    sys.exit(0 if success else 1)
