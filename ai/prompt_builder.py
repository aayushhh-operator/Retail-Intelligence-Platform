"""Prompt Construction."""
from pathlib import Path
from ai.schema_loader import load_schema

PROMPTS_DIR = Path(__file__).parent / "prompts"

def build_sql_prompt(question: str) -> str:
    schema = load_schema()
    with open(PROMPTS_DIR / "sql_generation_prompt.txt", "r") as f:
        template = f.read()
    return template.format(schema=schema, question=question)

def build_explanation_prompt(question: str, sql: str, data_summary: str) -> str:
    with open(PROMPTS_DIR / "explanation_prompt.txt", "r") as f:
        template = f.read()
    return template.format(question=question, sql=sql, data_summary=data_summary)
