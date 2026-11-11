import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import re
import streamlit as st
from pydantic import BaseModel, Field
from src.rag_engine import retrieve_relevant_schema

# Configuration for Local vs Cloud
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"
GROQ_MODEL = "openai/gpt-oss-20b"

def get_groq_api_key():
    """Safely fetch Groq API key from Streamlit secrets or environment variables."""
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY")

class SQLResponse(BaseModel):
    raw_response: str
    cleaned_sql: str = Field(..., description="Extracted executable SQL query")

def build_prompt(user_question: str, schema_context: str) -> str:
    """Module 4.3: Engineers a strict Text-to-SQL prompt merging schema context and safety guardrails."""
    return f"""You are an expert PostgreSQL database engineer.
Your task is to write a precise, syntactically correct PostgreSQL query based ONLY on the provided schema context below.

=== DATABASE SCHEMA CONTEXT ===
{schema_context}

=== RULES ===
1. Return ONLY the raw SQL query. Do not include markdown code ticks (like ```sql), conversational filler, or explanations.
2. Use exact table and column names as defined in the schema.
3. Do NOT perform an INNER JOIN with the `orders` table unless the user explicitly asks about orders, purchases, or order status.
4. For simple queries asking for customer lists, names, or locations (e.g., "customers from Bengaluru"), query ONLY the `customers` table directly.
5. Ensure proper JOINs are used only when multiple tables are strictly necessary based on the question.

=== USER QUESTION ===
{user_question}

SQL Query:"""

def generate_sql(user_question: str) -> SQLResponse:
    """Module 4.2 & 7.1: Dual-mode LLM engine supporting local Ollama and Groq cloud SDK fallback."""
    print(f"Retrieving relevant schema context for: '{user_question}'...")
    schema_chunks = retrieve_relevant_schema(user_question, n_results=3)
    schema_context = "\n\n".join(schema_chunks)

    prompt = build_prompt(user_question, schema_context)
    groq_api_key = get_groq_api_key()

    # Use Groq Cloud SDK if API key is present (Cloud Deployment Mode)
    if groq_api_key:
        from groq import Groq
        print(f"Sending prompt to Groq Cloud API ({GROQ_MODEL})...")
        try:
            client = Groq(api_key=groq_api_key)
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert PostgreSQL database engineer that outputs only raw SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            raw_text = completion.choices[0].message.content.strip()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Groq API: {str(e)}")

    # Otherwise, fallback to local Ollama (Local Development Mode)
    else:
        import requests
        print(f"Sending prompt to local Ollama ({OLLAMA_MODEL})...")
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
            response.raise_for_status()
            result_json = response.json()
            raw_text = result_json.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Could not connect to Ollama and no Groq API key found. Make sure Ollama is running locally or GROQ_API_KEY is configured in Streamlit secrets.")

    # Clean and extract SQL using regex parsing
    cleaned = re.sub(r"```sql|```", "", raw_text).strip()

    # Validate through Pydantic model
    validated_output = SQLResponse(
        raw_response=raw_text,
        cleaned_sql=cleaned
    )
    return validated_output

if __name__ == "__main__":
    print("--- Phase 7: Testing Dual-Mode LLM SQL Generation Engine ---")
    test_question = "List all customers living in Coimbatore."

    sql_result = generate_sql(test_question)

    print("\n=== GENERATED SQL RESULT ===")
    print(f"Raw LLM Output:\n{sql_result.raw_response}\n")
    print(f"Cleaned Executable SQL:\n{sql_result.cleaned_sql}")