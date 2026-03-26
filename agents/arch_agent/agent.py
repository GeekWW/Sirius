from veadk import Agent, SequentialAgent
from pydantic import BaseModel


# 定义ISA规范输出模型
class InstructionSpec(BaseModel):
    opcode: str
    name: str
    description: str
    format: str
    opencl_operation: str
    type: str  # "必选" or "可选"


class ISASpec(BaseModel):
    arithmetic_instructions: list[InstructionSpec]
    logical_instructions: list[InstructionSpec]
    memory_instructions: list[InstructionSpec]
    control_flow_instructions: list[InstructionSpec]
    parallel_instructions: list[InstructionSpec]


# 定义微架构模块模型
class ModuleInterface(BaseModel):
    module_name: str
    inputs: list[str]
    outputs: list[str]
    description: str


class MicroarchSpec(BaseModel):
    modules: list[ModuleInterface]
    pipeline_stages: int
    description: str


# 子Agent 1: ISA精化Agent
isa_refine_agent = Agent(
    name="ISA_Refine_Agent",
    description="精化ISA规范，将README中的初步设计转化为完整的技术文档",
    instruction="""你是一位GPU架构师，负责精化Sirius GPGPU的ISA规范。

任务：
1. 读取项目README.md中的ISA设计
2. 将6大类指令（算术、逻辑、内存、控制流、并行、类型转换）完整定义
3. 为每条指令提供：opcode、名称、功能描述、操作数格式、对应OpenCL操作、类型（必选/可选）
4. 输出结构化的ISA规范

要求：
- 指令定义要完整、无歧义
- 操作数格式要清晰（8位+8位+8位等）
- 必选指令优先，可选指令补充
- 输出使用结构化格式""",
    model_extra_config={"response_format": ISASpec},
)


# 子Agent 2: 微架构设计Agent
microarch_agent = Agent(
    name="Microarch_Agent",
    description="设计微架构，拆分模块并定义接口",
    instruction="""你是一位GPU微架构设计师，负责Sirius GPGPU的微架构设计。

任务：
1. 基于ISA规范，设计完整的微架构
2. 拆分核心模块：取指、译码、执行、内存、缓存等
3. 定义每个模块的输入输出接口
4. 设计流水线阶段

要求：
- 模块边界清晰
- 接口定义无歧义
- 考虑简化版超标量、乱序执行的实现
- 提供完整的模块列表和接口定义""",
    model_extra_config={"response_format": MicroarchSpec},
)


# 子Agent 3: 文档生成Agent
doc_gen_agent = Agent(
    name="Doc_Gen_Agent",
    description="生成完整的架构设计文档",
    instruction="""你是一位技术文档工程师，负责将架构设计转化为清晰的Markdown文档。

任务：
1. 接收ISA规范和微架构设计
2. 生成三个文档：
   - docs/architecture/isa_spec.md
   - docs/architecture/microarch.md
   - docs/architecture/module_interfaces.md
3. 文档结构清晰，便于后续开发

要求：
- Markdown格式规范
- 章节结构清晰
- 代码示例正确
- 图表使用Mermaid格式""",
)


# 根Agent：按顺序执行
root_agent = SequentialAgent(
    name="Sirius_ArchAgent",
    description="Sirius GPGPU架构设计Agent - 负责ISA精化、微架构设计、文档生成",
    sub_agents=[
        isa_refine_agent,
        microarch_agent,
        doc_gen_agent,
    ],
)
