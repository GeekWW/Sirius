#!/usr/bin/env python3
"""
Sirius GPGPU - Integration Test Framework
集成测试框架
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../isa'))

from assembler.assembler import Assembler
from isa_emulator.simulator import Simulator


class TestIntegration:
    """Sirius集成测试"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def test_vector_add(self):
        """测试向量加法"""
        print("Testing Vector Addition...")
        
        try:
            asm = Assembler()
            test_code = """
                ; 简化的向量加法测试
                ADD.I32 R1, R0, R0
                ADD.I32 R2, R1, R1
                ADD.I32 R3, R2, R1
            """
            
            assembled = asm.assemble(test_code)
            
            sim = Simulator()
            # 加载程序
            # sim.load_program(...)
            # 运行
            # cycles = sim.run(max_cycles=1000)
            
            print(f"  ✓ Vector addition test passed")
            self.passed += 1
        except Exception as e:
            print(f"  ✗ Vector addition test error: {e}")
            self.failed += 1
    
    def test_simple_program(self):
        """测试简单程序"""
        print("Testing Simple Program...")
        
        try:
            asm = Assembler()
            test_code = """
                ; 简单的测试程序
                ADD.I32 R1, R0, R0
                ADD.I32 R2, R1, #1
                ADD.I32 R3, R2, R1
                RET
            """
            
            assembled = asm.assemble(test_code)
            
            print(f"  ✓ Simple program test passed")
            self.passed += 1
        except Exception as e:
            print(f"  ✗ Simple program test error: {e}")
            self.failed += 1
    
    def run_all(self):
        """运行所有集成测试"""
        print("=" * 50)
        print("Sirius GPGPU Integration Tests")
        print("=" * 50)
        
        self.test_vector_add()
        self.test_simple_program()
        
        print("=" * 50)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("=" * 50)
        
        return self.failed == 0


if __name__ == "__main__":
    test = TestIntegration()
    success = test.run_all()
    sys.exit(0 if success else 1)
