# Phase 10: AI-powered Data Analyst Agent

This directory contains the logic for the natural language analytics assistant. The agent is capable of dynamically reading the PostgreSQL warehouse schemas, formulating valid read-only SQL based on user queries, executing the SQL securely, generating visualizations, and returning business insights.

## Architecture

1. **Schema Loader (`schema_loader.py`)**: Automatically scans the PostgreSQL database (`information_schema`) to provide the LLM with live table definitions without hardcoding.
2. **Prompt Builder (`prompt_builder.py`)**: Injects the live schema and the user's question into strict system prompts.
3. **Groq LLM (`llm.py`)**: Fast inference engine utilizing the `openai/gpt-oss-120b` alias (or other configured Llama/Mixtral models).
4. **SQL Validator (`sql_validator.py`)**: **Strict Security Layer**. Uses Regex to absolutely block any `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, or semicolon-chained statements. If the LLM hallucinates DML, the request is immediately rejected before touching the database.
5. **Chart & Insight Generators**: Converts the SQL output into Plotly charts and natural language explanations.
6. **Streamlit Integration**: A fully functional chat UI located in `dashboard/pages/8_ai_analyst.py`.

---

## Manual Configuration Required

To run the AI Data Analyst Agent, you must complete the following manual configuration steps:

### 1. Environment Variables (`.env`)
You must add a valid Groq API Key to your `.env` file at the root of the project:
```env
GROQ_API_KEY=your_groq_api_key_here
```
*(You can get a free API key at [console.groq.com](https://console.groq.com)).*

Ensure your database connection variables remain populated:
```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=RetailIntelligencePlatform
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
```

### 2. Dependencies Added
The following package is required for the LLM client:
- `groq`

### 3. Changes to `requirements.txt`
Run the following in your terminal to install the new dependency:
```bash
pip install groq
```
*(The dependency has automatically been appended to `requirements.txt`).*

### 4. Dashboard Changes
No manual dashboard changes are required! A new page `8_ai_analyst.py` has been seamlessly integrated into your Streamlit left-hand sidebar.

### 5. Docker / Airflow / PostgreSQL Changes
None. The AI agent acts as a read-only client connecting over standard JDBC/SQLAlchemy protocols.

### 6. How to Launch
Make sure your PostgreSQL database is running (either via Docker or locally).
Then, launch the Streamlit app:
```bash
streamlit run dashboard/app.py
```
Navigate to the **🤖 AI Data Analyst** page on the sidebar.

### 7. Example Prompts to Test
- *"What is our total revenue for the entire platform?"*
- *"Show me the top 5 highest selling products by revenue."*
- *"Which region generated the most orders?"*
- *"Show me a list of all Airflow DAGs that have run recently."*

### 8. Troubleshooting
- **`AuthenticationError` from Groq**: Ensure your `GROQ_API_KEY` is correct in the `.env` file.
- **`UnsafeSQLError`**: The LLM hallucinated a modifying query (like `UPDATE`). Simply re-prompt the agent.
- **Database Connection Failed**: Ensure PostgreSQL is running and the `.env` DB variables match your environment.
- **Model not found**: If Groq removes the `openai/gpt-oss-120b` alias, you can change `MODEL_NAME` in `ai/config.py` to `llama3-70b-8192`.
