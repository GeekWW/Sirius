from veadk import Agent, SequentialAgent
from pydantic import BaseModel


# 定义测试用例输出模型
class TestCase(BaseModel):
    test_name: str
    test_type: str
    code: str


class TestOutput(BaseModel):
    test_cases: list[TestCase]
    success: bool
    errors: list[str]


# 子Agent 1: 单元测试生成Agent
unit_test_gen_agent = Agent(
    name="Unit_Test_Gen_Agent",
    description="生成单元测试用例",
    instruction="""你是一位验证工程师，负责生成Sirius GPGPU的单元测试用例。

任务：
1. 读取isa_spec.md中的ISA规范
2. 生成汇编器/反汇编器/模拟器的单元测试
3. 覆盖所有必选指令
4. 包含正常和边界情况

要求：
- 测试用例完整
- 自动化执行
- 带断言检查""",
    model_extra_config={"response_format": TestOutput},
)


# 子Agent 2: 集成测试生成Agent
integration_test_gen_agent = Agent(
    name="Integration_Test_Gen_Agent",
    description="生成集成测试用例",
    instruction="""你是一位验证工程师，负责生成Sirius GPGPU的集成测试用例。

任务：
1. 读取各模块的输出
2. 生成端到端集成测试
3. 测试完整流程：编译 → 汇编 → 模拟执行
4. 包含向量加法、矩阵乘法等示例

要求：
- 端到端测试
- 自动化执行
- 结果验证""",
)


# 子Agent 3: 形式化验证生成Agent
formal_ver_gen_agent = Agent(
    name="Formal_Ver_Gen_Agent",
    description="生成形式化验证脚本",
    instruction="""你是一位形式化验证工程师，负责生成Sirius GPGPU的形式化验证脚本。

任务：
1. 读取microarch.md中的微架构设计
2. 读取module_interfaces.md中的模块接口定义
3. 生成关键模块的形式化验证脚本
4. 验证关键不变量

要求：
- 关键模块验证
- 不变量检查
- 可自动化执行""",
)


# 子Agent 4: 覆盖率报告生成Agent
coverage_gen_agent = Agent(
    name="Coverage_Gen_Agent",
    description="生成覆盖率报告脚本",
    instruction="""你是一位验证工程师，负责生成Sirius GPGPU的覆盖率报告脚本。

任务：
1. 生成测试覆盖率收集脚本
2. 生成覆盖率报告模板
3. 支持代码覆盖率、功能覆盖率

要求：
- 覆盖率收集自动化
- 报告清晰易读
- 支持HTML/文本输出""",
)


# 根Agent：按顺序执行
root_agent = SequentialAgent(
    name="Sirius_VerifyAgent",
    description="Sirius GPGPU验证Agent - 负责测试用例、形式化验证",
    sub_agents=[
        unit_test_gen_agent,
        integration_test_gen_agent,
        formal_ver_gen_agent,
        coverage_gen_agent,
    ],
)
