; Sirius GPGPU - Complete Instruction Test
; 完整指令测试

.section .text
.global _start

_start:
    ; 测试算术运算
    ADD.I32 R1, R0, R0    ; R1 = 0
    ADD.I32 R2, R1, #1    ; R2 = 1
    ADD.I32 R3, R2, R2    ; R3 = 2
    SUB.I32 R4, R3, R2    ; R4 = 1
    MUL.I32 R5, R3, R2    ; R5 = 2
    REM.I32 R6, R5, R2    ; R6 = 0
    NEG.I32 R7, R3         ; R7 = -2
    
    ; 测试浮点运算
    ADD.F32 R10, R0, R0   ; R10 = 0.0
    SUB.F32 R11, R10, R0  ; R11 = 0.0
    MUL.F32 R12, R10, R0  ; R12 = 0.0
    DIV.F32 R13, R10, R0  ; R13 = 0.0 (除以零，实际应该避免)
    NEG.F32 R14, R10       ; R14 = -0.0
    
    ; 测试逻辑运算
    AND R20, R3, R2        ; R20 = R3 & R2
    OR R21, R3, R2         ; R21 = R3 | R2
    XOR R22, R3, R2        ; R22 = R3 ^ R2
    NOT R23, R3            ; R23 = ~R3
    
    ; 测试比较运算
    ICMP R24, R3, R2, 3    ; R24 = (R3 == R2) ? 1 : 0
    ICMP R25, R3, R2, 1    ; R25 = (R3 > R2) ? 1 : 0
    FCMP R26, R10, R11, 3  ; R26 = (R10 == R11) ? 1 : 0
    
    ; 测试内存访问（占位符，需要实际地址）
    ; LD.GLOBAL R30, R0, 0
    ; LD.LOCAL R31, R0, 0
    ; LD.PRIVATE R32, R0, 0
    ; LD.CONST R33, R0, 0
    ; ST.GLOBAL R0, R30, 0
    ; ST.LOCAL R0, R31, 0
    ; ST.PRIVATE R0, R32, 0
    ; GEP R34, R0, R1
    
    ; 测试控制流
    BR.UNCOND loop_label    ; 无条件跳转
    
loop_label:
    ; 循环测试
    ADD.I32 R40, R40, #1  ; 计数器加1
    ICMP R41, R40, #10, 1  ; 检查是否达到10
    BR.COND R41, loop_label ; 如果未达到，继续循环
    
    ; 测试并行相关
    ADD.I32 R50, R0, #0    ; 维度0
    GET_GLOBAL_ID R51, R50  ; R51 = get_global_id(0)
    GET_LOCAL_ID R52, R50   ; R52 = get_local_id(0)
    GET_GLOBAL_SIZE R53, R50 ; R53 = get_global_size(0)
    GET_LOCAL_SIZE R54, R50  ; R54 = get_local_size(0)
    GET_GROUP_ID R55, R50    ; R55 = get_group_id(0)
    GET_NUM_GROUPS R56, R50  ; R56 = get_num_groups(0)
    BARRIER_LOCAL            ; 局部内存屏障
    
    ; 结束
    RET
