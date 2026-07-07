"""Generate business explanations."""

from ai.llm import generate_completion
from ai.prompt_builder import build_explanation_prompt


def generate_insight(question: str, sql: str, data_summary: str) -> str:
    prompt = build_explanation_prompt(question, sql, data_summary)
    return generate_completion([{"role": "user", "content": prompt}])
