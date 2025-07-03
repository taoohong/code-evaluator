import re

from django.conf import settings
from groq import Groq

# Initialize Groq client with API key from settings
client = Groq(
    api_key=settings.GROQ_API_KEY,
)


def build_sql_prompt(content):
    return f"""
请使用中文对以下 SQL 文件内容进行风险分析。

要求：
1. 风险点识别范围：以下常见SQL风险点分类及建议风险分评分范围（可多选）：

- SQL注入风险，风险分8-10分
- 缺少WHERE条件，风险分7-9分
- 使用SELECT *，风险分4-6分
- 没有LIMIT，风险分5-7分
- 子查询性能差，风险分6-10分
- 不走索引，风险分5-8分
- 数据类型不匹配，风险分2-5分
- 大事务无拆分，风险分7-10分
- 重复数据插入，风险分6-9分
- NULL 条件遗漏，风险分3-5分
- 表设计不规范，风险分3-7分
- 可重复执行风险，风险分6-8分
- SQL语法错误，风险分8-10分

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


def build_code_prompt(content):
    return f"""
请使用中文对以下编程文件内容进行静态风险分析。

---

要求：
1. 确定文件使用的编程语言类型，并根据语言特性进行分析（可能为 Python、Java、C++ 等）。

2. 从以下常见风险点分类中识别所有存在的问题以及建议风险分评分范围（可多选）：

- 命令注入风险（如不可信输入拼接系统命令），风险分 7-9
- 输入校验缺失（未校验用户输入），风险分 7-9
- SQL 注入风险（编程中构造 SQL 时拼接），风险分7-9
- 敏感信息泄露（如硬编码密码、密钥），风险分 8-10
- 异常处理不当（未捕获异常或过度捕获），风险分 6-8
- XSS/HTML 注入（如拼接 HTML 无过滤），风险分7-10
- 函数过长（超过 80~100 行），风险分1-3
- 重复代码（Copy-Paste 编程），风险分4-6
- 缺乏注释（无函数/关键逻辑注释），风险分2-4
- 文件操作未关闭（未使用 with/finally），风险分 5-7
- 使用过时函数/库（如 Python 2 语法），风险分5-7
- 魔法数字/硬编码（未定义为常量），风险分1-3
- 全局变量滥用，风险分1-3
- 潜在死循环，风险分 6-8
- 多线程不安全/锁缺失，风险分 7-9
- 资源泄露（如未关闭文件、网络连接），风险分 6-8
- 内存泄漏（C/C++）: 风险分 7-9

3. 每个风险点输出以下字段：

- 风险点（名称）
- 原因说明（简洁中文）
- 风险分（1~10，分数越高风险越大）
- 修改建议（中文）

4. 输出格式：标准 JSON 数组，如下格式：

[
  {{
    "风险点": "命令注入风险",
    "原因": "用户输入未校验直接拼接进 os.system 命令中",
    "风险分": 9,
    "修改建议": "请使用安全 API 或严格校验输入"
  }},
  ...
]

5. 必须严格遵守 JSON 数组格式，不输出任何多余文本，不输出任何解释、分析过程、系统提示、思考过程、总结或 markdown等。

---

以下是文件内容：
{content}
"""


def build_prompt(content, file_type):
    if file_type == "sql":
        return build_sql_prompt(content)
    else:
        return build_code_prompt(content)


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
        json_array_pattern = re.compile(r"(\[\s*\{.*?\}\s*\])", re.DOTALL)
        match = json_array_pattern.search(text)
        if match:
            json_text = match.group(1)
            return json_text
        raise ValueError("无法在 LLM 输出中找到有效 JSON 数组。")
    except Exception as e:
        raise ValueError(f"JSON 提取失败: {e}")
