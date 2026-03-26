; Sirius GPGPU 汇编测试 - 简单加法测试

; 测试ADD.F32指令
; R1 = 1.0, R2 = 2.0, R3 = R1 + R2

    ; 这里应该有加载立即数的指令（暂未定义，先用占位符）
    ; 实际实现时需要添加LI（Load Immediate）指令或使用内存加载
    
    ; 测试ADD.F32
    ADD.F32 R3, R1, R2
    
    ; 测试ADD.I32
    ADD.I32 R6, R4, R5
    
    ; 测试逻辑运算
    AND R9, R7, R8
    OR R10, R7, R8
    XOR R11, R7, R8
    NOT R12, R7
    
    ; 测试内存访问（占位符）
    ; LD.GLOBAL R13, R14, 0
    ; ST.GLOBAL R14, R13, 0
    
    ; 测试分支（占位符）
    ; BR.UNCOND 100
    
    ; 结束
    RET
