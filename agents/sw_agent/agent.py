from veadk import Agent, SequentialAgent
from pydantic import BaseModel


# 定义LLVM后端输出模型
class LLVMBackendModule(BaseModel):
    module_name: str
    code: str


class LLVMBackendOutput(BaseModel):
    modules: list[LLVMBackendModule]
    success: bool
    errors: list[str]


# 子Agent 1: LLVM后端生成Agent
llvm_backend_gen_agent = Agent(
    name="LLVM_Backend_Gen_Agent",
    description="生成LLVM后端代码",
    instruction="""你是一位编译器工程师，负责生成Sirius GPGPU的LLVM后端代码。

任务：
1. 读取isa_spec.md中的ISA规范
2. 生成LLVM后端代码
3. 支持所有必选指令
4. 实现指令选择、寄存器分配、代码生成

要求：
- 遵循LLVM后端规范
- 代码结构清晰
- 带注释
- 可编译""",
    model_extra_config={"response_format": LLVMBackendOutput},
)


# 子Agent 2: OpenCL运行时生成Agent
ocl_runtime_gen_agent = Agent(
    name="OCL_Runtime_Gen_Agent",
    description="生成OpenCL运行时代码",
    instruction="""你是一位运行时工程师，负责生成Sirius GPGPU的OpenCL运行时代码。

任务：
1. 读取isa_spec.md中的ISA规范
2. 读取microarch.md中的微架构设计
3. 生成OpenCL运行时代码
4. 实现平台层、命令队列、内存管理

要求：
- 遵循OpenCL 1.2标准
- 代码结构清晰
- 带注释
- 可编译""",
)


# 子Agent 3: 驱动程序生成Agent
driver_gen_agent = Agent(
    name="Driver_Gen_Agent",
    description="生成驱动程序代码",
    instruction="""你是一位驱动工程师，负责生成Sirius GPGPU的驱动程序代码。

任务：
1. 读取module_interfaces.md中的模块接口定义
2. 生成Linux内核驱动或用户空间驱动
3. 实现设备发现、内存映射、命令提交

要求：
- 代码结构清晰
- 带注释
- 可编译""",
)


# 子Agent 4: 示例程序生成Agent
examples_gen_agent = Agent(
    name="Examples_Gen_Agent",
    description="生成示例程序",
    instruction="""你是一位软件工程师，负责生成Sirius GPGPU的示例程序。

任务：
1. 生成5个OpenCL示例程序
2. 涵盖向量加法、矩阵乘法、卷积等
3. 包含Makefile和编译脚本

要求：
- 示例代码可运行
- 带注释
- 自动化构建""",
)


# 根Agent：按顺序执行
root_agent = SequentialAgent(
    name="Sirius_SwAgent",
    description="Sirius GPGPU软件栈Agent - 负责LLVM后端、OpenCL运行时、驱动程序",
    sub_agents=[
        llvm_backend_gen_agent,
        ocl_runtime_gen_agent,
        driver_gen_agent,
        examples_gen_agent,
    ],
)
