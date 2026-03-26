from veadk import Agent, SequentialAgent
from pydantic import BaseModel


# 定义汇编器输出模型
class AssemblerInstruction(BaseModel):
    opcode: str
    name: str
    binary: str
    assembly: str


class AssemblerOutput(BaseModel):
    instructions: list[AssemblerInstruction]
    success: bool
    errors: list[str]


# 定义反汇编器输出模型
class DisassemblerOutput(BaseModel):
    assembly: str
    binary: str
    success: bool
    errors: list[str]


# 子Agent 1: 汇编器生成Agent
assembler_gen_agent = Agent(
    name="Assembler_Gen_Agent",
    description="生成汇编器代码",
    instruction="""你是一位编译器工程师，负责生成Sirius GPGPU的汇编器。

任务：
1. 读取isa_spec.md中的ISA规范
2. 生成Python汇编器代码
3. 支持所有必选指令（30条）
4. 输入：汇编代码
5. 输出：32位机器码（二进制或十六进制）

要求：
- 代码结构清晰
- 支持所有指令格式
- 错误处理完善
- 带单元测试""",
    model_extra_config={"response_format": AssemblerOutput},
)


# 子Agent 2: 反汇编器生成Agent
disassembler_gen_agent = Agent(
    name="Disassembler_Gen_Agent",
    description="生成反汇编器代码",
    instruction="""你是一位编译器工程师，负责生成Sirius GPGPU的反汇编器。

任务：
1. 读取isa_spec.md中的ISA规范
2. 生成Python反汇编器代码
3. 支持所有必选指令（30条）
4. 输入：32位机器码
5. 输出：汇编代码

要求：
- 代码结构清晰
- 支持所有指令格式
- 错误处理完善
- 带单元测试""",
    model_extra_config={"response_format": DisassemblerOutput},
)


# 子Agent 3: ISA模拟器生成Agent
simulator_gen_agent = Agent(
    name="Simulator_Gen_Agent",
    description="生成ISA模拟器代码",
    instruction="""你是一位计算机架构师，负责生成Sirius GPGPU的ISA模拟器。

任务：
1. 读取isa_spec.md中的ISA规范
2. 读取microarch.md中的微架构设计
3. 生成Python ISA模拟器代码
4. 模拟6级流水线（IF/ID/IS/EX/MEM/WB）
5. 支持所有必选指令执行
6. 支持寄存器、内存模型

要求：
- 代码结构清晰
- 流水线模拟准确
- 寄存器/内存状态跟踪
- 单步执行支持
- 带测试用例""",
)


# 子Agent 4: 测试用例生成Agent
test_gen_agent = Agent(
    name="Test_Gen_Agent",
    description="生成测试用例",
    instruction="""你是一位测试工程师，负责生成Sirius GPGPU的测试用例。

任务：
1. 读取isa_spec.md中的ISA规范
2. 生成汇编器/反汇编器/模拟器的测试用例
3. 覆盖所有必选指令
4. 包含正常和边界情况

要求：
- 测试用例完整
- 自动化执行
- 覆盖率报告""",
)


# 根Agent：按顺序执行
root_agent = SequentialAgent(
    name="Sirius_IsaToolAgent",
    description="Sirius GPGPU ISA工具Agent - 负责汇编器、反汇编器、ISA模拟器、测试用例",
    sub_agents=[
        assembler_gen_agent,
        disassembler_gen_agent,
        simulator_gen_agent,
        test_gen_agent,
    ],
)
