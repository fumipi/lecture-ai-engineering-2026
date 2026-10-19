"""第1回: 素のLLMに会話履歴を保って質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"  # 最初の質問を指定
    uv run python -m app.ask                         # 講座に固有の質問から開始

ツールは持たないが、同じチャット内の会話履歴は保持する「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(chat, question: str) -> str:
    response = chat.send_message(question)

    if response.usage_metadata is not None:
        usage = response.usage_metadata
        print(
            f"[トークン数] 入力: {usage.prompt_token_count}, "
            f"出力: {usage.candidates_token_count}"
        )

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="会話履歴を保って素のLLMに質問する")
    parser.add_argument("question", nargs="?")
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    try:
        client = genai.Client(api_key=get_api_key())
        chat = client.chats.create(model=MODEL)
        question = args.question or DEFAULT_QUESTION
        while True:
            print(f"[質問] {question}\n")
            print(ask(chat, question))
            try:
                question = input("\n次の質問（空行 / exit で終了）: ").strip()
            except EOFError:
                break
            if not question or question.lower() in {"exit", "quit"}:
                break
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
