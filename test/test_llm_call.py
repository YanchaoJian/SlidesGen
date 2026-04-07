"""第三方 OpenAI 兼容接口连通性测试。

用法:
    python test/test_llm_call.py                       # 使用默认模型 gpt-4o
    python test/test_llm_call.py gpt-5.3-codex         # 手动指定模型
    python test/test_llm_call.py gemini-3.1-pro-preview "用一句话介绍你自己"
"""
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_MODEL = "Qwen/Qwen3.5-35B-A3B"
DEFAULT_PROMPT = "Reply with exactly: pong"


def main() -> int:
    model = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
    prompt = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PROMPT

    base_url = os.environ.get("MS_BASE_URL")
    api_key = os.environ.get("MS_API_KEY")
    if not base_url or not api_key:
        print("[ERROR] MS_BASE_URL / MS_API_KEY 未在 .env 中设置")
        return 1

    print(f"[INFO] base_url = {base_url}")
    print(f"[INFO] model    = {model}")
    print(f"[INFO] prompt   = {prompt}")
    print("-" * 60)

    client = OpenAI(base_url=base_url, api_key=api_key)

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
    except Exception as e:
        print(f"[FAIL] 调用失败: {type(e).__name__}: {e}")
        return 2

    choice = resp.choices[0]
    content = choice.message.content
    usage = getattr(resp, "usage", None)

    print(f"[OK] finish_reason = {choice.finish_reason}")
    if usage:
        print(f"[OK] usage         = prompt={usage.prompt_tokens} "
              f"completion={usage.completion_tokens} total={usage.total_tokens}")
    print("-" * 60)
    print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
