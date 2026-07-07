"""AI Analyst Orchestrator."""
from ai.prompt_builder import build_sql_prompt, build_sql_correction_prompt
from ai.llm import generate_completion
from ai.sql_executor import execute_sql
from ai.result_formatter import format_dataframe
from ai.insight_generator import generate_insight
from ai.chart_generator import generate_chart
import time

class AIAnalystAgent:
    def process_query(self, user_question: str) -> dict:
        result = {"sql": "", "df": None, "chart": None, "explanation": "", "error": None, "execution_time": 0}
        try:
            start_time = time.time()
            # 1. Generate SQL
            sql_prompt = build_sql_prompt(user_question)
            raw_sql = generate_completion([{"role": "user", "content": sql_prompt}])
            result["sql"] = raw_sql
            
            # 2. Execute SQL with Self-Correction Retry Loop
            df = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    df = execute_sql(raw_sql)
                    result["sql"] = raw_sql # Update with the successful one if it changed
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        # Self-correct
                        correction_prompt = build_sql_correction_prompt(user_question, raw_sql, str(e))
                        raw_sql = generate_completion([{"role": "user", "content": correction_prompt}])
                    else:
                        raise e
            
            result["df"] = df
            result["execution_time"] = round(time.time() - start_time, 2)
            
            # 3. Format and Generate Insights
            data_summary = format_dataframe(df)
            result["explanation"] = generate_insight(user_question, raw_sql, data_summary)
            
            # 4. Generate Chart
            result["chart"] = generate_chart(df)
            
        except Exception as e:
            result["error"] = str(e)
            
        return result
