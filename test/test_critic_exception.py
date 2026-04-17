"""
测试 Style Critic 异常中是否包含模型原始返回

运行方式:
    cd S:/project/SlidesGen
    python test/test_critic_exception.py

测试场景:
1. 模拟 Pydantic 验证失败时的异常结构
2. 测试异常 str() 输出中包含的内容
3. 验证原始返回是否在异常中
"""

import json
from pydantic import BaseModel, Field, ValidationError


class StyleCritique(BaseModel):
    """模拟的风格审查模型"""
    is_approved: bool = Field(description="是否批准")
    critique: str = Field(description="审查意见")


def simulate_structured_output_with_markdown_response():
    """
    模拟场景：LLM 返回 Markdown 格式而非 JSON，Pydantic 验证失败
    """
    print("=" * 60)
    print("测试场景 1: LLM 返回 Markdown 而非 JSON")
    print("=" * 60)
    
    # 模拟 LLM 返回的 Markdown 格式文本（实际错误场景）
    mock_llm_response = """## Audit Result: **REJECTED**

### Issues Found:
1. Color scheme is wrong - Primary should be #005587 not #003366
2. Layout has issues - Header area is ~100px tall, not 160px as stated
3. Missing sections for cover page type

### Corrected Values:
| Item | Correct Value |
|------|---------------|
| Primary | #005587 |
| Header height | 100px |
"""
    
    print(f"\n[模拟 LLM 原始返回]\n{mock_llm_response[:500]}...")
    print(f"\n[返回长度] {len(mock_llm_response)} 字符")
    
    # 模拟 Pydantic 解析失败
    try:
        # 尝试解析为 JSON（会失败）
        parsed = json.loads(mock_llm_response)
        StyleCritique(**parsed)
    except json.JSONDecodeError as json_err:
        print(f"\n[JSON 解析异常]")
        print(f"  异常类型: {type(json_err).__name__}")
        print(f"  异常消息: {json_err}")
        print(f"  是否包含原始返回: {'Expecting value' in str(json_err)}")
        
    except ValidationError as val_err:
        print(f"\n[Pydantic 验证异常]")
        print(f"  异常类型: {type(val_err).__name__}")
        print(f"  异常消息: {val_err}")
        
        # 检查异常中是否有原始数据
        print(f"\n[异常结构分析]")
        print(f"  errors(): {val_err.errors()}")
        
    # 模拟 LangChain with_structured_output 的行为
    # 它内部会捕获 JSONDecodeError 并包装为 OutputParserException
    print("\n" + "-" * 40)
    print("模拟 LangChain with_structured_output 行为")
    print("-" * 40)
    
    try:
        # 这是 LangChain 内部会做的：尝试解析，失败则包装
        try:
            parsed = json.loads(mock_llm_response)
        except json.JSONDecodeError as inner_e:
            # LangChain 会包装这个异常
            raise Exception(f"Invalid JSON: {inner_e}") from inner_e
            
    except Exception as outer_e:
        print(f"\n[包装后的异常]")
        print(f"  异常类型: {type(outer_e).__name__}")
        print(f"  str(outer_e): {outer_e}")
        print(f"  \n  异常参数 (args): {outer_e.args}")
        
        # 检查 __cause__ (Python 3 异常链)
        if outer_e.__cause__:
            print(f"\n  __cause__ (原始异常): {outer_e.__cause__}")
            print(f"  __cause__ 类型: {type(outer_e.__cause__).__name__}")
        
        # 检查 __context__
        if outer_e.__context__:
            print(f"\n  __context__: {outer_e.__context__}")


def simulate_pydantic_json_invalid_error():
    """
    模拟实际的 Pydantic json_invalid 错误（从日志中观察到的格式）
    """
    print("\n" + "=" * 60)
    print("测试场景 2: 模拟日志中的 Pydantic 错误格式")
    print("=" * 60)
    
    # 从实际日志中提取的错误格式
    raw_response = """## Audit Result: **REJECTED**
Some long text here..."""
    
    error_msg = f"1 validation error for StyleCritique\n  Invalid JSON: expected value at line 1 column 1 [type=json_invalid, input_value='{raw_response[:50]}...or dark-bg page types |', input_type=str]"
    
    print(f"\n[模拟异常消息]\n{error_msg}")
    
    # 分析异常消息中包含了什么
    print(f"\n[内容分析]")
    print(f"  总长度: {len(error_msg)} 字符")
    print(f"  包含 'input_value': {'input_value=' in error_msg}")
    print(f"  包含原始响应片段: {raw_response[:30] in error_msg}")
    
    # 提取 input_value 内容
    import re
    match = re.search(r"input_value='([^']+)'", error_msg)
    if match:
        extracted = match.group(1)
        print(f"\n  提取到的 input_value: {extracted}")
        print(f"  input_value 长度: {len(extracted)} 字符")
        print(f"  是否被截断: {'...' in extracted}")


def simulate_actual_langchain_behavior():
    """
    更准确地模拟 LangChain 的异常结构
    """
    print("\n" + "=" * 60)
    print("测试场景 3: 模拟 LangChain OutputParserException")
    print("=" * 60)
    
    # LangChain 的 structured output 失败时通常会抛出 OutputParserException
    # 或 ValidationError
    
    raw_llm_output = """## Audit Result: **REJECTED**

### Color Issues
The color scheme needs correction.

### Layout Issues  
The header height is wrong."""

    class MockOutputParserException(Exception):
        """模拟 LangChain 的 OutputParserException"""
        def __init__(self, message, llm_output=None):
            super().__init__(message)
            self.llm_output = llm_output
    
    try:
        # 模拟解析失败
        try:
            json.loads(raw_llm_output)
        except json.JSONDecodeError as e:
            raise MockOutputParserException(
                f"Failed to parse. Got: {str(e)}",
                llm_output=raw_llm_output
            )
    except MockOutputParserException as e:
        print(f"\n[OutputParserException]")
        print(f"  str(e): {e}")
        print(f"  e.llm_output: {e.llm_output[:100] if e.llm_output else 'None'}...")
        print(f"  \n  llm_output 完整长度: {len(e.llm_output) if e.llm_output else 0}")


def test_pydantic_v2_error_details():
    """
    测试 Pydantic v2 的错误详情结构
    """
    print("\n" + "=" * 60)
    print("测试场景 4: Pydantic v2 错误详情结构")
    print("=" * 60)
    
    # Pydantic v2 的错误结构
    try:
        # 尝试用错误类型创建
        StyleCritique.model_validate_json("not json at all")
    except ValidationError as e:
        print(f"\n[ValidationError 详情]")
        print(f"  错误数量: {e.error_count()}")
        print(f"  错误列表: {json.dumps(e.errors(), indent=2, default=str)[:800]}")
        
        print(f"\n[str(e) 输出]")
        str_output = str(e)
        print(f"  长度: {len(str_output)}")
        print(f"  内容: {str_output[:500]}...")


def simulate_with_structured_output_api_response():
    """
    模拟实际 API 返回的解析错误场景
    """
    print("\n" + "=" * 60)
    print("测试场景 5: 模拟实际 API 调用 + 解析失败")
    print("=" * 60)
    
    # 模拟 OpenAI API 返回的内容（refusal 或格式错误）
    api_response_content = "I cannot provide that information."
    
    print(f"\n[模拟 API 返回]\n{api_response_content}")
    
    try:
        # 尝试解析为 JSON
        parsed = json.loads(api_response_content)
        StyleCritique(**parsed)
    except Exception as e:
        print(f"\n[解析失败]")
        print(f"  异常: {type(e).__name__}: {e}")
        print(f"\n  异常字符串表示:\n  {str(e)}")


if __name__ == "__main__":
    print("\n" + "[TEST] Style Critic 异常内容分析测试程序" + "\n")
    
    simulate_structured_output_with_markdown_response()
    simulate_pydantic_json_invalid_error()
    simulate_actual_langchain_behavior()
    test_pydantic_v2_error_details()
    simulate_with_structured_output_api_response()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("""
结论:
1. Pydantic ValidationError 的 str() 输出包含 input_value，但会被截断
2. 原始返回的完整内容需要通过其他方式获取（如 llm_output 属性）
3. 对于调试，建议在调用前/后添加日志记录原始返回
""")
