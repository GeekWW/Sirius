from veadk import Agent, SequentialAgent
from pydantic import BaseModel


# 定义RTL模块输出模型
class RTLModule(BaseModel):
    module_name: str
    ports: list[dict]
    code: str


class RTLOutput(BaseModel):
    modules: list[RTLModule]
    success: bool
    errors: list[str]


# 子Agent 1: 取指模块生成Agent
fetch_gen_agent = Agent(
    name="Fetch_Gen_Agent",
    description="生成取指模块RTL代码",
    instruction="""你是一位硬件工程师，负责生成Sirius GPGPU的取指模块RTL代码。

任务：
1. 读取microarch.md中的微架构设计
2. 读取module_interfaces.md中的模块接口定义
3. 生成Verilog RTL代码
4. 实现PC生成、指令缓存访问、分支预测

要求：
- 遵循模块接口定义
- 代码结构清晰
- 带注释
- 可综合的Verilog""",
    model_extra_config={"response_format": RTLOutput},
)


# 子Agent 2: 译码模块生成Agent
decode_gen_agent = Agent(
    name="Decode_Gen_Agent",
    description="生成译码模块RTL代码",
    instruction="""你是一位硬件工程师，负责生成Sirius GPGPU的译码模块RTL代码。

任务：
1. 读取isa_spec.md中的ISA规范
2. 读取module_interfaces.md中的模块接口定义
3. 生成Verilog RTL代码
4. 实现指令译码、寄存器重命名、操作数读取

要求：
- 支持所有必选指令
- 遵循模块接口定义
- 代码结构清晰
- 带注释
- 可综合的Verilog""",
    model_extra_config={"response_format": RTLOutput},
)


# 子Agent 3: 执行模块生成Agent
execute_gen_agent = Agent(
    name="Execute_Gen_Agent",
    description="生成执行模块RTL代码",
    instruction="""你是一位硬件工程师，负责生成Sirius GPGPU的执行模块RTL代码。

任务：
1. 读取microarch.md中的微架构设计
2. 读取module_interfaces.md中的模块接口定义
3. 生成Verilog RTL代码
4. 实现ALU、FPU、分支单元、比较单元

要求：
- 实现整数和浮点运算
- 遵循模块接口定义
- 代码结构清晰
- 带注释
- 可综合的Verilog""",
    model_extra_config={"response_format": RTLOutput},
)


# 子Agent 4: 访存模块生成Agent
memory_gen_agent = Agent(
    name="Memory_Gen_Agent",
    description="生成访存模块RTL代码",
    instruction="""你是一位硬件工程师，负责生成Sirius GPGPU的访存模块RTL代码。

任务：
1. 读取microarch.md中的微架构设计
2. 读取module_interfaces.md中的模块接口定义
3. 生成Verilog RTL代码
4. 实现加载/存储队列、L1数据缓存访问

要求：
- 支持四种内存空间
- 遵循模块接口定义
- 代码结构清晰
- 带注释
- 可综合的Verilog""",
    model_extra_config={"response_format": RTLOutput},
)


# 子Agent 5: 写回模块生成Agent
writeback_gen_agent = Agent(
    name="Writeback_Gen_Agent",
    description="生成写回模块RTL代码",
    instruction="""你是一位硬件工程师，负责生成Sirius GPGPU的写回模块RTL代码。

任务：
1. 读取microarch.md中的微架构设计
2. 读取module_interfaces.md中的模块接口定义
3. 生成Verilog RTL代码
4. 实现结果写回、ROB提交

要求：
- 遵循模块接口定义
- 代码结构清晰
- 带注释
- 可综合的Verilog""",
    model_extra_config={"response_format": RTLOutput},
)


# 子Agent 6: 测试平台生成Agent
testbench_gen_agent = Agent(
    name="Testbench_Gen_Agent",
    description="生成测试平台和仿真脚本",
    instruction="""你是一位验证工程师，负责生成Sirius GPGPU的测试平台和仿真脚本。

任务：
1. 生成各模块的测试平台（Testbench）
2. 生成仿真脚本（Makefile、仿真器调用）
3. 生成简单的测试向量

要求：
- 支持基本功能验证
- 带波形输出
- 自动化测试""",
)


# 根Agent：按顺序执行
root_agent = SequentialAgent(
    name="Sirius_HwAgent",
    description="Sirius GPGPU硬件实现Agent - 负责Verilog RTL、FPGA原型",
    sub_agents=[
        fetch_gen_agent,
        decode_gen_agent,
        execute_gen_agent,
        memory_gen_agent,
        writeback_gen_agent,
        testbench_gen_agent,
    ],
)
