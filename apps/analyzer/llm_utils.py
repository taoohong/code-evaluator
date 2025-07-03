import re
from groq import Groq
from django.conf import settings

# Initialize Groq client with API key from settings
client = Groq(
    api_key=settings.GROQ_API_KEY,
)

def build_prompt(content, file_type):
    if file_type == "sql":
        return f"""
请使用中文对以下 SQL 文件内容进行风险分析。

要求：
1. 风险点识别范围：以下常见SQL风险点分类及建议评分范围（可多选）：

- SQL注入风险，8-10分
- 缺少WHERE条件，7-9分
- 使用SELECT *，4-6分
- 没有LIMIT，5-7分
- 子查询性能差，6-10分
- 不走索引，5-8分
- 数据类型不匹配，2-5分
- 大事务无拆分，7-10分
- 重复数据插入，6-9分
- NULL 条件遗漏，3-5分
- 表设计不规范，3-7分
- 可重复执行风险，6-8分
- SQL语法错误，8-10分

2. 列出所有潜在风险点，每个风险点需包含以下字段：
- 风险点描述
- 风险原因说明
- 风险等级具体评分（1~10分，越高风险越大）
- 修改建议（中文）

3. 输出格式：严格使用 JSON 数组，每个风险点一个对象，字段如下：

[
  {{
    "风险点": "SQL注入风险",
    "原因": "存在动态拼接SQL，未使用参数化",
    "风险分": 9,
    "修改建议": "请使用参数化查询替代字符串拼接"
  }},
  ...
]

4.  必须严格遵守 JSON 数组格式，不输出任何多余文本，不输出任何解释、分析过程、系统提示、思考过程等。

以下是 SQL 文件内容：
{content}
"""
    else:
        return f"""
请使用中文评估以下代码文件的质量，重点关注可读性、可维护性、性能、安全性、编码风格一致性。请给出一个 0 到 100 的评分，并提供详细改进建议。

内容如下：
{content}
"""


def call_groq_llm(content, file_type):
    prompt = build_prompt(content, file_type)
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="deepseek-r1-distill-llama-70b",
            temperature=0.6,
        )
        return extract_json_array(chat_completion.choices[0].message.content)
    except Exception as e:
        return {"evalution": f"Error calling Groq API: {e}"}
    
def extract_json_array(text: str) -> str:
    print(f"原始 LLM 输出: {text}")
    try:
        # 正则匹配第一个 JSON 数组 (包括换行，空格等)
        json_array_pattern = re.compile(r'(\[\s*\{.*?\}\s*\])', re.DOTALL)
        match = json_array_pattern.search(text)
        if match:
            json_text = match.group(1)
            return json_text
        raise ValueError("无法在 LLM 输出中找到有效 JSON 数组。")
    except Exception as e:
        raise ValueError(f"JSON 提取失败: {e}")