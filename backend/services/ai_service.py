import os
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Literal

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


Lang = Literal["zh", "en"]
Verdict = Literal["yes", "no", "irrelevant"]


@dataclass(frozen=True)
class AiReply:
    verdict: Verdict
    solved: bool
    reply: str


class AiService:
    """Minimal Turtle Soup judge.

    Intentionally loose: no strict output format, no parsing/fallback. We only pass the puzzle
    situation + truth to the model and return its natural reply.
    """

    @staticmethod
    def detect_language(text: str) -> Lang:
        if re.search(r"[\u4e00-\u9fff]", text or ""):
            return "zh"
        return "en"

    @staticmethod
    @staticmethod
    @lru_cache(maxsize=1)
    def _client():
        api_key = os.environ.get("ARK_API_KEY")
        if not api_key:
            raise ValueError("Missing API key: set ARK_API_KEY (Volcengine Ark).")
        return OpenAI(
            api_key=api_key,
            base_url=os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
        )

    @staticmethod
    def _model_name() -> str:
        return os.environ.get("ARK_MODEL", "doubao-seed-1-6-251015")

    @staticmethod
    def respond(
        description_zh: str,
        truth_zh: str,
        description_en: Optional[str],
        truth_en: Optional[str],
        user_text: str,
        lang: Optional[Lang] = None,
    ) -> AiReply:
        lang = lang or AiService.detect_language(user_text)

        situation = (description_en or description_zh) if lang == "en" else (description_zh or description_en or "")
        truth = (truth_en or truth_zh) if lang == "en" else (truth_zh or truth_en or "")

        if lang == "en":
            system = f"""
You are the judge/host of a Turtle Soup (Lateral Thinking) puzzle.
You are given both the Situation and the Truth.
The player will ask questions or propose explanations.
Reply naturally based on the Truth.
If the player has basically solved it, tell them they've solved it.

Situation:
{situation}

Truth:
{truth}
""".strip()
        else:
            system = f"""
你是海龟汤的裁判/主持人。
你会拿到题面和谜底。
玩家会提问或陈述推理。
请你基于谜底用自然语言回答,且你的回答表述出来的意思只能为“是”或“不是”或“无关”。
如果玩家已经基本猜中谜底，请直接告诉他“你已经猜对了”。

题面：
{situation}

谜底：
{truth}
""".strip()

        client = AiService._client()
        content = client.chat.completions.create(
            model=AiService._model_name(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_text},
            ],
            temperature=0.7,
        ).choices[0].message.content

        reply = (content or "").strip()
        solved = bool(
            re.search(
                r"(\byou(?:'| a)?ve\s+solved\b|\bsolved\b|\bcorrect\b|\bthat's it\b|你已经猜对了|你猜对了|你已经猜到了|猜对了|正确)",
                reply,
                flags=re.IGNORECASE,
            )
        )

        return AiReply(verdict="irrelevant", solved=solved, reply=reply)
