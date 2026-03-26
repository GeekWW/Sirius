; Sirius GPGPU 完整指令测试
; 测试所有必选指令

; 测试算术运算
    ADD.I32 R1, R0, R0   ; R1 = 0
    ADD.I32 R2, R1, #1    ; R2 = 1 (占位符，实际需要LI指令)
    ADD.I32 R3, R2, R2    ; R3 = 2
    SUB.I32 R4, R3, R2    ; R4 = 1
    MUL.I32 R5, R3, R2    ; R5 = 2
    
    ; 浮点运算（简化）
    ADD.F32 R10, R0, R0
    SUB.F32 R11, R10, R10
    MUL.F32 R12, R10, R10
    DIV.F32 R13, R10, R10

; 测试逻辑运算
    AND R20, R3, R2       ; R20 = R3 & R2
    OR R21, R3, R2        ; R21 = R3 | R2
    XOR R22, R3, R2       ; R22 = R3 ^ R2
    NOT R23, R3           ; R23 = ~R3
    
    ; 比较
    ICMP R24, R3, R2, 3   ; == 比较
    ICMP R25, R3, R2, 1   ; > 比较
    FCMP R26, R10, R11, 3 ; 浮点 ==

; 测试内存访问（占位符）
    ; LD.GLOBAL R30, R0, 0
    ; ST.GLOBAL R0, R30, 0

; 测试控制流
    ; BR.UNCOND end
    
    ; 标签
loop:
    ; BR.UNCOND loop
    
end:
    ; 结束
    RET
