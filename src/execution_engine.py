import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import re
import requests
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import settings
from src.llm_engine import generate_sql, OLLAMA_API_URL, MODEL_NAME, GROQ_MODEL, get_groq_api_key

def execute_sql_query(sql_query: str) -> tuple[pd.DataFrame | None, str | None]:
    """Module 5.1: Safely executes a SQL query against PostgreSQL and returns a Pandas DataFrame."""
    engine = create_engine(settings.DATABASE_URL)
    try:
        # Using SQLAlchemy text() construct for secure execution
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df, None
    except Exception as e:
        return None, str(e)

def execute_with_self_correction(user_question: str, max_retries: int = 2) -> tuple[str, pd.DataFrame]:
    """Module 5.2: Self-correction loop that retries and fixes SQL if database throws an error."""
    # Step 1: Initial LLM Generation
    sql_res = generate_sql(user_question)
    current_sql = sql_res.cleaned_sql
    
    print(f"\n[Attempt 1] Executing SQL:\n{current_sql}")
    df, error = execute_sql_query(current_sql)
    
    retries = 0
    while error and retries < max_retries:
        retries += 1
        print(f"\n[Warning] Database Error Encountered: {error}")
        print(f"-> Initiating Self-Correction Loop (Attempt {retries}/{max_retries})...")
        
        # Build self-correction prompt containing the failed query and the explicit DB error
        correction_prompt = f"""You are an expert PostgreSQL developer. 
The previous SQL query failed to execute against the database. 
Fix the query based on the error message provided below.

=== USER QUESTION ===
{user_question}

=== FAILED SQL QUERY ===
{current_sql}

=== DATABASE ERROR ===
{error}

=== RULES ===
1. Return ONLY the corrected raw SQL query. No markdown formatting, code ticks, or explanations.
2. Fix the syntax or column/table mismatch identified in the error message.

Corrected SQL Query:"""

        groq_api_key = get_groq_api_key()

        # Use Groq Cloud SDK if API key is present (Cloud Deployment Mode)
        if groq_api_key:
            from groq import Groq
            try:
                client = Groq(api_key=groq_api_key)
                completion = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert PostgreSQL database engineer that outputs only raw SQL queries."},
                        {"role": "user", "content": correction_prompt}
                    ],
                    temperature=0.0
                )
                raw_text = completion.choices[0].message.content.strip()
            except Exception as e:
                raise ConnectionError(f"Failed to connect to Groq API during self-correction: {str(e)}")
        
        # Otherwise, fallback to local Ollama
        else:
            payload = {
                "model": MODEL_NAME if MODEL_NAME else "phi3",
                "prompt": correction_prompt,
                "stream": False,
                "options": {"temperature": 0.0}
            }
            try:
                response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
                response.raise_for_status()
                raw_text = response.json().get("response", "").strip()
            except Exception as e:
                raise ConnectionError(f"Could not connect to Ollama during self-correction: {str(e)}")
        
        # Clean response
        current_sql = re.sub(r"```sql|```", "", raw_text).strip()
        
        print(f"-> Retrying with corrected SQL:\n{current_sql}")
        df, error = execute_sql_query(current_sql)
        
    if error:
        raise RuntimeError(f"Query failed after {max_retries} self-correction attempts. Final Error: {error}")
        
    print("\nQuery executed successfully!")
    return current_sql, df

if __name__ == "__main__":
    print("--- Phase 5: Testing Self-Correction Execution Engine ---")
    
    test_question = "List all customers living in Coimbatore."
    final_sql, results_df = execute_with_self_correction(test_question)
    
    print(f"\n=== FINAL SUCCESSFUL SQL ===")
    print(final_sql)
    
    print(f"\n=== QUERY RESULTS (Pandas DataFrame) ===")
    print(results_df)